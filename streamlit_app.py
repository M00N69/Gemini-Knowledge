import streamlit as st
import google.generativeai as genai
from pathlib import Path
import hashlib

# Configure the API key using Streamlit secrets
api_key = st.secrets["api_key"]
genai.configure(api_key=api_key)

# Model setup
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

system_instruction = "Se référer en priorité aux documents qui ont été mis à disposition concernant IFSv8. Les bonnes pratiques de la reformulation de l'écart sont: doit être factuelle,doit être détaillée (référence de la procédure, zone /équipement, ….), doit justifier le choix de notation, en fonction du type de déviation/non-conformité, le risque produit doit être préciser en restant dans le contexte de l’exigence, ne doit pas être assimilable à du conseil, ne doit pas être rédigée sous forme de suggestions.La reformulation de l'écart doit de préférence inclure les 4 aspects suivants:1/ L’exigence exemple: La norme exige que ….. ou exigence interne 2/ Description de la défaillance : Les responsabilités, la méthode ou les informations documentées n’ont pas été prévues à ce sujet  OU Les dispositions prévues ne sont pas mises en œuvre OU Les dispositions prévues ne sont pas toujours mises en œuvre OU Les dispositions prévues et mises en œuvre ne sont pas toujours suffisamment efficaces à atteindre tel résultat prévu 3/ Preuve de la défaillance 4/ Conséquence / Impact de cet écart dans le contexte de l’exigence; toujours conclure en expliquant pour le risque est limité. Réaliser systématiquement les 2 reformulations ( toujours 1 en français et 1 en anglais) ne doivent pas inclure des conseils ou des recommandations dans la description du risque qui ne doit pas exagérer le danger. La reformulation doit être professionnelle sans citer les 4 étapes mais les rédigeant de manière harmonieuse et compréhensible"

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction=system_instruction,
    safety_settings=safety_settings
)

def main():
    st.title("Reformulation des Non-Conformités")

    # User question input
    user_input = st.text_input("Posez votre question ici:")

    # Optional file upload
    uploaded_file = st.file_uploader("Charger un document PDF (optionnel)", type=["pdf"])
    file_uri = None
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        hash_id = hashlib.sha256(bytes_data).hexdigest()
        file_uri = genai.upload_file(content=bytes_data, display_name=hash_id).uri

    # Submit button
    if st.button("Envoyer"):
        if file_uri:
            convo = model.start_chat(history=[
                {"role": "user", "parts": [f"File URI: {file_uri}"]},
                {"role": "user", "parts": [user_input]}
            ])
        else:
            convo = model.start_chat(history=[
                {"role": "user", "parts": [user_input]}
            ])

        with st.spinner('Attendez pendant que nous générons la réponse...'):
            response = convo.send_message(user_input)
            st.write(response.text)

    # Restart the app with a new question
    if st.button("Poser une nouvelle question"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
