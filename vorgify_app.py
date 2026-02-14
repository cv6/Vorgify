import os
import shutil
import time
import customtkinter as ctk
from datetime import datetime
from moviepy import VideoFileClip
from threading import Thread
from PIL import Image, ImageTk
from tkinter import filedialog
import utils
import logger as plogger
import renderer

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")




# --- HAUPT APP ---
class VorgifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vorgify - Complete Edition")
        self.geometry("950x1150")

        # --- Data ---
        self.source_folder = os.getcwd()
        self.destination_folder = os.path.join(os.getcwd(), "Output") # Default output folder
        
        self.clip_settings = {}
        self.refresh_file_list()
        
        self.clip_durations = {}
        self.check_vars = {} 
        self.selected_file = None
        self.is_rendering = False
        self.cancel_requested = False
        self.list_buttons = {}
        self.current_image = None
        self.thumbnail_cache = {}
        
        # Preview Playback Data
        self.preview_clip = None
        self.is_playing_preview = False
        self.preview_start_time = 0

        # --- UI LAYOUT ---
        self.label = ctk.CTkLabel(self, text="VORGIFY", font=("Roboto", 28, "bold"))
        self.label.pack(pady=15)

        # 1. LISTE
        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(pady=5, padx=20, fill="x")
        
        self.header_frame = ctk.CTkFrame(self.list_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(self.header_frame, text="Clip Library", font=("Roboto", 14, "bold")).pack(side="left")
        self.btn_source = ctk.CTkButton(self.header_frame, text="📁 Ordner wählen", width=100, height=24, fg_color="#1f538d", command=self.browse_source_folder)
        self.btn_source.pack(side="left", padx=10)
        self.btn_none = ctk.CTkButton(self.header_frame, text="☐ Keine", width=60, height=24, fg_color="#555", command=self.select_none)
        self.btn_none.pack(side="right", padx=5)
        self.btn_all = ctk.CTkButton(self.header_frame, text="☑ Alle", width=60, height=24, fg_color="#555", command=self.select_all)
        self.btn_all.pack(side="right", padx=5)
        
        # Source Path Label
        self.lbl_source_path = ctk.CTkLabel(self.header_frame, text=self.shorten_path(self.source_folder), text_color="gray", font=("Arial", 10))
        self.lbl_source_path.pack(side="left", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(self.list_container, width=800, height=350) # Increased height
        self.list_frame.pack(fill="x")
        self.scan_durations_and_refresh()

        # 2. DETAIL BEREICH (Split View)
        self.detail_container = ctk.CTkFrame(self, width=800, height=350, fg_color="#212121")
        self.detail_container.pack(pady=10, padx=20)
        self.detail_container.pack_propagate(False) 
        self.detail_container.grid_propagate(False)
        self.detail_container.grid_columnconfigure(0, weight=1, uniform="group1")
        self.detail_container.grid_columnconfigure(1, weight=1, uniform="group1")
        self.detail_container.grid_rowconfigure(0, weight=1)

        # Links: Vorschau
        self.preview_frame = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        self.preview_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add Play Button Overlay (Initially hidden or part of rebuild)
        self.btn_play_preview = ctk.CTkButton(self.preview_frame, text="▶ Play", width=80, command=self.toggle_preview_playback, fg_color="#1f538d")
        # will be placed by rebuild_preview_label

        self.rebuild_preview_label(text="Kein Clip ausgewählt")

        # Rechts: Settings
        self.settings_frame = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        self.settings_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Container for all settings widgets
        self.settings_inner_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        
        self.lbl_title = ctk.CTkLabel(self.settings_inner_frame, text="", font=("Roboto", 18, "bold"), wraplength=350)
        self.lbl_title.pack(pady=(20, 5))

        # REMOVED: self.sort_frame (Up/Down buttons moved to list)

        self.lbl_speed = ctk.CTkLabel(self.settings_inner_frame, text="Clip-Speed: 1.0x")
        self.lbl_speed.pack(pady=5)
        self.slider_speed = ctk.CTkSlider(self.settings_inner_frame, from_=0.2, to=3.0, command=self.update_clip_speed)
        self.slider_speed.pack(pady=5, fill="x", padx=30)
        self.chk_reverse = ctk.CTkCheckBox(self.settings_inner_frame, text="Rückwärts (Reverse)", command=self.update_clip_rev)
        self.chk_reverse.pack(pady=10)
        self.btn_close = ctk.CTkButton(self.settings_inner_frame, text="Auswahl aufheben", fg_color="#444", command=self.deselect_video, height=30)
        self.btn_close.pack(pady=20, side="bottom")

        # 3. GLOBAL SETTINGS
        self.global_frame = ctk.CTkFrame(self)
        self.global_frame.pack(pady=10, padx=20, fill="x")

        # Row 1: Global Speed
        self.row1 = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.row1, text="Global Speed:").pack(side="left")
        self.lbl_global_speed = ctk.CTkLabel(self.row1, text="1.00x", font=("bold", 14), text_color="#1f538d")
        self.lbl_global_speed.pack(side="right")
        self.slider_global = ctk.CTkSlider(self.global_frame, from_=0.2, to=3.0, command=self.update_global_label)
        self.slider_global.set(1.0)
        self.slider_global.pack(fill="x", padx=20, pady=5)

        # Row 1.5: Fades
        self.row_fades = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row_fades.pack(fill="x", padx=10, pady=10)
        self.row_fades.grid_columnconfigure(0, weight=1); self.row_fades.grid_columnconfigure(1, weight=1); self.row_fades.grid_columnconfigure(2, weight=1)
        
        self.lbl_fade_in = ctk.CTkLabel(self.row_fades, text="Fade In: 1.5s"); self.lbl_fade_in.grid(row=0, column=0)
        self.slider_fade_in = ctk.CTkSlider(self.row_fades, from_=0, to=5.0, number_of_steps=50, command=self.upd_fade_in); self.slider_fade_in.set(1.5); self.slider_fade_in.grid(row=1, column=0, padx=5, sticky="ew")
        
        self.lbl_cross = ctk.CTkLabel(self.row_fades, text="Überblendung: 1.0s"); self.lbl_cross.grid(row=0, column=1)
        self.slider_cross = ctk.CTkSlider(self.row_fades, from_=0, to=3.0, number_of_steps=30, command=self.upd_cross); self.slider_cross.set(1.0); self.slider_cross.grid(row=1, column=1, padx=5, sticky="ew")
        
        self.lbl_fade_out = ctk.CTkLabel(self.row_fades, text="Fade Out: 2.0s"); self.lbl_fade_out.grid(row=0, column=2)
        self.slider_fade_out = ctk.CTkSlider(self.row_fades, from_=0, to=5.0, number_of_steps=50, command=self.upd_fade_out); self.slider_fade_out.set(2.0); self.slider_fade_out.grid(row=1, column=2, padx=5, sticky="ew")

        # Row 2: Audio & Mode
        self.row2 = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row2.pack(fill="x", pady=5)
        self.var_audio = ctk.BooleanVar(value=True)
        self.chk_audio = ctk.CTkCheckBox(self.row2, text="Ton entfernen", variable=self.var_audio)
        self.chk_audio.pack(side="left", padx=20)
        self.var_mode = ctk.StringVar(value="Preview")
        self.seg_mode = ctk.CTkSegmentedButton(self.row2, values=["Preview", "Full"], variable=self.var_mode)
        self.seg_mode.pack(side="right", padx=20)

        # Row 3: Dateiname
        self.row3 = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row3.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(self.row3, text="Dateiname:", font=("Roboto", 14)).pack(side="left", padx=(0, 10))
        self.entry_filename = ctk.CTkEntry(self.row3, placeholder_text="Dateiname...")
        self.entry_filename.pack(side="left", fill="x", expand=True)
        default_name = f"vorgify_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.entry_filename.insert(0, default_name)
        ctk.CTkLabel(self.row3, text=".mp4", text_color="gray").pack(side="left", padx=(5, 10))
        
        self.btn_dest = ctk.CTkButton(self.row3, text="📂 Ziel wählen", width=100, command=self.browse_destination)
        self.btn_dest.pack(side="right")
        
        # Destination Path Label (below row3 or inside) - let's put it below row3
        self.lbl_dest_path = ctk.CTkLabel(self.global_frame, text=f"Ziel: {self.shorten_path(self.destination_folder)}", text_color="gray", font=("Arial", 10))
        self.lbl_dest_path.pack(pady=(0, 5))


        # --- ACTION AREA ---
        self.action_container = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.action_container.pack(pady=10, padx=40, fill="x")
        self.action_container.pack_propagate(False)

        # State 1: Start Button
        self.btn_render = ctk.CTkButton(self.action_container, text="START RENDERING", command=self.start_thread, 
                                        height=50, font=("Roboto", 18, "bold"), fg_color="green", hover_color="darkgreen")
        
        # State 2: Progress (Grid)
        self.progress_frame = ctk.CTkFrame(self.action_container, fg_color="transparent")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=0)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=50, corner_radius=8)
        self.progress_bar.set(0)
        self.btn_stop = ctk.CTkButton(self.progress_frame, text="⬛", width=50, height=50, 
                                     fg_color="red", hover_color="darkred", command=self.request_cancel, font=("Arial", 24))
        self.lbl_prog_text = ctk.CTkLabel(self.progress_frame, text="Initialisiere...", font=("Roboto", 16, "bold"), 
                                         text_color="white", fg_color="transparent")

        self.btn_render.pack(fill="both", expand=True)

        self.lbl_total_duration = ctk.CTkLabel(self, text="Geschätzte Länge: Berechne...", font=("Roboto", 18, "bold"), text_color="#4ea8de")
        self.lbl_total_duration.pack(pady=5)
        
        self.lbl_status = ctk.CTkLabel(self, text="Bereit.", text_color="gray")
        self.lbl_status.pack(pady=5)

        self.calculate_total_time()

    # --- PROGRESS LOGIC ---
    def update_progress_safe(self, val, text_msg):
        self.after(0, lambda: self._update_ui(val, text_msg))

    def _update_ui(self, val, text_msg):
        self.progress_bar.set(val)
        self.lbl_prog_text.configure(text=text_msg)
        self.lbl_prog_text.lift()

    def request_cancel(self):
        self.cancel_requested = True
        self.lbl_prog_text.configure(text="Abbruch...")
        self.btn_stop.configure(state="disabled")

    def toggle_ui(self, rendering):
        if rendering:
            self.btn_render.pack_forget()
            self.progress_frame.pack(fill="both", expand=True)
            self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.btn_stop.grid(row=0, column=1)
            self.lbl_prog_text.place(relx=0.45, rely=0.5, anchor="center")
            self.progress_bar.set(0)
            self.lbl_prog_text.configure(text="Starte Engine...")
            self.btn_stop.configure(state="normal")
            self.cancel_requested = False
        else:
            self.progress_frame.pack_forget()
            self.btn_render.pack(fill="both", expand=True)

    # --- HELPERS ---
    def shorten_path(self, path, max_len=50):
        if len(path) <= max_len: return path
        return "..." + path[-(max_len-3):]

    # Moved to utils.py

    
    # --- PREVIEW LOGIC ---
    def rebuild_preview_label(self, image=None, text=""):
        # Stop preview if running
        if self.is_playing_preview:
            self.stop_preview()

        for widget in self.preview_frame.winfo_children():
            if widget != self.btn_play_preview:
                widget.destroy()

        if image:
            lbl = ctk.CTkLabel(self.preview_frame, text="", image=image)
        else:
            lbl = ctk.CTkLabel(self.preview_frame, text=text)

        lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Ensure Play button is on top if a clip is selected
        if self.selected_file:
            self.btn_play_preview.place(relx=0.5, rely=0.9, anchor="center")
            self.btn_play_preview.configure(text="▶ Play", fg_color="#1f538d", command=self.toggle_preview_playback)
            self.btn_play_preview.lift()
        else:
            self.btn_play_preview.place_forget()

        self.lbl_preview_image = lbl # Reference for updating frame

    def toggle_preview_playback(self):
        if self.is_playing_preview:
            self.stop_preview()
        else:
            self.start_preview()

    def start_preview(self):
        if not self.selected_file: return
        self.is_playing_preview = True
        self.btn_play_preview.configure(text="■ Stop", fg_color="red")
        
        try:
            full_path = os.path.join(self.source_folder, self.selected_file)
            self.preview_clip = VideoFileClip(full_path)

            # Apply speed effects for preview? Maybe too heavy. Raw preview for now.
            # s = self.clip_settings[self.selected_file]
            # if s["speed"] != 1.0 ... logic would be here
            
            self.preview_start_time = time.time()
            self.update_preview_loop()
        except Exception as e:
            print(f"Preview error: {e}")
            self.stop_preview()

    def stop_preview(self):
        self.is_playing_preview = False
        self.btn_play_preview.configure(text="▶ Play", fg_color="#1f538d")
        if self.preview_clip:
            try: self.preview_clip.close()
            except: pass
            self.preview_clip = None
        
        # Restore thumbnail
        if self.selected_file and self.selected_file in self.thumbnail_cache:
            self.lbl_preview_image.configure(image=self.thumbnail_cache[self.selected_file])

    def update_preview_loop(self):
        if not self.is_playing_preview or not self.preview_clip:
            return

        current_time = time.time() - self.preview_start_time
        
        if current_time > self.preview_clip.duration:
            self.stop_preview()
            return

        try:
            # Get frame at current time
            frame = self.preview_clip.get_frame(current_time)
            img = Image.fromarray(frame)
            img.thumbnail((360, 300), Image.Resampling.NEAREST) # Nearest for speed
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.lbl_preview_image.configure(image=ctk_img)
            
            # Schedule next update (approx 15fps = 66ms, 24fps = 41ms)
            self.after(50, self.update_preview_loop)
        except Exception as e:
            print(f"Frame error: {e}")
            self.stop_preview()

    # Moved to utils.py
    
    def calculate_total_time(self, *args):
        g_speed = self.slider_global.get(); cross = self.slider_cross.get(); total = 0
        active = [f for f in self.video_files if f in self.check_vars and self.check_vars[f].get()]
        for f in active:
            total += (self.clip_durations.get(f, 0) / (g_speed * self.clip_settings.get(f, {"speed": 1.0, "reverse": False})["speed"]))
        if len(active) > 1: total -= (len(active)-1)*cross
        self.estimated_duration = total # Store for Progress Bar
        self.lbl_total_duration.configure(text=f"Geschätzte Länge ({len(active)} Clips): {utils.format_seconds(total)}")


    def select_all(self):
        for v in self.check_vars.values(): v.set(True)
        self.calculate_total_time()
    def select_none(self):
        for v in self.check_vars.values(): v.set(False)
        self.calculate_total_time()
    
    def scan_durations_and_refresh(self):
        # Clear list first
        for w in self.list_frame.winfo_children(): w.destroy()
        self.list_buttons = {}
        
        if not self.video_files:
            return

        # Show loading indicator
        self.lbl_loading = ctk.CTkLabel(self.list_frame, text="Lade Videos...", font=("Roboto", 16))
        self.lbl_loading.pack(pady=20)
        
        # Disable buttons during load? 
        self.btn_source.configure(state="disabled")
        
        # Start Thread
        Thread(target=self._thread_scan_durations, daemon=True).start()

    def _thread_scan_durations(self):
        # 1. Scan durations in background
        for f in self.video_files:
             if f not in self.clip_durations:
                try: 
                    full_path = os.path.join(self.source_folder, f)
                    with VideoFileClip(full_path) as c: 
                        dur = c.duration
                except: 
                    dur = 0
                self.clip_durations[f] = dur
        
        # 2. Schedule UI build on main thread
        self.after(0, self._build_list_ui)

    def _build_list_ui(self):
        # Remove loading label
        if hasattr(self, 'lbl_loading'):
            self.lbl_loading.destroy()
            
        self.btn_source.configure(state="normal")
        
        total_files = len(self.video_files)
        
        for i, f in enumerate(self.video_files):
            if f not in self.check_vars: self.check_vars[f] = ctk.BooleanVar(value=True)
            
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Checkbox
            ctk.CTkCheckBox(row, text="", width=24, variable=self.check_vars[f], command=self.calculate_total_time).pack(side="left", padx=5)
            
            # Sort Buttons
            if i > 0:
                btn_up = ctk.CTkButton(row, text="▲", width=30, height=24, fg_color="#333", command=lambda n=f: self.move_item_by_name(n, -1))
                btn_up.pack(side="left", padx=2)
            else:
                ctk.CTkLabel(row, text="", width=34).pack(side="left")

            if i < total_files - 1:
                btn_down = ctk.CTkButton(row, text="▼", width=30, height=24, fg_color="#333", command=lambda n=f: self.move_item_by_name(n, 1))
                btn_down.pack(side="left", padx=2)
            else:
                ctk.CTkLabel(row, text="", width=34).pack(side="left")

            display_text = f"{i+1}. {utils.shorten_filename(f)}"
            btn = ctk.CTkButton(row, text=display_text, anchor="w", fg_color="transparent", hover_color="#3b3b3b", command=lambda n=f: self.select_video(n))
            btn.pack(side="left", fill="x", expand=True, padx=5)
            
            self.list_buttons[f] = btn

        self.calculate_total_time()


    def refresh_file_list(self):
        try:
             self.video_files = sorted([f for f in os.listdir(self.source_folder) if f.lower().endswith('.mp4')])
        except:
             self.video_files = []
        
        # Keep settings for existing files, init for new
        for f in self.video_files:
            if f not in self.clip_settings:
                self.clip_settings[f] = {"speed": 1.0, "reverse": False}
        
    def browse_source_folder(self):
        folder = filedialog.askdirectory(initialdir=self.source_folder, title="Ordner mit Videos wählen")
        if folder:
            self.source_folder = folder
            self.lbl_source_path.configure(text=self.shorten_path(self.source_folder))
            self.refresh_file_list()
            # Reset checks logic or keep? Let's reset for new folder
            self.check_vars = {} 
            self.clip_durations = {} 
            self.scan_durations_and_refresh()
            self.calculate_total_time()

    def browse_destination(self):
        folder = filedialog.askdirectory(initialdir=self.destination_folder, title="Zielordner wählen")
        if folder:
             self.destination_folder = folder
             self.lbl_dest_path.configure(text=f"Ziel: {self.shorten_path(self.destination_folder)}")
             self.lbl_status.configure(text=f"Zielordner: {utils.shorten_filename(folder, 40)}", text_color="#4ea8de")



    def upd_fade_in(self, v): self.lbl_fade_in.configure(text=f"Fade In: {v:.1f}s")
    def upd_fade_out(self, v): self.lbl_fade_out.configure(text=f"Fade Out: {v:.1f}s")
    def upd_cross(self, v): self.lbl_cross.configure(text=f"Überblendung: {v:.1f}s"); self.calculate_total_time()
    def update_clip_speed(self, v): 
        if self.selected_file: self.clip_settings[self.selected_file]["speed"]=round(v, 2); self.lbl_speed.configure(text=f"Clip-Speed: {v:.2f}x"); self.calculate_total_time()
    def update_clip_rev(self): 
        if self.selected_file: self.clip_settings[self.selected_file]["reverse"]=self.chk_reverse.get()
    def update_global_label(self, v): self.lbl_global_speed.configure(text=f"{v:.2f}x"); self.calculate_total_time()
    
    def move_item_by_name(self, name, d):
        if name not in self.video_files: return
        i = self.video_files.index(name)
        if 0 <= i+d < len(self.video_files):
            self.video_files[i], self.video_files[i+d] = self.video_files[i+d], self.video_files[i]
            self.scan_durations_and_refresh()
            # Reselect if it was selected
            if self.selected_file == name:
                self.select_video(name)

    def select_video(self, name):
        # Stop preview if changing video
        if self.is_playing_preview and self.selected_file != name:
            self.stop_preview()

        for f, b in self.list_buttons.items(): b.configure(fg_color="#1f538d" if f==name else "transparent", border_width=1 if f==name else 0)
        self.selected_file = name; 
        
        # Check cache for thumbnail
        if name in self.thumbnail_cache:
            self.current_image = self.thumbnail_cache[name]
            self.rebuild_preview_label(image=self.current_image)
        else:
            self.rebuild_preview_label(text="Lade...")
            self.preview_frame.update()
            try:
                full_path = os.path.join(self.source_folder, name)
                c = VideoFileClip(full_path); t = min(0.5, c.duration/2); f=c.get_frame(t); i=Image.fromarray(f); i.thumbnail((360,300), Image.Resampling.LANCZOS)
                self.current_image = ctk.CTkImage(light_image=i, dark_image=i, size=i.size)
                self.thumbnail_cache[name] = self.current_image  # Cache it!
                self.rebuild_preview_label(image=self.current_image); c.close()
            except: self.rebuild_preview_label(text="Keine Vorschau")

        
        # --- UI FIX: Pack SINGLE container instead of individual widgets ---
        self.settings_inner_frame.pack(fill="both", expand=True)

        self.lbl_title.configure(text=utils.shorten_filename(name, 30))
        # Update values
        self.slider_speed.set(self.clip_settings[name]["speed"])
        self.lbl_speed.configure(text=f"Clip-Speed: {self.clip_settings[name]['speed']:.2f}x")
        self.chk_reverse.select() if self.clip_settings[name]["reverse"] else self.chk_reverse.deselect()

    def deselect_video(self):
        self.stop_preview()
        self.selected_file = None; self.rebuild_preview_label(text="Kein Clip")
        for b in self.list_buttons.values(): b.configure(fg_color="transparent", border_width=0)
        
        # --- UI FIX: Unpack the container ---
        self.settings_inner_frame.pack_forget()

    def start_thread(self):
        if not any(self.check_vars[f].get() for f in self.video_files): return
        if not self.is_rendering: self.is_rendering=True; self.toggle_ui(True); Thread(target=self.render, daemon=True).start()

    def render(self):
        try:
            start = time.time()
            
            # Prepare Logger
            # We pass callbacks for update and cancel check
            est_dur = getattr(self, 'estimated_duration', 100)
            logger = plogger.MyBarLogger(
                update_callback=self.update_progress_safe,
                cancel_check_callback=lambda: self.cancel_requested,
                estimated_duration=est_dur
            )

            # Prepare Config
            config = {
                "source_folder": self.source_folder,
                "destination_folder": self.destination_folder,
                "output_filename": self.entry_filename.get().strip() or f"vorgify_{datetime.now().strftime('%H%M%S')}.mp4",
                "video_files": [f for f in self.video_files if self.check_vars[f].get()],
                "clip_settings": self.clip_settings,
                "global_speed": self.slider_global.get(),
                "fade_in": self.slider_fade_in.get(),
                "fade_out": self.slider_fade_out.get(),
                "crossfade": self.slider_cross.get(),
                "audio_enabled": self.var_audio.get(),
                "mode": self.var_mode.get(),
                "threads": 6
            }
            
            # Ensure filename ends with mp4
            if not config["output_filename"].lower().endswith(".mp4"):
                config["output_filename"] += ".mp4"

            # Call Renderer
            out_file = renderer.render_video(config, logger, lambda: self.cancel_requested)
            
            self.lbl_status.configure(text=f"Fertig! {os.path.basename(out_file)} ({time.time()-start:.1f}s)", text_color="green")
            self.update_progress_safe(1.0, "Fertig!")
        
        except Exception as e:
            msg = str(e)
            if "Abbruch" in msg: self.lbl_status.configure(text="Vorgang abgebrochen.", text_color="orange")
            else: self.lbl_status.configure(text=f"Fehler: {msg}", text_color="red")
        finally:
            self.is_rendering = False
            self.after(2000, lambda: self.toggle_ui(False))

if __name__ == "__main__":
    app = VorgifyApp()
    app.mainloop()