import streamlit as st
import requests
import google.generativeai as genai
# hashlib n'est pas utilisé, on peut le retirer
# import hashlib

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
# Le CSS est intégré directement ici
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
    .css-1d3z3hf, .css-hxt7z, .css-1lc0jr3, .css-1v3fvcr, .css-uf99v8 { /* Selecteurs pour la barre latérale */
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

     /* Bouton de connexion spécifique */
    .login-button>button {
        background-color: #22c55e; /* Vert */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 100%; /* Pleine largeur dans la colonne */
    }
    .login-button>button:hover {
        background-color: #16a34a; /* Vert foncé */
    }


    /* Zones de texte */
    .stTextArea textarea {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
        width: 100%; /* Assure que la zone de texte prend toute la largeur disponible */
    }
    /* Champ de mot de passe */
     .stTextInput input[type="password"] {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
        width: 100%; /* Pleine largeur dans la colonne */
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
        border-radius: 5까요px; /* Adjusted radius */
    }
    .stAlert.error {
        background-color: #fee2e2; /* Fond rouge très clair */
        color: #991b1b; /* Texte rouge foncé */
        border-left-color: #ef4444; /* Ligne rouge */
    }
     .stAlert.warning { /* Style pour st.warning */
        background-color: #fef3c7; /* Fond jaune très clair */
        color: #92400e; /* Texte orange foncé */
        border-left-color: #f59e0b; /* Ligne orange */
    }
    .stAlert.info {
         background-color: #dbeafe; /* Fond bleu très clair */
        color: #1e40af; /* Texte bleu foncé */
        border-left-color: #3b82f6; /* Ligne bleue */
    }

    /* Style pour la section "Documents chargés" */
    .document-info {
        font-size: 0.9em;
        color: #555;
        margin-bottom: 15px;
        font-style: italic;
    }
    .document-info strong {
        color: #1e3a8a;
    }

    /* Centrer le formulaire de connexion */
    .center-form {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 60vh; /* Centre verticalement dans 60% de la hauteur de la vue */
    }
    .center-form > div {
        min-width: 300px; /* Largeur minimale du formulaire */
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f9fafb;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }

</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Initialisation de l'état de la session ---
# Utiliser st.session_state pour gérer l'état de l'authentification
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# --- Logique d'authentification ---
if not st.session_state['authenticated']:
    # Utiliser une colonne pour centrer le formulaire de connexion
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2: # Afficher le formulaire dans la colonne du milieu
        st.title("🔒 Accès restreint")
        st.write("Veuillez entrer le mot de passe pour accéder à l'application.")

        # Récupérer le mot de passe secret
        try:
            expected_password = st.secrets["app_password"]
        except KeyError:
            st.error("❌ Erreur : Le mot de passe secret ('app_password') n'est pas configuré dans `st.secrets`. L'application ne peut pas démarrer.")
            st.stop() # Arrête l'exécution si le secret n'est pas trouvé

        password_input = st.text_input("Mot de passe :", type="password", key="login_password_input")

        # Bouton de connexion avec une classe CSS spécifique
        login_button_pressed = st.button("Se connecter", key="login_button") # Utilisation de la classe CSS par défaut pour simplicté ici, le sélecteur CSS .login-button>button existe mais n'est pas appliqué directement par Streamlit ici. On garde le CSS général des boutons.


        if login_button_pressed:
            if password_input == expected_password:
                st.session_state['authenticated'] = True
                st.success("Connexion réussie ! Redirection...")
                st.rerun() # Rerun pour afficher le contenu principal
            else:
                st.error("❌ Mot de passe incorrect.")

    st.stop() # Arrête l'exécution ici si l'utilisateur n'est pas authentifié

# --- Le reste de l'application est exécuté UNIQUEMENT si authenticated est True ---

# --- Fonctions Utilitaires ---

# Fonction pour configurer le modèle Gemini
def configure_model(document_text):
    try:
        # La vérification de la clé API a déjà été faite au-dessus
        genai.configure(api_key=st.secrets["api_key"])
    except Exception as e:
        st.error(f"❌ Erreur de configuration de l'API Gemini : {e}.")
        return None

    # Paramètres de génération
    generation_config = {
        "temperature": 2,
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
            model_name="gemini-2.5-flash-preview-04-17",
            generation_config=generation_config,
            system_instruction=document_text,
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
         st.error(f"❌ Erreur lors de l'initialisation du modèle Gemini avec 'gemini-1.5-flash-latest': {e}. Veuillez vérifier le nom du modèle ou vos paramètres API.")
         return None


# Fonction pour charger un document depuis GitHub avec mise en cache
@st.cache_data(ttl=86400, show_spinner="Chargement du document depuis GitHub...")
def load_document_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Échec du téléchargement du document depuis GitHub ({url}): {str(e)}")
        return None

# Fonction pour charger des documents depuis Google Drive avec mise en cache
@st.cache_data(ttl=86400, show_spinner="Chargement des documents depuis Google Drive...")
def load_documents_from_drive(file_ids):
    documents_text = []
    loaded_file_ids = []
    for file_id in file_ids:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            response = requests.get(url)
            if "Vous n'avez pas accès" in response.text or "We're sorry, a server error occurred." in response.text:
                 st.warning(f"⚠️ Avertissement : Accès refusé ou erreur serveur pour l'ID {file_id}. Veuillez vérifier les permissions du fichier Google Drive.")
                 continue
            response.raise_for_status()
            documents_text.append(response.text)
            loaded_file_ids.append(file_id)
        except requests.exceptions.HTTPError as e:
            st.warning(f"⚠️ Avertissement HTTP Error: Échec du téléchargement du document Google Drive avec l'ID {file_id}. Il ne sera pas inclus. Erreur : {str(e)}")
        except requests.exceptions.RequestException as e:
             st.warning(f"⚠️ Avertissement Request Error: Erreur de requête pour l'ID {file_id}. Il ne sera pas inclus. Erreur : {str(e)}")

    if not documents_text:
        # On n'affiche pas l'erreur critique ici si loaded_file_ids est vide, car des avertissements ont déjà été émis.
        # Le message "Impossible de poser une question..." sera affiché dans la page spécifique.
        return None, []

    return "\n\n".join(documents_text), loaded_file_ids


# --- Fonctions pour chaque Page (Spécialité) ---

def brcgs_page():
    st.title("❓ Questions sur la norme BRCGS V9")

    url = "https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/BRC9_GUIde%20_interpretation.txt"
    document_text = load_document_from_github(url)

    if document_text:
        st.markdown(f'<div class="document-info">📄 Document chargé : <strong>BRC9_GUIde_interpretation.txt</strong> depuis GitHub</div>', unsafe_allow_html=True)
        model = configure_model(document_text)

        if model:
            user_input = st.text_area("Posez votre question sur la norme BRCGS V9 ici :", height=150, key="brcgs_input")
            if st.button("Envoyer la question BRCGS", key="brcgs_button"):
                if user_input:
                    with st.spinner('✨ Génération de la réponse...'):
                        try:
                            convo = model.start_chat(history=[])
                            response = convo.send_message(user_input)
                            st.write(response.text)
                        except Exception as e:
                             st.error(f"❌ Erreur lors de la génération de la réponse : {e}")
                else:
                    st.warning("⚠️ Veuillez entrer une question.")
    else:
        pass # Messages d'erreur déjà affichés par load_document_from_github


def ifs_pam_page():
    st.title("❓ Questions sur IFSv8 et PAM")

    # Liste des IDs de fichiers Google Drive spécifiques à IFSv8 et PAM
    # SUPPRESSION de l'ID problematic (1n2i979l-VfW0oxO3wIYTy3Yu2fdYqC9)
    file_ids_pam = [
        "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8",
        "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW",
        # "1n2i979l-VfW0oxO3wIYTy3Yu2fdYqC9" <-- Cet ID est supprimé
    ]
    document_text, loaded_ids = load_documents_from_drive(file_ids_pam)

    if document_text:
        st.markdown(f'<div class="document-info">📄 Documents chargés depuis Google Drive : <strong>{", ".join(loaded_ids)}</strong></div>', unsafe_allow_html=True)
        model = configure_model(document_text)

        if model:
            user_input = st.text_area("Posez votre question sur IFSv8 et PAM ici :", height=150, key="ifs_pam_input")
            if st.button("Envoyer la question IFSv8 & PAM", key="ifs_pam_button"):
                if user_input:
                    with st.spinner('✨ Génération de la réponse...'):
                         try:
                            convo = model.start_chat(history=[])
                            response = convo.send_message(user_input)
                            st.write(response.text)
                         except Exception as e:
                            st.error(f"❌ Erreur lors de la génération de la réponse : {e}")
                else:
                    st.warning("⚠️ Veuillez entrer une question.")
    else:
         st.warning("⚠️ Impossible de poser une question sur IFSv8/PAM car les documents nécessaires n'ont pas pu être chargés.")


def ifs_mcda_page():
    st.title("❓ Questions sur IFSv8 et MCDA")

    # Liste des IDs de fichiers Google Drive spécifiques à IFSv8 et MCDA
    file_ids_mcda = [
        "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8",
        "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW",
        "1pLieGU6lIO0RAzPFGy0oR2I6nxAA8tjc"
    ]
    document_text, loaded_ids = load_documents_from_drive(file_ids_mcda)

    if document_text:
        st.markdown(f'<div class="document-info">📄 Documents chargés depuis Google Drive : <strong>{", ".join(loaded_ids)}</strong></div>', unsafe_allow_html=True)
        model = configure_model(document_text)

        if model:
            user_input = st.text_area("Posez votre question sur IFSv8 et MCDA ici :", height=150, key="ifs_mcda_input")
            if st.button("Envoyer la question IFSv8 & MCDA", key="ifs_mcda_button"):
                if user_input:
                    with st.spinner('✨ Génération de la réponse...'):
                        try:
                            convo = model.start_chat(history=[])
                            response = convo.send_message(user_input)
                            st.write(response.text)
                        except Exception as e:
                            st.error(f"❌ Erreur lors de la génération de la réponse : {e}")
                else:
                    st.warning("⚠️ Veuillez entrer une question.")
    else:
        st.warning("⚠️ Impossible de poser une question sur IFSv8/MCDA car les documents nécessaires n'ont pas pu être chargés.")


# --- Le reste de l'application est exécuté UNIQUEMENT si authenticated est True ---
# On place tout ce contenu DANS le bloc `if st.session_state['authenticated']:` au début du script
# et on le supprime d'ici.

# (Le code ci-dessous n'apparaît plus ici, il est déplacé au début sous la condition d'authentification)
# # Contenu de la Barre Latérale
# st.sidebar.markdown(...)
# st.sidebar.header(...)
# page_selection = st.sidebar.radio(...)
# with st.sidebar.expander(...): ...
#
# # Logique Principale
# image_path = '...'
# st.image(...)
# if page_selection == "...": ...
# st.markdown("---")
# st.markdown("© ...")

# --- Contenu de la Barre Latérale (Déplacé ici pour être sous condition d'authentification) ---
# Le code du logo, menu et "À propos" doit maintenant être sous la condition `if st.session_state['authenticated']:`,
# mais comme le code se déroule séquentiellement, il suffit de le laisser *après* la logique d'authentification
# qui contient le `st.stop()`. Tout ce qui est après le `st.stop()` initial ne sera exécuté que si l'authentification réussit.

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
    ["BRCGS V9", "IFSv8 et PAM", "IFSv8 et MCDA"],
    key="sidebar_radio"
)

# Section "À propos" dans la barre latérale
with st.sidebar.expander("À propos de cette application"):
    st.write("""
    ## À propos

    Bienvenue dans l'application VisiPilot, conçue pour vous aider à poser des questions sur les normes BRCGS V9, IFSv8, PAM et MCDA.
    Elle utilise l'intelligence artificielle (`gemini-2.5-flash-preview-04-17`) pour analyser des documents spécifiques et fournir des réponses.

    **Fonctionnalités :**
    - **BRCGS V9 :** Questions basées sur un guide d'interprétation (document GitHub).
    - **IFSv8 et PAM :** Questions basées sur des documents spécifiques (documents Google Drive). Notez qu'un fichier a été retiré de la liste en raison d'une erreur de chargement.
    - **IFSv8 et MCDA :** Questions basées sur un autre ensemble de documents spécifiques (documents Google Drive).

    Sélectionnez une spécialité dans le menu ci-dessus pour commencer.
    """)

# --- Logique Principale de l'Application (Déplacé ici pour être sous condition d'authentification) ---

# Affichage d'une image en haut de la page principale (non dans la sidebar)
image_path = 'https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/visipilot%20banner.PNG'
st.image(image_path, use_container_width=True) # Utilisation de use_container_width

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
