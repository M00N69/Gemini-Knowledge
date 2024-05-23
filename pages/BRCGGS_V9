import streamlit as st
import requests

# Supposition que la bibliothèque google.generativeai est fictive pour cet exemple
import google.generativeai as genai

# Fonction pour configurer le modèle avec les paramètres de génération
def configure_model(api_key, document_text):
    genai.configure(api_key=api_key)
    generation_config = {
        "temperature": 2,
        "top_p": 0.4,
        "top_k": 32,
        "max_output_tokens": 8192,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        system_instruction=document_text,
        safety_settings=safety_settings
    )
    return model

@st.cache(allow_output_mutation=True, ttl=86400)
def load_document_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # S'assurer que les mauvaises réponses sont gérées
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Échec de téléchargement du document: {str(e)}")
        return None

def main():
 # Configuration de la page
    st.set_page_config(
        page_title="VisiPilot App Helper",
        page_icon="⚔️​",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "This is a sample Streamlit app using Genai API."
        }
    )

    # CSS pour personnaliser la police et d'autres styles
    css = """
    <style>
        html, body, [class*="css"] {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 16px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    st.title("Question sur les matériaux en contact avec des denrées alimentaires")

    # URL du fichier texte sur GitHub
    url = "https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/BRC9_GUIde%20_interpretation.txt"
    document_text = load_document_from_github(url)

    if document_text:
        api_key = st.secrets["api_key"]
        model = configure_model(api_key, document_text)

        user_input = st.text_area("Posez votre question ici:", height=300)
        if st.button("Envoyer"):
            with st.spinner('Attendez pendant que nous générons la réponse...'):
                convo = model.start_chat(history=[{"role": "user", "parts": [user_input]}])
                response = convo.send_message(user_input)
                st.write(response.text)
    else:
        st.error("Erreur de chargement des documents. Impossible de continuer sans les données du document.")

if __name__ == "__main__":
    main()
