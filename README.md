# Robot Vacuum Live Activity for Home Assistant

This Home Assistant blueprint shows your robot vacuum's status on iPhone and Android while it is cleaning, paused, or returning to its dock. It updates the same Live Activity or Live Update and dismisses it when the run ends. It does not send commands to the vacuum.

## Requirements

- **Home Assistant Core 2026.7.0 or later** and an up-to-date Home Assistant Companion app with notifications enabled.
- **iPhone with iOS 17.2 or later:** The Live Activity appears on the Lock Screen and in the Dynamic Island on supported models. Check **Settings → Live Activities** in the Companion app to see whether the feature is available and enabled. The Companion documentation describes the iOS feature as beta. Open the app at least once after setup, and make sure it can reach your Home Assistant server when you are away.
- **Android 16 or later:** Live Updates may include a Lock Screen notification and a status bar chip, depending on the device. On Samsung, you may need to enable **Live notifications for all apps** in Developer options for the chip to appear. Older Android versions do not support native Live Updates.
- **Robot vacuum:** A `vacuum.*` entity that reports [standard Home Assistant vacuum states](https://www.home-assistant.io/integrations/vacuum/#vacuum-states). Cleaning progress and a separate battery sensor are optional.

The [Companion documentation for Live Activities and Live Updates](https://companion.home-assistant.io/docs/notifications/live-activities/) covers platform requirements and the shared notification payload. The blueprint uses the [Companion `url` and `clickAction` fields](https://companion.home-assistant.io/docs/notifications/notifications-basic/) to open a destination on tap.

## Installation

This GitHub repository is private. Download the [blueprint YAML](blueprints/automation/vacuum_live_activity.yaml) from GitHub and copy it to `/config/blueprints/automation/local/vacuum_live_activity.yaml`. Importing it by URL will not work unless your Home Assistant server can authenticate to GitHub and access this repository.

1. Open **Settings → Automations & scenes → Blueprints**. If the blueprint does not appear, reload automations or restart Home Assistant.
2. Create an automation from **Robot Vacuum: Live Activity for iOS and Android** and select your `vacuum.*` entity.
3. In **Developer tools → Actions**, search for `notify.mobile_app_`. Add one full action name per phone. You can use iPhone and Android recipients in the same automation.
4. Optionally, select a cleaning progress sensor or a battery sensor with values from 0 to 100, or enter a relative dashboard path. If the path is blank, tapping the notification opens the vacuum's more-info dialog.
5. Save the automation and start a cleaning run. On both phones, verify that the notification appears, updates when the vacuum pauses, and disappears when it docks.

## Behavior

| Vacuum state | Notification |
| --- | --- |
| `cleaning` | Cleaning |
| `paused` | Paused |
| `returning` | Returning to dock |
| `docked`, `idle`, `error`, or another inactive state | Dismissed |
| `unknown` or `unavailable` | Stays visible through a brief disconnect and is dismissed if the state persists for two minutes |

The blueprint responds to vacuum state changes as they happen. While a run is active, it also refreshes optional readings every five minutes. The progress bar appears only when a valid cleaning progress reading is available; battery level is displayed separately. After a Home Assistant restart, or when you select **Run actions**, the blueprint updates or dismisses the notification based on the current state.

Use one automation per vacuum. The notification tag is derived from the vacuum's entity ID, so two automations for the same vacuum would overwrite each other's notification on the same phone. Notification text and readings can be visible on the Lock Screen.

## Troubleshooting

- **Nothing appears:** Send a regular test notification using each `notify.mobile_app_*` action. Then check the OS version, Companion app version, and permissions. iOS may throttle new Live Activities if you rapidly start and stop them during testing.
- **Android shows only an icon:** Depending on the manufacturer and available space, the status bar chip may show only the icon. Check the Lock Screen or notification shade for the full notification.
- **No progress bar:** Check the sensor in **Developer tools → States**. The blueprint ignores `unknown`, `unavailable`, numbers outside 0 to 100, and text such as `50%`. The sensor can still have `%` as its separate unit of measurement.

## Automated tests

The tests load the blueprint in Home Assistant Core, simulate vacuum state changes, and verify the captured notification calls. They do not test push delivery or how the notification looks on a physical phone.

```sh
uv run --no-project --python 3.14 --with 'homeassistant==2026.7.0' python -m unittest discover -s tests -v
```
