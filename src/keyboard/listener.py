"""
Push-to-Talk listener using evdev.
Works at kernel level - compatible with Wayland and X11.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from evdev import InputDevice, ecodes, list_devices

logger = logging.getLogger(__name__)


class PTTListener:
    """Push-to-Talk listener - detects key press and release."""

    # Device names to skip (virtual/non-essential)
    EXCLUDED_NAMES = {'ydotoold', 'virtual'}

    def __init__(self, ptt_key: str = "KEY_RIGHTCTRL"):
        self.ptt_key = ptt_key
        self._validate_ptt_key()
        self.devices = self._find_keyboards()

    def _validate_ptt_key(self) -> None:
        """Validate that PTT_KEY is a valid evdev key code."""
        if not hasattr(ecodes, self.ptt_key):
            valid_keys = [k for k in dir(ecodes) if k.startswith("KEY_")]
            raise ValueError(
                f"Invalid PTT key: '{self.ptt_key}'. "
                f"Must be a valid evdev key code (e.g., KEY_RIGHTCTRL). "
                f"Available keys: {', '.join(valid_keys[:10])}..."
            )

    def _find_keyboards(self) -> list[InputDevice]:
        """Finds all physical keyboards."""
        keyboards = []
        for path in list_devices():
            device = InputDevice(path)

            # Skip virtual devices
            name_lower = device.name.lower()
            if any(excl in name_lower for excl in self.EXCLUDED_NAMES):
                continue

            caps = device.capabilities()
            if ecodes.EV_KEY in caps:
                keys = caps[ecodes.EV_KEY]
                # Check if it has typical keyboard keys + PTT key
                ptt_code = getattr(ecodes, self.ptt_key)
                if ecodes.KEY_A in keys and ecodes.KEY_ENTER in keys and ptt_code in keys:
                    keyboards.append(device)

        if not keyboards:
            raise RuntimeError(
                "No keyboard found. "
                "Check permissions - user must be in 'input' group. "
                "Run: sudo usermod -a -G input $USER"
            )

        return keyboards

    async def _listen_device(
        self,
        device: InputDevice,
        on_press: Callable[[], Awaitable[None]],
        on_release: Callable[[], Awaitable[None]],
    ) -> None:
        """Listens on a single device."""
        ptt_code = getattr(ecodes, self.ptt_key)

        try:
            async for event in device.async_read_loop():
                if event.type == ecodes.EV_KEY and event.code == ptt_code:
                    if event.value == 1:  # Key press
                        await on_press()
                    elif event.value == 0:  # Key release
                        await on_release()
        except Exception:
            logger.exception("Error listening on device %s", device.name)

    async def listen(
        self,
        on_press: Callable[[], Awaitable[None]],
        on_release: Callable[[], Awaitable[None]],
    ) -> None:
        """
        Listens for PTT key on all keyboards.

        Args:
            on_press: async callback called when key is pressed
            on_release: async callback called when key is released
        """
        tasks = [
            self._listen_device(device, on_press, on_release)
            for device in self.devices
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Device %s failed: %s", self.devices[i].name, result)
