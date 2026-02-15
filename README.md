# Vorgify

A Python-based video editing tool with GUI, specialized in quickly concatenating and editing MP4 clips (e.g. from Google Veo).

[Deutsche Version](README.de.md)

## 🚀 Overview

The script `vorgify_app.py` is a fully functional `customtkinter` application.

**Current Features:**

* **Auto-Import:** Automatically reads all `.mp4` files in the folder.
* **Batch Processing:** Concatenate clips with crossfades.
* **Individual Control:** Speed & Reverse adjustable per clip.
* **Global Effects:** Global Speed, Fade In/Out, Crossfade Duration.
* **Video Quality:** Configurable presets (Ultrafast to Veryslow) and quality control (CRF or Bitrate) for both Preview and Full render modes.
* **GUI:** Custom Dark Menu Bar, Thumbnails (Smart-Crop), Drag & Drop replacement via sort buttons, Singleton modal windows.
* **Performance:** Multithreading Rendering with `moviepy` and optimized `proglog` integration for smooth progress updates.
* **Selection:** Checkboxes to select/deselect individual clips.
* **Time Calculation:** Real-time calculation of expected video length.

## 🛠 Tech Stack

* **Python 3.10+**
* **GUI:** `customtkinter`, `tkinter`, `Pillow` (PIL)
* **Video Engine:** `moviepy` (v1.0.3 or compatible), `proglog`
* **System:** Windows optimized (NVMe Support Logic)

## 🌍 Translation

Vorgify supports multiple languages through the `localization.py` file.

**Adding a New Language:**

1. Open `localization.py`.
2. Add your language code (e.g., `"fr"` for French) to **every** key in the `TRANSLATIONS` dictionary.
3. Update the `get_available_languages()` list and `get_language_name(code)` function.
4. Restart the application to see your new language in the settings.

See [docs/TRANSLATIONS.md](docs/TRANSLATIONS.md) for a detailed guide.

## 📋 To-Do / Known Issues

1. **Memory:** Thumbnails are cached; large folders might consume memory.
2. **Audio:** Very large number of clips might cause audio sync issues in rare cases (MoviePy limitation).

## 📦 Installation

```bash
pip install moviepy customtkinter pillow proglog
```

## 🎮 Usage

1. Start the script.
2. Select a folder with videos.
3. Select/deselect clips (checkboxes).
4. **Settings:**
    * **Language:** Switch between English and German.
    * **Video Quality:** Adjust encoding speed and quality (CRF/Bitrate) for Preview and Final renders.
5. Click on a clip to open details (Right): Speed, Reverse, Sorting.
6. Bottom: Adjust Global Speed and Fades.
7. "Start Rendering" -> Wait until the progress bar is full and shows "Done!".

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
