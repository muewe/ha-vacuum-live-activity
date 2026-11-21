# Saugroboter: Live Activity für Home Assistant

Ein Blueprint für iPhone und Android. Sobald der Saugroboter reinigt, pausiert oder zur Station zurückfährt, erscheint sein Status als Live Activity bzw. Live Update. Der Blueprint aktualisiert dieselbe Anzeige und entfernt sie, sobald der Einsatz endet. Er sendet keine Befehle an den Roboter.

## Voraussetzungen

- **Home Assistant Core 2026.7.0 oder neuer** und eine aktuelle Home-Assistant-Companion-App mit erlaubten Mitteilungen.
- **iPhone mit iOS 17.2 oder neuer:** Live Activity auf dem Sperrbildschirm und, falls vorhanden, in der Dynamic Island. Prüfe in der Companion-App unter **Einstellungen → Live Activities**, ob die Funktion verfügbar und aktiviert ist. Die Companion-Doku beschreibt die Funktion auf iOS als Beta. Öffne die App nach der Einrichtung mindestens einmal und achte darauf, dass die App den HA-Server auch unterwegs erreichen kann.
- **Android 16 oder neuer:** Live Update, je nach Gerät mit Statusleisten-Chip und Sperrbildschirm-Anzeige. Bei Samsung kann für den Chip die Entwickleroption **Live-Benachrichtigungen für alle Apps** nötig sein. Auf älteren Android-Versionen ist keine native Live-Update-Anzeige zu erwarten.
- **Saugroboter:** Eine `vacuum.*`-Entität mit den [Standardzuständen von Home Assistant](https://www.home-assistant.io/integrations/vacuum/#vacuum-states). Reinigungsfortschritt und separater Akkusensor sind optional.

Die [Companion-Dokumentation zu Live Activities und Live Updates](https://companion.home-assistant.io/docs/notifications/live-activities/) beschreibt die Voraussetzungen und die gemeinsame Payload. Für das Antippen nutzt der Blueprint die [Companion-Felder `url` und `clickAction`](https://companion.home-assistant.io/docs/notifications/notifications-basic/).

## Installation

Das GitHub-Repository ist privat. Lade die [Blueprint-YAML](blueprints/automation/vacuum_live_activity.yaml) in GitHub herunter und kopiere sie nach `/config/blueprints/automation/local/vacuum_live_activity.yaml`. Der Import über eine GitHub-URL funktioniert für ein privates Repository ohne GitHub-Zugang des HA-Servers nicht.

1. Öffne **Einstellungen → Automatisierungen & Szenen → Blueprints**. Wenn der Blueprint nicht angezeigt wird, lade die Automatisierungen neu oder starte Home Assistant neu.
2. Erstelle eine Automatisierung aus **Saugroboter: Live Activity für iOS und Android** und wähle deine `vacuum.*`-Entität.
3. Suche unter **Entwicklerwerkzeuge → Aktionen** nach `notify.mobile_app_`. Trage pro Handy den vollständigen Aktionsnamen in die Liste ein. Du kannst iPhone und Android in derselben Automatisierung verwenden.
4. Optional: Wähle einen Fortschritts- oder Akkusensor mit Werten von 0 bis 100 oder trage einen relativen Dashboard-Pfad ein. Ohne Dashboard-Pfad öffnet Antippen den Mehr-Infos-Dialog des Roboters.
5. Speichere die Automatisierung. Starte einen Reinigungslauf und prüfe auf beiden Geräten, ob die Anzeige erscheint, beim Pausieren aktualisiert wird und beim Andocken verschwindet.

## Verhalten

| Zustand | Anzeige |
| --- | --- |
| `cleaning` | Reinigt |
| `paused` | Pausiert |
| `returning` | Fährt zur Station |
| `docked`, `idle`, `error` oder andere inaktive Zustände | Anzeige wird entfernt |
| `unknown` oder `unavailable` | Anzeige bleibt bei einem kurzen Aussetzer stehen und wird nach zwei Minuten durchgängigem Zustand entfernt |

Änderungen des Roboterzustands werden direkt verarbeitet. Während eines aktiven Laufs werden optionale Messwerte zusätzlich alle fünf Minuten abgefragt. Ohne gültigen Fortschrittswert zeigt der Blueprint keinen Balken; der Akkustand wird getrennt angezeigt und dient nicht als Fortschritt. Nach einem HA-Neustart oder bei **Aktionen ausführen** gleicht der Blueprint die Anzeige mit dem aktuell bekannten Zustand ab.

Verwende eine Automation je Saugroboter: Die Anzeige-ID basiert auf der Entität, sodass sich zwei Automationen für denselben Roboter auf demselben Handy gegenseitig überschreiben würden. Benachrichtigungstext und Messwerte können auf dem Sperrbildschirm sichtbar sein.

## Fehlersuche

- **Keine Anzeige:** Schicke zuerst eine gewöhnliche Testbenachrichtigung an jede `notify.mobile_app_*`-Aktion. Prüfe dann Betriebssystemversion, Companion-App und Live-Berechtigungen. iOS kann neue Live Activities drosseln; nach vielen schnellen Start-/Stopp-Tests kann der nächste Start ausbleiben, bis sich das Budget erholt.
- **Nur ein Symbol auf Android:** Bei wenig Platz und je nach Hersteller kann Android im Statusleisten-Chip nur das Symbol zeigen. Prüfe auch die Anzeige im Sperrbildschirm bzw. in der Benachrichtigungsleiste.
- **Kein Fortschrittsbalken:** Prüfe den Sensor in **Entwicklerwerkzeuge → Zustände**. Werte wie `unknown`, `unavailable`, Zahlen außerhalb von 0 bis 100 und Textwerte wie `50 %` werden nicht als Fortschritt verwendet. Die Einheit `%` darf als separates Sensorattribut gesetzt sein.

## Automatisierte Tests

Die Tests laden den Blueprint in Home Assistant Core, lösen Zustandswechsel aus und prüfen die abgefangenen Notify-Aufrufe. Sie prüfen nicht die tatsächliche Push-Zustellung oder das Aussehen auf einem Smartphone.

```sh
uv run --no-project --python 3.14 --with 'homeassistant==2026.7.0' python -m unittest discover -s tests -v
```
