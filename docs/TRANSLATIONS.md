# How to Translate Vorgify

Vorgify supports multiple languages through the `localization.py` file.

## Adding a New Language

1. Open `localization.py`.
2. Find the `TRANSLATIONS` dictionary.
3. Add your language code (e.g., `"fr"` for French) to **every** key in the dictionary.

### Example

```python
    "app_title": {
        "en": "Vorgify - Complete Edition",
        "de": "Vorgify - Complete Edition",
        "fr": "Vorgify - Édition Complète"  # <--- New Language
    },
```

## Registering the Language

1. Open `localization.py`.
2. Update `get_available_languages()`:

```python
def get_available_languages():
    return ["en", "de", "fr"] # Add your code here
```

1. Update `get_language_name(code)` if you want a nice display name:

```python
def get_language_name(code):
    names = {
        "en": "English",
        "de": "Deutsch",
        "fr": "Français"
    }
    return names.get(code, code.upper())
```

## Testing

Restart the application. Your new language should appear in the language selector at the top right.
