# Powershell-skript Stream-verarbeitungworks

**Automatisch generiert aus**: 9915c528-8a69-4fac-9a5e-0aae1742228b_powershell_streamworks.txt  
**Konvertiert am**: 04.07.2025 14:42  
**Typ**: StreamWorks-Dokumentation

---

```
**PowerShell** (PowerShell-Skript) Integration in StreamWorks
```


### GRUNDLAGEN

```
PowerShell-Skripte können als Tasks in StreamWorks Jobs integriert werden.
```

Vorteil: Mächtige Windows-Automatisierung mit .NET Integration.


## EXECUTION POLICY

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser


### PARAMETER ÜBERGABE

```
StreamWorks kann Parameter an PowerShell-Skripte übergeben:
```

param(
```
    [string]$InputPath,
    [string]$OutputPath,
    [string]$LogLevel = "Info"
```

)


### BEISPIEL-SKRIPT

# StreamWorks Data Processing Script
param(
```
    [Parameter(Mandatory=$true)]
    [string]$SourcePath,
```

```
    [Parameter(Mandatory=$true)]
    [string]$TargetPath
```

)

try {
    Write-Host "Starting data processing..."

    # Get all **CSV** (CSV-Datenverarbeitung) files
```
    $csvFiles = Get-ChildItem -Path $SourcePath -Filter "*.csv"
```

```
    foreach ($file in $csvFiles) {
        Write-Host "Processing: $($file.Name)"
```

        # **Import** (Datenimport) and process data
```
        $data = Import-Csv $file.FullName
        $processedData = $data | Where-Object { $_.Status -eq "Active" }
```

        # **Export** (Datenexport) to target
```
        $outputFile = Join-Path $TargetPath $file.Name
        $processedData | Export-Csv -Path $outputFile -NoTypeInformation
```

```
        Write-Host "Completed: $($file.Name)"
```

    }

    Write-Host "All files processed successfully"
    exit 0  # Success
}
catch {
```
    Write-**Error** (Fehlerbehandlung) "Error: $($_.Exception.Message)"
```

    exit 1  # Failure
}


## ❌ ERROR HANDLING

- Try-Catch Blöcke für Fehlerbehandlung
- Exit-Codes: 0 = Erfolg, 1+ = Fehler
- Write-Error für StreamWorks Logs


### LOGGING

> ℹ️ **Hinweis**: Write-Host "Info message"
> ⚠️ **Warnung**: Write-Warning "Warning message"
Write-Error "Error message"


## BEST PRACTICES

- Parameter Validation verwenden
- Ausführliche Logging implementieren
- Exit-Codes korrekt setzen
- Ressourcen ordnungsgemäß freigeben

---

## 📊 Dokumenten-Metadaten

### 🏷️ Schlüsselwörter
csv, data, error, export, file, import, job, log, parameter, powershell, process, script, stream, streamworks, string

### 🎯 Themen
Batch-Verarbeitung, Monitoring, Konfiguration, Troubleshooting, Datenverarbeitung, PowerShell

### 📈 Komplexität
Mittel (Fortgeschritten)

### 🌐 Sprache
Deutsch

### 🔍 Suchbegriffe
batch verarbeitung, csv, csv-datenverarbeitung, data, datenexport, datenimport, datenstream, datenverarbeitung, error, export, fehler, fehlerbehandlung, file, import, job

### 📏 Statistiken
- **Wortanzahl**: 185 Wörter
- **Zeilen**: 70 Zeilen
- **Geschätzte Lesezeit**: 1 Minuten

---

*Dieses Dokument wurde automatisch für StreamWorks-KI optimiert - 04.07.2025 14:42*
