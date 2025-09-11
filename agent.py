import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the Generative AI library with the API key from environment variables
try:
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # If the key is not found, raise an error to be caught by the except block
        raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring Google AI: {e}. Please make sure your GOOGLE_API_KEY is set correctly in the .env file.")
    st.stop() # Stop the app if the key is not found/invalid

# Load KB from file
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        knowledge_text = f.read()
except FileNotFoundError:
    st.error("Error: knowledge1.txt not found. Please create this file.")
    knowledge_text = "This is a default knowledge base because the file was not found."


# --- Model Initialization ---
# Initialize the Gemini model. 'gemini-1.5-flash-latest' is fast and efficient.
model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')


# --- Prompt Construction ---
# We build the full prompt string here, combining the system instructions and the knowledge base.
system_prompt = f"""You are Oracle, a platform-specific chatbot for an web platform named "Wink n Wear".
Only answer questions based on the following knowledge base.

--- KNOWLEDGE BASE ---
{knowledge_text}
----------------------
"""

# Streamlit UI
st.set_page_config(page_title="Wink n Wear Super App Chatbot", page_icon="🤖")
st.title("Wink n Wear Super App Chatbot")

# Keep chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history on app rerun
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if user_input := st.chat_input("Ask me something about the Wink n wear platform..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Display a loading spinner while waiting for the model's response
    with st.spinner("Thinking..."):
        # --- RUN GEMINI MODEL ---
        # The new way to call the model. We send the full context (system prompt + user input).
        full_prompt = system_prompt + "\nUser question: " + user_input
        
        response = model.generate_content(full_prompt)

        # Extract the text from the response
        response_text = response.text

        # Add assistant message to session state and display it
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)

