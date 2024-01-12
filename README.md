![Alt text](https://github.com/admin-youno/aiti/blob/main/static/Color%20logo%20-%20small.png)

# Demo Prototype - Marktrecherche LLM Tool

### Anleitung

**Schritt 1: Konto erstellen**<br>
Wenn du noch kein Konto hast, registriere dich zuerst auf [pythonanywhere](https://www.eu.pythonanywhere.com/).

**Schritt 2: Neue Konsole starten**<br>
Logge dich in dein Konto ein und öffne eine neue Bash-Konsole über den *Consoles*-Tab.

**Schritt 3: GitHub-Repository klonen**<br>
Klone dein GitHub-Repository mit dem Befehl `git clone` gefolgt von der URL deines Repos:

```
git clone https://github.com/admin-youno/aiti.git
```

**Schritt 4: Virtuelle Umgebung erstellen**<br>
Erstelle eine virtuelle Umgebung mit:

```
mkvirtualenv venv --python=/usr/bin/python3.10
```

**Schritt 5: Pakete installieren**<br>
Wechsle in das Verzeichnis deines geklonten Repos (aiti) und installiere alle benötigten Pakete aus deiner `requirements.txt`:

```
workon venv
pip install -r requirements.txt
```

**Schritt 6: Web-App erstellen**<br>
Gehe zum "Web"-Tab und erstelle eine neue Flask Web-App. Wähle Python Version 3.10 und ändere den Pfad von /home/[username]/mysite/flask_app.py zu /home/[username]/aiti/flask_app.py.

**Schritt 7: Web-App konfigurieren**

PythonAnywhere verwendet WSGI, um deine App zu starten. Kopiere den folgenden Code in die WSGI-Konfigurationsdatei ("Web"-Tab) :

```
import sys
import os

from dotenv import load_dotenv

project_folder = os.path.expanduser('~/aiti')
load_dotenv(os.path.join(project_folder, '.env'))

# add your project directory to the sys.path
project_home = '/home/'+ os.getenv("USERNAME") + '/aiti'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from app import app as application  # noqa
```

Gehe dann zum "Web"-Tab" zurück und setze den Pfad zu deiner virtuellen Umgebung im Abschnitt "Virtualenv":

```
/home/[username]/.virtualenvs/venv
```

Aktiviere abschließend noch den den Button "Force HTTPS". Falls gewünscht, kann zusätzlich auch noch eine Passwort Protection eingerichtet werden. Dazu einfach die "Password Protection" aktivieren und einen Usernamen und PW vergeben (wird beim Aufruf der Seite abgefragt).

**Schritt 8: Datenbank erstellen**

Gehe auf den "Database"-Tab und erstelle eine neues MySQL Passwort um die Datenbank zu initialisieren.
Erstelle danach eine neue Datenbank mit dem Namen "aiti".
Öffne die MySQL Konsole "aiti" und führe das folgende Statement aus:

```
CREATE TABLE `Message` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `chat_id` varchar(36) DEFAULT NULL,
  `model` varchar(100) NOT NULL,
  `system` varchar(4000) NOT NULL,
  `prompt` varchar(4000)  NOT NULL,
  `response` varchar(4000)  NOT NULL,
  `temperature` float NOT NULL,
  `max_token` int NOT NULL,
  `top_p` float NOT NULL,
  `frequency` float NOT NULL,
  `presence` float NOT NULL,
  `time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
);
```

Überprüfe mit dem folgenden Statement ob die Tabelle angelegt wurde:

```
describe Message;
```
**Schritt 9: Google Custom Search einrichten**<br>

Siehe [Anleitung](https://developers.google.com/custom-search/v1/introduction?hl=de)

*Hinweis: CX = Suchmaschinen-ID*

**Schritt 10: Environment Variablen setzen**<br>
Wechsle zum "Files"-Tab und navigiere zu folgendem Pfad: /home/[username]/aiti und öffne die .env Datei und befülle die entsprechenden Variablen:

```
USERNAME= [pythonanywhere Login-Name]
OPENAI_API_KEY= [API Key (aus Google Colab NB)]
MYSQL_API_KEY= [Passwort aus Schritt 8]
GOOGLE_API_KEY= [API Key aus Schritt 9]
GOOGLE_API_CX= [Suchmaschinen-ID aus Schritt 9]
```

**Schritt 11: Web-App aktualisieren**<br>
Nachdem du alles konfiguriert hast, klicke auf "Reload" auf deinem PythonAnywhere "Web"-Tab.

**Schrit 12: Wep-App ausführen**<br>
Klicke auf den Link im "Web"-Tab, um deine Applikation zu testen.

### Weitere Ressourcen

[Github Upload](https://help.pythonanywhere.com/pages/UploadingAndDownloadingFiles/)<br>
[Virtuelle Umgebung](https://help.pythonanywhere.com/pages/Virtualenvs/)
