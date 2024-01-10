![Alt text](https://github.com/admin-youno/aiti/blob/main/static/Color%20logo%20-%20small.png)

# Demo Prototype - Marktrecherche LLM Tool

### Anleitung

**Schritt 1: Konto erstellen**<br>
Wenn du noch kein Konto hast, registriere dich zuerst auf [pythonAnywhere](https://www.pythonanywhere.com/).

**Schritt 2: Neue Konsole starten**<br>
Logge dich in dein Konto ein und öffne eine neue Bash-Konsole über den *Consoles*-Tab.

**Schritt 3: GitHub-Repository klonen**<br>
Klone dein GitHub-Repository mit dem Befehl `git clone` gefolgt von der URL deines Repos:

```
git clone [https://github.com/admin-youno/aiti.git
```

**Schritt 4: Virtuelle Umgebung erstellen**<br>
Erstelle eine virtuelle Umgebung mit:

```
mkvirtualenv venv --python=/usr/bin/python3.10
```

**Schritt 5: Pakete installieren**<br>
Wechsle in das Verzeichnis deines geklonten Repos und installiere alle benötigten Pakete aus deiner `requirements.txt`:

```
workon venv
pip install -r requirements.txt
```

**Schritt 6: Web-App erstellen**<br>
Gehe zum "Web"-Tab und erstelle eine neue Flask Web-App. Wähle die manuelle Konfiguration (Python) und die Version, die zu deiner virtuellen Umgebung passt.

**Schritt 7: WSGI-Datei konfigurieren**
PythonAnywhere verwendet WSGI, um deine App zu starten. Passe die WSGI-Konfigurationsdatei an, um auf deine Anwendung zu verweisen. Du findest diese Datei im "Web"-Tab.

**Schritt 8: Datenbank erstellen**

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

```
show Tables;
```

**Schritt 9: Web-App aktualisieren**<br>
Nachdem du alles konfiguriert hast, klicke auf "Reload" auf deinem PythonAnywhere "Web"-Tab.

**Schrit 10: Wep-App ausführen**<br>
Klicke auf den Link im "Web"-Tab, um deine Applikation zu testen.

### Weitere Ressourcen

[Github Upload](https://help.pythonanywhere.com/pages/UploadingAndDownloadingFiles/)<br>
[Virtuelle Umgebung](https://help.pythonanywhere.com/pages/Virtualenvs/)

