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
def load_documents():
    file_ids = [
        "1NIMYhm5i_J5T_yBnNtKRiLLqj7lwfhB8",
        "1Qo6uMueCO_9boMu13RSlF_J8L4MhIhWW",
        "1pLieGU6lIO0RAzPFGy0oR2I6nxAA8tjc"
    ]
    documents_text = []
    for file_id in file_ids:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Ensure we notice bad responses
            documents_text.append(response.text)
        except requests.exceptions.HTTPError as e:
            st.error(f"Failed to download document with ID {file_id}: {str(e)}")
            return None  # Or handle the error differently if needed
    return "\n\n".join(documents_text), file_ids  # Return both documents_text and file_ids

def main():
    # Displaying an image without a caption
    image_path = 'https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/visipilot%20banner.PNG'  # Ensure the path to your image file is correct
    st.image(image_path, use_column_width=True)

    st.title("Question sur IFSv8 et MCDA")
    document_text, file_ids = load_documents()  # Receive both values from load_documents

    if document_text is not None:
        st.write(f"Documents chargés : {', '.join(file_ids)}")
        model = configure_model(document_text)

        user_input = st.text_area("Posez votre question ici:", height=300)
        if st.button("Envoyer"):
            with st.spinner('Attendez pendant que nous générons la réponse...'):
                convo = model.start_chat(history=[{"role": "user", "parts": [user_input]}])
                response = convo.send_message(user_input)
                st.write(response.text)
    else:
        st.error("Error loading documents. Unable to proceed without document data.")

if __name__ == "__main__":
    main()
