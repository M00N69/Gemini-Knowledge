import streamlit as st
import requests
import google.generativeai as genai
import hashlib

# Assuming the model and generation settings are defined as per your earlier description
def configure_model(document_text):
    genai.configure(api_key=st.secrets["api_key"])
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
def load_document():
    url = "https://drive.google.com/uc?export=download&id=1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.text

def main():
    document_text = load_document()
    model = configure_model(document_text)

    st.title("Reformulation des Non-Conformités")
    user_input = st.text_area("Posez votre question ici:", height=300)

    if st.button("Envoyer"):
        with st.spinner('Attendez pendant que nous générons la réponse...'):
            convo = model.start_chat(history=[{"role": "user", "parts": [user_input]}])
            response = convo.send_message(user_input)
            st.write(response.text)

if __name__ == "__main__":
    main()

