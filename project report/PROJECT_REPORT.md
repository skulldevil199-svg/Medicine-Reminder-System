# Project Report — Medicine Reminder System
### BYOP Capstone Submission | Python / Programming Course

---

## 1. Problem Statement

Medication non-adherence — the failure to take prescribed medicines at the correct time and in the correct dose — is one of the most significant yet overlooked public health challenges. According to the World Health Organization, only about 50% of patients with chronic diseases follow their prescribed medication schedules consistently. The consequences range from worsened health outcomes to avoidable hospital readmissions.

This problem is especially common among:
- Elderly individuals managing multiple medicines simultaneously
- Working adults with irregular schedules
- Anyone on a multi-dose-per-day regimen where timing matters (e.g. antibiotics, insulin, blood pressure medication)

The root cause is simple: **people forget.** No sophisticated diagnosis is required. What is needed is a reliable, private, always-available reminder system that also helps users see, at a glance, whether they have kept up with their regimen.

I chose this problem because it is observable in everyday life — including within my own family — and because the solution maps naturally onto the Python programming concepts covered in this course.

---

## 2. Why This Problem Matters

A missed dose is rarely a single event. Missed doses compound: patients feel better after a few days of antibiotics and stop taking them, enabling antibiotic resistance. A diabetic patient skips a morning dose and their blood sugar spikes by evening. A cardiac patient forgets their evening pill and their pressure is elevated through the night.

A desktop reminder application does not replace a doctor, but it can:

- Reduce cognitive load by automating dose-time tracking
- Create a visible log that patients can share with healthcare providers
- Build accountability through status marking (taken / missed / skipped)

The solution is intentionally simple and local — no cloud, no account, no privacy risks.

---

## 3. Solution Overview

I built a desktop GUI application in Python called the **Medicine Reminder System**. It has three main components:

### 3.1 Data Layer (`storage.py`)
All medicine information and dose logs are persisted as JSON files in a local `data/` directory. The storage module exposes clean functions for CRUD operations on medicines and append-only operations on logs. Using JSON and the standard `json` library was a deliberate choice — it keeps the project dependency-free and the stored data human-readable.

### 3.2 Reminder Engine (`reminder.py`)
A background daemon thread (`ReminderThread`) runs throughout the application's lifetime. It wakes every 30 seconds, reads the current system time, and compares it against every scheduled dose time across all medicines. If a match is found — and that specific (medicine, time, date) combination has not already been alerted — a callback fires the popup onto the main GUI thread via `root.after()`. This design keeps the GUI thread unblocked while still delivering accurate, once-per-dose-per-day alerts.

### 3.3 GUI (`main.py`)
The interface is built using tkinter with ttk widgets for a consistent look. It is organized into three tabs:

- **My Medicines** — full CRUD interface with a Treeview list and an Add/Edit modal dialog
- **Today's Schedule** — a dynamically generated view showing every scheduled dose for today, colour-coded by its current status (pending, taken, skipped, missed)
- **Dose History** — a reverse-chronological log of all recorded dose events

---

## 4. Technical Decisions and Justification

| Decision | Rationale |
|---|---|
| **tkinter over CLI** | A GUI is more usable for the target audience (non-technical users managing health). tkinter is part of Python's standard library, so no extra installation is needed. |
| **JSON over SQLite** | JSON files are simpler to inspect and understand. For a project of this scale, a full relational database would be overengineering. |
| **Daemon thread for reminders** | Ensures the thread exits automatically when the main app closes, avoiding lingering background processes. |
| **`root.after()` for UI updates from thread** | tkinter is not thread-safe. Scheduling UI updates via `after()` keeps all widget operations on the main thread, preventing race conditions. |
| **One-file-per-concern structure** | Splitting logic into `main.py`, `storage.py`, and `reminder.py` follows the single-responsibility principle and makes the codebase easier to navigate and test. |

---

## 5. Concepts Applied from the Course

- **Functions and modules** — Logic is encapsulated in named functions with clear signatures; modules separate concerns.
- **File I/O** — `json.load()` and `json.dump()` handle all data persistence.
- **Object-Oriented Programming** — `MedicineReminderApp`, `MedicineDialog`, and `ReminderThread` are implemented as classes with `__init__` and instance methods.
- **Strings and datetime manipulation** — `strptime` / `strftime` for parsing and formatting time strings; string methods for validation.
- **Conditional logic and loops** — Used throughout for filtering records, validating input, and matching scheduled times.
- **Exception handling** — Input validation errors are caught in the dialog; the reminder thread wraps its check loop in try/except to avoid silent crashes.
- **Data structures** — Lists of dicts are the core data model; set is used in the reminder thread to track already-notified events without duplication.

---

## 6. Challenges Faced

**Challenge 1: Thread-safe GUI updates**
When the reminder thread detects a due medicine, it cannot directly call tkinter functions — doing so from outside the main thread causes unpredictable crashes. The fix was to use `root.after(0, callback)`, which schedules the popup to be displayed on the main event loop safely.

**Challenge 2: Preventing duplicate reminders**
Without tracking what has already been alerted, the reminder thread would fire a new popup every 30 seconds for as long as the minute matched. I solved this using a `set` of `(medicine_id, time_slot, date)` tuples. Each combination is added to the set on first trigger and ignored on all subsequent checks within the same day.

**Challenge 3: Linking today's doses to existing log entries**
The "Today" tab needed to show the correct status for each scheduled dose. I solved this by building a lookup dictionary keyed on `(medicine_id, HH:MM)` from that day's logs, then using `.get()` with a default of `"pending"` for each medicine-time pair.

**Challenge 4: Modal dialog return values**
tkinter dialogs do not have a built-in return-value mechanism. I implemented this by storing the result in `self.result` on the `Toplevel` instance and calling `self.wait_window()` so the parent window blocks until the dialog closes, then reads the result.

---

## 7. Limitations and Future Improvements

| Limitation | Potential Improvement |
|---|---|
| Reminders only work while the app is open | Use the OS task scheduler (e.g. Windows Task Scheduler, cron) to auto-launch the app at login |
| No weekly summary or adherence statistics | Add a fourth tab with a chart (matplotlib) showing taken-vs-missed rates |
| No multi-user support | Add user profiles, each with their own data directory |
| No sound alert | Use the `playsound` library to play a gentle chime alongside the popup |
| Single-machine only | Cloud sync (e.g. with a simple SQLite + file sync approach) for cross-device support |

---

## 8. What I Learned

This project taught me that the most important programming skill is **decomposing a problem into independently testable pieces**. Writing `storage.py` as a pure data layer with no GUI code, and `reminder.py` with no knowledge of tkinter, meant I could reason about each part in isolation.

I also learned the practical meaning of thread safety — not as an abstract concept but as a real constraint that caused visible, reproducible bugs until I understood `root.after()`.

Finally, working with a user-facing GUI forced me to think about edge cases I would have ignored in a CLI project: what if the user clicks "Edit" without selecting a row? What if they enter `8:00` instead of `08:00`? Defensive programming and clear error messages turned out to be as important as the core logic.

---

## 9. Conclusion

The Medicine Reminder System is a purposeful, real-world application that directly addresses a common health problem using pure Python. It demonstrates clean module design, GUI development, multi-threading, file persistence, and user experience thinking — all within a codebase that is small enough to understand fully, but rich enough to reflect genuine software engineering decisions.

---

*Submitted as part of the BYOP Capstone Activity.*
