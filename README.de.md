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
* **Videoqualität:** Konfigurierbare Presets (Ultrafast bis Veryslow) und Qualitätskontrolle (CRF oder Bitrate) für Vorschau- und Final-Render-Modus.
* **GUI:** Benutzerdefinierte dunkle Menüleiste, Vorschaubilder (Smart-Crop), Drag&Drop-Ersatz durch Sortier-Buttons, Singleton-Fenster.
* **Performance:** Multithreading Rendering mit `moviepy` und optimierter `proglog` Integration für flüssige Fortschrittsanzeige.
* **Selection:** Checkboxen zum An-/Abwählen einzelner Clips.
* **Time Calculation:** Echtzeit-Berechnung der voraussichtlichen Videolänge.

## 🛠 Tech Stack

* **Python 3.10+**
* **GUI:** `customtkinter`, `tkinter`, `Pillow` (PIL)
* **Video Engine:** `moviepy` (v1.0.3 oder kompatibel), `proglog`
* **System:** Windows optimiert (NVMe Support Logik)

## 🌍 Übersetzung

Vorgify unterstützt mehrere Sprachen durch die Datei `localization.py`.

**Neue Sprache hinzufügen:**

1. Öffne `localization.py`.
2. Füge deinen Sprachcode (z.B. `"fr"` für Französisch) zu **jedem** Schlüssel im `TRANSLATIONS`-Dictionary hinzu.
3. Aktualisiere die `get_available_languages()`-Liste und die `get_language_name(code)`-Funktion.
4. Starte die Anwendung neu, um deine neue Sprache in den Einstellungen zu sehen.

Siehe [docs/TRANSLATIONS.md](docs/TRANSLATIONS.md) für eine detaillierte Anleitung (Englisch).

## 📋 To-Do / Bekannte Issues

1. **Memory:** Vorschaubilder werden gecacht; große Ordner können Arbeitsspeicher beanspruchen.
2. **Audio:** Das Rendern von Audio bei sehr vielen Clips kann in seltenen Fällen Probleme machen (MoviePy Limitierung).

## 📦 Installation

```bash
pip install moviepy customtkinter pillow proglog
```

## 🎮 Bedienung

1. Skript starten.
2. Order mit Videos auswählen
3. Clips auswählen/abwählen (Checkboxen).
4. **Einstellungen:**
    * **Sprache:** Wechsel zwischen Englisch und Deutsch.
    * **Videoqualität:** Anpassung von Encoding-Geschwindigkeit und Qualität (CRF/Bitrate) für Vorschau und finalen Render.
5. Klick auf Clip öffnet Details (Rechts): Speed, Reverse, Sortierung.
6. Unten: Global Speed und Fades einstellen.
7. "Start Rendering" -> Warten bis der Progress-Balken voll ist und "Done!" anzeigt.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die [LICENSE](LICENSE) Datei für Details.
