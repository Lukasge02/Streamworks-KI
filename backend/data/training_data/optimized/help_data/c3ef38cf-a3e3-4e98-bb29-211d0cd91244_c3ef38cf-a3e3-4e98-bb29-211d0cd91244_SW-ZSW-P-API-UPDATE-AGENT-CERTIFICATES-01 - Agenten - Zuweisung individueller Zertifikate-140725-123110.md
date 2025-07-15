Der Stream wurde erstellt um per REST API Agenten des Arvato Systems-Mandanten ein individuelles Zertifikat zuzuweisen. Die Aktionist ansonsten nur über die GUI ausführbar was bei einer größeren Anzahl Agenten aufwendiger ist. Die API Aufrufe sind in Powershellgekapselt. 
Vor Ausführung sind die gewünschten Agenten im Job 00200 im Jobscript zu hinterlegen. 
Ansprechpartner: Igor Kölmel / PAO Team 1
Achtung: Dieser Stream kann nicht für die Zuweisung von individuellen Zertifikaten zu Agenten von Nicht-Arvato Systems-Mandanten(z. B. OGE) verwendet werden. Diesen Agenten muss das Zertifikat dann manuell über die GUI-Funktion "Agent Control" zugewiesenwerden mit folgenden Schritten:
1.) Agent stoppen (Running  →  Listening)
2.) Initiate Certificate-Update
3.) ggf. Agent wieder starten (Listening  →  Running), falls der Agent nicht das Autostart-Flag besitzt.

1.) Agent stoppen (Running  →  Listening)
2.) Initiate Certificate-Update
3.) ggf. Agent wieder starten (Listening  →  Running), falls der Agent nicht das Autostart-Flag besitzt.
Was ist zu beachten: Um dem Agenten ein individuelles Zertifikat zuzuordnen, muss der Agent mind. die Version 5.1.1 haben, damit dasauch funktioniert, wenn zu dem Zeitpunkt Jobs aktiv sind.
SQL von Kriete01 zur Ermittlung aller Windows- und Unix-Agenten des Mandanten "Arvato Systems", die noch kein Zertifikat habenund die Agentenversion >=5.1.1:

use streamworksselect m.MandatorName, ad.AgentName, ads.AgentIPName,CASE ad.AgentTypeCd WHEN 1 THEN 'Windows' WHEN 2 THEN 'Unix' END AS Typ,CASE CHARINDEX('[', rag.OSInfo) WHEN 0 THEN rag.OSInfo ELSE LEFT(rag.OSInfo, CHARINDEX('[', rag.OSInfo) - 1) END AS OSBase,CASE ah.RunningStatusCd WHEN NULL THEN 'None' WHEN 1 THEN 'Listening' WHEN 2 THEN 'Running' WHEN 3 THEN 'Stopped' WHEN4 THEN 'Disconnected' END AS Status,ad.Description, ads.AgentPortNo, rag.AgentSoftwareVersion, ads.agentCertificateId, ads.ClusterNamefrom AgentDetail adleft join AgentHeartbeat ah on ah.AgentId = ad.AgentIdjoin AgentDetailSystem ads on ads.AgentId = ad.AgentIdjoin RuntimeAgentDetail rag on rag.AgentId = ad.AgentIdjoin Mandator m on m.MandatorId = ad.MandatorIdand ads.AgentCertificateId IS NULL--where ad.Description like '%Abbau%' and ad.Description like '%OMM-SWS-AGT-DEL%'--and ad.AgentName in ('gtlnmswin2012','acs1','acs2','apoprdhsap01')and ads.Virtual = 0 -- Virtuelle anzeigen Ja (1) oder Nein (0)--and

like '%Abbau%' and ad.Description like '%OMM-SWS-AGT-DEL%'--and ad.AgentName in ('gtlnmswin2012','acs1','acs2','apoprdhsap01')and ads.Virtual = 0 -- Virtuelle anzeigen Ja (1) oder Nein (0)--and ad.OSInfo like '%Agent(%2.3%' -- Hier bestimmte Agentenversion eintragen oder Zeile auskommentieren für alle Agentenand m.MandatorCode = '0100' -- Mandant vorgeben oder Zeile auskommentieren für alle Mandanten--and ad.AgentTypeCd = 2 -- Nach Windows (1) oder Unix (2) filternand ah.RunningStatusCd in (1,2) -- None = 0, Listening = 1, Running = 2, Stopped = 3, Disconnected = 4and (rag.AgentSoftwareVersion >= '5.1.1')order by MandatorName, AgentName

00100-ZSW-P-API-UPDATE-AGENT-CERTIFICATES-01
Erstellung eines Arbeitsverzeichnisses
00200-ZSW-P-API-UPDATE-AGENT-CERTIFICATES-01
Erstellung einer Inputliste mit den zu bearbeitenden Agenten. Die Agenten einfach im Jobscript hinterlegen. 
00300-ZSW-P-API-UPDATE-AGENT-CERTIFICATES-01
Ausgabe der Agentenliste
ZSW-P-API-UPDATE-AGENT-CERTIFICATES-01 - Agenten - Zuweisungindividueller Zertifikate

01000-ZSW-P-API-UPDATE-AGENT-CERTIFICATES-01
Durchführung des eigentlichen Updates inkl. Fehlerhandling. Die Aktionen werden in einer Schleife pro Agent durchgeführt.
Aktion 1: Stoppen des jeweiligen Agenten
Aktion 2: Zertifikatsupdate anstoßen
Aktion 3: Prüfen ob der Agent wieder im Status Running steht.
Der Job bricht ab sofern es bei einem Agenten ein Problem gab. Der/die fehlerhafte(n) Agent(en) wird/werden am Ende aufgeführt. Überdie Suche im Joblog kann dann die konkrete fehlerhafte REST Response angezeigt werden. Der Job kann, ggf. nach manueller Korrektur,einfach neugestartet werden. Der Job bearbeitet dann die fehlerhaften erneut.