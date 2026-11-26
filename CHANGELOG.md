# Changelog

## 1.1.0

- Keep a "Cleaning complete" live activity after the vacuum docks at the end of a run, instead of dismissing it.
- Add the optional `show_completion` input (default: enabled) to turn the completion message off. Existing automations pick it up without changes.

## 1.0.0 - 2026-11-21

- Initial public release for iOS Live Activities and Android Live Updates.
- Display cleaning, paused, and returning-to-dock states, with optional cleaning progress and battery level.
- Update a single notification per vacuum and phone, then dismiss it when the run ends.
- Provide a stable Home Assistant import URL, in-place re-import instructions, and a tagged version for users who want to pin it.
