import cv2
import os
import queue
import subprocess
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

W, H = 480, 640
BTN_BLUE   = ("#2563eb", "#1d4ed8")
BTN_HOVER  = ("#1d4ed8", "#1e40af")
BTN_GRAY   = ("#374151", "#1f2937")
BTN_GHOVER = ("#1f2937", "#111827")
BTN_RED    = ("#dc2626", "#b91c1c")
BTN_RHOVER = ("#b91c1c", "#991b1b")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Extractor")
        self.resizable(False, False)

        self._queue        = queue.Queue()
        self._thread       = None
        self._cancel_event = threading.Event()
        self._video_path   = ""
        self._folder_path  = ""
        self._total_frames = 0
        self._estimate_var = ctk.StringVar(value="")

        self._build()
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - W) // 2
        y = (self.winfo_screenheight() - H) // 2
        self.geometry(f"{W}x{H}+{x}+{y}")

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build(self):
        self._header()
        self._body()
        self._footer()

    def _header(self):
        hdr = ctk.CTkFrame(self, fg_color="#111827",
                           corner_radius=0, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="Video Extractor",
                     font=ctk.CTkFont(size=21, weight="bold"),
                     text_color="#f9fafb").pack(side="left", padx=24)

        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right", padx=24)
        ctk.CTkLabel(right, text="Nezamilab",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#60a5fa").pack(anchor="e")
        ctk.CTkLabel(right, text="Developed by Amir Rouhollahi, PhD",
                     font=ctk.CTkFont(size=9),
                     text_color="#9ca3af").pack(anchor="e")

    def _body(self):
        body = ctk.CTkFrame(self, fg_color="#f3f4f6", corner_radius=0)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        inner = ctk.CTkFrame(body, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        self._file_card(inner)
        self._folder_card(inner)
        self._interval_card(inner)
        self._action_area(inner)

    # ── Cards ──────────────────────────────────────────────────────────────────

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color="#6b7280",
                     anchor="w").pack(fill="x", pady=(0, 5))

    def _path_box(self, parent, var):
        box = ctk.CTkFrame(parent, fg_color="#f3f4f6",
                           corner_radius=8, height=38)
        box.pack(fill="x", pady=(0, 8))
        box.pack_propagate(False)
        ctk.CTkLabel(box, textvariable=var,
                     font=ctk.CTkFont(size=11),
                     text_color="#6b7280",
                     anchor="w").pack(fill="both", expand=True, padx=12)
        return box

    def _file_card(self, parent):
        self._section_label(parent, "VIDEO FILE")
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        self._video_var = ctk.StringVar(value="No file selected")
        self._video_box_lbl = ctk.CTkLabel(
            inner, textvariable=self._video_var,
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af", anchor="w")
        self._video_box_lbl.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(inner, text="Choose Video File",
                      command=self._pick_video,
                      fg_color=BTN_GRAY, hover_color=BTN_GHOVER,
                      height=38, corner_radius=8,
                      font=ctk.CTkFont(size=12, weight="bold")).pack(fill="x")

    def _folder_card(self, parent):
        self._section_label(parent, "OUTPUT FOLDER")
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        self._folder_var = ctk.StringVar(value="No folder selected")
        self._folder_box_lbl = ctk.CTkLabel(
            inner, textvariable=self._folder_var,
            font=ctk.CTkFont(size=11),
            text_color="#9ca3af", anchor="w")
        self._folder_box_lbl.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(inner, text="Choose Output Folder",
                      command=self._pick_folder,
                      fg_color=BTN_GRAY, hover_color=BTN_GHOVER,
                      height=38, corner_radius=8,
                      font=ctk.CTkFont(size=12, weight="bold")).pack(fill="x")

    def _interval_card(self, parent):
        self._section_label(parent, "FRAME INTERVAL")
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x")

        self._interval_entry = ctk.CTkEntry(
            row, width=76, height=48,
            font=ctk.CTkFont(size=20, weight="bold"),
            justify="center")
        self._interval_entry.insert(0, "1")
        self._interval_entry.pack(side="left")
        self._interval_entry.bind("<KeyRelease>", lambda _: self._update_estimate())

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="left", padx=(14, 0))

        ctk.CTkLabel(right, text="Extract every Nth frame",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#111827", anchor="w").pack(anchor="w")
        ctk.CTkLabel(right,
                     text="1 = every frame   ·   2 = every other   ·   3 = every third",
                     font=ctk.CTkFont(size=10),
                     text_color="#6b7280", anchor="w").pack(anchor="w", pady=(3, 4))
        ctk.CTkLabel(right, textvariable=self._estimate_var,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#16a34a", anchor="w").pack(anchor="w")

    def _action_area(self, parent):
        self._extract_btn = ctk.CTkButton(
            parent, text="Extract Frames",
            command=self._start,
            fg_color=BTN_BLUE, hover_color=BTN_HOVER,
            height=48, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"))
        self._extract_btn.pack(fill="x", pady=(4, 0))

        self._open_btn = ctk.CTkButton(
            parent, text="Open Output Folder  →",
            command=self._open_folder,
            fg_color="transparent",
            text_color="#2563eb",
            hover_color="#eff6ff",
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"))

    def _footer(self):
        foot = ctk.CTkFrame(self, fg_color="#e5e7eb",
                            corner_radius=0, height=70)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)

        self._progress = ctk.CTkProgressBar(foot, height=8, corner_radius=4,
                                             progress_color="#2563eb",
                                             fg_color="#d1d5db")
        self._progress.set(0)
        self._progress.pack(fill="x", padx=18, pady=(14, 4))

        self._status_var = ctk.StringVar(
            value="Ready — choose a video and output folder to begin.")
        ctk.CTkLabel(foot, textvariable=self._status_var,
                     font=ctk.CTkFont(size=10),
                     text_color="#6b7280",
                     anchor="w").pack(fill="x", padx=18)

    # ── Actions ────────────────────────────────────────────────────────────────

    def _pick_video(self):
        p = filedialog.askopenfilename(
            title="Choose Video File",
            filetypes=[("Video files",
                        "*.mp4 *.mov *.avi *.mkv *.m4v *.wmv *.flv *.webm"),
                       ("All files", "*.*")])
        if p:
            self._video_path = p
            self._video_var.set(os.path.basename(p))
            self._video_box_lbl.configure(text_color="#111827")
            threading.Thread(target=self._load_info, args=(p,),
                             daemon=True).start()

    def _pick_folder(self):
        p = filedialog.askdirectory(title="Choose Output Folder")
        if p:
            self._folder_path = p
            self._folder_var.set(p)
            self._folder_box_lbl.configure(text_color="#111827")

    def _load_info(self, path):
        cap = cv2.VideoCapture(path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        self._total_frames = max(total, 0)
        self.after(0, self._update_estimate)

    def _update_estimate(self):
        if not self._total_frames:
            self._estimate_var.set("")
            return
        try:
            n = max(int(self._interval_entry.get()), 1)
        except ValueError:
            n = 1
        est = (self._total_frames + n - 1) // n
        self._estimate_var.set(
            f"≈ {est:,} frames will be saved  ({self._total_frames:,} total)")

    def _open_folder(self):
        if self._folder_path and os.path.isdir(self._folder_path):
            subprocess.run(["open", self._folder_path])

    def _start(self):
        errors = []
        if not self._video_path or not os.path.isfile(self._video_path):
            errors.append("• Choose a video file")
        if not self._folder_path or not os.path.isdir(self._folder_path):
            errors.append("• Choose an output folder")
        if errors:
            messagebox.showerror("Missing Information",
                                 "Please complete:\n\n" + "\n".join(errors))
            return

        try:
            interval = max(int(self._interval_entry.get()), 1)
        except ValueError:
            interval = 1

        self._open_btn.pack_forget()
        self._extract_btn.configure(text="Cancel",
                                     fg_color=BTN_RED,
                                     hover_color=BTN_RHOVER,
                                     command=self._cancel)
        self._cancel_event.clear()
        self._progress.set(0)
        self._status_var.set("Starting…")

        self._thread = threading.Thread(
            target=self._run,
            args=(self._video_path, self._folder_path, interval),
            daemon=True)
        self._thread.start()
        self.after(50, self._poll)

    def _cancel(self):
        self._cancel_event.set()
        self._extract_btn.configure(state="disabled", text="Cancelling…")

    def _restore(self):
        self._extract_btn.configure(text="Extract Frames",
                                     fg_color=BTN_BLUE,
                                     hover_color=BTN_HOVER,
                                     state="normal",
                                     command=self._start)

    # ── Extraction thread ──────────────────────────────────────────────────────

    def _run(self, video_path, output_dir, interval):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self._queue.put(("error",
                "Could not open the video file. It may be corrupted or unsupported."))
            return

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            total = None

        idx = saved = 0
        try:
            while cap.isOpened():
                if self._cancel_event.is_set():
                    self._queue.put(("cancelled", saved))
                    return
                ret, frame = cap.read()
                if not ret:
                    break
                if idx % interval == 0:
                    ok = cv2.imwrite(
                        os.path.join(output_dir, f"frame_{saved:05d}.jpg"), frame)
                    if not ok:
                        self._queue.put(("error",
                            "Failed to write a frame — disk may be full or folder is read-only."))
                        return
                    saved += 1
                idx += 1
                pct = (idx / total) if total else 0
                self._queue.put(("progress", pct, idx, total, saved))
        except Exception as exc:
            self._queue.put(("error", str(exc)))
            return
        finally:
            cap.release()

        self._queue.put(("done", saved))

    def _poll(self):
        try:
            while True:
                msg = self._queue.get_nowait()
                k = msg[0]

                if k == "progress":
                    _, pct, idx, total, saved = msg
                    self._progress.set(pct)
                    t = f"{total:,}" if total else "?"
                    self._status_var.set(
                        f"Frame {idx:,} / {t}   ·   {saved:,} saved")

                elif k == "done":
                    saved = msg[1]
                    self._progress.set(1)
                    self._status_var.set(f"Done — {saved:,} frames extracted.")
                    self._restore()
                    self._open_btn.pack(fill="x", pady=(8, 0))
                    return

                elif k == "cancelled":
                    saved = msg[1]
                    self._progress.set(0)
                    self._status_var.set(
                        f"Cancelled — {saved:,} frames saved.")
                    self._restore()
                    return

                elif k == "error":
                    self._progress.set(0)
                    self._status_var.set(f"Error: {msg[1]}")
                    self._restore()
                    messagebox.showerror("Error", msg[1])
                    return

        except queue.Empty:
            pass

        if self._thread and self._thread.is_alive():
            self.after(50, self._poll)


if __name__ == "__main__":
    app = App()
    app.mainloop()
