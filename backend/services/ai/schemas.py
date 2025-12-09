"""
Pydantic Schemas for Streamworks Parameter Extraction
Defines structured models for all job types based on real XML analysis
"""
from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class StreamworksParams(BaseModel):
    """
    Universal parameter model for Streamworks stream extraction.
    Based on analysis of real Streamworks export XMLs.
    """
    
    # Job Type Detection
    job_type: Literal["STANDARD", "FILE_TRANSFER", "SAP"] = Field(
        description="Erkannter Job-Typ: FILE_TRANSFER wenn Dateien kopiert/übertragen werden, SAP für SAP-Reports, STANDARD für Scripts/Befehle"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0, le=1.0,
        description="Konfidenz der Erkennung (0.0 - 1.0)"
    )
    
    # ============ STREAM LEVEL PARAMETERS ============
    stream_name: Optional[str] = Field(
        default=None,
        description="Name des Streams, z.B. 'BACKUP_DAILY' oder 'FT_SERVER_SYNC'. Generiere einen passenden Namen wenn nicht explizit genannt."
    )
    short_description: Optional[str] = Field(
        default=None,
        description="Kurze Beschreibung des Streams (was er macht)"
    )
    stream_documentation: Optional[str] = Field(
        default=None,
        description="Ausführliche Dokumentation/Beschreibung"
    )
    stream_owner: Optional[str] = Field(
        default=None,
        description="Verantwortlicher Benutzer oder Team"
    )
    stream_path: Optional[str] = Field(
        default=None,
        description="Pfad/Ordner für den Stream, z.B. '/Abteilung/Team'"
    )
    agent_detail: Optional[str] = Field(
        default=None,
        description="Standard-Agent/Server auf dem der Stream läuft"
    )
    calendar_id: Optional[str] = Field(
        default=None,
        description="Kalender-ID für Scheduling, z.B. 'GER-STANDARD'"
    )
    max_stream_runs: Optional[int] = Field(
        default=None,
        description="Maximale Anzahl gleichzeitiger Stream-Runs"
    )
    stream_priority: Optional[int] = Field(
        default=None,
        description="Priorität des Streams (0-10)"
    )
    stream_queue: Optional[str] = Field(
        default=None,
        description="Queue Name"
    )
    
    # ============ ADVANCED FLAGS ============
    status_flag: Optional[bool] = Field(
        default=None,
        description="Stream ist aktiv/inaktiv (True/False)"
    )
    business_service_flag: Optional[bool] = Field(
        default=None,
        description="Markierung als Business Service"
    )
    enable_stream_run_cancelation: Optional[bool] = Field(
        default=None,
        description="Erlaubt Abbruch laufender Streams"
    )
    concurrent_stream_runs_enabled: Optional[bool] = Field(
        default=None,
        description="Erlaubt parallele Ausführung des Streams"
    )
    deploy_as_active: Optional[bool] = Field(
        default=None,
        description="Direkt als aktiv deployen"
    )
    tags: Optional[str] = Field(
        default=None,
        description="Kommagetrennte Tags für den Stream"
    )
    run_variables: Optional[str] = Field(
        default=None,
        description="Variablen Definitionen (Text oder XML-Snippet)"
    )
    
    # ============ JOB LEVEL PARAMETERS ============
    job_name: Optional[str] = Field(
        default=None,
        description="Name des Haupt-Jobs, oft im Format '0100_StreamName'"
    )
    job_short_description: Optional[str] = Field(
        default=None,
        description="Kurzbeschreibung des Jobs"
    )
    main_script: Optional[str] = Field(
        default=None,
        description="Auszuführendes Script oder Befehl für STANDARD Jobs. Z.B. 'python backup.py' oder 'echo Hallo'"
    )
    script_type: Optional[str] = Field(
        default=None,
        description="Art des Scripts: Windows, Unix, Python, PowerShell, Lua"
    )
    run_as_user: Optional[str] = Field(
        default=None,
        description="OS User unter dem der Job läuft"
    )
    job_timeout: Optional[int] = Field(
        default=None,
        description="Timeout in Minuten"
    )
    retry_count: Optional[int] = Field(
        default=None,
        description="Anzahl der Wiederholungen bei Fehler"
    )
    job_hold_flag: Optional[bool] = Field(
        default=None,
        description="Job initial auf HOLD setzen"
    )
    bypass_status: Optional[bool] = Field(
        default=None,
        description="Job überspringen (Bypass)"
    )
    job_severity_group: Optional[str] = Field(
        default=None,
        description="Severity Gruppe für Alerting"
    )
    job_category: Optional[str] = Field(
        default=None,
        description="Kategorie des Jobs (Normal, EndPoint, usw.)"
    )
    
    # ============ DEPENDENCIES ============
    external_dependency_stream: Optional[str] = Field(
        default=None,
        description="Name eines Streams, von dem dieser Job abhängt"
    )
    external_dependency_job: Optional[str] = Field(
        default=None,
        description="Name des Jobs im externen Stream, von dem abgehangen wird"
    )
    external_dependency_type: Optional[Literal["Success", "Failure", "Complete"]] = Field(
        default=None,
        description="Art der Abhängigkeit (Success, Failure, Complete)"
    )
    file_dependency_path: Optional[str] = Field(
        default=None,
        description="Dateipfad für Datei-Trigger/Abhängigkeit"
    )
    file_dependency_condition: Optional[Literal["Exists", "Missing"]] = Field(
        default=None,
        description="Bedingung für Datei (Exists, Missing)"
    )
    file_dependency_interval: Optional[int] = Field(
        default=None,
        description="Prüfintervall für Datei in Sekunden"
    )

    # ============ FILE TRANSFER PARAMETERS ============
    source_agent: Optional[str] = Field(
        default=None,
        description="Quell-Agent/Server VON dem Dateien kopiert werden"
    )
    target_agent: Optional[str] = Field(
        default=None,
        description="Ziel-Agent/Server AUF den Dateien kopiert werden"
    )
    source_file_pattern: Optional[str] = Field(
        default=None,
        description="Quell-Dateipfad oder Pattern, z.B. '/data/*.csv' oder 'E:\\backup\\*.txt'"
    )
    target_file_path: Optional[str] = Field(
        default=None,
        description="Ziel-Verzeichnis für die Dateien, z.B. '/backup/' oder 'E:\\target\\'"
    )
    transfer_mode: Optional[Literal["BINARY", "ASCII"]] = Field(
        default=None,
        description="Übertragungsmodus"
    )
    overwrite_target: Optional[Literal["YES", "NO"]] = Field(
        default=None,
        description="Ziel überschreiben falls existent"
    )
    source_login_object: Optional[str] = Field(
        default=None,
        description="Login-Objekt für Quell-Zugriff"
    )
    target_login_object: Optional[str] = Field(
        default=None,
        description="Login-Objekt für Ziel-Zugriff"
    )
    source_file_delete_flag: Optional[bool] = Field(
        default=None,
        description="Quelldateien nach Transfer löschen (True/False)"
    )
    target_file_exists_handling: Optional[str] = Field(
        default=None,
        description="Verhalten bei existierenden Zieldateien: Overwrite, Skip, Abort"
    )
    
    # ============ SAP PARAMETERS ============
    sap_system: Optional[str] = Field(
        default=None,
        description="SAP System-ID, z.B. 'P01', 'D01', 'PA1'"
    )
    sap_client: Optional[str] = Field(
        default=None,
        description="SAP Mandant, z.B. '100', '200'"
    )
    sap_user: Optional[str] = Field(
        default=None,
        description="SAP User"
    )
    sap_report: Optional[str] = Field(
        default=None,
        description="SAP Report/Programm Name, z.B. 'ZREPORT_DAILY', 'ZTV123'"
    )
    sap_variant: Optional[str] = Field(
        default=None,
        description="SAP Variante für den Report"
    )
    sap_jobname: Optional[str] = Field(
        default=None,
        description="Interner SAP Jobname"
    )
    
    # ============ SCHEDULING PARAMETERS ============
    schedule: Optional[str] = Field(
        default=None,
        description="Zeitplan in natürlicher Sprache: 'täglich', 'wöchentlich', 'monatlich', 'jede Stunde'"
    )
    start_time: Optional[str] = Field(
        default=None,
        description="Startzeit im Format HH:MM, z.B. '08:00', '23:30'"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Startdatum"
    )
    time_zone: Optional[str] = Field(
        default=None,
        description="Zeitzone (CET, UTC, etc.)"
    )
    
    # ============ CONTACT PARAMETERS ============
    contact_first_name: Optional[str] = Field(
        default=None,
        description="Vorname der Kontaktperson"
    )
    contact_last_name: Optional[str] = Field(
        default=None,
        description="Nachname der Kontaktperson"
    )
    contact_email: Optional[str] = Field(
        default=None,
        description="Email Adresse"
    )
    company_name: Optional[str] = Field(
        default=None,
        description="Firmenname"
    )
    department: Optional[str] = Field(
        default=None,
        description="Abteilung"
    )
    contact_type: Optional[str] = Field(
        default=None,
        description="Typ des Kontakts (Owner, Notification)"
    )
    notify_on_error: Optional[Literal["YES", "NO"]] = Field(
        default=None,
        description="Benachrichtigung bei Fehler aktivieren"
    )
    
    # ============ AI CONVERSATION CONTROL ============
    missing_required: List[str] = Field(
        default_factory=list,
        description="Liste der fehlenden Pflichtfelder"
    )
    follow_up_question: Optional[str] = Field(
        default=None,
        description="Nächste Frage an den Benutzer für fehlende Informationen"
    )
