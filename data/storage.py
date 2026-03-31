"""
storage.py — Data persistence layer for Medicine Reminder System.
Handles reading/writing medicines and dose logs to local JSON files.
"""

import json
import os
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MEDICINES_FILE = os.path.join(DATA_DIR, "medicines.json")
LOGS_FILE = os.path.join(DATA_DIR, "logs.json")


def _ensure_data_dir():
    """Create data directory and empty JSON files if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MEDICINES_FILE):
        with open(MEDICINES_FILE, "w") as f:
            json.dump([], f)
    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "w") as f:
            json.dump([], f)


# ──────────────────────────────────────────────
#  Medicine CRUD
# ──────────────────────────────────────────────

def load_medicines():
    """Return list of all saved medicines."""
    _ensure_data_dir()
    with open(MEDICINES_FILE, "r") as f:
        return json.load(f)


def save_medicines(medicines):
    """Persist the medicines list to disk."""
    _ensure_data_dir()
    with open(MEDICINES_FILE, "w") as f:
        json.dump(medicines, f, indent=2)


def add_medicine(name, dosage, times, notes=""):
    """
    Add a new medicine entry.

    Args:
        name    (str): Medicine name, e.g. "Aspirin"
        dosage  (str): Dosage string, e.g. "100 mg"
        times   (list[str]): List of HH:MM strings, e.g. ["08:00", "20:00"]
        notes   (str): Optional instructions, e.g. "Take with food"

    Returns:
        dict: The newly created medicine record.
    """
    medicines = load_medicines()
    medicine = {
        "id": str(uuid.uuid4()),
        "name": name,
        "dosage": dosage,
        "times": times,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
    }
    medicines.append(medicine)
    save_medicines(medicines)
    return medicine


def update_medicine(med_id, name, dosage, times, notes=""):
    """Update an existing medicine record by ID."""
    medicines = load_medicines()
    for med in medicines:
        if med["id"] == med_id:
            med["name"] = name
            med["dosage"] = dosage
            med["times"] = times
            med["notes"] = notes
            med["updated_at"] = datetime.now().isoformat()
            break
    save_medicines(medicines)


def delete_medicine(med_id):
    """Remove a medicine record and its associated future schedules."""
    medicines = load_medicines()
    medicines = [m for m in medicines if m["id"] != med_id]
    save_medicines(medicines)


# ──────────────────────────────────────────────
#  Dose Log
# ──────────────────────────────────────────────

def load_logs():
    """Return all dose log entries."""
    _ensure_data_dir()
    with open(LOGS_FILE, "r") as f:
        return json.load(f)


def save_logs(logs):
    """Persist dose logs to disk."""
    _ensure_data_dir()
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def log_dose(medicine_id, medicine_name, scheduled_time, status):
    """
    Record a dose event.

    Args:
        medicine_id   (str): UUID of the medicine.
        medicine_name (str): Human-readable medicine name.
        scheduled_time(str): "YYYY-MM-DD HH:MM" string.
        status        (str): One of "taken", "missed", "skipped".

    Returns:
        dict: The newly created log entry.
    """
    logs = load_logs()
    entry = {
        "id": str(uuid.uuid4()),
        "medicine_id": medicine_id,
        "medicine_name": medicine_name,
        "scheduled_time": scheduled_time,
        "status": status,
        "logged_at": datetime.now().isoformat(),
    }
    logs.append(entry)
    save_logs(logs)
    return entry


def get_today_logs():
    """Return only the log entries for today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    return [entry for entry in load_logs() if entry["scheduled_time"].startswith(today)]
