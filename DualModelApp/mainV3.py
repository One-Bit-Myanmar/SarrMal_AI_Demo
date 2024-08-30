import streamlit as st
import google.generativeai as genai
import openai
import os
from components import chat_bots, image_searchings, food_suggestions
from dotenv import load_dotenv
import json
import requests
from PIL import Image, ImageOps
from io import BytesIO

load_dotenv()

# Set your API keys
openai.api_key = os.environ.get("OPEN_AI_API_KEY")

# Function to generate a food suggestion using Gemini model
def generate_food_suggestion_gemini(prompt):
    return food_suggestions.generate_gemini_v3(prompt)

# Function to generate a food suggestion using OpenAI model
def generate_food_suggestion_openai(prompt):
    return food_suggestions.generate_openai(prompt)

# Function to fetch an image from Unsplash
def fetch_food_image(food_name):
    if image_engine == "Google":
        return image_searchings.fetch_google(food_name)
    else:
        return image_searchings.fetch_unsplash(food_name)

def load_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        content_type = response.headers['Content-Type']
        
        # Check if the content is an image
        if 'image' not in content_type:
            st.warning("⚠️ The URL does not point to a valid image.")
            return None
        
        img = Image.open(BytesIO(response.content))
        return img
    except requests.exceptions.RequestException as e:
        st.warning(f"😔 Oops! Failed to retrieve the web image.")
        return None
    except IOError as e:
        st.warning(f"❌ Sorry, we couldn't open the image.")
        return None

def resize_to_square(image, size=(512, 400)):
    return ImageOps.fit(image, size, Image.Resampling.LANCZOS)

def display_meal_plan(response):
    if response:
        st.subheader("Meal Plan")
        for meal_time, meal_info in response['response'].items():
            st.write(f"### {meal_time.capitalize()}")
            
            # Create two columns for main dish and side dish
            col1, col2 = st.columns(2)

            # Display main dish in the first column
            with col1:
                main_dish = meal_info.get("main_dish", {})
                if main_dish:
                    st.write(f"**Main Dish:** {main_dish.get('name')}")
                    image_url = fetch_food_image(main_dish.get('name'))
                    
                    if image_url:
                        # st.image(image_url, caption=main_dish.get('name'), use_column_width=True)
                        image = load_image(image_url)
                        if image:
                            square_img = resize_to_square(image)
                            st.image(square_img, caption=main_dish.get('name'), use_column_width=True)
                        # else:
                        #     st.write("🚫 Oops! No image found for this food.")
                        
                         
                    st.write(f"- Calories: {main_dish.get('calories')} kcal")
                    st.write(f"- Category: {main_dish.get('category')}")
                    
                    ingredients = ', '.join(main_dish.get('ingredients', []))
                    st.write(f"- Ingredients: {ingredients}")
                    
                    st.write(f"- How to Cook: {main_dish.get('how_to_cook')}")
                    st.write(f"- Meal Time: {main_dish.get('meal_time')}")
            
            # Display side dish in the second column
            with col2:
                side_dish = meal_info.get("side_dish", {})
                if side_dish:
                    st.write(f"**Side Dish:** {side_dish.get('name')}")
                    image_url = fetch_food_image(side_dish.get('name'))
                                        
                    if image_url:
                        # st.image(image_url, caption=side_dish.get('name'), use_column_width=True)
                        image = load_image(image_url)
                        if image:
                            square_img = resize_to_square(image)
                            st.image(square_img, caption=side_dish.get('name'), use_column_width=True)
                        # else:
                        #     st.write("🚫 Oops! No image found for this food.")
                            
                    st.write(f"- Calories: {side_dish.get('calories')} kcal")
                    st.write(f"- Category: {side_dish.get('category')}")
                    
                    ingredients = ', '.join(side_dish.get('ingredients', []))
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
model_choice = st.sidebar.radio("Choose the AI model", options=["SarrMal (Tuning)", "OpenAI (GPT-4)"])
st.sidebar.write("🌟 Please note that the OpenAI model is currently in beta and may occasionally produce results that are not entirely accurate.")
st.sidebar.write("🌟 Additionally, the format for ingredients may vary slightly between models.")
if st.sidebar.radio("Choose Image Generator", options=["Unsplash", "Google"]) == "Google":
    image_engine  = "Google"
    # st.write("Google Image Searching is Active.")
else:
    image_engine = "Unsplash"
    # st.write("Unsplash Image Searching is Active.")
st.sidebar.write("📓 Please note that the Google Image Generator is currently in beta and may occasionally produce results that are not entirely accurate.")


if functionality_choice == "Generate Meal Plan":
    if model_choice == "SarrMal (Tuning)":
        st.write("SarrMal (Tuning) model is Active.")
    else:
        st.write("OpenAI (GPT-4) model is Active.")
    # User input fields for generating the food suggestion prompt
    if image_engine == "Google":
        st.write("Google Image Searching is Active.")
    else:
        st.write("Unsplash Image Searching is Active.")
        
    st.subheader("Your Details")
    weight = st.number_input("Weight (kg)", min_value=1, max_value=300, value=70)
    height = st.number_input("Height (cm)", min_value=30, max_value=250, value=175)
    age = st.number_input("Age", min_value=1, max_value=120, value=25)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    exercise = st.selectbox("Exercise Level", ["None", "Light", "Moderate", "Intense"])
    diseases = st.multiselect("List any diseases", ["None", "Diabetes", "Hypertension", "Celiac Disease", "Food Allergies"], default=["None"])
    allergies = st.multiselect("List any allergies", ["None", "Peanuts", "Shellfish", "Eggs", "Milk"], default=["None"])
    preferred_food = st.selectbox("Preferred Food", ["Burmese", "Thiland", "Chinese", "Western", "Japanese", "Korean", "Indian", "Other"])
    food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian","Healthy","Gym-Rat","High-Calorie", "High-Fibre", "Low-Sugar", "High-Protein", "Balanced","Other"])

    # Generate the prompt based on user input
    prompt = f"""{{
        "weight": {weight},
        "height": {height},
        "age": {age},
        "diseases": {diseases},
        "allergies": {allergies},
        "gender": "{gender}",
        "exercise": "{exercise}",
        "preferred": "{preferred_food}",
        "food-type": "{food_type}"
    }}"""

    #For Model1 and Model2
    
    # prompt = f"""{{
    #     "weight": {weight},
    #     "height": {height},
    #     "age": {age},
    #     "diseases": [{', '.join([f'"{disease.strip()}"' for disease in diseases.split(',')])}],
    #     "allergies": [{', '.join([f'"{allergy.strip()}"' for allergy in allergies.split(',')])}],
    #     "gender": "{gender}",
    #     "exercise": "{exercise}",
    # }}"""

    st.write("### Your Preferences and Details")
    st.code(prompt)

    # Button to generate and display the food suggestion
    if st.button("Get Food Suggestion"):
        with st.spinner("Generating food suggestion..."):
            if model_choice == "SarrMal (Tuning)":
                response = generate_food_suggestion_gemini(prompt)
            else:
                response = generate_food_suggestion_openai(prompt)
            
            if response:
                display_meal_plan(response)
            else:
                st.warning("No response generated. Please check your input or try again later.")

elif functionality_choice == "Chat about Food and Nutrition":
    if model_choice == "SarrMal (Tuning)":
        st.write("SarrMal (Tuning) is Active.")
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
                if model_choice == "SarrMal (Tuning)":
                    response = chat_bots.gemini_chat_oauth(user_input)
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