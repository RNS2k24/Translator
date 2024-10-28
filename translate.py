from googletrans import Translator
from requests.exceptions import RequestException
import time
import requests

# Add your Gemini API key
GEMINI_API_KEY = 'AIzaSyBYIGpV8yE5ZxeDa4GKK4ranZQai0T665Q'

LANGUAGE_CODES = {
    "Afrikaans": "af",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Armenian": "hy",
    "Azerbaijani": "az",
    "Basque": "eu",
    "Belarusian": "be",
    "Bengali": "bn",
    "Bosnian": "bs",
    "Bulgarian": "bg",
    "Catalan": "ca",
    "Cebuano": "ceb",
    "Chinese (Simplified)": "zh-cn",
    "Chinese (Traditional)": "zh-tw",
    "Corsican": "co",
    "Croatian": "hr",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Esperanto": "eo",
    "Estonian": "et",
    "Finnish": "fi",
    "French": "fr",
    "Frisian": "fy",
    "Galician": "gl",
    "Georgian": "ka",
    "German": "de",
    "Greek": "el",
    "Gujarati": "gu",
    "Haitian Creole": "ht",
    "Hausa": "ha",
    "Hawaiian": "haw",
    "Hebrew": "he",
    "Hindi": "hi",
    "Hmong": "hmn",
    "Hungarian": "hu",
    "Icelandic": "is",
    "Igbo": "ig",
    "Indonesian": "id",
    "Irish": "ga",
    "Italian": "it",
    "Japanese": "ja",
    "Javanese": "jv",
    "Kannada": "kn",
    "Kazakh": "kk",
    "Khmer": "km",
    "Kinyarwanda": "rw",
    "Korean": "ko",
    "Kurdish": "ku",
    "Kyrgyz": "ky",
    "Lao": "lo",
    "Latin": "la",
    "Latvian": "lv",
    "Lithuanian": "lt",
    "Luxembourgish": "lb",
    "Macedonian": "mk",
    "Malagasy": "mg",
    "Malay": "ms",
    "Malayalam": "ml",
    "Maltese": "mt",
    "Maori": "mi",
    "Marathi": "mr",
    "Mongolian": "mn",
    "Myanmar (Burmese)": "my",
    "Nepali": "ne",
    "Norwegian": "no",
    "Nyanja (Chichewa)": "ny",
    "Odia (Oriya)": "or",
    "Pashto": "ps",
    "Persian": "fa",
    "Polish": "pl",
    "Portuguese": "pt",
    "Punjabi": "pa",
    "Romanian": "ro",
    "Russian": "ru",
    "Samoan": "sm",
    "Scots Gaelic": "gd",
    "Serbian": "sr",
    "Sesotho": "st",
    "Shona": "sn",
    "Sindhi": "sd",
    "Sinhala (Sinhalese)": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Somali": "so",
    "Spanish": "es",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tagalog (Filipino)": "tl",
    "Tajik": "tg",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Thai": "th",
    "Turkish": "tr",
    "Turkmen": "tk",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uyghur": "ug",
    "Uzbek": "uz",
    "Vietnamese": "vi",
    "Welsh": "cy",
    "Xhosa": "xh",
    "Yiddish": "yi",
    "Yoruba": "yo",
    "Zulu": "zu"
}

def detect_language(text):
    translator = Translator()
    detection = translator.detect(text)
    return detection.lang, detection.confidence

def translate_text(text, target_language, retries=3):
    translator = Translator()
    max_length = 5000
    if len(text) > max_length:
        text_chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    else:
        text_chunks = [text]
    
    translated_text = []
    google_accuracy = 0

    for chunk in text_chunks:
        for attempt in range(retries):
            try:
                translation = translator.translate(chunk, dest=target_language)
                translated_text.append(translation.text)
                google_accuracy = 1  # Assume 100% accuracy for Google translation
                break
            except RequestException as req_err:
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    return {"google_translation": f"Error: {req_err}", "google_accuracy": 0}
            except Exception as err:
                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    return {"google_translation": f"Unexpected error: {err}", "google_accuracy": 0}
    
    # Gemini translation
    gemini_translated_text = gemini_translate(text, target_language)

    return {
        "google_translation": ' '.join(translated_text),
        "google_accuracy": google_accuracy,
        "gemini_translation": gemini_translated_text
    }

def gemini_translate(text, target_language):
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=GEMINI_API_KEY",
        json={"content": text, "language": target_language}  # Adjusted field names based on typical API structures
    )

    # Print the response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        return response.json().get('translated_text', 'No translation available.')
    else:
        return f"Error calling Gemini API: {response.status_code} - {response.text}"

def main():
    print("Available languages:")
    for language in LANGUAGE_CODES.keys():
        print(language)

if __name__ == "__main__":
    main()
