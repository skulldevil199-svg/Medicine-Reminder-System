# 💊 Medicine Reminder System

A desktop application built with Python and tkinter that helps users manage their daily medicines, receive on-time reminders, and track whether each dose was taken, skipped, or missed.

---

## 🩺 Problem Statement

Medication non-adherence is a widespread health problem. Patients — especially those on multiple daily medicines — frequently miss doses simply because they forget. This application provides a lightweight, offline-first solution to schedule reminders and maintain a dose log, directly on the user's desktop.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Add / Edit / Delete Medicines** | Store medicine name, dosage, one or more daily reminder times, and optional instructions |
| **Popup Reminders** | A background thread checks every 30 seconds and shows a desktop alert when a dose is due |
| **Today's Schedule** | See all doses for the current day at a glance; mark each as Taken, Skipped, or Missed |
| **Dose History** | Full log of every recorded dose event, colour-coded by status |
| **Persistent Storage** | All data is saved locally as JSON — no database or internet connection required |

---

## 📁 Project Structure

```
medicine_reminder/
│
├── main.py          # GUI application (tkinter) — entry point
├── storage.py       # Data layer — read/write medicines & logs as JSON
├── reminder.py      # Background daemon thread for due-time alerts
├── requirements.txt # No third-party dependencies
├── .gitignore
│
└── data/            # Auto-created on first run
    ├── medicines.json
    └── logs.json
```

---

## 🚀 Setup & Running

### Prerequisites

- **Python 3.8 or higher**
- tkinter (ships with Python on Windows and most Linux distros)

> **macOS users:** If tkinter is missing, install it via Homebrew:
> ```bash
> brew install python-tk
> ```

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/medicine-reminder.git
cd medicine-reminder

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

# 3. No packages to install — uses standard library only
#    (Verify with: pip install -r requirements.txt)

# 4. Run the application
python main.py
```

---

## 🖥️ How to Use

### Adding a Medicine
1. Open the **💊 My Medicines** tab.
2. Click **➕ Add Medicine**.
3. Fill in the name, dosage, reminder times (comma-separated, 24-hour format, e.g. `08:00, 14:00, 21:00`), and any notes.
4. Click **Save**.

### Receiving Reminders
The app automatically checks every 30 seconds. When the current clock time matches a scheduled dose, a popup appears with the medicine name, dosage, and any notes. Each reminder fires once per dose per day.

> ⚠️ Keep the application running in the background for reminders to work.

### Marking Doses
1. Go to the **📅 Today's Schedule** tab.
2. Select a dose row.
3. Click **✅ Mark Taken**, **⏭️ Mark Skipped**, or **❌ Mark Missed**.

### Viewing History
Switch to the **📋 Dose History** tab to see all past dose records. Entries are shown in reverse chronological order and colour-coded:
- 🟢 **Green** — Taken
- 🔴 **Red** — Missed
- 🟡 **Amber** — Skipped

---

## 🗂️ Data Storage

Data is stored locally in the `data/` directory:

| File | Contents |
|---|---|
| `data/medicines.json` | List of medicine records (id, name, dosage, times, notes) |
| `data/logs.json` | List of dose log events (medicine, scheduled time, status, logged_at) |

Both files are created automatically on first run. They are excluded from version control via `.gitignore`.

---

## 🧪 Running with Sample Data

To test the app quickly, you can add two sample medicines after launching:

| Medicine | Dosage | Times |
|---|---|---|
| Vitamin D | 1000 IU | `08:00` |
| Metformin | 500 mg | `07:30, 19:30` |

Set one reminder time to a minute or two in the future to see the popup alert in action.

---

## 🛠️ Key Concepts Used

- **tkinter & ttk** — GUI framework (Notebook tabs, Treeview, Toplevel dialogs)
- **threading.Thread** — Background reminder daemon
- **JSON file I/O** — Persistent local storage without a database
- **uuid** — Unique identifiers for each record
- **datetime & strptime** — Time parsing and schedule matching
- **OOP** — `MedicineReminderApp`, `MedicineDialog`, `ReminderThread` classes

---

## 📄 License

MIT License — free to use, modify, and distribute.
# Medicine-Reminder-System
 Never miss a dose. A Python app that reminds you to take your medicines on time and keeps a log of your daily dose history.
