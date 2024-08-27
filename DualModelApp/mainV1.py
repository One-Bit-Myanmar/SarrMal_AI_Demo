import streamlit as st
import google.generativeai as genai
import openai
import os
import json
import requests
from components import chat_bots, food_suggestions
from dotenv import load_dotenv

load_dotenv()

# Set your API keys
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
openai.api_key = os.environ.get("OPEN_AI_API_KEY")

# Function to generate a food suggestion using Gemini model
def generate_food_suggestion_gemini(prompt):
    try:
        model = genai.GenerativeModel(model_name='tunedModels/food-suggestion-ai-v1-uss801z982xp')
        result = model.generate_content(prompt)
        response = json.loads(result.text)
        return response
    except json.JSONDecodeError as json_err:
        st.error("There was an error processing the response. Please try again later.")
        st.write(json_err)
        return None
    except Exception as e:
        st.error("An unexpected error occurred. Please try again.")
        st.write(e)
        return None

# Function to generate a food suggestion using OpenAI model
def generate_food_suggestion_openai(prompt):
    return food_suggestions.generate_gemini(prompt)

# Function to fetch an image from Unsplash
def fetch_food_image(food_name):
    url = f"https://api.unsplash.com/search/photos?page=1&query={food_name} food&client_id={UNSPLASH_ACCESS_KEY}&per_page=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['small']
        else:
            return None
    else:
        st.error(f"Error fetching image: {response.status_code}")
        return None

# Function to display the meal plan
def display_meal_plan(response):
    if response:
        st.subheader("Meal Plan")
        for meal_time, meal_info in response['response'].items():
            st.write(f"### {meal_time.capitalize()}")
            main_dish = meal_info.get("main_dish", {})
            side_dish = meal_info.get("side_dish", {})

            if main_dish:
                st.write(f"**Main Dish:** {main_dish.get('name')}")
                image_url = fetch_food_image(main_dish.get('name'))
                if image_url:
                    st.image(image_url, caption=main_dish.get('name'), use_column_width=True)
                st.write(f"- Calories: {main_dish.get('calories')} kcal")
                st.write(f"- Category: {main_dish.get('category')}")
                
                if model_choice == "OpenAI (GPT-4)":
                    # Ingredients are likely a list in OpenAI model
                    ingredients = ', '.join(main_dish.get('ingredients', []))
                else:
                    # Ingredients might be a string in Google model
                    ingredients = main_dish.get('ingredients', '')

                # Display the ingredients as a comma-separated string
                st.write(f"- Ingredients: {ingredients}")
                    
                st.write(f"- How to Cook: {main_dish.get('how_to_cook')}")
                st.write(f"- Meal Time: {main_dish.get('meal_time')}")

            if side_dish:
                st.write(f"**Side Dish:** {side_dish.get('name')}")
                image_url = fetch_food_image(side_dish.get('name'))
                if image_url:
                    st.image(image_url, caption=side_dish.get('name'), use_column_width=True)
                st.write(f"- Calories: {side_dish.get('calories')} kcal")
                st.write(f"- Category: {side_dish.get('category')}")
                
                if model_choice == "OpenAI (GPT-4)":
                    # Ingredients are likely a list in OpenAI model
                    ingredients = ', '.join(side_dish.get('ingredients', []))
                else:
                    # Ingredients might be a string in Google model
                    ingredients = side_dish.get('ingredients', '')

                # Display the ingredients as a comma-separated string
                st.write(f"- Ingredients: {ingredients}")
                    
                st.write(f"- How to Cook: {side_dish.get('how_to_cook')}")
                st.write(f"- Meal Time: {side_dish.get('meal_time')}")
            st.write("\n")

# Streamlit app layout
st.title("AI-Powered Food Suggestion System Demo")
st.write("Get personalized food suggestions or chat about nutrition!")

# Sidebar for selecting functionality
functionality_choice = st.sidebar.selectbox(
    "Choose Functionality",
    ["Generate Meal Plan", "Chat about Food and Nutrition"]
)

# Toggle for selecting the AI model
model_choice = st.sidebar.radio("Choose the AI model", options=["Gemini (Google)", "OpenAI (GPT-4)"])
st.sidebar.write("Please note that the OpenAI model is currently in beta and may occasionally produce results that are not entirely accurate. Additionally, the format for ingredients may vary slightly between models.")

if functionality_choice == "Generate Meal Plan":
    # User input fields for generating the food suggestion prompt
    st.subheader("Your Details")
    weight = st.number_input("Weight (kg)", min_value=1, max_value=300, value=70)
    height = st.number_input("Height (cm)", min_value=30, max_value=250, value=175)
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    exercise = st.selectbox("Exercise Level", ["None", "Light", "Moderate", "Intense"])
    diseases = st.text_area("List any diseases (comma-separated)", "None")
    allergies = st.text_area("List any allergies (comma-separated)", "Peanuts")

    # Generate the prompt based on user input
    prompt = f"""{{
        "weight": {weight},
        "height": {height},
        "age": {age},
        "diseases": [{', '.join([f'"{disease.strip()}"' for disease in diseases.split(',')])}],
        "allergies": [{', '.join([f'"{allergy.strip()}"' for allergy in allergies.split(',')])}],
        "gender": "{gender}",
        "exercise": "{exercise}"
    }}"""

    st.write("### Generated Prompt")
    st.code(prompt)

    # Button to generate and display the food suggestion
    if st.button("Get Food Suggestion"):
        with st.spinner("Generating food suggestion..."):
            if model_choice == "Gemini (Google)":
                response = generate_food_suggestion_gemini(prompt)
            else:
                response = generate_food_suggestion_openai(prompt)
            
            if response:
                display_meal_plan(response)
            else:
                st.warning("No response generated. Please check your input or try again later.")

elif functionality_choice == "Chat about Food and Nutrition":
    if model_choice == "Gemini (Google)":
        st.write("Gemini (Google) is Active.")
    else:
        st.write("OpenAI (GPT-4) is Active.")

    # Function to display chat messages
    def display_chat_message(role, message):
        with st.chat_message(role):
            st.write(message)

    # Initialize session state for chat history if not already initialized
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Container for chat messages
    chat_container = st.container()

    # User input
    user_input = st.text_input("You:", "")

    # Handle user input
    if st.button("Send"):
        if user_input:
            # Append user message to chat history
            st.session_state.chat_history.append({"role": "user", "message": user_input})

            # Generate response
            with st.spinner("Generating response..."):
                if model_choice == "Gemini (Google)":
                    response = "Chat with Gemini (Google) is not available because the Chat API is unusable when using Google OAuth2.0."
                else:
                    response = chat_bots.openai_chat(user_input)

            # Append AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "message": response})

            # Clear input field after sending
            # st.text_input("You:", "", key="user_input")

        else:
            st.warning("Please enter a message before sending.")

    # Display the entire chat history
    with chat_container:
        for message in st.session_state.chat_history:
            display_chat_message(message["role"], message["message"])

    # Button to clear the chat history
    if st.button("Clear Chat"):
        st.session_state.chat_history = []