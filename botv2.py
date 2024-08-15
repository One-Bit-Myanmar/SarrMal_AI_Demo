import streamlit as st
import google.generativeai as genai
import os
import env

# Configuration
genai.configure(api_key=env.GEMINI_AI_API_KEY)
generation_config = {"temperature": 0.25, "max_output_tokens": 1024, "top_k": 40, "top_p": 0.95}

# Function to generate a response using Google Generative AI
def generate_response(prompt):
    model = genai.GenerativeModel("gemini-pro", generation_config=generation_config)
    chat_session = genai.ChatSession(model=model)  # Initialize chat session
    gemini_response = chat_session.send_message(prompt)

   # Access text using the correct attribute (replace 'content.parts[0].text' if needed)
    generated_text = gemini_response.candidates[0].content.parts[0].text  

    return generated_text

# Streamlit app layout
st.title("Mini Chatbot with Gemini AI")
st.write("Ask me anything!")

# User input
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        with st.spinner("Generating response..."):
            response = generate_response(user_input)
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                st.write(response)
    else:
        st.write("Please enter a message.")