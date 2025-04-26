import streamlit as st
import requests
import google.generativeai as genai
import re # Pour la recherche de clause et le chunking
import time # Pour ajouter un petit délai dans le spinner
import hashlib # Utilisé pour identifier les chunks uniques dans la recherche de clause

# --- Configuration Initiale de l'Application ---
st.set_page_config(
    page_title="VisiPilot - Assistant Conformité",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Application d'aide à la conformité aux normes basée sur Google Gemini."
    }
)

# --- CSS pour améliorer le design ---
css = """
<style>
    /* Police de caractères */
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
        color: #333;
    }

    /* Titres */
    h1, h2, h3, h4, h5, h6 {
        color: #1e3a8a;
        margin-bottom: 0.5em;
    }

    /* Barre latérale */
    .css-1d3z3hf, .css-hxt7z, .css-1lc0jr3, .css-1v3fvcr, .css-uf99v8, .css-1xw8zdh {
        background-color: #f0f2f6;
        color: #333;
    }

    /* Style du logo dans la barre latérale */
    .sidebar-logo-container {
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 20px;
        border-bottom: 1px solid #ccc;
    }
    .sidebar-logo {
        max-width: 80%;
        height: auto;
        border-radius: 10px;
    }

    /* Boutons */
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #164e8a;
    }

     /* Bouton de connexion spécifique (ajusté pour le CSS général) */
    .login-button>button {
        background-color: #22c55e; /* Vert */
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
        width: 100%;
    }
    /* Champ de mot de passe et Recherche de clause */
     .stTextInput input[type="password"], .stTextInput input[type="text"] {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 16px;
        width: 100%;
    }


    /* Spinner */
    .stSpinner > div > div {
        border-top-color: #1e3a8a;
    }

    /* Expander "À propos" */
    .streamlit-expanderHeader {
        background-color: #e0e7ff;
        color: #1e3a8a;
        border-radius: 5px;
        padding: 10px;
        cursor: pointer;
        margin-bottom: 10px;
    }
    .streamlit-expanderContent {
       background-color: #f9fafb;
       padding: 10px;
       border-left: 3px solid #1e3a8a;
       border-bottom-left-radius: 5px;
       border-bottom-right-radius: 5px;
       margin-bottom: 10px;
    }

    /* Messages d'information/erreur/avertissement */
    .stAlert {
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .stAlert.error {
        background-color: #fee2e2;
        color: #991b1b;
        border-left-color: #ef4444;
    }
     .stAlert.warning {
        background-color: #fef3c7;
        color: #92400e;
        border-left-color: #f59e0b;
    }
    .stAlert.info {
         background-color: #dbeafe;
        color: #1e40af;
        border-left-color: #3b82f6;
    }
    .stAlert.success {
        background-color: #d1fae5;
        color: #065f46;
        border-left-color: #34d399;
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

    /* Style pour la section de conversation */
    .chat-container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Styles pour les messages individuels */
    .chat-message {
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 15px;
        max-width: 80%;
        word-wrap: break-word;
    }

    .chat-message.user {
        background-color: #e0e7ff;
        margin-left: auto;
        border-bottom-right-radius: 2px;
    }

    .chat-message.assistant {
        background-color: #f0f2f6;
        margin-right: auto;
        border-bottom-left-radius: 2px;
    }

    .chat-message strong {
        display: block;
        margin-bottom: 5px;
        font-size: 0.9em;
        color: #1e3a8a;
    }

    /* Style pour les citations dans la réponse de l'assistant */
    .chat-message.assistant p strong {
        font-size: 1em;
    }
     .chat-message.assistant em {
        display: block;
        margin-top: 8px;
        font-size: 0.85em;
        color: #555;
        border-left: 3px solid #ccc;
        padding-left: 8px;
        font-style: normal;
     }

    /* Centrer le formulaire de connexion */
    .center-form {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 60vh;
    }
    .center-form > div {
        min-width: 300px;
        padding: 20px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f9fafb;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }

    /* Espacement pour les éléments principaux */
    .main-content-container {
        padding-top: 20px;
    }


</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Initialisation de l'état de la session ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'documents_data' not in st.session_state:
     st.session_state.documents_data = {'all_chunks': None, 'loaded_docs_info': []}


# --- Logique d'authentification ---
if not st.session_state['authenticated']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Accès restreint")
        st.write("Veuillez entrer le mot de passe pour accéder à l'application.")
        try:
            expected_password = st.secrets["app_password"]
        except KeyError:
            st.error("❌ Erreur : Le mot de passe secret ('app_password') n'est pas configuré dans `st.secrets`. L'application ne peut pas démarrer.")
            st.stop()

        password_input = st.text_input("Mot de passe :", type="password", key="login_password_input")
        login_button_pressed = st.button("Se connecter", key="login_button")

        if login_button_pressed:
            if password_input == expected_password:
                st.session_state['authenticated'] = True
                st.success("Connexion réussie ! Chargement de l'application...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect.")
    st.stop() # Arrête l'exécution ici si l'utilisateur n'est pas authentifié

# --- Le reste de l'application est exécuté UNIQUEMENT si authenticated est True ---

# --- Configuration des documents (Nom Lisible -> Google Drive ID ou GitHub URL) ---
# Nous utilisons un dictionnaire pour associer un nom lisible à l'ID/URL
# Pour GitHub, l'ID sera l'URL elle-même
document_sources = {
    "BRCGS V9 Guide": "https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/BRC9_GUIde%20_interpretation.txt", # URL GitHub pour BRCGS
    "IFS v8 Document A": "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8", # Google Drive ID
    "IFS v8 Document B": "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW", # Google Drive ID
    # "PAM Document": "...", # Ajoutez l'ID Google Drive ou l'URL GitHub pour le document PAM spécifique
    # "MCDA Document": "...", # Ajoutez l'ID Google Drive ou l'URL GitHub pour le document MCDA spécifique
    "IFS v8 Document C (MCDA/PAM)": "1pLieGU6lIO0RAzPFGy0oR2I6nxAA8tjc", # Cet ID était utilisé pour MCDA, je lui donne un nom et le conserve. Assurez-vous qu'il contient bien des infos pour les deux si c'est le cas.
}

# --- Fonctions Utilitaires pour Chargement, RAG et Modèle ---

# Fonction pour configurer le modèle Gemini
def configure_model():
    try:
        if "api_key" not in st.secrets:
             st.error("❌ Clé API Gemini non trouvée dans st.secrets.")
             return None

        genai.configure(api_key=st.secrets["api_key"])

        # Instruction système générique demandant de citer les SOURCES (noms lisibles) et SECTIONS
        system_instruction = (
            "You are an AI assistant specializing in quality norms, specifically BRCGS V9, IFSv8, PAM, "
            "and MCDA. Your purpose is to help auditors and quality managers understand these norms based "
            "*only* on the provided document snippets (context). Your knowledge is limited to these documents.\n"
            "Follow these instructions carefully:\n"
            "1. Answer the user's question concisely and accurately using *only* the information available in the `Context:` section below.\n"
            "2. **Cite your sources explicitly and frequently.** For *each piece of information* you provide that comes from the context, include a citation formatted as `[Source: Document Name, Section: Relevant Section/Clause]` right after the relevant sentence or phrase. Use the 'Source' and 'Section' names exactly as provided in the context snippets.\n"
            "3. If the answer to the question cannot be found *strictly* within the provided context, state clearly and politely that you cannot answer the question based on the available documents.\n"
            "4. Do not introduce information from outside the provided context or your general knowledge.\n"
            "5. Maintain a helpful, professional, and objective tone appropriate for quality professionals.\n"
            "6. Avoid conversational filler; get straight to the answer based on the context.\n"
        )


        generation_config = {
            "temperature": 0.5,
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 4000,
        }

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-preview-04-17",
            generation_config=generation_config,
            system_instruction=system_instruction,
            safety_settings=safety_settings
        )
        return model
    except Exception as e:
         st.error(f"❌ Erreur lors de l'initialisation du modèle Gemini avec 'gemini-2.5-flash-preview-04-17': {e}. Vérifiez le nom du modèle ou vos paramètres API.")
         return None

# Fonction pour découper le texte en chunks avec métadonnées
def chunk_document(text, source_name, chunk_size=500, overlap=50):
    chunks = []
    paragraphs = re.split(r'\n\n+', text)
    current_chunk_text = ""
    current_section = "Début du document"
    section_pattern = re.compile(r'^\s*(\d+(\.\d+)*(\s+[A-Z].+)?)(?=\s)', re.MULTILINE) # Ajusté pour gérer espaces début de ligne


    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        match_section = section_pattern.match(paragraph)
        if match_section:
             current_section = match_section.group(1).strip()


        # Logique de découpage simplifiée basée sur la taille
        # Si le paragraphe actuel + le texte du chunk actuel dépasse la taille limite, on ferme le chunk actuel et on en démarre un nouveau.
        # L'overlap n'est pas géré dans cette version simple.
        if len(current_chunk_text) + len(paragraph) + 2 > chunk_size and current_chunk_text:
             chunks.append({
                 "text": current_chunk_text.strip(),
                 "source": source_name,
                 "section": current_section
             })
             # Commence le nouveau chunk avec le paragraphe actuel
             current_chunk_text = paragraph
        else:
             # Ajouter le paragraphe au chunk actuel
             current_chunk_text += (paragraph + "\n\n")

    # Ajouter le dernier chunk s'il n'est pas vide
    if current_chunk_text.strip():
        chunks.append({
            "text": current_chunk_text.strip(),
            "source": source_name,
            "section": current_section
        })

    # Fallback si aucun section pattern trouvé
    if all('Section: Début du document' in c.get('section', '') for c in chunks) and chunks:
         for i, chunk in enumerate(chunks):
              first_words = " ".join(chunk['text'].split()[:15]) + "..." # Plus de mots pour le placeholder
              chunk['section'] = f"Section approximative (début du chunk {i+1}: {first_words})"

    return chunks

# Fonction pour charger TOUS les documents (GitHub ou Drive) et les traiter en chunks
# Prend un dictionnaire { "Nom Lisible du Document": "Google Drive ID ou URL GitHub" }
@st.cache_data(ttl=86400, show_spinner="Chargement et traitement des documents...")
def load_process_and_chunk_documents(document_sources_map):
    all_chunks = []
    loaded_docs_info = [] # Liste pour les messages d'état (Nom -> Succès/Erreur)

    for doc_name, source_id_or_url in document_sources_map.items():
        doc_text = None
        error_msg = None

        if source_id_or_url.startswith("http"): # C'est une URL (supposons GitHub)
            url = source_id_or_url
            try:
                response = requests.get(url)
                response.raise_for_status()
                doc_text = response.text
            except requests.exceptions.RequestException as e:
                error_msg = f"GitHub ({url}): {str(e)}"
        else: # C'est un Google Drive ID
             file_id = source_id_or_url
             url = f"https://drive.google.com/uc?export=download&id={file_id}"
             try:
                response = requests.get(url)
                # Vérifier si la réponse est une page d'erreur Google Drive
                if "Vous n'avez pas accès" in response.text or "We're sorry, a server error occurred." in response.text or "Not Found" in response.text:
                     error_msg = f"Drive ID ({file_id}): Accès refusé, non trouvé ou erreur serveur. Vérifiez l'ID et les permissions."
                else:
                     response.raise_for_status()
                     doc_text = response.text
             except requests.exceptions.RequestException as e:
                 error_msg = f"Drive ID ({file_id}): Erreur de requête. {str(e)}"

        if doc_text:
            try:
                chunks = chunk_document(doc_text, doc_name) # Utilise le nom lisible comme source
                all_chunks.extend(chunks)
                loaded_docs_info.append(f"✅ **{doc_name}**")
            except Exception as e:
                error_msg = f"Traitement des chunks pour '{doc_name}': {str(e)}"
                loaded_docs_info.append(f"❌ **{doc_name}** (Erreur de traitement: {error_msg})")

        if error_msg:
            st.warning(f"⚠️ Échec du chargement ou du traitement pour **{doc_name}**: {error_msg}")
            loaded_docs_info.append(f"❌ **{doc_name}** (Échec du chargement: {error_msg})")


    if not all_chunks:
        st.error("❌ Aucun contenu pertinent n'a pu être chargé ou traité à partir des sources fournies.")
        return None, loaded_docs_info

    # Retourne les chunks et la liste des documents chargés/échoués
    return all_chunks, loaded_docs_info


# Fonction simple de recherche de chunks pertinents (basée sur mots-clés)
def retrieve_relevant_chunks(query, all_chunks, top_n=7): # Augmenté top_n
    if not all_chunks:
        return []
    query_keywords = set(query.lower().split())
    # Supprimer les mots très courants (stop words basiques)
    stop_words = set(["le", "la", "les", "un", "une", "des", "de", "du", "des", "à", "au", "aux", "et", "ou", "ni", "car", "mais", "où", "donc", "or", "ni", "car", "est", "sont", "a", "ont", "pour", "avec", "dans", "sur", "par", "il", "elle", "ils", "elles", "ce", "cet", "cette", "ces", "mon", "ton", "son", "notre", "votre", "leur", "mes", "tes", "ses", "nos", "vos", "leurs", "qui", "que", "quoi", "dont", "où", "quand", "comment", "pourquoi", "quoi", "quels", "quelle", "quelles", "quel", "qu'est-ce", "c'est", "il", "elle", "on", "nous", "vous", "ils", "elles", "se", "me", "te", "lui", "leur", "en", "y", "si", "alors", "donc", "pourtant", "cependant", "ainsi", "aussi", "plus", "moins", "très", "tout", "tous", "toute", "toutes", "même", "mêmes", "autre", "autres", "tel", "telle", "tels", "telles", "différents", "différentes", "certains", "certaines", "plusieurs", "chaque", "tout", "tous", "toute", "toutes", "aucun", "aucune", "nul", "nulle", "personne", "rien", "quelque", "quelques", "chaque", "plusieurs", "certains", "certaines", "lesquels", "lesquelles", "duquel", "de laquelle", "desquels", "desquelles", "auquel", "à laquelle", "auxquels", "auxquelles", "lequel", "laquelle"])
    query_keywords = {word for word in query_keywords if word not in stop_words and len(word) > 2}

    scored_chunks = []
    for chunk in all_chunks:
        chunk_keywords = set(re.findall(r'\w+', chunk['text'].lower())) # Utilise regex pour mots
        score = len(query_keywords.intersection(chunk_keywords))
        # Bonus si la query est trouvée exactement dans le chunk
        if query.lower() in chunk['text'].lower():
            score += 5
        # Bonus si la query est trouvée dans la section
        if chunk.get('section') and query.lower() in chunk['section'].lower():
            score += 10

        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_n]]

# Fonction pour formater les chunks pour le prompt de l'IA
def format_chunks_for_prompt(chunks):
    if not chunks:
        return ""
    formatted_text = "Context:\n"
    for chunk in chunks:
        # Utilise le nom lisible du document et la section/clause trouvée
        formatted_text += f"[Source: {chunk['source']}, Section: {chunk.get('section', 'N/A')}]\n"
        formatted_text += chunk['text'] + "\n\n"
    return formatted_text

# --- Fonction de recherche de clause directe ---
def find_clause_in_text(query, all_chunks):
    query = query.strip()
    if not query or not all_chunks:
        return []

    found_sections = []
    query_lower = query.lower()

    for chunk in all_chunks:
        # Recherche par Section (si le chunking a bien extrait la section)
        # Cherche si la query est une sous-chaîne de la section
        if chunk.get('section') and query_lower in chunk['section'].lower():
            found_sections.append({
                 "source": chunk['source'],
                 "section": chunk['section'],
                 "text": chunk['text']
            })
            continue # Passer au chunk suivant si trouvé dans la section

        # Recherche par texte (si la clause est mentionnée dans le corps du texte)
        # Limiter la recherche textuelle à des phrases contenant la query pour réduire les faux positifs
        # Ceci est une approche simple, une recherche plein texte indexée serait plus efficace pour des docs très longs
        sentences = re.split(r'(?<=[.!?])\s+', chunk['text']) # Diviser en phrases basiques
        relevant_sentences = [sent for sent in sentences if query_lower in sent.lower()]
        if relevant_sentences:
             # Joindre les phrases pertinentes et ajouter comme résultat
             found_sections.append({
                 "source": chunk['source'],
                 "section": f"{chunk.get('section', 'N/A')} (Trouvé dans le texte)", # Indiquer où c'est trouvé
                 "text": " ".join(relevant_sentences) # Montrer seulement les phrases pertinentes
             })


    # Éliminer les doublons basés sur source+section+texte (hash simple)
    unique_sections = []
    seen_hashes = set()
    for section in found_sections:
        # Utiliser un hash pour identifier les doublons
        item_hash = hashlib.md5((section['source'] + section['section'] + section['text']).encode('utf-8')).hexdigest()
        if item_hash not in seen_hashes:
            unique_sections.append(section)
            seen_hashes.add(item_hash)

    return unique_sections[:10] # Limiter le nombre de résultats


# --- Fonctions pour chaque Page (Spécialité) ---

def brcgs_page(all_chunks):
    st.title("🛡️ BRCGS V9 Assistant")

    # Définir les noms de documents pertinents pour cette page
    relevant_doc_names = ["BRCGS V9 Guide"]

    # Filtrer les chunks pertinents pour cette page
    page_chunks = [c for c in all_chunks if c['source'] in relevant_doc_names]

    if not page_chunks:
         st.warning("⚠️ Aucun contenu BRCGS V9 n'a été chargé ou trouvé. Impossible de répondre aux questions.")
         model = None
    else:
        loaded_docs_names = {c['source'] for c in page_chunks} # Get unique source names actually found
        st.markdown(f'<div class="document-info">📄 Documents pertinents chargés : <strong>{", ".join(loaded_docs_names)} ({len(page_chunks)} sections disponibles)</strong></div>', unsafe_allow_html=True)
        model = configure_model() # Configure le modèle une fois que les documents sont prêts

    if model:
        # Section Recherche de Clause
        st.subheader("🔍 Rechercher une Clause ou une Section Spécifique")
        clause_query = st.text_input("Entrez le numéro ou le nom de la clause (ex: 4.2.1, Food Defence) :", key="brcgs_clause_lookup")
        if clause_query:
            with st.spinner(f'Recherche de sections pour "{clause_query}"...'):
                found_clauses = find_clause_in_text(clause_query, page_chunks) # Rechercher uniquement dans les chunks de la page
                if found_clauses:
                    st.info(f"🔍 Sections trouvées pour '{clause_query}':")
                    for item in found_clauses:
                         st.write(f"**[{item['source']} - {item['section']}]**")
                         # Utiliser st.expander si le texte est long
                         with st.expander("Voir le contenu complet"):
                             st.write(item['text'])
                         # st.write(item['text']) # Afficher le texte si pas trop long
                         st.markdown("---") # Séparateur
                else:
                    st.info(f"Pas de sections trouvées contenant '{clause_query}' dans les documents BRCGS chargés.")
        st.markdown("---") # Séparateur entre lookup et chat

        # Section Chat Assistant
        st.subheader("💬 Chat Assistant BRCGS V9")
        st.write("Posez vos questions sur la norme BRCGS V9 en vous basant sur les documents chargés.")

        # Bouton Nouvelle Conversation
        if st.button("🗑️ Nouvelle Conversation", key="brcgs_new_chat_button"): # Bouton générique
            st.session_state.messages = [] # Vide l'historique
            st.rerun()

        # Afficher les messages précédents
        for message in st.session_state.messages:
            role = "user" if message["role"] == "user" else "assistant"
            # Vous pouvez ajouter des avatars si vous voulez
            # avatar = "🧑‍💻" if role == "user" else "🤖"
            st.markdown(f'<div class="chat-message {role}"><strong>{role.capitalize()}:</strong> {message["content"]}</div>', unsafe_allow_html=True)


        # Zone de texte pour que l'utilisateur pose ses questions
        user_input = st.text_area("Posez votre question ici:", height=100, key="brcgs_chat_input")

        if st.button("Envoyer", key="brcgs_send_button"): # Bouton générique
            if user_input:
                # Ajouter la question utilisateur à l'historique
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.spinner('✨ Analyse et génération de la réponse...'):
                    try:
                        # 1. Récupérer les chunks pertinents
                        relevant_chunks = retrieve_relevant_chunks(user_input, page_chunks)

                        if not relevant_chunks:
                            response_text = "Désolé, je n'ai pas trouvé d'informations pertinentes dans les documents BRCGS chargés pour répondre à votre question."
                        else:
                            # 2. Formater les chunks pour le prompt
                            context_prompt = format_chunks_for_prompt(relevant_chunks)

                            # 3. Construire le prompt complet pour le modèle
                            # Inclure l'historique de conversation pour le contexte
                            model_history = []
                            # Préparer l'historique pour le modèle
                            for msg in st.session_state.messages[:-1]:
                                model_history.append({"role": msg["role"], "parts": [msg["content"]]})

                            # Message actuel incluant le contexte RAG
                            current_message_parts = [
                                context_prompt, # Le contexte RAG
                                f"User Question: {user_input}" # La question utilisateur
                                # On pourrait ajouter "Answer ONLY based on the provided context." ici aussi
                            ]

                            convo = model.start_chat(history=model_history)
                            response = convo.send_message(current_message_parts)

                            response_text = response.text

                        # Ajouter la réponse de l'assistant à l'historique
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun()

                    except Exception as e:
                         st.error(f"❌ Erreur lors de la génération de la réponse : {e}")


            else:
                st.warning("⚠️ Veuillez entrer une question.")


def ifs_pam_page(all_chunks):
    st.title("🛡️ IFSv8 et PAM Assistant")

    # Définir les noms de documents pertinents pour cette page
    relevant_doc_names = ["IFS v8 Document A", "IFS v8 Document B", "IFS v8 Document C (MCDA/PAM)"] # Inclure les noms pertinents ici

    # Filtrer les chunks pertinents pour cette page
    page_chunks = [c for c in all_chunks if c['source'] in relevant_doc_names]

    if not page_chunks:
         st.warning("⚠️ Aucun contenu IFSv8/PAM n'a été chargé ou trouvé. Impossible de répondre aux questions.")
         model = None
    else:
        loaded_docs_names = {c['source'] for c in page_chunks}
        st.markdown(f'<div class="document-info">📄 Documents pertinents chargés : <strong>{", ".join(loaded_docs_names)} ({len(page_chunks)} sections disponibles)</strong></div>', unsafe_allow_html=True)
        model = configure_model()

    if model:
        # Section Recherche de Clause
        st.subheader("🔍 Rechercher une Clause ou une Section Spécifique")
        clause_query = st.text_input("Entrez le numéro ou le nom de la clause (ex: IFS 4.2.1) :", key="ifspam_clause_lookup")
        if clause_query:
            with st.spinner(f'Recherche de sections pour "{clause_query}"...'):
                found_clauses = find_clause_in_text(clause_query, page_chunks)
                if found_clauses:
                    st.info(f"🔍 Sections trouvées pour '{clause_query}':")
                    for item in found_clauses:
                         st.write(f"**[{item['source']} - {item['section']}]**")
                         with st.expander("Voir le contenu complet"):
                             st.write(item['text'])
                         st.markdown("---")
                else:
                    st.info(f"Pas de sections trouvées contenant '{clause_query}' dans les documents IFSv8/PAM chargés.")
        st.markdown("---")

        # Section Chat Assistant
        st.subheader("💬 Chat Assistant IFSv8 et PAM")
        st.write("Posez vos questions sur les normes IFSv8 et PAM en vous basant sur les documents chargés.")

        # Bouton Nouvelle Conversation
        if st.button("🗑️ Nouvelle Conversation", key="ifspam_new_chat_button"):
            st.session_state.messages = []
            st.rerun()

        # Afficher les messages précédents
        for message in st.session_state.messages:
            role = "user" if message["role"] == "user" else "assistant"
            st.markdown(f'<div class="chat-message {role}"><strong>{role.capitalize()}:</strong> {message["content"]}</div>', unsafe_allow_html=True)

        # Zone de texte pour que l'utilisateur pose ses questions
        user_input = st.text_area("Posez votre question ici:", height=100, key="ifs_pam_chat_input")

        if st.button("Envoyer", key="ifs_pam_send_button"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.spinner('✨ Analyse et génération de la réponse...'):
                     try:
                        relevant_chunks = retrieve_relevant_chunks(user_input, page_chunks)
                        if not relevant_chunks:
                            response_text = "Désolé, je n'ai pas trouvé d'informations pertinentes dans les documents IFSv8/PAM chargés pour répondre à votre question."
                        else:
                            context_prompt = format_chunks_for_prompt(relevant_chunks)
                            model_history = []
                            for msg in st.session_state.messages[:-1]:
                                model_history.append({"role": msg["role"], "parts": [msg["content"]]})

                            current_message_parts = [context_prompt, f"User Question: {user_input}"]

                            convo = model.start_chat(history=model_history)
                            response = convo.send_message(current_message_parts)

                            response_text = response.text

                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun()

                     except Exception as e:
                        st.error(f"❌ Erreur lors de la génération de la réponse : {e}")


            else:
                st.warning("⚠️ Veuillez entrer une question.")


def ifs_mcda_page(all_chunks):
    st.title("🛡️ IFSv8 et MCDA Assistant")

    # Définir les noms de documents pertinents pour cette page
    relevant_doc_names = ["IFS v8 Document A", "IFS v8 Document B", "IFS v8 Document C (MCDA/PAM)"] # Inclure les noms pertinents ici

    # Filtrer les chunks pertinents pour cette page
    page_chunks = [c for c in all_chunks if c['source'] in relevant_doc_names] # Les mêmes docs que PAM? Ajustez si MCDA utilise un set différent

    if not page_chunks:
         st.warning("⚠️ Aucun contenu IFSv8/MCDA n'a été chargé ou trouvé. Impossible de répondre aux questions.")
         model = None
    else:
        loaded_docs_names = {c['source'] for c in page_chunks}
        st.markdown(f'<div class="document-info">📄 Documents pertinents chargés : <strong>{", ".join(loaded_docs_names)} ({len(page_chunks)} sections disponibles)</strong></div>', unsafe_allow_html=True)
        model = configure_model()

    if model:
        # Section Recherche de Clause
        st.subheader("🔍 Rechercher une Clause ou une Section Spécifique")
        clause_query = st.text_input("Entrez le numéro ou le nom de la clause (ex: IFS 4.2.1) :", key="ifsmcda_clause_lookup")
        if clause_query:
            with st.spinner(f'Recherche de sections pour "{clause_query}"...'):
                found_clauses = find_clause_in_text(clause_query, page_chunks)
                if found_clauses:
                    st.info(f"🔍 Sections trouvées pour '{clause_query}':")
                    for item in found_clauses:
                         st.write(f"**[{item['source']} - {item['section']}]**")
                         with st.expander("Voir le contenu complet"):
                             st.write(item['text'])
                         st.markdown("---")
                else:
                    st.info(f"Pas de sections trouvées contenant '{clause_query}' dans les documents IFSv8/MCDA chargés.")
        st.markdown("---")

        # Section Chat Assistant
        st.subheader("💬 Chat Assistant IFSv8 et MCDA")
        st.write("Posez vos questions sur les normes IFSv8 et MCDA en vous basant sur les documents chargés.")

        # Bouton Nouvelle Conversation
        if st.button("🗑️ Nouvelle Conversation", key="ifsmcda_new_chat_button"):
            st.session_state.messages = []
            st.rerun()

        # Afficher les messages précédents
        for message in st.session_state.messages:
            role = "user" if message["role"] == "user" else "assistant"
            st.markdown(f'<div class="chat-message {role}"><strong>{role.capitalize()}:</strong> {message["content"]}</div>', unsafe_allow_html=True)

        # Zone de texte pour que l'utilisateur pose ses questions
        user_input = st.text_area("Posez votre question ici:", height=100, key="ifs_mcda_chat_input")

        if st.button("Envoyer", key="ifsmcda_send_button"):
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.spinner('✨ Analyse et génération de la réponse...'):
                    try:
                        relevant_chunks = retrieve_relevant_chunks(user_input, page_chunks)
                        if not relevant_chunks:
                             response_text = "Désolé, je n'ai pas trouvé d'informations pertinentes dans les documents IFSv8/MCDA chargés pour répondre à votre question."
                        else:
                            context_prompt = format_chunks_for_prompt(relevant_chunks)
                            model_history = []
                            for msg in st.session_state.messages[:-1]:
                                model_history.append({"role": msg["role"], "parts": [msg["content"]]})

                            current_message_parts = [context_prompt, f"User Question: {user_input}"]

                            convo = model.start_chat(history=model_history)
                            response = convo.send_message(current_message_parts)

                            response_text = response.text

                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        st.rerun()

                    except Exception as e:
                         st.error(f"❌ Erreur lors de la génération de la réponse : {e}")


            else:
                st.warning("⚠️ Veuillez entrer une question.")


# --- Contenu de la Barre Latérale (Visible après authentification) ---

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
with st.sidebar.expander("ℹ️ À propos de cet assistant"):
    st.write("""
    Cet assistant est conçu pour aider les professionnels de la qualité à naviguer dans les normes BRCGS V9, IFSv8, PAM et MCDA.

    Il utilise l'intelligence artificielle (`gemini-2.5-flash-preview-04-17`) pour :
    - Répondre à vos questions en se basant sur des documents de référence.
    - Citer les sources (document et section) pour justifier les réponses.
    - Permettre une recherche rapide de clauses spécifiques.
    - Maintenir le contexte de votre conversation.

    **Documents utilisés :**
    """)
    # Afficher les documents chargés ici
    if st.session_state.documents_data['loaded_docs_info']:
         for doc_info in st.session_state.documents_data['loaded_docs_info']:
              st.write(f"- {doc_info}")
    else:
         st.info("Aucun document n'a encore été chargé.")

    st.write("""
    Sélectionnez une spécialité dans le menu ci-dessus pour commencer ou poser une question.
    """)


# --- Logique Principale de l'Application (Exécutée si authentifié) ---

# Chargement, traitement et chunking de tous les documents sources définis (mis en cache)
# Stocke les résultats dans st.session_state.documents_data
all_chunks, loaded_docs_info = load_process_and_chunk_documents(document_sources)
st.session_state.documents_data['all_chunks'] = all_chunks
st.session_state.documents_data['loaded_docs_info'] = loaded_docs_info # Stocker l'info des chargements pour l'afficher dans "À propos"


# Affichage d'une image en haut de la page principale
image_path = 'https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/visipilot%20banner.PNG'
st.image(image_path, use_container_width=True)

# Ajouter un conteneur stylisé pour le contenu principal
with st.container():
    st.markdown('<div class="main-content-container">', unsafe_allow_html=True) # Appliquer le padding CSS

    # Appel de la fonction de page appropriée en fonction de la sélection
    if st.session_state.documents_data['all_chunks'] is None:
        st.error("L'application ne peut pas fonctionner car aucun contenu pertinent n'a pu être chargé à partir des documents sources.")
    else:
        # Passer les chunks globaux à chaque page
        if page_selection == "BRCGS V9":
            brcgs_page(st.session_state.documents_data['all_chunks'])
        elif page_selection == "IFSv8 et PAM":
            ifs_pam_page(st.session_state.documents_data['all_chunks'])
        elif page_selection == "IFSv8 et MCDA":
            ifs_mcda_page(st.session_state.documents_data['all_chunks'])

    st.markdown('</div>', unsafe_allow_html=True) # Fermer le conteneur


# Pied de page
st.markdown("---")
st.markdown("© 2023 VisiPilot. Application développée avec Streamlit et Google Gemini.")
