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
import webbrowser
import localization as loc

# Theme Colors (Logo Based)
COLOR_BG = "#191921"
COLOR_PANEL = "#25252d" 
COLOR_ACCENT = "#1f538d"
COLOR_ACCENT_HOVER = "#163d69"
COLOR_TEXT = "#e0e0e0"
COLOR_TEXT_GRAY = "gray"
COLOR_TEXT_HIGHLIGHT = "#4ea8de"
COLOR_BUTTON_GRAY = "#555"
COLOR_BUTTON_DARK = "#333"
COLOR_BUTTON_CLOSE = "#444"
COLOR_SUCCESS = "green"
COLOR_SUCCESS_HOVER = "darkgreen"
COLOR_ERROR = "red"
COLOR_ERROR_HOVER = "darkred"

# Fonts
FONT_MAIN = ("Roboto", 14)
FONT_HEADER = ("Roboto", 28, "bold")
FONT_SUBHEADER = ("Roboto", 18, "bold")
FONT_BOLD = ("Roboto", 16, "bold")
FONT_SMALL = ("Roboto", 12)

# Dimensions
DIM_BTN_H_NORMAL = 30
DIM_BTN_H_ACTION = 40
DIM_BTN_H_LARGE = 60

DIM_BTN_W_ICON = 30
DIM_BTN_W_SMALL = 60
DIM_BTN_W_NORMAL = 100
DIM_BTN_W_ACTION = 140

DIM_LIST_H = 250
DIM_DETAIL_H = 300

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") # We will override specific colors anyway




# --- HAUPT APP ---
class VorgifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(loc.get_text("app_title"))
        self.geometry("950x1050") # Resized to fit content
        self.configure(fg_color=COLOR_BG)

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
        # Logo & Title Header
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(pady=(15, 5))
        
        try:
            pil_img = Image.open("vorgify_logo.png")
            pil_img.thumbnail((50, 50), Image.Resampling.LANCZOS)
            self.header_logo = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            ctk.CTkLabel(self.logo_frame, text="", image=self.header_logo).pack(side="left", padx=10)
        except Exception:
            pass

        self.label = ctk.CTkLabel(self.logo_frame, text=loc.get_text("header_logo_text"), font=FONT_HEADER)
        self.label.pack(side="left")

        # 1. LISTE
        self.list_container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.list_container.pack(pady=5, padx=20, fill="x")
        
        self.header_frame = ctk.CTkFrame(self.list_container, fg_color=COLOR_BG)
        self.header_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(self.header_frame, text=loc.get_text("library_title"), font=FONT_MAIN).pack(side="left")
        self.btn_source = ctk.CTkButton(self.header_frame, text=loc.get_text("btn_select_folder"), width=DIM_BTN_W_NORMAL, height=DIM_BTN_H_NORMAL, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_SMALL, command=self.browse_source_folder)
        self.btn_source.pack(side="left", padx=10)
        self.btn_none = ctk.CTkButton(self.header_frame, text=loc.get_text("btn_none"), width=DIM_BTN_W_SMALL, height=DIM_BTN_H_NORMAL, fg_color=COLOR_BUTTON_GRAY, font=FONT_SMALL, command=self.select_none)
        self.btn_none.pack(side="right", padx=5)
        self.btn_all = ctk.CTkButton(self.header_frame, text=loc.get_text("btn_all"), width=DIM_BTN_W_SMALL, height=DIM_BTN_H_NORMAL, fg_color=COLOR_BUTTON_GRAY, font=FONT_SMALL, command=self.select_all)
        self.btn_all.pack(side="right", padx=5)
        
        self.btn_about = ctk.CTkButton(self.header_frame, text=loc.get_text("btn_info"), width=DIM_BTN_W_SMALL, height=DIM_BTN_H_NORMAL, fg_color=COLOR_BUTTON_CLOSE, font=FONT_SMALL, command=self.open_about)
        self.btn_about.pack(side="right", padx=5)
        
        # Source Path Label
        self.lbl_source_path = ctk.CTkLabel(self.header_frame, text=self.shorten_path(self.source_folder), text_color=COLOR_TEXT_GRAY, font=FONT_SMALL)
        self.lbl_source_path.pack(side="left", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(self.list_container, width=800, height=DIM_LIST_H) # Reduced height
        self.list_frame.pack(fill="x")
        self.scan_durations_and_refresh()

        # 2. DETAIL BEREICH (Split View)
        self.detail_container = ctk.CTkFrame(self, width=800, height=DIM_DETAIL_H, fg_color=COLOR_PANEL)
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
        self.btn_play_preview = ctk.CTkButton(self.preview_frame, text=loc.get_text("btn_play"), width=80, command=self.toggle_preview_playback, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, font=FONT_MAIN)
        # will be placed by rebuild_preview_label

        self.rebuild_preview_label(text=loc.get_text("lbl_no_clip"))

        # Rechts: Settings
        self.settings_frame = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        self.settings_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Container for all settings widgets
        self.settings_inner_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        
        self.lbl_title = ctk.CTkLabel(self.settings_inner_frame, text="", font=FONT_SUBHEADER, wraplength=350)
        self.lbl_title.pack(pady=(20, 5))

        # REMOVED: self.sort_frame (Up/Down buttons moved to list)

        self.lbl_speed = ctk.CTkLabel(self.settings_inner_frame, text=loc.get_text("lbl_clip_speed", 1.0), font=FONT_MAIN)
        self.lbl_speed.pack(pady=5)
        self.slider_speed = ctk.CTkSlider(self.settings_inner_frame, from_=0.2, to=3.0, command=self.update_clip_speed)
        self.slider_speed.pack(pady=5, fill="x", padx=30)
        self.chk_reverse = ctk.CTkCheckBox(self.settings_inner_frame, text=loc.get_text("chk_reverse"), font=FONT_MAIN, command=self.update_clip_rev)
        self.chk_reverse.pack(pady=10)
        self.btn_close = ctk.CTkButton(self.settings_inner_frame, text=loc.get_text("btn_deselect"), fg_color=COLOR_BUTTON_CLOSE, font=FONT_MAIN, command=self.deselect_video, height=DIM_BTN_H_NORMAL)
        self.btn_close.pack(pady=20, side="bottom")

        # 3. GLOBAL SETTINGS
        self.global_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.global_frame.pack(pady=10, padx=20, fill="x")

        # Estimated Duration (Moved to Top of Global)
        self.lbl_total_duration = ctk.CTkLabel(self.global_frame, text=loc.get_text("lbl_est_duration"), font=FONT_BOLD, text_color=COLOR_TEXT_HIGHLIGHT)
        self.lbl_total_duration.pack(pady=(5, 10))

        # Row 1: Global Speed
        self.row1 = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row1.pack(fill="x", padx=10, pady=5)
# ... (rest of row 1 logic in separate edits if needed, but I need to inject the duration label FIRST).
        ctk.CTkLabel(self.row1, text=loc.get_text("lbl_global_speed"), font=FONT_MAIN).pack(side="left")
        self.lbl_global_speed = ctk.CTkLabel(self.row1, text="1.00x", font=FONT_MAIN, text_color=COLOR_ACCENT)
        self.lbl_global_speed.pack(side="right")
        self.slider_global = ctk.CTkSlider(self.global_frame, from_=0.2, to=3.0, command=self.update_global_label)
        self.slider_global.set(1.0)
        self.slider_global.pack(fill="x", padx=20, pady=5)

        # Row 1.5: Fades
        self.row_fades = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row_fades.pack(fill="x", padx=10, pady=10)
        self.row_fades.grid_columnconfigure(0, weight=1); self.row_fades.grid_columnconfigure(1, weight=1); self.row_fades.grid_columnconfigure(2, weight=1)
        
        self.lbl_fade_in = ctk.CTkLabel(self.row_fades, text=loc.get_text("lbl_fade_in", 1.5), font=FONT_SMALL); self.lbl_fade_in.grid(row=0, column=0)
        self.slider_fade_in = ctk.CTkSlider(self.row_fades, from_=0, to=5.0, number_of_steps=50, command=self.upd_fade_in); self.slider_fade_in.set(1.5); self.slider_fade_in.grid(row=1, column=0, padx=5, sticky="ew")
        
        self.lbl_cross = ctk.CTkLabel(self.row_fades, text=loc.get_text("lbl_crossfade", 1.0), font=FONT_SMALL); self.lbl_cross.grid(row=0, column=1)
        self.slider_cross = ctk.CTkSlider(self.row_fades, from_=0, to=3.0, number_of_steps=30, command=self.upd_cross); self.slider_cross.set(1.0); self.slider_cross.grid(row=1, column=1, padx=5, sticky="ew")
        
        self.lbl_fade_out = ctk.CTkLabel(self.row_fades, text=loc.get_text("lbl_fade_out", 2.0), font=FONT_SMALL); self.lbl_fade_out.grid(row=0, column=2)
        self.slider_fade_out = ctk.CTkSlider(self.row_fades, from_=0, to=5.0, number_of_steps=50, command=self.upd_fade_out); self.slider_fade_out.set(2.0); self.slider_fade_out.grid(row=1, column=2, padx=5, sticky="ew")

        # Row 2: Audio & Mode
        self.row2 = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row2.pack(fill="x", pady=5)
        self.var_audio = ctk.BooleanVar(value=True)
        self.chk_audio = ctk.CTkCheckBox(self.row2, text=loc.get_text("chk_remove_audio"), font=FONT_MAIN, variable=self.var_audio)
        self.chk_audio.pack(side="left", padx=20)
        self.var_mode = ctk.StringVar(value="Preview")
        self.seg_mode = ctk.CTkSegmentedButton(self.row2, values=[loc.get_text("mode_preview"), loc.get_text("mode_full")], font=FONT_SMALL, variable=self.var_mode)
        self.seg_mode.pack(side="right", padx=20)

        # Row 3: Filename & Destination
        self.row3 = ctk.CTkFrame(self.global_frame, fg_color="transparent")
        self.row3.pack(fill="x", pady=10, padx=20)
        
        # Filename (Smaller)
        ctk.CTkLabel(self.row3, text=loc.get_text("lbl_filename"), font=FONT_MAIN).pack(side="left", padx=(0, 10))
        self.entry_filename = ctk.CTkEntry(self.row3, placeholder_text=loc.get_text("placeholder_filename"), font=FONT_MAIN, width=200) # Reduced width
        self.entry_filename.pack(side="left", padx=5)
        default_name = f"vorgify_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.entry_filename.insert(0, default_name)
        ctk.CTkLabel(self.row3, text=".mp4", text_color=COLOR_TEXT_GRAY, font=FONT_MAIN).pack(side="left", padx=(0, 20))
        
        # Destination Button (Expanded with path)
        self.btn_dest = ctk.CTkButton(self.row3, text=loc.get_text("btn_destination_fmt", self.shorten_path(self.destination_folder, 25)), font=FONT_MAIN, command=self.browse_destination)
        self.btn_dest.pack(side="right", fill="x", expand=True) # Fill remaining space

        # REMOVED: self.lbl_dest_path (merged into button)


        # --- ACTION AREA ---
        self.action_container = ctk.CTkFrame(self, fg_color="transparent")
        self.action_container.pack(pady=10, padx=40, fill="x")
        # Removed fixed height and propagate(False) to allow button to show fully

        # State 1: Start Button
        self.btn_render = ctk.CTkButton(self.action_container, text=loc.get_text("btn_start_render"), command=self.start_thread, 
                                        height=DIM_BTN_H_LARGE, font=FONT_SUBHEADER, fg_color=COLOR_SUCCESS, hover_color=COLOR_SUCCESS_HOVER)
        
        # State 2: Progress (Grid)
        self.progress_frame = ctk.CTkFrame(self.action_container, fg_color="transparent")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=0)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=50, corner_radius=8, progress_color=COLOR_ACCENT)
        self.progress_bar.set(0)
        self.btn_stop = ctk.CTkButton(self.progress_frame, text="⬛", width=50, height=50, 
                                     fg_color=COLOR_ERROR, hover_color=COLOR_ERROR_HOVER, command=self.request_cancel, font=("Arial", 24))
        self.lbl_prog_text = ctk.CTkLabel(self.progress_frame, text=loc.get_text("status_initializing"), font=FONT_BOLD, 
                                         text_color="white", fg_color="transparent")

        self.btn_render.pack(fill="both", expand=True)

        # REMOVED: self.lbl_total_duration (Moved up)
        # REMOVED: self.lbl_status ("Bereit." removed)

        self.calculate_total_time()

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
        self.lbl_prog_text.configure(text=loc.get_text("status_cancelling"))
        self.btn_stop.configure(state="disabled")

    def toggle_ui(self, rendering):
        if rendering:
            self.btn_render.pack_forget()
            self.progress_frame.pack(fill="both", expand=True)
            self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            self.btn_stop.grid(row=0, column=1)
            self.lbl_prog_text.place(relx=0.45, rely=0.5, anchor="center")
            self.progress_bar.set(0)
            self.lbl_prog_text.configure(text=loc.get_text("status_starting"))
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
            self.btn_play_preview.configure(text="▶ Play", fg_color=COLOR_ACCENT, command=self.toggle_preview_playback)
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
        self.btn_play_preview.configure(text="■ Stop", fg_color=COLOR_ERROR)
        
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
        self.btn_play_preview.configure(text="▶ Play", fg_color=COLOR_ACCENT)
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
        self.lbl_total_duration.configure(text=loc.get_text("lbl_est_duration_fmt", len(active), utils.format_seconds(total)))


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
        self.lbl_loading = ctk.CTkLabel(self.list_frame, text=loc.get_text("lbl_loading"), font=FONT_BOLD)
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
                btn_up = ctk.CTkButton(row, text="▲", width=DIM_BTN_W_ICON, height=DIM_BTN_H_NORMAL, fg_color=COLOR_BUTTON_DARK, command=lambda n=f: self.move_item_by_name(n, -1))
                btn_up.pack(side="left", padx=2)
            else:
                ctk.CTkLabel(row, text="", width=DIM_BTN_W_ICON+4).pack(side="left")

            if i < total_files - 1:
                btn_down = ctk.CTkButton(row, text="▼", width=DIM_BTN_W_ICON, height=DIM_BTN_H_NORMAL, fg_color=COLOR_BUTTON_DARK, command=lambda n=f: self.move_item_by_name(n, 1))
                btn_down.pack(side="left", padx=2)
            else:
                ctk.CTkLabel(row, text="", width=DIM_BTN_W_ICON+4).pack(side="left")

            display_text = f"{i+1}. {utils.shorten_filename(f)}"
            btn = ctk.CTkButton(row, text=display_text, anchor="w", fg_color="transparent", hover_color=COLOR_BUTTON_DARK, font=FONT_MAIN, command=lambda n=f: self.select_video(n))
            btn.pack(side="left", fill="x", expand=True, padx=5)
            
            self.list_buttons[f] = btn

        self.calculate_total_time()


    def refresh_file_list(self):
        try:
             # Filter out temp files and own output files to avoid cycles/errors
             self.video_files = sorted([
                 f for f in os.listdir(self.source_folder) 
                 if f.lower().endswith('.mp4') 
                 and not f.startswith(('vorgify_', 'veo_', 'TEMP_MPY'))
                 and 'TEMP_MPY' not in f
             ])
        except:
             self.video_files = []
        
        # Keep settings for existing files, init for new
        for f in self.video_files:
            if f not in self.clip_settings:
                self.clip_settings[f] = {"speed": 1.0, "reverse": False}
        
    def browse_source_folder(self):
        folder = filedialog.askdirectory(initialdir=self.source_folder, title=loc.get_text("dialog_source_title"))
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
        folder = filedialog.askdirectory(initialdir=self.destination_folder, title=loc.get_text("dialog_dest_title"))
        if folder:
             self.destination_folder = folder
             self.btn_dest.configure(text=loc.get_text("btn_destination_fmt", self.shorten_path(self.destination_folder, 25)))
             # self.lbl_status was removed, so we don't update it here properly? 
             # Maybe show a toast or just rely on the button text.



    def upd_fade_in(self, v): self.lbl_fade_in.configure(text=f"Fade In: {v:.1f}s")
    def upd_fade_out(self, v): self.lbl_fade_out.configure(text=f"Fade Out: {v:.1f}s")
    def upd_cross(self, v): self.lbl_cross.configure(text=f"Crossfade: {v:.1f}s"); self.calculate_total_time()
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

        for f, b in self.list_buttons.items(): b.configure(fg_color=COLOR_ACCENT if f==name else "transparent", border_width=1 if f==name else 0)
        self.selected_file = name; 
        
        # Check cache for thumbnail
        if name in self.thumbnail_cache:
            self.current_image = self.thumbnail_cache[name]
            self.rebuild_preview_label(image=self.current_image)
        else:
            self.rebuild_preview_label(text=loc.get_text("lbl_loading_preview"))
            self.preview_frame.update()
            try:
                full_path = os.path.join(self.source_folder, name)
                c = VideoFileClip(full_path); t = min(0.5, c.duration/2); f=c.get_frame(t); i=Image.fromarray(f); i.thumbnail((360,300), Image.Resampling.LANCZOS)
                self.current_image = ctk.CTkImage(light_image=i, dark_image=i, size=i.size)
                self.thumbnail_cache[name] = self.current_image  # Cache it!
                self.rebuild_preview_label(image=self.current_image); c.close()
            except: self.rebuild_preview_label(text=loc.get_text("lbl_no_preview"))

        
        # --- UI FIX: Pack SINGLE container instead of individual widgets ---
        self.settings_inner_frame.pack(fill="both", expand=True)

        self.lbl_title.configure(text=utils.shorten_filename(name, 30))
        # Update values
        self.slider_speed.set(self.clip_settings[name]["speed"])
        self.lbl_speed.configure(text=f"Clip-Speed: {self.clip_settings[name]['speed']:.2f}x")
        self.chk_reverse.select() if self.clip_settings[name]["reverse"] else self.chk_reverse.deselect()

    def deselect_video(self):
        self.stop_preview()
        self.selected_file = None; self.rebuild_preview_label(text=loc.get_text("lbl_no_clip"))
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
            
            # self.lbl_status was removed
            self.update_progress_safe(1.0, loc.get_text("status_done"))
        
        except Exception as e:
            msg = str(e)
            if "Abbruch" in msg: self.update_progress_safe(0, loc.get_text("status_cancelled"))
            else: self.update_progress_safe(0, loc.get_text("status_error", msg))
        finally:
            self.is_rendering = False
            self.after(2000, lambda: self.toggle_ui(False))

    def open_about(self):
        AboutWindow(self)

class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Über Vorgify")
        self.geometry("400x550")
        self.configure(fg_color=COLOR_BG)
        self.resizable(False, False)
        
        # Logo
        try:
            img = Image.open("vorgify_logo.png")
            img.thumbnail((250, 250), Image.Resampling.LANCZOS)
            self.logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            ctk.CTkLabel(self, text="", image=self.logo_img).pack(pady=20)
        except Exception as e:
            print(f"Logo error: {e}")
            ctk.CTkLabel(self, text="[Vorgify Logo]", font=FONT_HEADER, text_color=COLOR_TEXT).pack(pady=20)

        ctk.CTkLabel(self, text=loc.get_text("about_title"), font=FONT_HEADER, text_color=COLOR_TEXT).pack(pady=(0,5))
        ctk.CTkLabel(self, text=loc.get_text("about_subtitle"), font=FONT_MAIN, text_color=COLOR_TEXT_GRAY).pack(pady=0)
        
        ctk.CTkLabel(self, text=loc.get_text("about_community"), font=FONT_SUBHEADER, text_color=COLOR_TEXT).pack(pady=(30, 5))
        
        link = ctk.CTkLabel(self, text="forum.dice-dragons.de", font=("Roboto", 14, "underline"), text_color=COLOR_TEXT_HIGHLIGHT, cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open("https://forum.dice-dragons.de"))
        
        ctk.CTkButton(self, text=loc.get_text("btn_close"), width=DIM_BTN_W_ACTION, height=DIM_BTN_H_ACTION, fg_color=COLOR_BUTTON_DARK, font=FONT_MAIN, command=self.destroy).pack(side="bottom", pady=20)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        self.focus_force()            

if __name__ == "__main__":
    app = VorgifyApp()
    app.mainloop()