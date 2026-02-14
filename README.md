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
* **GUI:** Dark Mode, Thumbnails (Smart-Crop), Drag & Drop replacement via sort buttons.
* **Performance:** Multithreading Rendering with `moviepy` and `proglog` integration for progress bar.
* **Selection:** Checkboxes to select/deselect individual clips.
* **Time Calculation:** Real-time calculation of expected video length.

## 🛠 Tech Stack

* **Python 3.10+**
* **GUI:** `customtkinter`, `tkinter`, `Pillow` (PIL)
* **Video Engine:** `moviepy` (v1.0.3 or compatible), `proglog`
* **System:** Windows optimized (NVMe Support Logic)

## 📋 To-Do / Known Issues

1. **UI Glitches:** Sometimes elements disappear in the detail panel (right area) when switching wildly between clips. The `.pack()` logic needs robust checking.
2. **Audio:** Rendering audio with very many clips can hang (MoviePy `chunk` problem).
3. **Memory:** Thumbnails are cached, Garbage Collection must run cleanly (`self.current_image`).

## 📦 Installation

```bash
pip install moviepy customtkinter pillow proglog
```

## 🎮 Usage

1. Start the script.
2. Select a folder with videos.
3. Select/deselect clips (checkboxes).
4. Click on a clip to open details (Right): Speed, Reverse, Sorting.
5. Bottom: Adjust Global Speed and Fades.
6. "Start Rendering" -> Wait until the progress bar is full.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
