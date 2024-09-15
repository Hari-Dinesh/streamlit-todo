import streamlit as st
import pymongo
from screens.utils import hash_password, verify_password
import os
# MongoDB Client Setup
# if os.getenv("DB_URL"):
#     # Use environment variable (for local development)
#     mongo_url = os.getenv("DB_URL")
# else:
#     # Use Streamlit secrets (for Streamlit Cloud)
#     mongo_url = st.secrets["db_url"]
client = pymongo.MongoClient("mongodb+srv://dinesh:Asdfg123&()@cluster0.5nxca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_manager"]
users_collection = db["users"]

# User Schema
def create_user(username, password, role):
    return {
        "username": username,
        "password": hash_password(password),  # Store the hashed password
        "role": role,
        # "email": email,
        # "phone_number": phone_number
    }

# Create Member Function
def signup():
    st.title("Create Member")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type='password', key="signup_password")
    # email = st.text_input("Email", key="signup_email")
    role = st.selectbox("Role", ["member", "team lead"], key="signup_role")
    # phone_number = st.text_input("Phone Number", key="signup_phone_number")  

    if st.button("Create Member", key="signup_button"):
        if users_collection.find_one({"username": username}):
            st.error("Username already exists. Please choose a different username.")
        else:
            user = create_user(username, password, role)
            users_collection.insert_one(user)
            st.success(f"{role} created successfully!")
            st.sleep(2)
            st.rerun()

# Login Function
def login():
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type='password', key="login_password")
    
    if st.button("Login",disabled=username.strip()=="" or password.strip()=="", key="login_button"):
        user = users_collection.find_one({"username": username})
        if user and verify_password(password, user["password"]):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user["role"]
            st.session_state["query_params"] = {"tab": "add_task"}
            st.session_state["navigate_to_task_manager"] = True  # Set a flag to navigate
            st.success(f"Welcome {username}")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# Task Manager Function (Stub)
def task_manager():
    st.title("Task Manager")
    st.write("Manage your tasks here.")

# Main Application Function
def main():
    # Check for login state in cookies
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None

    if st.session_state["logged_in"]:
        st.sidebar.title(f"Welcome, {st.session_state['username']}")
        menu = ["Task Manager"]
        if st.session_state["role"] == "team lead":
            menu.append("Create Member")
        menu.append("Logout")

        choice = st.sidebar.selectbox("Menu", menu)

        if st.session_state.get("navigate_to_task_manager"):
            st.session_state["navigate_to_task_manager"] = False  # Reset the flag
            task_manager()  # Navigate to Task Manager
        elif choice == "Task Manager" or st.session_state.get("query_params", {}).get("tab") == "add_task":
            task_manager()
        elif choice == "Create Member" and st.session_state["role"] == "team lead":
            signup()
        elif choice == "Logout":
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["role"] = None
            st.rerun()  # Refresh the app to show the login screen
    else:
        login()

if __name__ == '__main__':
    main()
