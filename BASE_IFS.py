import streamlit as st
import requests
import google.generativeai as genai
import hashlib # Utilisé dans un des exemples originaux, conservé au cas où.
import css_styles # Nous allons créer un fichier ou une section pour le CSS

# --- Configuration Initiale de l'Application ---
# doit être appelée en premier
st.set_page_config(
    page_title="VisiPilot App Helper",
    page_icon="⚔️",
    layout="wide", # Utilise tout l'espace disponible
    initial_sidebar_state="expanded", # Barre latérale ouverte par défaut
    menu_items={ # Masque les options de menu par défaut de Streamlit
        'Get Help': None,
        'Report a bug': None,
        'About': "Application d'aide à la conformité aux normes basée sur Gemini 1.5 Flash."
    }
)

# --- CSS pour améliorer le design ---
# Vous pouvez mettre ce CSS dans un fichier séparé (css_styles.py)
# ou le laisser ici. Pour la simplicité, je le mets directement.
css = """
<style>
    /* Police de caractères */
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
        color: #333; /* Couleur du texte */
    }

    /* Titres */
    h1, h2, h3, h4, h5, h6 {
        color: #1e3a8a; /* Couleur bleue foncée pour les titres */
    }

    /* Barre latérale */
    .css-1d3z3hf, .css-hxt7z { /* Selecteurs pour la barre latérale */
        background-color: #f0f2f6; /* Fond gris clair */
        color: #333;
    }

    /* Style du logo dans la barre latérale */
    .sidebar-logo-container {
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid #ccc; /* Ligne séparatrice */
    }
    .sidebar-logo {
        max-width: 80%; /* Ajuste la taille du logo */
        height: auto;
        border-radius: 10px; /* Coins arrondis */
    }

    /* Boutons */
    .stButton>button {
        background-color: #1e3a8a; /* Fond bleu */
        color: white; /* Texte blanc */
        border-radius: 5px; /* Coins arrondis */
        padding: 10px 20px; /* Espacement interne */
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease; /* Animation au survol */
    }
    .stButton>button:hover {
        background-color: #164e8a; /* Bleu légèrement plus foncé au survol */
    }

    /* Zones de texte */
    .stTextArea textarea {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
    }

    /* Spinner */
    .stSpinner > div > div {
        border-top-color: #1e3a8a; /* Couleur du spinner */
    }
    
    /* Expander "À propos" */
    .streamlit-expanderHeader {
        background-color: #e0e7ff; /* Fond bleu très clair */
        color: #1e3a8a; /* Texte bleu foncé */
        border-radius: 5px;
        padding: 10px;
        cursor: pointer;
    }
    .streamlit-expanderContent {
       background-color: #f9fafb; /* Fond blanc cassé */
       padding: 10px;
       border-left: 3px solid #1e3a8a; /* Ligne bleue sur le côté */
       border-bottom-left-radius: 5px;
       border-bottom-right-radius: 5px;
    }

    /* Messages d'information/erreur */
    .stAlert {
        border-radius: 5px;
    }
    .stAlert.error {
        background-color: #fee2e2; /* Fond rouge très clair */
        color: #991b1b; /* Texte rouge foncé */
        border-left-color: #991b1b; /* Ligne rouge */
    }
    .stAlert.info {
         background-color: #dbeafe; /* Fond bleu très clair */
        color: #1e40af; /* Texte bleu foncé */
        border-left-color: #1e40af; /* Ligne bleue */
    }

</style>
"""
st.markdown(css, unsafe_allow_html=True)


# --- Fonctions Utilitaires ---

# Fonction pour configurer le modèle Gemini
# Utilise gemini-1.5-flash-latest comme demandé (version stable du flash)
def configure_model(document_text):
    try:
        genai.configure(api_key=st.secrets["api_key"])
    except Exception as e:
        st.error(f"Erreur de configuration de l'API Gemini : {e}. Assurez-vous que 'api_key' est définie dans st.secrets.")
        return None

    # Paramètres de génération
    generation_config = {
        "temperature": 2, # Garde le paramètre de température élevé comme dans l'original
        "top_p": 0.4,
        "top_k": 32,
        "max_output_tokens": 8192,
    }

    # Paramètres de sécurité
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    try:
        # Création du modèle
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest", # Utilisation du modèle flash le plus récent
            generation_config=generation_config,
            system_instruction=document_text, # Le texte du document sert d'instruction système
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
         st.error(f"Erreur lors de l'initialisation du modèle Gemini : {e}. Vérifiez le nom du modèle ou les paramètres.")
         return None


# Fonction pour charger un document depuis GitHub avec mise en cache
@st.cache_data(ttl=86400, show_spinner="Chargement du document depuis GitHub...")
def load_document_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une erreur pour les mauvais codes de statut (4xx ou 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Échec du téléchargement du document depuis GitHub ({url}): {str(e)}")
        return None

# Fonction pour charger des documents depuis Google Drive avec mise en cache
@st.cache_data(ttl=86400, show_spinner="Chargement des documents depuis Google Drive...")
def load_documents_from_drive(file_ids):
    documents_text = []
    loaded_file_ids = [] # Stocke les IDs des fichiers qui ont été chargés avec succès
    for file_id in file_ids:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            documents_text.append(response.text)
            loaded_file_ids.append(file_id)
        except requests.exceptions.HTTPError as e:
            st.warning(f"Avertissement : Échec du téléchargement du document Google Drive avec l'ID {file_id}. Il ne sera pas inclus. Erreur : {str(e)}")
        except requests.exceptions.RequestException as e:
             st.warning(f"Avertissement : Erreur de requête pour l'ID {file_id}. Il ne sera pas inclus. Erreur : {str(e)}")

    if not documents_text:
        st.error("Aucun document n'a pu être chargé depuis Google Drive avec les IDs fournis.")
        return None, [] # Retourne None pour le texte si aucun document n'est chargé
        
    return "\n\n".join(documents_text), loaded_file_ids


# --- Fonctions pour chaque Page (Spécialité) ---

def brcgs_page():
    st.title("❓ Questions sur la norme BRCGS V9")

    # URL du fichier texte sur GitHub
    url = "https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/BRC9_GUIde%20_interpretation.txt"
    document_text = load_document_from_github(url)

    if document_text:
        st.info(f"Document chargé : BRC9_GUIde_interpretation.txt depuis GitHub")
        model = configure_model(document_text)

        if model:
            user_input = st.text_area("Posez votre question sur la norme BRCGS V9 ici :", height=200)
            if st.button("Envoyer la question BRCGS"):
                if user_input:
                    with st.spinner('Attendez pendant que nous générons la réponse...'):
                        try:
                            # Démarrage d'une nouvelle conversation pour chaque question ( stateless )
                            convo = model.start_chat(history=[]) # History vide pour une nouvelle question
                            response = convo.send_message(user_input)
                            st.write(response.text)
                        except Exception as e:
                             st.error(f"Erreur lors de la génération de la réponse : {e}")
                else:
                    st.warning("Veuillez entrer une question.")
    else:
        # Le message d'erreur est déjà affiché par load_document_from_github
        pass # Rien de plus à faire ici si le chargement a échoué


def ifs_pam_page():
    st.title("❓ Questions sur IFSv8 et PAM")

    # Liste des IDs de fichiers Google Drive spécifiques à IFSv8 et PAM
    file_ids_pam = [
        "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8",
        "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW",
        "1n2i979l-VfW0oxO3wIYTy3Yu2fdYqC9" # ID présent dans l'original pour PAM
    ]
    document_text, loaded_ids = load_documents_from_drive(file_ids_pam)

    if document_text:
        st.info(f"Documents chargés depuis Google Drive : {', '.join(loaded_ids)}")
        model = configure_model(document_text)

        if model:
            user_input = st.text_area("Posez votre question sur IFSv8 et PAM ici :", height=200)
            if st.button("Envoyer la question IFSv8 & PAM"):
                if user_input:
                    with st.spinner('Attendez pendant que nous générons la réponse...'):
                         try:
                            convo = model.start_chat(history=[])
                            response = convo.send_message(user_input)
                            st.write(response.text)
                         except Exception as e:
                            st.error(f"Erreur lors de la génération de la réponse : {e}")
                else:
                    st.warning("Veuillez entrer une question.")
    else:
         # Le message d'erreur est déjà affiché par load_documents_from_drive
         pass # Rien de plus à faire ici si le chargement a échoué


def ifs_mcda_page():
    st.title("❓ Questions sur IFSv8 et MCDA")

    # Liste des IDs de fichiers Google Drive spécifiques à IFSv8 et MCDA
    # J'utilise les IDs du troisième bloc de code original pour cette section
    file_ids_mcda = [
        "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8",
        "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW",
        "1pLieGU6lIO0RAzPFGy0oR2I6nxAA8tjc" # ID présent dans l'original pour MCDA
    ]
    document_text, loaded_ids = load_documents_from_drive(file_ids_mcda)

    if document_text:
        st.info(f"Documents chargés depuis Google Drive : {', '.join(loaded_ids)}")
        model = configure_model(document_text)

        if model:
            user_input = st.text_area("Posez votre question sur IFSv8 et MCDA ici :", height=200)
            if st.button("Envoyer la question IFSv8 & MCDA"):
                if user_input:
                    with st.spinner('Attendez pendant que nous générons la réponse...'):
                        try:
                            convo = model.start_chat(history=[])
                            response = convo.send_message(user_input)
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"Erreur lors de la génération de la réponse : {e}")
                else:
                    st.warning("Veuillez entrer une question.")
    else:
        # Le message d'erreur est déjà affiché par load_documents_from_drive
        pass # Rien de plus à faire ici si le chargement a échoué


# --- Contenu de la Barre Latérale ---

# Logo VisiPilot
st.sidebar.markdown(
    """
    <div class="sidebar-logo-container">
        <a href="https://www.visipilot.com" target="_blank">
            <img src="https://raw.githubusercontent.com/M00N69/RAPPELCONSO/main/logo%2004%20copie.jpg" alt="Visipilot Logo" class="sidebar-logo">
        </a>
    </div>
    """, unsafe_allow_html=True
)

# Menu de navigation
st.sidebar.header("Navigation par Spécialité")
page_selection = st.sidebar.radio(
    "Choisissez une spécialité :",
    ["BRCGS V9", "IFSv8 et PAM", "IFSv8 et MCDA"]
)

# Section "À propos" dans la barre latérale
with st.sidebar.expander("À propos de cette application"):
    st.write("""
    ## À propos

    Bienvenue dans l'application VisiPilot, conçue pour vous aider à poser des questions sur les normes BRCGS V9, IFSv8, PAM et MCDA.
    Elle utilise l'intelligence artificielle (`gemini-1.5-flash-latest`) pour analyser des documents spécifiques et fournir des réponses.

    **Fonctionnalités :**
    - **BRCGS V9 :** Questions basées sur un guide d'interprétation (document GitHub).
    - **IFSv8 et PAM :** Questions basées sur des documents spécifiques (documents Google Drive).
    - **IFSv8 et MCDA :** Questions basées sur un autre ensemble de documents spécifiques (documents Google Drive).

    Sélectionnez une spécialité dans le menu ci-dessus pour commencer.
    """)

# --- Logique Principale de l'Application ---

# Affichage d'une image en haut de la page principale (non dans la sidebar)
image_path = 'https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/visipilot%20banner.PNG'
st.image(image_path, use_column_width=True)

# Appel de la fonction de page appropriée en fonction de la sélection
if page_selection == "BRCGS V9":
    brcgs_page()
elif page_selection == "IFSv8 et PAM":
    ifs_pam_page()
elif page_selection == "IFSv8 et MCDA":
    ifs_mcda_page()

# Vous pouvez ajouter un pied de page si vous le souhaitez
st.markdown("---")
st.markdown("© 2023 VisiPilot. Application développée avec Streamlit et Google Gemini.")
