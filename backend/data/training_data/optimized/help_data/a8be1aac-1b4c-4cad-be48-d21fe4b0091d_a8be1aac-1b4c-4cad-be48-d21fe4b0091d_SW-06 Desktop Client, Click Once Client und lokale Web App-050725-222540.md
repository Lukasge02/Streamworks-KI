Click Once InstallationClient Downloads:Silent Installation per MSI InstallerWeb App:
Click Once Installation
Installation über Click Once und Autoupdate bei neuen Versionen. Eine voher über den MSI Installation durchgeführte Version solltevorher deinstalliert werden.
Die Click Once Installationen verwendet die Instanznamen Inte1 bzw. Prod1. Sofern die GUI zuvor unter denselben Instanznameninstalliert war, wird nach der Installation über Click Onde das alte Profil wiedergefunden. Der Pfad zum Benutzerprofil bleibt gleich.
Die Installationsdateien sowie die Streamworks.exe.config wird in einem vom Betriebssystem generierten Pfad unter folgendem Pfadabgelegt. Pfad kann variieren. C:\Users\<USERNAME>\AppData\Local\Apps\2.0\XHRB8MXP.W1W\L461H0TK.KHL\stre..orks_ea35a008f2b96106_0016.0000_63cf113a0b90660f
Prod: https://sw-dl.arvato-systems.de
Inte: https://sw-dl-inte.arvato-systems.de
Client Downloads:
Produktionsclient und Zertifikat Download
Silent Installation per MSI Installer

Prod: https://sw-dl.arvato-systems.de
Inte: https://sw-dl-inte.arvato-systems.de
Client Downloads:
Produktionsclient und Zertifikat Download
Silent Installation per MSI Installer
Es ist möglich die Client (De- und) Installation im Hintergrund laufen zu lassen.
Dafür den Client Installer und das Endpointzertifikat (Link siehe unter Client Downloads) herunterladen und im VerzeichnisC:\WORK\StreamworksSetup\AutoInstall platzieren. 
In den nachfolgenden Scripts müssen die Pfade bei den Parametern  STREAMWORKSINSTALLDIR und WIXUI_INSTALLDIR ggf.angepasst werden.
Ggf. ist eine Anpassung des Registry-Keys (KEY_NAME) notwendig.
Web App:
Prod: https://sw-webapp.arvato-systems.de/
Inte: https://sw-webapp-inte.arvato-systems.de/
06 Desktop Client, Click Once Client und lokale Web App
Installationsskript Produktionsclient
 Quelle erweitern
Installationsskript Integrationsclient
 Quelle erweitern