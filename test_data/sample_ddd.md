# Domain Driven Design: Benutzer-Verwaltungssystem

## 1. Übersicht

Das Benutzer-Verwaltungssystem (BVS) ermöglicht die zentrale Verwaltung von Benutzern, Rollen und Berechtigungen für die Streamworks-Plattform.

## 2. Bounded Context

### Hauptakteure
- **System Administrator**: Kann alle Benutzer und Rollen verwalten
- **Mandant Administrator**: Kann Benutzer innerhalb seines Mandanten verwalten  
- **Standard User**: Kann eigenes Profil bearbeiten

### Aggregate: User
```
User {
  id: UUID (PK)
  email: String (unique, max 255 chars)
  username: String (unique, max 50 chars)
  password_hash: String
  role: Enum(ADMIN, MANDANT_ADMIN, USER)
  mandant_id: UUID (FK)
  status: Enum(ACTIVE, INACTIVE, LOCKED)
  failed_login_attempts: Integer (max 5)
  last_login: DateTime
  created_at: DateTime
  updated_at: DateTime
}
```

### Aggregate: Mandant
```
Mandant {
  id: UUID (PK)
  name: String (unique, max 100 chars)
  max_users: Integer (default 100, max 2000)
  active_users_count: Integer
  license_valid_until: Date
  created_at: DateTime
}
```

## 3. Business Rules

### BR-001: Benutzer-Erstellung
- Email muss eindeutig sein (Fehlercode: E-1001 bei Duplikat)
- Username muss alphanumerisch sein (Fehlercode: E-1002 bei ungültigem Format)
- Mandant darf max_users nicht überschreiten (Fehlercode: E-1003)

### BR-002: Passwort-Richtlinien
- Mindestens 12 Zeichen
- Mindestens 1 Großbuchstabe, 1 Kleinbuchstabe, 1 Zahl, 1 Sonderzeichen
- Fehlercode E-2001 bei Nichteinhaltung

### BR-003: Login-Sperrmechanismus
- Nach 5 fehlerhaften Login-Versuchen wird der Account für 30 Minuten gesperrt
- Status wechselt zu LOCKED
- Fehlercode E-3001 bei gesperrtem Account

### BR-004: Mandanten-Limiten
- Ein Mandant kann maximal 2000 Benutzer haben
- Bei Überschreitung: Fehlercode E-4001
- Warnung bei 90% Auslastung

## 4. Use Cases

### UC-001: Benutzer anlegen
**Akteur**: System Administrator, Mandant Administrator
**Vorbedingung**: Akteur ist authentifiziert und hat entsprechende Berechtigung
**Schritte**:
1. Akteur gibt Benutzerdaten ein (email, username, rolle)
2. System validiert Eingaben
3. System prüft Mandanten-Limit
4. System erstellt Benutzer mit Status INACTIVE
5. System sendet Aktivierungsmail

**Erwartetes Ergebnis**: Benutzer ist angelegt mit Status INACTIVE

### UC-002: Passwort zurücksetzen
**Akteur**: Standard User, System Administrator
**Vorbedingung**: Benutzer existiert
**Schritte**:
1. Benutzer fordert Reset an via Email
2. System generiert Token (gültig 24h)
3. Benutzer setzt neues Passwort
4. System validiert Passwort-Richtlinien

**Erwartetes Ergebnis**: Passwort ist aktualisiert

### UC-003: Benutzer sperren
**Akteur**: System Administrator
**Vorbedingung**: Benutzer existiert und ist ACTIVE
**Schritte**:
1. Administrator wählt Benutzer
2. Administrator setzt Status auf LOCKED
3. System protokolliert Aktion

**Erwartetes Ergebnis**: Benutzer kann sich nicht mehr einloggen

## 5. Domänen-Events

- `UserCreated` - bei erfolgreicher Erstellung
- `UserActivated` - bei Aktivierung
- `UserLocked` - bei Sperrung (manuell oder automatisch)
- `UserUnlocked` - bei Entsperrung
- `PasswordChanged` - bei Passwortänderung
- `LoginFailed` - bei fehlerhaftem Login
- `LoginSucceeded` - bei erfolgreichem Login

## 6. API Endpoints

### POST /api/users
Erstellt einen neuen Benutzer.
- Body: `{ email, username, role, mandant_id }`
- Response 201: `{ id, email, username, status }`
- Response 400: `{ error: "E-1001", message: "Email bereits vorhanden" }`

### PUT /api/users/{id}/lock
Sperrt einen Benutzer manuell.
- Response 200: `{ status: "LOCKED" }`
- Response 404: `{ error: "USER_NOT_FOUND" }`

### POST /api/auth/login
Authentifiziert einen Benutzer.
- Body: `{ email, password }`
- Response 200: `{ token, expires_at }`
- Response 401: `{ error: "E-3001", message: "Account gesperrt" }`
- Response 429: `{ retry_after: 1800 }` (bei Rate Limiting)
