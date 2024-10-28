import streamlit as st
from utils.extract_text import extract_text
from utils.translate import translate_text, LANGUAGE_CODES
from utils.languagesfull import LANGUAGE_FULL
from utils.HaveLang import Language_having
import io
import time
from langdetect import detect, DetectorFactory

# Set the seed for the language detector to make results consistent
DetectorFactory.seed = 0

st.set_page_config(
    page_title="Language Translator",
    page_icon="🌐",
    layout="wide"
)

CONTINENT_COUNTRY_LANGUAGES = Language_having

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("assets/styles.css")

def display_header():
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1 class='header'>🌐 Language Translator</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

display_header()
st.write("Translate content from images, PDFs, DOCX, PPTX, and TXT files into your desired language.")

st.sidebar.header("Settings")

continent = st.sidebar.selectbox("Select Continent", list(CONTINENT_COUNTRY_LANGUAGES.keys()))
countries = list(CONTINENT_COUNTRY_LANGUAGES[continent].keys())
country = st.sidebar.selectbox("Select Country", countries)
target_languages = CONTINENT_COUNTRY_LANGUAGES[continent][country]
target_language = st.sidebar.selectbox("Select Target Language", target_languages)

st.sidebar.markdown("Developed by Student.")

user_input = st.text_area("Input Text", height=150)

if st.button("Translate Input"):
    if user_input.strip():
        with st.spinner("Translating user input text..."):
            @st.cache_data
            def cached_translate(text, target_lang):
                try:
                    result = translate_text(text, LANGUAGE_CODES[target_lang])
                    return result["google_translation"], result["google_accuracy"]
                except Exception as e:
                    st.error(f"Translation failed: {e}")
                    return None, 0.0

            start_time = time.time()
            translated_text, accuracy = cached_translate(user_input, target_language)
            elapsed_time = time.time() - start_time
            
        if translated_text:
            st.success("✅ Translation Complete!")
            st.subheader("User Input")
            st.write(user_input)

            st.subheader("Translated Text")
            formatted_translated_text = f"****  \n{translated_text}"
            st.markdown(formatted_translated_text, unsafe_allow_html=True)

            st.subheader("Translation Accuracy")
            st.write(f"Confidence: {accuracy * 100:.1f}%")

            formatted_for_download = (
                f"**Translated Text**\n\n"
                f"    {translated_text.replace('\n', '\n\n    ')}\n"
            )
            st.download_button(
                label="Download Translated Text (.txt)",
                data=formatted_for_download,
                file_name='translated_text.txt',
                mime='text/plain',
            )
        else:
            st.warning("⚠️ Translation was not successful. Please try again.")
    else:
        st.warning("⚠️ Please input valid text to translate.")

uploaded_file = st.file_uploader("Upload a file", type=["png", "jpg", "jpeg", "pdf", "docx", "pptx", "txt"])

if st.button("Translate File"):
    if uploaded_file:
        with st.spinner("Extracting text from the file..."):
            extracted_text = extract_text(uploaded_file)

        if extracted_text and extracted_text != "Unsupported file type.":
            with st.spinner("Translating text..."):
                @st.cache_data
                def cached_translate(text, target_lang):
                    try:
                        result = translate_text(text, LANGUAGE_CODES[target_lang])
                        return result["google_translation"], result["google_accuracy"]
                    except Exception as e:
                        st.error(f"Translation failed: {e}")
                        return None, 0.0

                start_time = time.time()
                translated_text, accuracy = cached_translate(extracted_text, target_language)
                elapsed_time = time.time() - start_time
                
            if translated_text:
                st.success("✅ Translation Complete!")
                st.subheader("Extracted Text from File")
                formatted_extracted_text = f"**Extracted Text**\n\n    {extracted_text.replace('\n', '\n\n    ')}\n"
                st.markdown(formatted_extracted_text, unsafe_allow_html=True)

                st.subheader("Translated Text")
                formatted_translated_text = f"**Translated Text**\n\n    {translated_text.replace('\n', '\n\n    ')}\n"
                st.markdown(formatted_translated_text, unsafe_allow_html=True)

                st.subheader("Translation Accuracy")
                st.write(f"Confidence: {accuracy * 100:.1f}%")

                buffer = io.BytesIO(uploaded_file.read())
                extracted_text = extract_text(buffer)

                # Detect the language of the extracted text
                detected_language_code = detect(extracted_text)

                # Convert the language code to full form
                detected_languages = LANGUAGE_FULL

                detected_language = detected_languages.get(detected_language_code, detected_language_code)

                # Display the detected language and the translation
                st.subheader("Detected Language:")
                st.write(detected_language)

                formatted_for_download = (
                    f"**Translated Text**\n\n"
                    f"    {translated_text.replace('\n', '\n\n    ')}\n"
                )
                st.download_button(
                    label="Download Translated Text (.txt)",
                    data=formatted_for_download,
                    file_name='translated_text.txt',
                    mime='text/plain',
                )
            else:
                st.warning("⚠️ Translation was not successful. Please try again.")
        else:
            st.error("❌ No text found or unsupported file type.")
    else:
        st.warning("⚠️ Please upload a file to translate.")
