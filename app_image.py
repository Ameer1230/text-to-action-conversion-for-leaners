import streamlit as st
from streamlit import session_state
import json
import os
import whisper
from st_audiorec import st_audiorec
import difflib

session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0
    
def transcribe_audio_from_data(file_data):
    with open("temp.mp3", "wb") as f:
        f.write(file_data)
    model = whisper.load_model("base")
    result = model.transcribe("temp.mp3")
    os.remove("temp.mp3")
    return result["text"]

def signup(json_file_path="data.json"):
    st.title("Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")
        
        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(
                    name,
                    email,
                    age,
                    sex,
                    password,
                    json_file_path,
                )
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["users"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                return user
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(json_file_path="data.json"):
    try:
        if not os.path.exists(json_file_path):
            data = {"users": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(
    name,
    email,
    age,
    sex,
    password,
    json_file_path="data.json",
):
    try:

        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"users": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
        }
        data["users"].append(user_info)

        # Save the updated data to JSON
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        st.success("Account created successfully! You can now login.")
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="data.json"):
    st.title("Login Page")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["users"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None

def render_dashboard(user_info, json_file_path="data.json"):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        
        st.subheader("User Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
        st.image("image.jpeg", caption="Text-to-Action Conversion for Learners", use_column_width=True)
        
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def main(json_file_path="data.json"):

    st.sidebar.title("Text-to-Action Conversion for Learners")
    page = st.sidebar.selectbox(
        "Go to",
        (
            "Signup/Login",
            "Dashboard",
            "Text-to-Action Conversion for Learners",
        ),
        key="Text-to-Action Conversion for Learners",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"])
        else:
            st.warning("Please login/signup to view the dashboard.")
            
            
    elif page == "Text-to-Action Conversion for Learners":
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            st.title("Text-to-Action Conversion for Learners")
            st.write("Record or upload an audio file to get the sign")
            paths = {}            
            signs = []
            for image in os.listdir("images"):
                path = "images//"+image
                sign = image.split(".")[0]
                paths[sign] = path
                signs.append(sign)
            st.info("Enter the word you want to translate to sign language")
            text = st.text_input("Enter the word:")
            if text is not None and len(text)>0:
                transcription = text.upper()
                if transcription:
                    words = difflib.get_close_matches(transcription,signs,cutoff=0.5)
                    word = "HAPPY"
                    if len(words)>0:
                        word = words[0]
                    st.write(word)
                    st.image(paths[word], caption=word, use_column_width=True)
            
        else:
            st.warning("Please login/signup to Text-to-Action Conversion for Learners.")
if __name__ == "__main__":
    initialize_database()
    main()
