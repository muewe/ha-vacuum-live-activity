"""Exercise the blueprint on real Home Assistant Core with captured notify calls."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

from homeassistant import loader
from homeassistant.bootstrap import async_load_base_functionality
from homeassistant.config_entries import ConfigEntries
from homeassistant.core import HomeAssistant, callback
from homeassistant.setup import async_setup_component

BLUEPRINT = (
    Path(__file__).resolve().parents[1]
    / "blueprints/automation/vacuum_live_activity.yaml"
)
VACUUM = "vacuum.test_robot"
AUTOMATION = "automation.test_vacuum_activity"
PHONES = ("mobile_app_iphone", "mobile_app_android")


class BlueprintTests(unittest.IsolatedAsyncioTestCase):
    async def set_up_blueprint(self, *, with_metrics=False, initial_state="docked"):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        config = Path(directory.name)
        folder = config / "blueprints/automation/local"
        folder.mkdir(parents=True)
        shutil.copyfile(BLUEPRINT, folder / BLUEPRINT.name)
        self.hass = hass = HomeAssistant(directory.name)
        self.addAsyncCleanup(hass.async_stop)
        hass.config.skip_pip = True
        loader.async_setup(hass)
        hass.config_entries = ConfigEntries(hass, {})
        self.assertTrue(await async_load_base_functionality(hass))
        self.calls = []

        @callback
        def capture(call):
            self.calls.append((call.service, dict(call.data)))

        for phone in PHONES:
            hass.services.async_register("notify", phone, capture)
        self.attrs = {"friendly_name": "Test Vacuum"}
        hass.states.async_set(VACUUM, initial_state, self.attrs)
        inputs = {
            "vacuum_entity": VACUUM,
            "notify_actions": [
                f"notify.{PHONES[0]}",
                f" notify.{PHONES[1]} ",
                f"notify.{PHONES[0]}",
                "homeassistant.stop",
            ],
        }
        if with_metrics:
            inputs.update(
                progress_sensor="sensor.progress",
                battery_sensor="sensor.battery",
                tap_path="/dashboard-home/cleaning",
            )
        self.assertTrue(
            await async_setup_component(
                hass,
                "automation",
                {
                    "automation": [
                        {
                            "id": "test_vacuum_activity",
                            "alias": "Test Vacuum Activity",
                            "use_blueprint": {
                                "path": f"local/{BLUEPRINT.name}",
                                "input": inputs,
                            },
                        }
                    ]
                },
            )
        )
        await hass.async_start()
        await hass.async_block_till_done()
        self.assertEqual(hass.states.get(AUTOMATION).state, "on")

    async def set_vacuum(self, state):
        self.calls.clear()
        self.hass.states.async_set(VACUUM, state, self.attrs)
        await self.hass.async_block_till_done()

    async def manually_run(self):
        self.calls.clear()
        await self.hass.services.async_call(
            "automation", "trigger", {"entity_id": AUTOMATION}, blocking=True
        )
        await self.hass.async_block_till_done()

    def payload(self):
        self.assertEqual([service for service, _ in self.calls], list(PHONES))
        self.assertEqual(self.calls[0][1], self.calls[1][1])
        return self.calls[0][1]

    async def test_lifecycle_and_stable_tag(self):
        await self.set_up_blueprint()
        await self.set_vacuum("cleaning")
        first = self.payload()
        data = first["data"]
        tag = data["tag"]
        self.assertTrue(re.fullmatch("[a-zA-Z0-9_-]{1,64}", tag))
        self.assertEqual(first["title"], "Test Vacuum")
        self.assertEqual(first["message"], "Cleaning")
        self.assertIs(data["live_update"], True)
        self.assertNotIn("progress", data)
        self.assertEqual(data["url"], f"/?more-info-entity-id={VACUUM}")
        self.assertEqual(data["clickAction"], data["url"])

        for state, label, chip in (
            ("paused", "Paused", "Paused"),
            ("returning", "Returning to dock", "Docking"),
        ):
            await self.set_vacuum(state)
            update = self.payload()
            self.assertEqual(update["data"]["tag"], tag)
            self.assertEqual(update["message"], label)
            self.assertEqual(update["data"]["critical_text"], chip)

        await self.set_vacuum("docked")
        self.assertEqual(
            self.payload(), {"message": "clear_notification", "data": {"tag": tag}}
        )

    async def test_metrics_and_unavailable_values(self):
        await self.set_up_blueprint(with_metrics=True)
        self.attrs["battery_level"] = 75
        self.hass.states.async_set("sensor.progress", "0")
        self.hass.states.async_set("sensor.battery", "90")
        await self.set_vacuum("cleaning")
        payload = self.payload()
        self.assertEqual(payload["message"], "Cleaning · 0% complete · Battery 90%")
        self.assertEqual(payload["data"]["progress"], 0)
        self.assertEqual(payload["data"]["progress_max"], 100)
        self.assertEqual(payload["data"]["url"], "/dashboard-home/cleaning")
        self.assertEqual(payload["data"]["critical_text"], "0%")

        self.hass.states.async_set("sensor.progress", "101")
        self.hass.states.async_set("sensor.battery", "unavailable")
        await self.manually_run()
        payload = self.payload()
        self.assertEqual(payload["message"], "Cleaning · Battery 75%")
        self.assertNotIn("progress", payload["data"])

    async def test_startup_and_brief_offline(self):
        await self.set_up_blueprint(initial_state="cleaning")
        self.assertEqual(self.payload()["message"], "Cleaning")
        await self.set_vacuum("unavailable")
        self.assertEqual(self.calls, [])
        await self.set_vacuum("returning")
        self.assertEqual(self.payload()["message"], "Returning to dock")
        await self.set_vacuum("error")
        self.assertEqual(self.payload()["message"], "clear_notification")
