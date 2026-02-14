# Vorgify

Ein Python-basiertes Video-Editing-Tool mit GUI, spezialisiert auf das schnelle Zusammenfügen und Bearbeiten von MP4-Clips (z.B. von Google Veo).

[English Version](README.md)

## 🚀 Status Quo

Das Skript `vorgify_app.py` ist eine voll funktionsfähige `customtkinter` Anwendung.

**Aktuelle Features:**

* **Auto-Import:** Liest automatisch alle `.mp4` Dateien im Ordner.
* **Batch-Verarbeitung:** Zusammenfügen (Concatenate) mit Crossfades.
* **Individuelle Kontrolle:** Speed & Reverse pro Clip einstellbar.
* **Globale Effekte:** Global Speed, Fade In/Out, Überblenddauer.
* **GUI:** Dark Mode, Vorschaubilder (Smart-Crop), Drag&Drop-Ersatz durch Sortier-Buttons.
* **Performance:** Multithreading Rendering mit `moviepy` und `proglog` Integration für Progress-Bar.
* **Selection:** Checkboxen zum An-/Abwählen einzelner Clips.
* **Time Calculation:** Echtzeit-Berechnung der voraussichtlichen Videolänge.

## 🛠 Tech Stack

* **Python 3.10+**
* **GUI:** `customtkinter`, `tkinter`, `Pillow` (PIL)
* **Video Engine:** `moviepy` (v1.0.3 oder kompatibel), `proglog`
* **System:** Windows optimiert (NVMe Support Logik)

## 📋 To-Do / Bekannte Issues

1. **UI Glitches:** Manchmal verschwinden Elemente im Detail-Panel (rechter Bereich), wenn man wild zwischen Clips wechselt. Die `.pack()` Logik muss robust geprüft werden.
2. **Audio:** Das Rendern von Audio bei sehr vielen Clips kann hängen (MoviePy `chunk` Problem).
3. **Memory:** Vorschaubilder werden gecacht, Garbage Collection muss sauber laufen (`self.current_image`).

## 📦 Installation

```bash
pip install moviepy customtkinter pillow proglog
```

## 🎮 Bedienung

1. Skript starten.
2. Order mit Videos auswählen
3. Clips auswählen/abwählen (Checkboxen).
4. Klick auf Clip öffnet Details (Rechts): Speed, Reverse, Sortierung.
5. Unten: Global Speed und Fades einstellen.
6. "Start Rendering" -> Warten bis der Progress-Balken voll ist.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die [LICENSE](LICENSE) Datei für Details.
