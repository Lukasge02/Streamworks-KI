# Streamworks Stream-Konfigurationen

Dieses Dokument beschreibt die benötigten automatisierten Dateitransfers und Jobs.

## 1. Täglicher Backup-Job

Wir benötigen einen **täglichen Backup-Job** der jeden Tag um 23:00 Uhr läuft.

- **Server:** BACKUP_SERVER_01
- **Script:** /opt/scripts/backup_daily.sh
- **Beschreibung:** Sichert alle wichtigen Datenbanken auf den Backup-Storage
- **Priorität:** Hoch (5)
- **Verantwortlicher:** Max Mustermann

## 2. SAP Report Export

Ein SAP-Report soll automatisiert ausgeführt werden:

- **Name:** SAP_MONTHLY_EXPORT
- **SAP-System:** PA1
- **Report:** ZEXPORT_MONTHLY_DATA
- **Mandant:** 100
- **Zeitplan:** Jeden 1. des Monats um 06:00 Uhr

## 3. Dateitransfer PROD zu ARCHIVE

Transfer wichtiger Log-Dateien vom Produktionsserver zum Archiv:

- **Stream-Name:** FT_LOGS_ARCHIVE
- **Quell-Server:** PROD_WEB_01
- **Ziel-Server:** ARCHIVE_STORAGE
- **Quelldatei:** /var/log/app/*.log
- **Zielpfad:** /archive/logs/daily/
- **Zeitplan:** Täglich um 02:00 Uhr
- **Beschreibung:** Archiviert alle Application Logs vom Produktionsserver

## 4. Stündliche Synchronisation

Dateisynchronisation zwischen zwei Entwicklungsservern:

- **Name:** FT_DEV_SYNC
- **Von:** DEV_SERVER_A
- **Nach:** DEV_SERVER_B  
- **Dateimuster:** /shared/code/*.java
- **Zielverzeichnis:** /sync/incoming/
- **Frequenz:** Stündlich
