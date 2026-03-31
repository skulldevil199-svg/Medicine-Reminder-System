"""
reminder.py — Background reminder thread for Medicine Reminder System.

Runs as a daemon thread; checks every 30 seconds whether any medicine
is due at the current HH:MM time and fires a callback if so.
Each (medicine_id, time_slot, date) combination is only triggered once
per day to avoid repeated popups.
"""

import threading
import time
from datetime import datetime


class ReminderThread(threading.Thread):
    """
    A daemon thread that periodically checks for due medicines and
    calls `on_reminder(medicine, time_slot)` when one is found.

    Args:
        get_medicines_func (callable): Zero-argument function that returns
                                       the current list of medicine dicts.
        on_reminder_func   (callable): Called with (medicine_dict, time_str)
                                       when a reminder fires.
    """

    def __init__(self, get_medicines_func, on_reminder_func):
        super().__init__(daemon=True)
        self.get_medicines = get_medicines_func
        self.on_reminder = on_reminder_func
        self._notified = set()          # tracks (med_id, time_slot, date)
        self._stop_event = threading.Event()

    # ── Public API ──────────────────────────────

    def stop(self):
        """Signal the thread to exit cleanly."""
        self._stop_event.set()

    # ── Internal ────────────────────────────────

    def run(self):
        while not self._stop_event.is_set():
            try:
                self._check_reminders()
            except Exception as exc:
                # Never crash the reminder thread silently
                print(f"[ReminderThread] Error during check: {exc}")
            self._stop_event.wait(timeout=30)   # sleep 30 s between checks

    def _check_reminders(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")

        for med in self.get_medicines():
            for slot in med.get("times", []):
                key = (med["id"], slot, today)
                if slot == current_time and key not in self._notified:
                    self._notified.add(key)
                    self.on_reminder(med, slot)
