"""
TRANSLATION SYSTEM DOCUMENTATION

The Abu Mukh Car Parts Management System uses a flexible translation system
that supports both code-based and file-based translations.

USING TRANSLATIONS IN YOUR CODE:

1. In widgets and components:

   # First, accept a translator in your __init__ method:
   def __init__(self, translator, ...):
       self.translator = translator

   # Then use it to translate UI elements:
   self.button.setText(self.translator.t('add_button'))

2. For adding new translations:

   A. First determine what namespace your translations belong to:
      - ui: For general UI elements like buttons, labels, etc.
      - navigation: For navigation elements
      - products: For product-related terms
      - settings: For settings-related terms
      - etc.

   B. Edit the appropriate JSON file in translations/data/
      Format:
      {
        "key": {
          "en": "English value",
          "he": "Hebrew value"
        }
      }

   C. Use the translation with its namespace:
      translator.t('namespace:key')

      For example:
      translator.t('products:add_product')

      If you don't specify a namespace, the system will search through
      all JSON files.

FEATURES:

1. Namespace support
   - Organize translations by feature/module
   - Access with 'namespace:key' syntax

2. Fallback to original translations
   - The system will first look in JSON files
   - If not found, it will fall back to the original TRANSLATIONS dict

3. Placeholder support
   - You can use Python's string formatting in translations
   - Example: translator.t('count_items', count=5)

4. Default language fallback
   - If a translation is missing in the current language,
     it falls back to English

EXTENDING THE SYSTEM:

1. To add support for a new language:
   - Add the new language code to all JSON files
   - Update the language dropdown in the settings page

2. To add new translation files:
   - Create a new JSON file in translations/data/
   - Follow the same format as existing files
   - The file's name (without extension) becomes the namespace

For more help, contact the system administrator.
"""