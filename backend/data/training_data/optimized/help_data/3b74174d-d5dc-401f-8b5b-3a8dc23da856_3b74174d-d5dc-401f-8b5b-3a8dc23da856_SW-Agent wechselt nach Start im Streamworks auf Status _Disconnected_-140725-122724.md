Es wurden die normalen Schritte zum Anlegen eines Agenten ausgeführt bzw. der Agent wurde automatisiert angelegt. Nach dem Startendes Agenten in streamworks wechselt der Agent aber auf den Status "Disconnected".
Für eine fehlgeschlagene Verbindung kann es unterschiedliche Ursachen geben. Beispiele:

Für eine fehlgeschlagene Verbindung kann es unterschiedliche Ursachen geben. Beispiele: 
1. Agenten IP-Adresse wird nicht aufgelöst (Fehlermeldung no such host is known in den System Incidents). -> Orderer ansprechenund korrekten Alias in Erfahrung bringen, bzw. den Alias anlegen lassen falls es den server.arvato-systems.de nicht gibt.2. Der Agent wechselt auf Running, steht aber ein paar Minuten später wieder auf Disconnected: In diesem Fall hat der Agent lokalin der streamworks.conf als Listenaddress den Namen eingetragen, der im Streamworks unter IP-Adresse eingetragen ist. DerAgent kann diesen Alias lokal aber nicht auflösen und beendet sich. In der Folge schickt der Agent keine Heartbeats mehr undwird nach spätestens 15 Minuten im Streamworks als Disconnected angezeigt. 3. Die Firewallfreischaltung zum Agenten fehlt.
Firewall-Policy beantragen

Firewall-Policy beantragen
1. Unter http://metastorm.arvato-systems.de/FirewallRequest/PolicyBrowser.aspx "New Policy Request" auswählen2. Haken setzen bei "Yes! I´m sure that I can approve this request and confirm the automatic approval."3. Bei "Purpose" etwas in die Richtung von "Streamworks Freischaltung Verbindung Processing Server -> Agent" eintragen, IPv4-Domain "Bertelsmann" auswählen4. Source IPs sind die Processing Server IPs, Destination IP die IP (Nicht der DNS-Name!) des Agenten. Port 30000 TCP, es seidenn der Agent benötigt einen anderen Port, z.B. bei einem Proxyagenten.5. Falls der Weg vom Agenten zum Processing Server ebenfalls nicht funktioniert, einen weiteren Eintrag hinzufügen mit Source-und Destination-IP vertauscht, Port ist hier die 9600 TCP
Beispiel für eine Excelvorlage zum direkten Upload
Siehe Firewall Request.png für ein Beispiel eines Policy-Requests.
Agent wechselt nach Start im Streamworks auf Status "Disconnected"