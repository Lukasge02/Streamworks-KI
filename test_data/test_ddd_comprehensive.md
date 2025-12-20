# Domain Driven Design - Test System

## Projekt: User Management System

### Einleitung

Dieses DDD beschreibt ein umfassendes Benutzerverwaltungssystem mit Authentifizierung, Rollenverwaltung und Zugriffskontrolle.

---

## Use Cases

### UC-001: Benutzer-Registrierung
**Akteure:** Anonymer Benutzer  
**Vorbedingungen:** Keine  
**Hauptablauf:**
1. Benutzer öffnet Registrierungsseite
2. Benutzer gibt E-Mail, Passwort und Name ein
3. System validiert Eingaben
4. System erstellt Benutzerkonto
5. System sendet Bestätigungs-E-Mail
6. Benutzer erhält Erfolgsmeldung

**Fehlerfälle:**
- E-Mail bereits vorhanden → E-0001
- Passwort zu schwach → E-0002
- Ungültige E-Mail-Adresse → E-0003

**Nachbedingungen:** Neuer Benutzer ist im System registriert

---

### UC-002: Benutzer-Login
**Akteure:** Registrierter Benutzer  
**Vorbedingungen:** Benutzerkonto existiert  
**Hauptablauf:**
1. Benutzer öffnet Login-Seite
2. Benutzer gibt E-Mail und Passwort ein
3. System validiert Credentials
4. System erstellt Session
5. System leitet Benutzer zum Dashboard weiter

**Fehlerfälle:**
- Falsche Credentials → E-0004
- Konto gesperrt → E-0005
- Zu viele Login-Versuche → E-0006

**Nachbedingungen:** Benutzer ist eingeloggt

---

### UC-003: Passwort zurücksetzen
**Akteure:** Registrierter Benutzer  
**Vorbedingungen:** Benutzerkonto existiert  
**Hauptablauf:**
1. Benutzer klickt auf "Passwort vergessen"
2. Benutzer gibt E-Mail ein
3. System sendet Reset-Link per E-Mail
4. Benutzer klickt auf Link
5. Benutzer gibt neues Passwort ein
6. System aktualisiert Passwort

**Fehlerfälle:**
- E-Mail nicht gefunden → E-0007
- Reset-Link abgelaufen → E-0008

**Nachbedingungen:** Passwort wurde zurückgesetzt

---

### UC-004: Profil bearbeiten
**Akteure:** Eingeloggter Benutzer  
**Vorbedingungen:** Benutzer ist eingeloggt  
**Hauptablauf:**
1. Benutzer öffnet Profilseite
2. Benutzer ändert Name oder E-Mail
3. System validiert Änderungen
4. System speichert Änderungen
5. Benutzer erhält Bestätigung

**Fehlerfälle:**
- Ungültige E-Mail → E-0003
- Name zu kurz → E-0009

**Nachbedingungen:** Profil wurde aktualisiert

---

### UC-005: Benutzer löschen (Admin)
**Akteure:** Administrator  
**Vorbedingungen:** Admin ist eingeloggt  
**Hauptablauf:**
1. Admin öffnet Benutzerliste
2. Admin wählt Benutzer aus
3. Admin klickt auf "Löschen"
4. System bestätigt Löschung
5. System löscht Benutzerkonto

**Fehlerfälle:**
- Benutzer nicht gefunden → E-0010
- Keine Berechtigung → E-0011

**Nachbedingungen:** Benutzer wurde gelöscht

---

## Business Rules

### BR-001: E-Mail-Validierung
**Beschreibung:** E-Mail-Adressen müssen dem Format `user@domain.com` entsprechen und eine gültige Domain haben.  
**Priorität:** Kritisch  
**Validierungstyp:** Constraint

### BR-002: Passwort-Stärke
**Beschreibung:** Passwörter müssen mindestens 8 Zeichen lang sein, mindestens einen Großbuchstaben, einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten.  
**Priorität:** Hoch  
**Validierungstyp:** Constraint

### BR-003: Session-Timeout
**Beschreibung:** Benutzersessions laufen nach 30 Minuten Inaktivität ab.  
**Priorität:** Mittel  
**Validierungstyp:** Constraint

### BR-004: Login-Versuche
**Beschreibung:** Nach 5 fehlgeschlagenen Login-Versuchen wird das Konto für 15 Minuten gesperrt.  
**Priorität:** Hoch  
**Validierungstyp:** Constraint

### BR-005: E-Mail-Eindeutigkeit
**Beschreibung:** Jede E-Mail-Adresse kann nur einmal im System verwendet werden.  
**Priorität:** Kritisch  
**Validierungstyp:** Constraint

### BR-006: Admin-Berechtigung
**Beschreibung:** Nur Benutzer mit der Rolle "Administrator" können andere Benutzer löschen oder Rollen ändern.  
**Priorität:** Kritisch  
**Validierungstyp:** Authorization

### BR-007: Name-Länge
**Beschreibung:** Benutzernamen müssen zwischen 2 und 50 Zeichen lang sein.  
**Priorität:** Mittel  
**Validierungstyp:** Constraint

### BR-008: Passwort-Reset-Gültigkeit
**Beschreibung:** Passwort-Reset-Links sind 24 Stunden gültig.  
**Priorität:** Mittel  
**Validierungstyp:** Constraint

---

## Error Codes

### E-0001: E-Mail bereits vorhanden
**Beschreibung:** Die angegebene E-Mail-Adresse ist bereits im System registriert.  
**HTTP-Status:** 409 Conflict  
**Auslöser:** Versuch, sich mit bereits existierender E-Mail zu registrieren

### E-0002: Passwort zu schwach
**Beschreibung:** Das eingegebene Passwort erfüllt nicht die Sicherheitsanforderungen.  
**HTTP-Status:** 400 Bad Request  
**Auslöser:** Passwort erfüllt nicht BR-002

### E-0003: Ungültige E-Mail-Adresse
**Beschreibung:** Die eingegebene E-Mail-Adresse hat ein ungültiges Format.  
**HTTP-Status:** 400 Bad Request  
**Auslöser:** E-Mail erfüllt nicht BR-001

### E-0004: Falsche Credentials
**Beschreibung:** E-Mail oder Passwort sind falsch.  
**HTTP-Status:** 401 Unauthorized  
**Auslöser:** Login mit falschen Credentials

### E-0005: Konto gesperrt
**Beschreibung:** Das Benutzerkonto wurde aufgrund zu vieler fehlgeschlagener Login-Versuche gesperrt.  
**HTTP-Status:** 403 Forbidden  
**Auslöser:** BR-004 wurde ausgelöst

### E-0006: Zu viele Login-Versuche
**Beschreibung:** Zu viele fehlgeschlagene Login-Versuche in kurzer Zeit.  
**HTTP-Status:** 429 Too Many Requests  
**Auslöser:** Mehr als 5 Login-Versuche in 5 Minuten

### E-0007: E-Mail nicht gefunden
**Beschreibung:** Die angegebene E-Mail-Adresse existiert nicht im System.  
**HTTP-Status:** 404 Not Found  
**Auslöser:** Passwort-Reset mit nicht existierender E-Mail

### E-0008: Reset-Link abgelaufen
**Beschreibung:** Der Passwort-Reset-Link ist abgelaufen und nicht mehr gültig.  
**HTTP-Status:** 410 Gone  
**Auslöser:** Reset-Link älter als 24 Stunden (BR-008)

### E-0009: Name zu kurz
**Beschreibung:** Der eingegebene Name ist zu kurz (muss mindestens 2 Zeichen lang sein).  
**HTTP-Status:** 400 Bad Request  
**Auslöser:** Name erfüllt nicht BR-007

### E-0010: Benutzer nicht gefunden
**Beschreibung:** Der angeforderte Benutzer existiert nicht im System.  
**HTTP-Status:** 404 Not Found  
**Auslöser:** Versuch, nicht existierenden Benutzer zu löschen

### E-0011: Keine Berechtigung
**Beschreibung:** Der Benutzer hat nicht die erforderliche Berechtigung für diese Aktion.  
**HTTP-Status:** 403 Forbidden  
**Auslöser:** Nicht-Admin versucht Admin-Aktion (BR-006)

---

## Domain Entities

- **User**: Benutzer mit E-Mail, Name, Passwort-Hash, Rolle
- **Session**: Aktive Benutzersession mit Token, Ablaufzeit
- **Role**: Benutzerrolle (User, Admin, Moderator)
- **PasswordReset**: Passwort-Reset-Anfrage mit Token und Ablaufzeit

---

## Akteure

- **Anonymer Benutzer**: Nicht eingeloggter Benutzer
- **Registrierter Benutzer**: Eingeloggter Standard-Benutzer
- **Administrator**: Benutzer mit Admin-Rechten
- **Moderator**: Benutzer mit Moderator-Rechten

---

## Numerische Limits

- **Maximale Session-Dauer**: 30 Minuten Inaktivität
- **Maximale Login-Versuche**: 5 Versuche vor Sperre
- **Sperrdauer nach fehlgeschlagenen Logins**: 15 Minuten
- **Passwort-Reset-Link-Gültigkeit**: 24 Stunden
- **Minimale Passwort-Länge**: 8 Zeichen
- **Minimale Name-Länge**: 2 Zeichen
- **Maximale Name-Länge**: 50 Zeichen
- **Maximale E-Mail-Länge**: 255 Zeichen

---

## Technische Anforderungen

### API-Endpunkte

- `POST /api/auth/register` - Benutzer registrieren
- `POST /api/auth/login` - Benutzer einloggen
- `POST /api/auth/logout` - Benutzer ausloggen
- `POST /api/auth/reset-password` - Passwort zurücksetzen anfordern
- `POST /api/auth/reset-password/confirm` - Passwort zurücksetzen bestätigen
- `GET /api/users/me` - Eigenes Profil abrufen
- `PATCH /api/users/me` - Eigenes Profil aktualisieren
- `GET /api/users` - Benutzerliste (nur Admin)
- `DELETE /api/users/{id}` - Benutzer löschen (nur Admin)

---

## Zusammenfassung

Dieses System verwaltet Benutzer mit vollständiger Authentifizierung, Rollenverwaltung und Zugriffskontrolle. Es umfasst 5 Use Cases, 8 Business Rules und 11 Error Codes für umfassende Testabdeckung.
