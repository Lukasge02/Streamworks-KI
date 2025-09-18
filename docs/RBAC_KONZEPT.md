# Streamworks-KI RBAC-System - Entwicklungskonzept

> **Vereinfachtes 3-Stufen RBAC-System für Development**
> Owner → Streamworks Admin → Kunde mit JWT-Authentifizierung

---

## 📋 **System-Übersicht**

**Streamworks-KI** erhält ein benutzerfreundliches RBAC-System mit:
- **3-Stufen Rollenhierarchie** (Owner, Streamworks Admin, Kunde)
- **JWT-basierte Authentifizierung** ohne E-Mail-Verifikation (Dev-Phase)
- **Multi-Tenant Architektur** mit Company-Isolation
- **Einfache Registrierung/Login** für schnelle Entwicklung

---

## 🏗️ **Datenbank-Schema**

### **Neue Tabellen**

#### **1. users - Benutzer-Management**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'kunde',
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,

    -- Status und Metadaten
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT check_role CHECK (role IN ('owner', 'streamworks_admin', 'kunde')),
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indizes für Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_company_id ON users(company_id);
CREATE INDEX idx_users_role ON users(role);
```

#### **2. companies - Mandanten-Verwaltung**
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),

    -- Metadaten
    settings JSONB DEFAULT '{}'::jsonb,
    created_by_owner UUID REFERENCES users(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(domain)
);

-- Indizes
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_created_by ON companies(created_by_owner);
```

#### **3. user_sessions - Session-Management (Optional)**
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    jwt_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Metadaten für Security
    ip_address INET,
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT false
);

-- Indizes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
```

### **Erweiterte bestehende Tabellen**

#### **Migration bestehender Tabellen**
```sql
-- Dokumente erweitern
ALTER TABLE documents
ADD COLUMN user_id UUID REFERENCES users(id),
ADD COLUMN company_id UUID REFERENCES companies(id);

-- Ordner erweitern
ALTER TABLE folders
ADD COLUMN user_id UUID REFERENCES users(id),
ADD COLUMN company_id UUID REFERENCES companies(id);

-- XML-Streams erweitern
ALTER TABLE xml_streams
ADD COLUMN user_id UUID REFERENCES users(id),
ADD COLUMN company_id UUID REFERENCES companies(id);

-- Chat-Sessions erweitern
ALTER TABLE chat_sessions
ADD COLUMN company_id UUID REFERENCES companies(id);

-- Chat-XML-Sessions erweitern
ALTER TABLE chat_xml_sessions
ADD COLUMN company_id UUID REFERENCES companies(id);
```

---

## 🎯 **Rollen & Berechtigungen**

### **1. Owner (System-Eigentümer)**
```python
OWNER_PERMISSIONS = {
    "system": ["full_access", "create_admins", "system_config"],
    "users": ["create", "read", "update", "delete", "manage_roles"],
    "companies": ["create", "read", "update", "delete"],
    "documents": ["all_companies_read", "all_companies_write"],
    "xml_streams": ["all_companies_read", "all_companies_write"],
    "chat": ["all_companies_read", "monitor"],
    "admin_panel": ["full_access"]
}
```

### **2. Streamworks Admin**
```python
STREAMWORKS_ADMIN_PERMISSIONS = {
    "users": ["create_customers", "read_customers", "update_customers"],
    "companies": ["read_assigned", "update_assigned"],
    "documents": ["company_read", "company_write", "support_access"],
    "xml_streams": ["company_read", "company_write", "template_management"],
    "chat": ["company_read", "support_mode"],
    "admin_panel": ["customer_management", "support_tools"]
}
```

### **3. Kunde**
```python
KUNDE_PERMISSIONS = {
    "users": ["read_self", "update_self"],
    "companies": ["read_own"],
    "documents": ["own_read", "own_write", "own_delete"],
    "xml_streams": ["own_read", "own_write", "own_delete"],
    "chat": ["own_sessions"],
    "folders": ["own_read", "own_write", "own_delete"]
}
```

---

## 🔐 **Authentifizierung-System**

### **Vereinfachter Auth-Flow (Development)**

#### **Registrierung**
```python
# POST /auth/register
{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "Max",
    "last_name": "Mustermann",
    "company_name": "Mustermann GmbH"  # Optional, auto-generiert
}

# Response
{
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "role": "kunde",
        "company_id": "uuid"
    },
    "token": "jwt_token",
    "company": {
        "id": "uuid",
        "name": "Mustermann GmbH"
    }
}
```

#### **Login**
```python
# POST /auth/login
{
    "email": "user@example.com",
    "password": "password123"
}

# Response
{
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "role": "kunde",
        "company_id": "uuid"
    },
    "token": "jwt_token"
}
```

### **JWT-Token Struktur**
```python
JWT_PAYLOAD = {
    "user_id": "uuid",
    "email": "user@example.com",
    "role": "kunde",
    "company_id": "uuid",
    "exp": 1234567890,  # 24h für Dev
    "iat": 1234567890,
    "sub": "user_id"
}
```

---

## 🚀 **Backend-Implementation**

### **Neue Service-Module**

#### **1. services/auth/auth_service.py**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "dev-secret-key"  # Aus ENV in Prod
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_HOURS = 24  # Lange für Dev

    async def create_user(self, user_data: dict) -> User:
        # Password hashen
        # Company erstellen falls nicht vorhanden
        # User erstellen
        pass

    async def authenticate_user(self, email: str, password: str) -> User:
        # User finden und Passwort prüfen
        pass

    def create_access_token(self, user: User) -> str:
        # JWT Token erstellen
        pass

    async def get_current_user(self, token: str) -> User:
        # Token validieren und User zurückgeben
        pass
```

#### **2. services/auth/permission_service.py**
```python
from typing import List, Optional
from models.core import User

class PermissionService:
    def __init__(self):
        self.role_permissions = {
            "owner": OWNER_PERMISSIONS,
            "streamworks_admin": STREAMWORKS_ADMIN_PERMISSIONS,
            "kunde": KUNDE_PERMISSIONS
        }

    def has_permission(self, user: User, permission: str, resource_id: Optional[str] = None) -> bool:
        # Permission-Check basierend auf Rolle
        pass

    def filter_by_user_access(self, user: User, query):
        # SQLAlchemy Query mit User-/Company-Filter erweitern
        if user.role == "owner":
            return query  # Alles sichtbar
        elif user.role == "streamworks_admin":
            return query.filter(model.company_id.in_(user.managed_companies))
        else:  # kunde
            return query.filter(model.user_id == user.id)
```

### **Neue Router-Module**

#### **1. routers/auth.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(user_data: UserCreate):
    # Registrierung ohne E-Mail-Verifikation
    pass

@router.post("/login")
async def login(login_data: UserLogin):
    # Login mit JWT-Token-Generierung
    pass

@router.get("/me")
async def get_current_user(current_user: User = Depends(get_current_user)):
    # Aktueller User
    pass

@router.post("/logout")
async def logout():
    # Logout (Token invalidieren optional)
    pass
```

#### **2. routers/users.py**
```python
from fastapi import APIRouter, Depends
from services.auth.permission_service import PermissionService

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    pass

@router.put("/me")
async def update_my_profile(profile_data: UserUpdate, current_user: User = Depends(get_current_user)):
    pass

@router.get("/", dependencies=[Depends(require_admin)])
async def list_users(current_user: User = Depends(get_current_user)):
    # Nur für Owner/Admin
    pass

@router.post("/", dependencies=[Depends(require_admin)])
async def create_user(user_data: UserCreate, current_user: User = Depends(get_current_user)):
    # Nur für Owner/Admin
    pass
```

### **Auth-Middleware**
```python
# middleware/auth_middleware.py
from fastapi import Request, HTTPException, Depends
from jose import JWTError, jwt

async def get_current_user(request: Request) -> User:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = await get_user_by_id(user_id)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if not has_role_access(current_user.role, required_role):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Usage: @router.get("/admin", dependencies=[Depends(require_role("streamworks_admin"))])
```

---

## 🎨 **Frontend-Implementation**

### **Auth-Context**

#### **1. contexts/AuthContext.tsx**
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'owner' | 'streamworks_admin' | 'kunde';
  companyId: string;
  company?: Company;
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false
  });

  const login = async (email: string, password: string) => {
    // API-Call zu /auth/login
    // Token in localStorage speichern
    // User-State aktualisieren
  };

  const register = async (userData: RegisterData) => {
    // API-Call zu /auth/register
    // Automatischer Login nach Registrierung
  };

  const logout = () => {
    // Token entfernen
    // State zurücksetzen
    // Redirect zu Login
  };

  return (
    <AuthContext.Provider value={{ ...authState, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### **Permission Guards**

#### **2. components/auth/PermissionGuard.tsx**
```typescript
interface PermissionGuardProps {
  requiredRole?: 'owner' | 'streamworks_admin' | 'kunde';
  requiredPermission?: string;
  fallback?: ReactNode;
  children: ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  requiredRole,
  requiredPermission,
  fallback = null,
  children
}) => {
  const { user } = useAuth();

  if (!user) return fallback;

  if (requiredRole && !hasRole(user.role, requiredRole)) {
    return fallback;
  }

  if (requiredPermission && !hasPermission(user, requiredPermission)) {
    return fallback;
  }

  return <>{children}</>;
};

// Usage:
// <PermissionGuard requiredRole="streamworks_admin">
//   <AdminPanel />
// </PermissionGuard>
```

### **Auth-Seiten**

#### **3. app/auth/login/page.tsx**
```typescript
export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      router.push('/dashboard'); // Role-basierte Weiterleitung
    } catch (error) {
      toast.error('Login fehlgeschlagen');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Streamworks-KI Login
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email">E-Mail-Adresse</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300"
            />
          </div>
          <div>
            <label htmlFor="password">Passwort</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300"
            />
          </div>
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              {isLoading ? 'Anmelden...' : 'Anmelden'}
            </button>
          </div>
          <div className="text-center">
            <Link href="/auth/register" className="font-medium text-indigo-600 hover:text-indigo-500">
              Noch kein Account? Jetzt registrieren
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
```

#### **4. app/auth/register/page.tsx**
```typescript
export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    companyName: ''
  });
  const { register, isLoading } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwörter stimmen nicht überein');
      return;
    }

    try {
      await register(formData);
      toast.success('Registrierung erfolgreich!');
      router.push('/dashboard');
    } catch (error) {
      toast.error('Registrierung fehlgeschlagen');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Streamworks-KI Registrierung
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="firstName">Vorname</label>
              <input
                id="firstName"
                type="text"
                value={formData.firstName}
                onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label htmlFor="lastName">Nachname</label>
              <input
                id="lastName"
                type="text"
                value={formData.lastName}
                onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>

          <div>
            <label htmlFor="email">E-Mail-Adresse</label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label htmlFor="companyName">Unternehmen</label>
            <input
              id="companyName"
              type="text"
              value={formData.companyName}
              onChange={(e) => setFormData({...formData, companyName: e.target.value})}
              placeholder="Wird automatisch erstellt falls leer"
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label htmlFor="password">Passwort</label>
            <input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword">Passwort bestätigen</label>
            <input
              id="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              {isLoading ? 'Registrierung...' : 'Registrieren'}
            </button>
          </div>

          <div className="text-center">
            <Link href="/auth/login" className="font-medium text-indigo-600 hover:text-indigo-500">
              Bereits ein Account? Jetzt anmelden
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

## 🔄 **API-Erwiterungen für RBAC**

### **Bestehende Routers erweitern**

#### **documents/crud.py**
```python
@router.get("/")
async def list_documents(
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    query = select(Document)

    # RBAC-Filter anwenden
    if current_user.role == "kunde":
        query = query.filter(Document.user_id == current_user.id)
    elif current_user.role == "streamworks_admin":
        # Nur Dokumente der verwalteten Companies
        query = query.filter(Document.company_id.in_(current_user.managed_companies))
    # Owner sieht alles (kein zusätzlicher Filter)

    if folder_id:
        query = query.filter(Document.folder_id == folder_id)

    result = await db.execute(query)
    return result.scalars().all()

@router.post("/")
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    # Automatisch user_id und company_id setzen
    document = Document(
        **document_data.dict(),
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    db.add(document)
    await db.commit()
    return document
```

---

## 🧪 **Development-Features**

### **Seed-Data für Testing**

#### **scripts/seed_users.py**
```python
async def create_seed_users():
    """Erstellt Test-User für alle Rollen"""

    # Owner
    owner = User(
        email="owner@streamworks.dev",
        password_hash=hash_password("owner123"),
        first_name="System",
        last_name="Owner",
        role="owner"
    )

    # Streamworks Admin
    admin = User(
        email="admin@streamworks.dev",
        password_hash=hash_password("admin123"),
        first_name="Support",
        last_name="Admin",
        role="streamworks_admin"
    )

    # Test-Kunde
    kunde = User(
        email="kunde@test.dev",
        password_hash=hash_password("kunde123"),
        first_name="Test",
        last_name="Kunde",
        role="kunde",
        company_id=test_company.id
    )

    # In DB speichern
    db.add_all([owner, admin, kunde])
    await db.commit()
```

### **Debug-Endpoints**

#### **routers/debug.py** (nur für Dev)
```python
@router.post("/switch-user/{user_id}")
async def switch_user(user_id: str):
    """Schneller User-Wechsel für Testing"""
    user = await get_user_by_id(user_id)
    token = create_access_token(user)
    return {"token": token, "user": user}

@router.get("/test-permissions")
async def test_permissions(current_user: User = Depends(get_current_user)):
    """Zeigt alle Permissions des aktuellen Users"""
    return {
        "user": current_user,
        "permissions": get_user_permissions(current_user)
    }
```

---

## 📋 **3-Phasen Implementierungsplan**

### **Phase 1: Foundation (Woche 1)**
1. **Database-Schema** ✅
   - Users, Companies, Sessions Tabellen erstellen
   - Bestehende Tabellen erweitern (Migration)
   - Indizes und Constraints hinzufügen

2. **Backend-Auth** ✅
   - User-Models erstellen
   - AuthService (Registrierung, Login, JWT)
   - Basic Auth-Middleware
   - Auth-Router (/auth/register, /auth/login)

3. **Testing** ✅
   - Seed-Data für Test-User
   - Postman/Thunder-Client Tests
   - Basic Auth-Flow validieren

### **Phase 2: Frontend-Integration (Woche 2)**
1. **Auth-Context** ✅
   - React Context für Auth-State
   - API-Service für Auth-Calls
   - Token-Management (localStorage)

2. **Auth-Pages** ✅
   - Login-Seite (/auth/login)
   - Registrierung-Seite (/auth/register)
   - Navigation mit Auth-State

3. **Permission Guards** ✅
   - Role-basierte Component-Guards
   - Route-Protection implementieren
   - UI-Elemente basierend auf Rolle anzeigen/verstecken

### **Phase 3: RBAC-Integration (Woche 3)**
1. **API-Erwiterungen** ✅
   - Alle bestehenden Endpoints mit User-/Company-Filter erweitern
   - Permission-Checks in Services
   - Error-Handling für unberechtigte Zugriffe

2. **Admin-Panel** ✅
   - User-Management für Owner/Admin
   - Company-Management
   - Role-Assignment Interface

3. **Testing & Polish** ✅
   - E2E-Tests für Auth-Flow
   - Permission-Tests für alle Rollen
   - Bug-Fixes und UX-Verbesserungen

---

## 🔧 **Technische Details**

### **Environment-Variablen (.env)**
```bash
# JWT Configuration
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24

# Password Hashing
BCRYPT_ROUNDS=12

# Database
SUPABASE_DB_URL=postgresql://...

# CORS (Frontend URL)
FRONTEND_URL=http://localhost:3000
```

### **Dependencies**

#### **Backend (requirements.txt)**
```txt
# Bereits vorhandene Dependencies...

# Auth-spezifische Packages
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
```

#### **Frontend (package.json)**
```json
{
  "dependencies": {
    // Bereits vorhanden...
    "@types/js-cookie": "^3.0.3",
    "js-cookie": "^3.0.5"
  }
}
```

---

## 🚀 **Getting Started**

### **Quick-Start für Entwickler**

1. **Backend starten**
```bash
cd backend
pip install -r requirements.txt
python scripts/seed_users.py  # Test-User erstellen
python main.py
```

2. **Frontend starten**
```bash
cd frontend
npm install
npm run dev
```

3. **Test-Login**
- **Owner**: owner@streamworks.dev / owner123
- **Admin**: admin@streamworks.dev / admin123
- **Kunde**: kunde@test.dev / kunde123

### **API-Testing**
```bash
# Registrierung
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new@test.com",
    "password": "test123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new@test.com",
    "password": "test123"
  }'

# Geschützten Endpoint testen
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 **Monitoring & Debugging**

### **Logs für Auth-Events**
```python
# In AuthService
logger.info(f"User {user.email} logged in successfully")
logger.warning(f"Failed login attempt for {email}")
logger.error(f"JWT validation failed: {str(e)}")
```

### **Health-Check für Auth**
```python
@router.get("/auth/health")
async def auth_health():
    return {
        "status": "healthy",
        "jwt_algorithm": JWT_ALGORITHM,
        "token_expire_hours": JWT_ACCESS_TOKEN_EXPIRE_HOURS,
        "timestamp": datetime.utcnow()
    }
```

---

## 🎯 **Next Steps nach Implementation**

1. **Security-Hardening**
   - E-Mail-Verifikation hinzufügen
   - Rate-Limiting für Auth-Endpoints
   - HTTPS-Enforcement

2. **UX-Verbesserungen**
   - "Remember Me" Funktionalität
   - Password-Reset Flow
   - Profile-Management erweitern

3. **Enterprise-Features**
   - Single Sign-On (SSO) Integration
   - Audit-Logs für User-Actions
   - Advanced Permission-System

---

**🔧 Dieses Konzept bietet eine solide Foundation für ein produktionsreifes RBAC-System in Streamworks-KI!**