# Robot Vacuum Live Activity for Home Assistant

This Home Assistant blueprint shows your robot vacuum's status on iPhone and Android while it is cleaning, paused, or returning to its dock. It updates the same Live Activity or Live Update and dismisses it when the run ends. It does not send commands to the vacuum.

[![Import the robot vacuum blueprint into Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fmuewe%2Fha-vacuum-live-activity%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fvacuum_live_activity.yaml)

See [GitHub releases](https://github.com/muewe/ha-vacuum-live-activity/releases) for tagged versions and the [changelog](CHANGELOG.md) for changes by version.

## Requirements

- **Home Assistant Core 2026.7.0 or later** and an up-to-date Home Assistant Companion app with notifications enabled.
- **iPhone with iOS 17.2 or later:** The Live Activity appears on the Lock Screen and in the Dynamic Island on supported models. Check **Settings → Live Activities** in the Companion app to see whether the feature is available and enabled. The Companion documentation describes the iOS feature as beta. Open the app at least once after setup, and make sure it can reach your Home Assistant server when you are away.
- **Android 16 or later:** Live Updates may include a Lock Screen notification and a status bar chip, depending on the device. On Samsung, you may need to enable **Live notifications for all apps** in Developer options for the chip to appear. Older Android versions do not support native Live Updates.
- **Robot vacuum:** A `vacuum.*` entity that reports [standard Home Assistant vacuum states](https://www.home-assistant.io/integrations/vacuum/#vacuum-states). Cleaning progress and a separate battery sensor are optional.

The [Companion documentation for Live Activities and Live Updates](https://companion.home-assistant.io/docs/notifications/live-activities/) covers platform requirements and the shared notification payload. The blueprint uses the [Companion `url` and `clickAction` fields](https://companion.home-assistant.io/docs/notifications/notifications-basic/) to open a destination on tap.

## Installation

1. Use the import button above, or open **Settings → Automations & scenes → Blueprints → Import blueprint** and paste the [blueprint URL from `main`](https://github.com/muewe/ha-vacuum-live-activity/blob/main/blueprints/automation/vacuum_live_activity.yaml). Select **Preview**, then **Import**.
2. Create an automation from **Robot Vacuum: Live Activity for iOS and Android** and select your `vacuum.*` entity.
3. In **Developer tools → Actions**, search for `notify.mobile_app_`. Add one full action name per phone. You can use iPhone and Android recipients in the same automation.
4. Optionally, select a cleaning progress sensor or a battery sensor with values from 0 to 100, or enter a relative dashboard path. If the path is blank, tapping the notification opens the vacuum's more-info dialog.
5. Save the automation and start a cleaning run. On both phones, verify that the notification appears, updates when the vacuum pauses, and disappears when it docks.

## Updating an existing installation

- **Imported from `main`:** In **Settings → Automations & scenes → Blueprints**, open the blueprint's menu and select **Re-import blueprint**. Review the preview and confirm the update. Home Assistant uses the saved source URL to replace the blueprint in place, retaining your automation inputs. This is a manual update, not an automatic one.
- **Copied locally before the repository was public:** Keep the original file path so your automation still points to the same blueprint. Replace the existing YAML with the current [blueprint YAML](blueprints/automation/vacuum_live_activity.yaml), then add the following line under `blueprint:` at the same indentation as `name:`. Reload automations to pick up the change. The saved URL lets you use **Re-import blueprint** in the future.

  ```yaml
    source_url: https://github.com/muewe/ha-vacuum-live-activity/blob/main/blueprints/automation/vacuum_live_activity.yaml
  ```

- **Installing a specific version:** Import the YAML from a GitHub release tag instead of `main`. Re-importing from a tag will continue to fetch that same version. Use `main` if you want to follow later releases.

See the [Home Assistant blueprint contributor guide](https://contributors.home-assistant.io/marketplace/guides/blueprints/) for how re-imports work.

## Behavior

| Vacuum state | Notification |
| --- | --- |
| `cleaning` | Cleaning |
| `paused` | Paused |
| `returning` | Returning to dock |
| `docked` right after `cleaning` or `returning` | Cleaning complete (stays until dismissed or the next run starts) |
| `docked`, `idle`, `error`, or another inactive state otherwise | Dismissed |
| `unknown` or `unavailable` | Stays visible through a brief disconnect and is dismissed if the state persists for two minutes |

The blueprint responds to vacuum state changes as they happen. While a run is active, it also refreshes optional readings every five minutes. The progress bar appears only when a valid cleaning progress reading is available; battery level is displayed separately. The completion message replaces the running activity and is not sticky, so tapping it dismisses it on Android. Turn it off with **Keep a completion message** under the optional display settings. A Home Assistant restart, a manual **Run actions**, or the vacuum going offline for two minutes dismisses it, because the blueprint can no longer tell that a run just finished. A paused run that is docked manually is not reported as complete. After a restart or manual run, the blueprint updates or dismisses the notification based on the current state.

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

## Release maintenance

Keep the import path and existing input keys and value formats stable. Give new optional inputs defaults and publish incompatible changes under a new blueprint path. When preparing a release, update the displayed version in the blueprint description and the changelog, run the tests, and publish a GitHub release with a matching `vMAJOR.MINOR.PATCH` tag. The `main` import URL should always point to a tested, backward-compatible version of this blueprint.
