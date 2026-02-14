# localization.py

# Dictionary containing all user-facing text strings
# Structure: "KEY_NAME": {"en": "English Text", "de": "German Text"}

current_language = "en"

TRANSLATIONS = {
    "app_title": {
        "en": "Vorgify - Complete Edition",
        "de": "Vorgify - Complete Edition"
    },
    "header_logo_text": {
        "en": "VORGIFY",
        "de": "VORGIFY"
    },
    "library_title": {
        "en": "Clip Library",
        "de": "Clip-Bibliothek"
    },
    "btn_select_folder": {
        "en": "📁 Select Folder",
        "de": "📁 Ordner wählen"
    },
    "btn_none": {
        "en": "☐ None",
        "de": "☐ Keine"
    },
    "btn_all": {
        "en": "☑ All",
        "de": "☑ Alle"
    },
    "btn_info": {
        "en": "ⓘ Info",
        "de": "ⓘ Info"
    },
    "lbl_loading": {
        "en": "Loading Videos...",
        "de": "Lade Videos..."
    },
    # Playback / Preview
    "btn_play": {
        "en": "▶ Play",
        "de": "▶ Abspielen"
    },
    "btn_stop": {
        "en": "■ Stop",
        "de": "■ Stopp"
    },
    "lbl_no_clip": {
        "en": "No clip selected",
        "de": "Kein Clip ausgewählt"
    },
    "lbl_no_preview": {
        "en": "No preview",
        "de": "Keine Vorschau"
    },
    "lbl_loading_preview": {
        "en": "loading...",
        "de": "lade..."
    },
    # Settings (Right Panel)
    "lbl_clip_speed": {
        "en": "Clip Speed: {:.2f}x",
        "de": "Clip-Tempo: {:.2f}x"
    },
    "chk_reverse": {
        "en": "Reverse",
        "de": "Rückwärts"
    },
    "btn_deselect": {
        "en": "Deselect",
        "de": "Abwählen"
    },
    # Global Settings
    "lbl_est_duration": {
        "en": "Est. Duration: Calculating...",
        "de": "Gesch. Dauer: Berechne..."
    },
    "lbl_est_duration_fmt": {
        "en": "Est. Duration ({} Clips): {}",
        "de": "Gesch. Dauer ({} Clips): {}"
    },
    "lbl_global_speed": {
        "en": "Global Speed:",
        "de": "Globales Tempo:"
    },
    "lbl_fade_in": {
        "en": "Fade In: {:.1f}s",
        "de": "Einblenden: {:.1f}s"
    },
    "lbl_crossfade": {
        "en": "Crossfade: {:.1f}s",
        "de": "Überblenden: {:.1f}s"
    },
    "lbl_fade_out": {
        "en": "Fade Out: {:.1f}s",
        "de": "Ausblenden: {:.1f}s"
    },
    "chk_remove_audio": {
        "en": "Remove Audio",
        "de": "Audio entfernen"
    },
    "mode_preview": {
        "en": "Preview",
        "de": "Vorschau"
    },
    "mode_full": {
        "en": "Full",
        "de": "Voll"
    },
    # Filename & Destination
    "lbl_filename": {
        "en": "Filename:",
        "de": "Dateiname:"
    },
    "placeholder_filename": {
        "en": "Filename...",
        "de": "Dateiname..."
    },
    "btn_destination_fmt": {
        "en": "📂 Destination: {}",
        "de": "📂 Ziel: {}"
    },
    "dialog_dest_title": {
        "en": "Select destination folder",
        "de": "Zielordner auswählen"
    },
    "dialog_source_title": {
        "en": "Select source folder",
        "de": "Quellordner auswählen"
    },
    # Action Area
    "btn_start_render": {
        "en": "start rendering",
        "de": "renderung starten"
    },
    "status_initializing": {
        "en": "initializing...",
        "de": "initialisiere..."
    },
    "status_starting": {
        "en": "Starting Engine...",
        "de": "Starte Engine..."
    },
    "status_cancelling": {
        "en": "Cancelling...",
        "de": "Breche ab..."
    },
    "status_done": {
        "en": "Done!",
        "de": "Fertig!"
    },
    "status_cancelled": {
        "en": "Cancelled",
        "de": "Abgebrochen"
    },
    "status_error": {
        "en": "Error: {}",
        "de": "Fehler: {}"
    },
    # About Window
    "about_title": {
        "en": "About Vorgify",
        "de": "Über Vorgify"
    },
    "about_subtitle": {
        "en": "Video Editing Tool",
        "de": "Videobearbeitungstool"
    },
    "about_community": {
        "en": "Community:",
        "de": "Community:"
    },
    "btn_close": {
        "en": "Close",
        "de": "Schließen"
    }
}

def get_text(key, *args):
    """
    Retrieves the translation for the given key in the current language.
    If args are provided, formats the string.
    """
    lang_dict = TRANSLATIONS.get(key, {})
    text = lang_dict.get(current_language, lang_dict.get("en", f"MISSING_{key}"))
    
    if args:
        try:
            return text.format(*args)
        except Exception:
            return text # Return unformatted if error
    return text

def set_language(lang_code):
    global current_language
    if lang_code in ["en", "de"]:
        current_language = lang_code
