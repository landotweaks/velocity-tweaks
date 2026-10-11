import os
import sys
import json
import subprocess
import platform
import ctypes
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "Velocity PC Optimizer"
CONFIG_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "VelocityOptimizer"
LOG_FILE = CONFIG_DIR / "actions.log"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# This list is deliberately limited to recognizable user applications.
# Core Windows services, security, drivers, and anti-cheat are never targets.
CANDIDATES = [
    {"name": "Discord", "process": "Discord.exe", "category": "Chat", "note": "Closes Discord desktop app. Save drafts/unsent messages first."},
    {"name": "Steam", "process": "steam.exe", "category": "Launcher", "note": "Closes Steam; do not select if your game needs the Steam client."},
    {"name": "Epic Games Launcher", "process": "EpicGamesLauncher.exe", "category": "Launcher", "note": "Closes Epic launcher; some games may need it open."},
    {"name": "Xbox app", "process": "XboxPcApp.exe", "category": "Launcher", "note": "Closes the Xbox app only, not Xbox services."},
    {"name": "Spotify", "process": "Spotify.exe", "category": "Media", "note": "Closes Spotify desktop app."},
    {"name": "Microsoft Teams", "process": "ms-teams.exe", "category": "Chat", "note": "Closes Teams. Avoid if you are in a call."},
    {"name": "Slack", "process": "slack.exe", "category": "Chat", "note": "Closes Slack desktop app."},
    {"name": "Telegram Desktop", "process": "Telegram.exe", "category": "Chat", "note": "Closes Telegram desktop app."},
    {"name": "WhatsApp", "process": "WhatsApp.exe", "category": "Chat", "note": "Closes WhatsApp desktop app."},
    {"name": "OneDrive", "process": "OneDrive.exe", "category": "Sync", "note": "Pauses sync by closing OneDrive. Do not select during active file uploads."},
    {"name": "Adobe Creative Cloud", "process": "Creative Cloud.exe", "category": "Creative", "note": "Closes Creative Cloud UI only; other Adobe components may remain."},
    {"name": "Battle.net", "process": "Battle.net.exe", "category": "Launcher", "note": "Closes Battle.net launcher; games may need it open."},
    {"name": "Riot Client", "process": "RiotClientServices.exe", "category": "Launcher", "note": "Not recommended while playing Riot games; close only when not using them."},
    {"name": "GOG Galaxy", "process": "GalaxyClient.exe", "category": "Launcher", "note": "Closes GOG Galaxy; some games may need it open."},
    {"name": "EA app", "process": "EADesktop.exe", "category": "Launcher", "note": "Closes EA app; EA games may need it open."},
    {"name": "Ubisoft Connect", "process": "upc.exe", "category": "Launcher", "note": "Closes Ubisoft Connect; Ubisoft games may need it open."},
    {"name": "Google Drive", "process": "GoogleDriveFS.exe", "category": "Sync", "note": "Stops Drive sync while closed. Avoid during active uploads."},
    {"name": "Dropbox", "process": "Dropbox.exe", "category": "Sync", "note": "Stops Dropbox sync while closed. Avoid during active uploads."},
    {"name": "Phone Link", "process": "PhoneExperienceHost.exe", "category": "Utility", "note": "Closes Phone Link UI; it may relaunch automatically."},
    {"name": "Widgets", "process": "Widgets.exe", "category": "Utility", "note": "Closes the Widgets process if present; Windows may restart it."},
    {"name": "YourPhone", "process": "YourPhone.exe", "category": "Utility", "note": "Closes legacy Phone Link process if present."},
    {"name": "Overwolf", "process": "Overwolf.exe", "category": "Overlay", "note": "Closes Overwolf and may affect related game overlays."},
    {"name": "OBS Studio", "process": "obs64.exe", "category": "Capture", "note": "Closes OBS. Do not select while recording or streaming."},
    {"name": "Medal", "process": "Medal.exe", "category": "Capture", "note": "Closes Medal capture app; unsaved clips or capture sessions may be affected."},
    {"name": "Outplayed", "process": "Outplayed.exe", "category": "Capture", "note": "Closes Outplayed capture app."},
    {"name": "NVIDIA App", "process": "NVIDIA app.exe", "category": "Utility", "note": "Closes the NVIDIA App UI only, not GPU driver processes."},
    {"name": "AMD Software", "process": "RadeonSoftware.exe", "category": "Utility", "note": "Closes AMD Software UI only, not driver components."},
    {"name": "Battle.net Update Agent", "process": "Agent.exe", "category": "Launcher", "note": "May be required for Battle.net updates or games; use only when idle."},
    {"name": "Razer Synapse", "process": "Razer Synapse 3.exe", "category": "Peripheral", "note": "May affect device profiles, macros, or lighting. Do not close if you rely on them."},
    {"name": "Logitech G HUB", "process": "lghub.exe", "category": "Peripheral", "note": "May affect mouse/keyboard profiles. Do not close if you rely on them."},
]

PROTECTED = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "winlogon.exe", "services.exe", "lsass.exe", "svchost.exe", "explorer.exe",
    "dwm.exe", "fontdrvhost.exe", "sihost.exe", "taskhostw.exe", "runtimebroker.exe",
    "audiodg.exe", "spoolsv.exe", "searchindexer.exe", "securityhealthservice.exe",
    "msmpeng.exe", "nissrv.exe", "antimalware service executable", "wudfhost.exe",
    "wininit.exe", "conhost.exe", "dllhost.exe", "ctfmon.exe", "gamebar.exe",
    "vgc.exe", "vgtray.exe", "easyanticheat.exe", "easyanticheat_eos.exe",
    "beservice.exe", "battleye.exe", "mhyprot2.sys", "faceitclient.exe",
}

def log_action(message):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except OSError:
        pass

def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def run_tasklist():
    try:
        out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True, timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        rows = []
        import csv, io
        for row in csv.reader(io.StringIO(out.stdout)):
            if row and len(row) >= 2:
                rows.append((row[0].strip('"'), row[1].strip('"')))
        return rows
    except Exception:
        return []

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1060x720")
        self.minsize(850, 600)
        self.configure(bg="#0b0e13")
        self.selected = set()
        self.proc_rows = []
        self._style()
        self._header()
        self._build_tabs()
        self.refresh_processes()
        self.detect_specs()

    def _style(self):
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TNotebook", background="#0b0e13", borderwidth=0)
        style.configure("TNotebook.Tab", background="#151d28", foreground="#9cabbc", padding=(16, 9), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", "#1b2a1c")], foreground=[("selected", "#a8f05a")])
        style.configure("Treeview", background="#111720", fieldbackground="#111720", foreground="#edf3fa", rowheight=28, bordercolor="#263241")
        style.configure("Treeview.Heading", background="#19222d", foreground="#a8f05a", relief="flat")
        style.map("Treeview", background=[("selected", "#294326")], foreground=[("selected", "#ffffff")])
        style.configure("TButton", background="#a8f05a", foreground="#10170a", padding=(12, 7), borderwidth=0)
        style.map("TButton", background=[("active", "#baff76")])
        style.configure("Secondary.TButton", background="#19222d", foreground="#edf3fa")
        style.configure("TLabel", background="#0b0e13", foreground="#edf3fa")
        style.configure("Muted.TLabel", background="#0b0e13", foreground="#91a0b4")
        style.configure("TCheckbutton", background="#111720", foreground="#edf3fa")
        style.configure("TEntry", fieldbackground="#111720", foreground="#edf3fa")

    def _header(self):
        top = tk.Frame(self, bg="#0b0e13")
        top.pack(fill="x", padx=22, pady=(18, 10))
        logo = tk.Label(top, text="V", bg="#a8f05a", fg="#10170a", font=("Segoe UI", 20, "bold"), width=2, height=1)
        logo.pack(side="left", padx=(0, 12))
        labels = tk.Frame(top, bg="#0b0e13"); labels.pack(side="left")
        tk.Label(labels, text="VELOCITY", bg="#0b0e13", fg="#edf3fa", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(labels, text="PC PERFORMANCE CONTROL CENTER", bg="#0b0e13", fg="#a8f05a", font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.admin_label = tk.Label(top, text="● STANDARD USER MODE", bg="#0b0e13", fg="#a8f05a", font=("Segoe UI", 9, "bold"))
        self.admin_label.pack(side="right")
        if is_admin():
            self.admin_label.config(text="● ADMIN SESSION (NOT REQUIRED)", fg="#e3c477")

    def _build_tabs(self):
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=22, pady=(0, 12))
        self.dashboard = tk.Frame(self.nb, bg="#0b0e13")
        self.specs = tk.Frame(self.nb, bg="#0b0e13")
        self.processes = tk.Frame(self.nb, bg="#0b0e13")
        self.guide = tk.Frame(self.nb, bg="#0b0e13")
        self.nb.add(self.dashboard, text="Dashboard")
        self.nb.add(self.specs, text="System Specs")
        self.nb.add(self.processes, text="Process Cleanup")
        self.nb.add(self.guide, text="Safe Tweaks")
        self._dashboard_tab()
        self._specs_tab()
        self._process_tab()
        self._guide_tab()

    def _panel(self, parent, title, desc=None):
        frame = tk.Frame(parent, bg="#111720", highlightbackground="#263241", highlightthickness=1)
        frame.pack(fill="x", padx=12, pady=8)
        tk.Label(frame, text=title, bg="#111720", fg="#a8f05a", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 3))
        if desc:
            tk.Label(frame, text=desc, bg="#111720", fg="#91a0b4", font=("Segoe UI", 9), wraplength=900, justify="left").pack(anchor="w", padx=14, pady=(0, 12))
        return frame

    def _dashboard_tab(self):
        p = self.dashboard
        tk.Label(p, text="Less background noise. More game time.", bg="#0b0e13", fg="#edf3fa", font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=12, pady=(16, 5))
        tk.Label(p, text="A review-first Windows optimizer. Nothing is killed unless you explicitly select it and confirm.", bg="#0b0e13", fg="#91a0b4", font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(0, 10))
        self._panel(p, "Quick cleanup", "Velocity only offers recognizable optional desktop apps. It never targets core Windows processes, security software, device drivers, or anti-cheat services.")
        row = tk.Frame(p, bg="#111720"); row.pack(fill="x", padx=25, pady=(0, 14))
        ttk.Button(row, text="Refresh running apps", command=self.refresh_processes).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Open Process Cleanup", style="Secondary.TButton", command=lambda: self.nb.select(self.processes)).pack(side="left")
        self.summary = tk.Label(p, text="Checking running apps…", bg="#0b0e13", fg="#a8f05a", font=("Segoe UI", 12, "bold"))
        self.summary.pack(anchor="w", padx=12, pady=12)
        self._panel(p, "Important", "This app closes selected user applications, not Windows services. Some apps may reopen themselves or be needed by your game. Close launchers only when you know your game can run without them. Never use this while recording, streaming, uploading, or in a call.")

    def _specs_tab(self):
        p = self.specs
        tk.Label(p, text="System Specs", bg="#0b0e13", fg="#edf3fa", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=12, pady=(15, 8))
        self.spec_text = tk.Text(p, bg="#111720", fg="#edf3fa", insertbackground="#edf3fa", relief="flat", font=("Consolas", 11), height=20, wrap="word")
        self.spec_text.pack(fill="both", expand=True, padx=12, pady=8)
        ttk.Button(p, text="Refresh specs", command=self.detect_specs).pack(anchor="w", padx=12, pady=8)

    def _process_tab(self):
        p = self.processes
        tk.Label(p, text="Optional App Cleanup", bg="#0b0e13", fg="#edf3fa", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=12, pady=(14, 4))
        tk.Label(p, text="Only checked, detected apps can be closed. Save work first. No administrator rights are needed for most of these.", bg="#0b0e13", fg="#91a0b4", font=("Segoe UI", 9), wraplength=950, justify="left").pack(anchor="w", padx=12, pady=(0, 10))
        toolbar = tk.Frame(p, bg="#0b0e13"); toolbar.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Button(toolbar, text="Refresh", command=self.refresh_processes).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="Select detected optional apps", style="Secondary.TButton", command=self.select_detected).pack(side="left", padx=(0, 7))
        ttk.Button(toolbar, text="Clear selection", style="Secondary.TButton", command=self.clear_selection).pack(side="left")
        cols = ("select", "app", "process", "status")
        self.tree = ttk.Treeview(p, columns=cols, show="headings", selectmode="none", height=13)
        self.tree.heading("select", text="SELECT")
        self.tree.heading("app", text="APPLICATION")
        self.tree.heading("process", text="PROCESS NAME")
        self.tree.heading("status", text="STATUS")
        self.tree.column("select", width=70, anchor="center")
        self.tree.column("app", width=220)
        self.tree.column("process", width=250)
        self.tree.column("status", width=160)
        self.tree.pack(fill="both", expand=True, padx=12, pady=4)
        self.tree.bind("<Button-1>", self._tree_click)
        self.tree.bind("<space>", self._toggle_focused)
        bottom = tk.Frame(p, bg="#0b0e13"); bottom.pack(fill="x", padx=12, pady=8)
        ttk.Button(bottom, text="Close selected apps", command=self.close_selected).pack(side="left", padx=(0, 10))
        tk.Label(bottom, text="Click a row to toggle its checkbox.", bg="#0b0e13", fg="#91a0b4").pack(side="left")
        self.process_status = tk.Label(p, text="", bg="#0b0e13", fg="#a8f05a", font=("Segoe UI", 9))
        self.process_status.pack(anchor="w", padx=12, pady=(0, 10))

    def _guide_tab(self):
        p = self.guide
        tk.Label(p, text="Safe Tweaks & Guidance", bg="#0b0e13", fg="#edf3fa", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=12, pady=(15, 8))
        tips = [
            ("Windows Game Mode", "Settings → Gaming → Game Mode. Turn it on and benchmark your games."),
            ("Startup apps", "Task Manager → Startup apps. Disable only apps you recognize and do not need at sign-in."),
            ("Graphics driver", "Use the official NVIDIA, AMD, Intel, or PC maker's update source."),
            ("Background recording", "Turn off background capture only if you do not use clips or recording."),
            ("Network latency", "Ethernet can be more consistent. Choose a nearby game server; DNS changes rarely improve game ping."),
            ("Avoid risky debloat scripts", "Do not blindly disable services, Defender, firewall, Windows Update, audio, network, GPU, or anti-cheat components."),
            ("Measure results", "Use the same game scene/settings and compare average FPS and 1% lows before and after one change."),
        ]
        for title, desc in tips:
            self._panel(p, title, desc)

    def detect_specs(self):
        info = []
        info.append(f"Operating system: {platform.platform()}")
        info.append(f"Windows version: {platform.version()}")
        info.append(f"Machine architecture: {platform.machine()}")
        info.append(f"Processor string: {platform.processor() or 'Not exposed by Windows Python'}")
        info.append(f"Logical CPU threads: {os.cpu_count() or 'Unknown'}")
        info.append(f"Python architecture: {platform.architecture()[0]}")
        info.append(f"Computer name: {os.environ.get('COMPUTERNAME', 'Unknown')}")
        info.append("")
        info.append("For exact GPU, RAM, storage and temperatures:")
        info.append("• Task Manager → Performance")
        info.append("• Start menu → run dxdiag")
        info.append("• Settings → System → About")
        info.append("")
        info.append("Note: exact hardware details vary by Windows/Python APIs. This starter app does not install drivers or request elevated access.")
        self.spec_text.config(state="normal")
        self.spec_text.delete("1.0", "end")
        self.spec_text.insert("1.0", "\n".join(info))
        self.spec_text.config(state="disabled")

    def refresh_processes(self):
        self.proc_rows = run_tasklist()
        running = {name.lower() for name, pid in self.proc_rows}
        if not hasattr(self, "tree"):
            self.summary.config(text=f"Detected {len(self.proc_rows)} running process entries. Review optional apps before closing anything.")
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.selected.clear()
        self.detected = {}
        for c in CANDIDATES:
            matches = [name for name in running if name == c["process"].lower()]
            detected = bool(matches)
            iid = c["process"]
            self.detected[iid] = detected
            status = "RUNNING" if detected else "Not detected"
            self.tree.insert("", "end", iid=iid, values=("☐", c["name"], c["process"], status), tags=("running" if detected else "idle",))
        self.tree.tag_configure("running", foreground="#a8f05a")
        self.tree.tag_configure("idle", foreground="#718096")
        count = sum(self.detected.values())
        self.summary.config(text=f"Detected {len(self.proc_rows)} process entries · {count} known optional apps currently running.")
        self.process_status.config(text=f"Last refreshed {datetime.now().strftime('%H:%M:%S')} · No processes changed.")
        log_action(f"REFRESH: {len(self.proc_rows)} process entries; {count} known optional apps running")

    def _tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._toggle_item(item)
            return "break"

    def _toggle_focused(self, event=None):
        item = self.tree.focus()
        if item: self._toggle_item(item)
        return "break"

    def _toggle_item(self, iid):
        if not getattr(self, "detected", {}).get(iid, False):
            self.process_status.config(text="That app is not currently detected; refresh the list.")
            return
        if iid in self.selected:
            self.selected.remove(iid)
        else:
            self.selected.add(iid)
        vals = list(self.tree.item(iid, "values"))
        vals[0] = "☑" if iid in self.selected else "☐"
        self.tree.item(iid, values=vals)
        self.process_status.config(text=f"{len(self.selected)} app(s) selected. No processes changed yet.")

    def select_detected(self):
        self.selected = {c["process"] for c in CANDIDATES if getattr(self, "detected", {}).get(c["process"], False)}
        for iid in self.tree.get_children():
            vals = list(self.tree.item(iid, "values"))
            vals[0] = "☑" if iid in self.selected else "☐"
            self.tree.item(iid, values=vals)
        self.process_status.config(text=f"{len(self.selected)} detected app(s) selected. Review the list carefully before closing.")

    def clear_selection(self):
        self.selected.clear()
        for iid in self.tree.get_children():
            vals = list(self.tree.item(iid, "values")); vals[0] = "☐"; self.tree.item(iid, values=vals)
        self.process_status.config(text="Selection cleared. No processes changed.")

    def close_selected(self):
        if not self.selected:
            messagebox.showinfo(APP_NAME, "Select one or more detected optional apps first.")
            return
        lookup = {c["process"]: c for c in CANDIDATES}
        chosen = [lookup[x] for x in self.selected if x in lookup]
        details = "\n".join(f"• {c['name']} ({c['process']})\n  {c['note']}" for c in chosen)
        ok = messagebox.askyesno("Confirm app cleanup", "Velocity will ask Windows to close the following selected applications by process name:\n\n" + details + "\n\nUnsaved work may be lost. Continue?")
        if not ok:
            return
        successes, failures = [], []
        for c in chosen:
            proc = c["process"]
            if proc.lower() in PROTECTED:
                failures.append(f"{c['name']}: protected process")
                continue
            # Exact process-name match, and only against our hard-coded allowlist.
            try:
                result = subprocess.run(["taskkill", "/IM", proc], capture_output=True, text=True, timeout=8, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                if result.returncode == 0:
                    successes.append(c["name"])
                    log_action(f"CLOSE REQUESTED: {c['name']} ({proc})")
                else:
                    msg = (result.stderr or result.stdout or "Windows did not close the process").strip().replace("\n", " ")
                    failures.append(f"{c['name']}: {msg[:150]}")
                    log_action(f"CLOSE FAILED: {c['name']} ({proc}) — {msg[:150]}")
            except Exception as e:
                failures.append(f"{c['name']}: {e}")
        report = ""
        if successes: report += "Close requested for:\n" + "\n".join("• " + x for x in successes) + "\n\n"
        if failures: report += "Not closed:\n" + "\n".join("• " + x for x in failures)
        messagebox.showinfo("Cleanup results", report or "No action was taken.")
        self.selected.clear()
        self.refresh_processes()

if __name__ == "__main__":
    if os.name != "nt":
        print("Velocity Windows Optimizer is designed for Windows 10/11.")
        input("Press Enter to exit...")
        sys.exit(1)
    App().mainloop()
