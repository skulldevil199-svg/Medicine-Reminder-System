"""
main.py — Entry point for the Medicine Reminder System.

Run with:
    python main.py

Requires Python 3.8+ (tkinter is included in the standard library).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import storage
from reminder import ReminderThread


# ══════════════════════════════════════════════════════════════════════════════
#  Dialog — Add / Edit Medicine
# ══════════════════════════════════════════════════════════════════════════════

class MedicineDialog(tk.Toplevel):
    """
    Modal dialog for creating or editing a medicine entry.
    Sets `self.result` to a dict on success, or leaves it None on cancel.
    """

    def __init__(self, parent, title="Medicine", prefill=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x310")
        self.resizable(False, False)
        self.grab_set()                 # make modal
        self.result = None
        self._build(prefill or {})
        self.wait_window()              # block until closed

    def _build(self, prefill):
        pad = {"padx": 12, "pady": 5}

        # ── Fields ──────────────────────────────
        tk.Label(self, text="Medicine Name *", anchor="w").grid(
            row=0, column=0, sticky="w", **pad)
        self.name_var = tk.StringVar(value=prefill.get("name", ""))
        tk.Entry(self, textvariable=self.name_var, width=28).grid(
            row=0, column=1, **pad)

        tk.Label(self, text="Dosage *", anchor="w").grid(
            row=1, column=0, sticky="w", **pad)
        self.dosage_var = tk.StringVar(value=prefill.get("dosage", ""))
        tk.Entry(self, textvariable=self.dosage_var, width=28).grid(
            row=1, column=1, **pad)

        tk.Label(self, text="Reminder Times *", anchor="w").grid(
            row=2, column=0, sticky="w", **pad)
        times_str = ", ".join(prefill.get("times", []))
        self.times_var = tk.StringVar(value=times_str)
        tk.Entry(self, textvariable=self.times_var, width=28).grid(
            row=2, column=1, **pad)
        tk.Label(self, text="   Comma-separated  e.g.  08:00, 14:00, 20:00",
                 fg="gray", font=("Helvetica", 8)).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=12)

        tk.Label(self, text="Notes / Instructions", anchor="w").grid(
            row=4, column=0, sticky="w", **pad)
        self.notes_var = tk.StringVar(value=prefill.get("notes", ""))
        tk.Entry(self, textvariable=self.notes_var, width=28).grid(
            row=4, column=1, **pad)

        # ── Buttons ─────────────────────────────
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=16)
        ttk.Button(btn_frame, text="  Save  ", command=self._save).pack(
            side=tk.LEFT, padx=8)
        ttk.Button(btn_frame, text=" Cancel ", command=self.destroy).pack(
            side=tk.LEFT, padx=8)

    def _save(self):
        name = self.name_var.get().strip()
        dosage = self.dosage_var.get().strip()
        times_raw = self.times_var.get().strip()

        if not name or not dosage or not times_raw:
            messagebox.showerror("Missing Fields",
                                 "Name, Dosage, and Times are required.",
                                 parent=self)
            return

        times = [t.strip() for t in times_raw.split(",") if t.strip()]
        for t in times:
            try:
                datetime.strptime(t, "%H:%M")
            except ValueError:
                messagebox.showerror(
                    "Invalid Time Format",
                    f"'{t}' is not valid. Please use HH:MM (24-hour) format.",
                    parent=self)
                return

        self.result = {
            "name": name,
            "dosage": dosage,
            "times": times,
            "notes": self.notes_var.get().strip(),
        }
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  Main Application
# ══════════════════════════════════════════════════════════════════════════════

class MedicineReminderApp:
    """
    Root application class.
    Builds a three-tab tkinter interface and starts the reminder daemon.
    """

    STATUS_EMOJI = {
        "taken":   "✅  Taken",
        "missed":  "❌  Missed",
        "skipped": "⏭️  Skipped",
        "pending": "⏳  Pending",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("💊 Medicine Reminder System")
        self.root.geometry("740x540")
        self.root.minsize(600, 460)

        self._apply_style()
        self._build_header()
        self._build_tabs()
        self._start_reminder_thread()
        self.refresh_all()

    # ── Styling ─────────────────────────────────────────────────────────────

    def _apply_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TNotebook.Tab", padding=[12, 5], font=("Helvetica", 10))
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Helvetica", 10))

    # ── Header ──────────────────────────────────────────────────────────────

    def _build_header(self):
        header = tk.Frame(self.root, bg="#2563EB", pady=12)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="💊  Medicine Reminder System",
            font=("Helvetica", 16, "bold"),
            bg="#2563EB", fg="white",
        ).pack()
        tk.Label(
            header,
            text="Track your medicines · Get timely reminders · Log every dose",
            font=("Helvetica", 9),
            bg="#2563EB", fg="#BFDBFE",
        ).pack()

    # ── Tabs ────────────────────────────────────────────────────────────────

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.tab_medicines = ttk.Frame(self.notebook, padding=4)
        self.tab_today     = ttk.Frame(self.notebook, padding=4)
        self.tab_logs      = ttk.Frame(self.notebook, padding=4)

        self.notebook.add(self.tab_medicines, text="  💊 My Medicines  ")
        self.notebook.add(self.tab_today,     text="  📅 Today's Schedule  ")
        self.notebook.add(self.tab_logs,      text="  📋 Dose History  ")

        self._build_medicines_tab()
        self._build_today_tab()
        self._build_logs_tab()

    # ── Tab 1 : My Medicines ────────────────────────────────────────────────

    def _build_medicines_tab(self):
        btn_row = tk.Frame(self.tab_medicines)
        btn_row.pack(fill=tk.X, pady=(4, 6))

        ttk.Button(btn_row, text="➕  Add Medicine",
                   command=self.add_medicine).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="✏️  Edit",
                   command=self.edit_medicine).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="🗑️  Delete",
                   command=self.delete_medicine).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="🔄  Refresh",
                   command=self.refresh_medicines).pack(side=tk.RIGHT, padx=3)

        cols = ("Name", "Dosage", "Reminder Times", "Notes")
        self.med_tree = ttk.Treeview(
            self.tab_medicines, columns=cols, show="headings", height=16)

        widths = {"Name": 160, "Dosage": 110, "Reminder Times": 170, "Notes": 260}
        for col in cols:
            self.med_tree.heading(col, text=col)
            self.med_tree.column(col, width=widths[col])

        vsb = ttk.Scrollbar(self.tab_medicines, orient=tk.VERTICAL,
                            command=self.med_tree.yview)
        self.med_tree.configure(yscrollcommand=vsb.set)
        self.med_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    # ── Tab 2 : Today's Schedule ────────────────────────────────────────────

    def _build_today_tab(self):
        info = tk.Label(
            self.tab_today,
            text="Select a row and mark its status for today.",
            font=("Helvetica", 10), fg="#555",
        )
        info.pack(anchor="w", pady=(2, 4))

        btn_row = tk.Frame(self.tab_today)
        btn_row.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(btn_row, text="✅  Mark Taken",
                   command=lambda: self.log_dose("taken")).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="⏭️  Mark Skipped",
                   command=lambda: self.log_dose("skipped")).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="❌  Mark Missed",
                   command=lambda: self.log_dose("missed")).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_row, text="🔄  Refresh",
                   command=self.refresh_today).pack(side=tk.RIGHT, padx=3)

        cols = ("Medicine", "Dosage", "Scheduled Time", "Status")
        self.today_tree = ttk.Treeview(
            self.tab_today, columns=cols, show="headings", height=16)

        widths = {"Medicine": 200, "Dosage": 120, "Scheduled Time": 140, "Status": 160}
        for col in cols:
            self.today_tree.heading(col, text=col)
            self.today_tree.column(col, width=widths[col])

        # Row colours by status
        self.today_tree.tag_configure("taken",   background="#D1FAE5")
        self.today_tree.tag_configure("missed",  background="#FEE2E2")
        self.today_tree.tag_configure("skipped", background="#FEF9C3")
        self.today_tree.tag_configure("pending", background="#FFFFFF")

        self.today_tree.pack(fill=tk.BOTH, expand=True)

    # ── Tab 3 : Dose History ────────────────────────────────────────────────

    def _build_logs_tab(self):
        btn_row = tk.Frame(self.tab_logs)
        btn_row.pack(fill=tk.X, pady=(4, 6))
        ttk.Button(btn_row, text="🔄  Refresh",
                   command=self.refresh_logs).pack(side=tk.RIGHT, padx=3)

        cols = ("Medicine", "Scheduled Time", "Status", "Logged At")
        self.log_tree = ttk.Treeview(
            self.tab_logs, columns=cols, show="headings", height=16)

        widths = {"Medicine": 185, "Scheduled Time": 175,
                  "Status": 110, "Logged At": 175}
        for col in cols:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=widths[col])

        self.log_tree.tag_configure("taken",   foreground="#15803D")
        self.log_tree.tag_configure("missed",  foreground="#DC2626")
        self.log_tree.tag_configure("skipped", foreground="#B45309")

        vsb = ttk.Scrollbar(self.tab_logs, orient=tk.VERTICAL,
                            command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=vsb.set)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    # ══════════════════════════════════════════════════════════════════════
    #  Actions
    # ══════════════════════════════════════════════════════════════════════

    def add_medicine(self):
        dlg = MedicineDialog(self.root, title="Add New Medicine")
        if dlg.result:
            storage.add_medicine(**dlg.result)
            self.refresh_medicines()
            self.refresh_today()

    def edit_medicine(self):
        sel = self.med_tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Please select a medicine row to edit.")
            return
        med_id = self.med_tree.item(sel[0], "tags")[0]
        med = next((m for m in storage.load_medicines() if m["id"] == med_id), None)
        if not med:
            return
        dlg = MedicineDialog(self.root, title="Edit Medicine", prefill=med)
        if dlg.result:
            storage.update_medicine(med_id, **dlg.result)
            self.refresh_medicines()
            self.refresh_today()

    def delete_medicine(self):
        sel = self.med_tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Please select a medicine row to delete.")
            return
        med_id = self.med_tree.item(sel[0], "tags")[0]
        if messagebox.askyesno("Confirm Delete",
                               "Delete this medicine? This cannot be undone."):
            storage.delete_medicine(med_id)
            self.refresh_medicines()
            self.refresh_today()

    def log_dose(self, status: str):
        sel = self.today_tree.selection()
        if not sel:
            messagebox.showwarning("Nothing Selected",
                                   "Please select a dose row to mark.")
            return
        tags = self.today_tree.item(sel[0], "tags")
        med_id, time_slot = tags[0], tags[1]

        med = next((m for m in storage.load_medicines() if m["id"] == med_id), None)
        if not med:
            return

        today = datetime.now().strftime("%Y-%m-%d")
        scheduled = f"{today} {time_slot}"
        storage.log_dose(med_id, med["name"], scheduled, status)
        self.refresh_today()
        self.refresh_logs()

    # ══════════════════════════════════════════════════════════════════════
    #  Refresh helpers
    # ══════════════════════════════════════════════════════════════════════

    def refresh_all(self):
        self.refresh_medicines()
        self.refresh_today()
        self.refresh_logs()

    def refresh_medicines(self):
        for row in self.med_tree.get_children():
            self.med_tree.delete(row)
        for med in storage.load_medicines():
            self.med_tree.insert(
                "", tk.END,
                values=(
                    med["name"],
                    med["dosage"],
                    ", ".join(med.get("times", [])),
                    med.get("notes", ""),
                ),
                tags=(med["id"],),
            )

    def refresh_today(self):
        for row in self.today_tree.get_children():
            self.today_tree.delete(row)

        today = datetime.now().strftime("%Y-%m-%d")
        today_logs = storage.get_today_logs()
        # Build a quick lookup: (med_id, HH:MM) → status
        logged = {
            (lg["medicine_id"], lg["scheduled_time"].split(" ")[1]): lg["status"]
            for lg in today_logs
        }

        for med in storage.load_medicines():
            for slot in med.get("times", []):
                status = logged.get((med["id"], slot), "pending")
                self.today_tree.insert(
                    "", tk.END,
                    values=(
                        med["name"],
                        med["dosage"],
                        slot,
                        self.STATUS_EMOJI.get(status, status),
                    ),
                    tags=(med["id"], slot, status),
                )

    def refresh_logs(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        for entry in reversed(storage.load_logs()):
            logged_at = entry["logged_at"][:16].replace("T", "  ")
            self.log_tree.insert(
                "", tk.END,
                values=(
                    entry["medicine_name"],
                    entry["scheduled_time"],
                    entry["status"].capitalize(),
                    logged_at,
                ),
                tags=(entry["status"],),
            )

    # ══════════════════════════════════════════════════════════════════════
    #  Reminder daemon
    # ══════════════════════════════════════════════════════════════════════

    def _start_reminder_thread(self):
        self._reminder = ReminderThread(
            get_medicines_func=storage.load_medicines,
            on_reminder_func=self._on_reminder,
        )
        self._reminder.start()

    def _on_reminder(self, med: dict, time_slot: str):
        """Called from the reminder thread; posts the popup onto the main thread."""
        note_line = f"\nNote:      {med['notes']}" if med.get("notes") else ""
        msg = (
            f"Time to take your medicine!\n\n"
            f"Medicine:  {med['name']}\n"
            f"Dosage:    {med['dosage']}\n"
            f"Time:      {time_slot}"
            f"{note_line}"
        )
        self.root.after(0, lambda: messagebox.showinfo("💊 Reminder", msg))
        self.root.after(0, self.refresh_today)


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicineReminderApp(root)
    root.mainloop()
