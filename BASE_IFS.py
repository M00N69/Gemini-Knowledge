import streamlit as st
import requests
import google.generativeai as genai

# Fonction pour configurer le modèle avec des paramètres spécifiques
def configure_model(document_text):
    # Configuration de l'API avec la clé secrète stockée dans Streamlit
    genai.configure(api_key=st.secrets["api_key"])
    
    # Paramètres de génération pour le modèle
    generation_config = {
        "temperature": 2,
        "top_p": 0.4,
        "top_k": 32,
        "max_output_tokens": 8192,
    }
    
    # Paramètres de sécurité pour filtrer les contenus inappropriés
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    # Création du modèle avec les configurations définies
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        system_instruction=document_text,
        safety_settings=safety_settings
    )
    return model

# Fonction pour charger les documents avec mise en cache pour une meilleure performance
@st.cache_data(ttl=86400)
def load_documents():
    # Liste des IDs de fichiers Google Drive
    file_ids = [
        "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8",
        "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW",
        "1n2i979l-VfW0oxO3wIYTy3Yu2fdvYqC9",
        "1VOYlPjzHiQTzVdz2SjnjXNZnJrPB_gBB"
    ]
    documents_text = []
    
    # Téléchargement de chaque fichier et ajout du contenu à la liste
    for file_id in file_ids:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Vérifie si la requête a réussi
            documents_text.append(response.text)
        except requests.exceptions.HTTPError as e:
            st.error(f"Échec du téléchargement du document avec l'ID {file_id} : {str(e)}")
            return None  # Retourne None en cas d'erreur
    
    # Retourne le texte des documents concaténés et les IDs des fichiers
    return "\n\n".join(documents_text), file_ids

# Configuration de la mise en page de la page Streamlit en mode large
st.set_page_config(layout="wide")

# Ajouter une section "À propos" dans un expandeur pour plus d'informations
with st.expander("À propos de cette application"):
    st.write("""
    ## À propos de cette application

    Bienvenue dans l'application VisiPilot, conçue pour vous aider à poser des questions sur les normes IFSv8, PAM, et BRCGS V9. Cette application utilise une intelligence artificielle pour analyser des documents spécifiques et fournir des réponses précises à vos questions.
    
    ## Fonctionnalités Principales
    
    ### Page 1 : Questions sur la norme BRCGS V9
    
    - **But** : Permet aux utilisateurs de poser des questions sur la norme BRCGS V9.
    - **Fonctionnement** :
      1. **Chargement du Document** : L'application télécharge un document contenant des informations sur la norme BRCGS V9 depuis un fichier hébergé sur GitHub.
      2. **Saisie de la Question** : Les utilisateurs peuvent saisir leur question dans un champ de texte.
      3. **Génération de la Réponse** : Une fois la question soumise, l'intelligence artificielle analyse le document et génère une réponse adaptée.
    
    ### Page 2 : Questions sur IFSv8 et PAM
    
    - **But** : Permet aux utilisateurs de poser des questions sur les normes IFSv8 et PAM.
    - **Fonctionnement** :
      1. **Chargement des Documents** : L'application télécharge plusieurs documents pertinents depuis Google Drive.
      2. **Saisie de la Question** : Les utilisateurs peuvent poser une question en lien avec ces normes.
      3. **Génération de la Réponse** : L'intelligence artificielle traite la question et renvoie une réponse basée sur le contenu des documents chargés.
    - **Documents Chargés** : L'application charge plusieurs fichiers depuis Google Drive 
    
    ### Page 3 : Questions sur IFSv8 et MCDA
    
    - **But** : Fournir des réponses aux questions liées à IFSv8 et MCDA (Méthode de Conception et Développement de l'Analyse).
    - **Fonctionnement** :
      1. **Chargement des Documents** : Comme pour la page sur IFSv8 et PAM, cette page charge des documents spécifiques depuis Google Drive.
      2. **Saisie de la Question** : Un champ de texte est disponible pour poser des questions sur IFSv8 et MCDA.
      3. **Génération de la Réponse** : L'intelligence artificielle répond aux questions en analysant le contenu des documents.
    - **Documents Chargés** : Les mêmes documents que ceux utilisés pour IFSv8 et PAM sont également utilisés ici.
        
        """)
# Affichage d'un logo et d'un lien vers un site web dans la barre latérale
st.sidebar.markdown(
    """
    <div class="sidebar-logo-container">
        <a href="https://www.visipilot.com" target="_blank">
            <img src="https://raw.githubusercontent.com/M00N69/RAPPELCONSO/main/logo%2004%20copie.jpg" alt="Visipilot Logo" class="sidebar-logo">
        </a>
    </div>
    """, unsafe_allow_html=True
)

def main():
    # Affichage d'une image en haut de la page
    image_path = 'https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/visipilot%20banner.PNG'  # Chemin vers l'image
    st.image(image_path, use_column_width=True)

    st.title("Question sur IFSv8 et PAM")
    
    # Chargement des documents et récupération des textes et IDs
    document_text, file_ids = load_documents()

    if document_text is not None:
        st.write(f"Documents chargés : {', '.join(file_ids)}")
        # Configuration du modèle avec le texte des documents
        model = configure_model(document_text)

        # Zone de texte pour que l'utilisateur pose ses questions
        user_input = st.text_area("Posez votre question ici:", height=300)
        if st.button("Envoyer"):
            with st.spinner('Attendez pendant que nous générons la réponse...'):
                # Démarrage d'une nouvelle conversation avec le modèle
                convo = model.start_chat(history=[{"role": "user", "parts": [user_input]}])
                response = convo.send_message(user_input)
                st.write(response.text)  # Affichage de la réponse du modèle
    else:
        st.error("Erreur lors du chargement des documents. Impossible de continuer sans les données des documents.")

if __name__ == "__main__":
    main()

