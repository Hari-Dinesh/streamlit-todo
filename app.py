import streamlit as st
import pymongo
from datetime import datetime
from auth import login, signup
from task_manager import task_manager
from utils import hash_password, verify_password

# MongoDB Client Setup
client = pymongo.MongoClient("mongodb+srv://dinesh:Asdfg123&()@cluster0.5nxca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_manager"]
users_collection = db["users"]
tasks_collection = db["tasks"]

# Function to view member tasks (Team Lead only)
def view_member_tasks():
    st.title("View Member Tasks")
    
    # Select a member
    members = users_collection.find({"role": "member"})
    member_usernames = [member["username"] for member in members]
    selected_member = st.selectbox("Select a member", member_usernames)
    
    # Select a date range
    start_date = st.date_input("Start Date", key="start_date")
    end_date = st.date_input("End Date", key="end_date")
    
    # Fetch and display tasks within the selected date range
    if selected_member:
        tasks = tasks_collection.find({
            "user": selected_member,
            "date": {
                "$gte": datetime.combine(start_date, datetime.min.time()),
                "$lte": datetime.combine(end_date, datetime.max.time())
            }
        })
        
        st.subheader(f"Tasks for {selected_member}")
        for task in tasks:
            task_date = task['date'].strftime("%A, %Y-%m-%d %I:%M %p")  # Format the date
            if st.button(task["task"][:5]+".....", key=f"history_task_button_{task['_id']}"):
                    st.text_area("Task Details on-"+task_date, value=task["task"], key=f"history_task_textarea_{task['_id']}", disabled=True)
        

# Function to update password
def update_password():
    st.title("Update Password")
    
    current_password = st.text_input("Current Password", type='password', key="current_password")
    new_password = st.text_input("New Password", type='password', key="new_password")
    confirm_new_password = st.text_input("Confirm New Password", type='password', key="confirm_new_password")
    
    if st.button("Update Password", key="update_password_button"):
        user = users_collection.find_one({"username": st.session_state["username"]})
        
        if user and verify_password(current_password, user["password"]):
            if new_password == confirm_new_password:
                new_hashed_password = hash_password(new_password)
                users_collection.update_one(
                    {"username": st.session_state["username"]},
                    {"$set": {"password": new_hashed_password}}
                )
                st.success("Your password has been updated successfully!")
            else:
                st.error("New passwords do not match.")
        else:
            st.error("Current password is incorrect.")

# Main Application Function
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None

    if st.session_state["logged_in"]:
        st.sidebar.title(f"Welcome, {st.session_state['username']}")

        # Sidebar navigation menu with radio buttons
        menu = ["Task Manager", "Update Password"]
        if st.session_state["role"] == "team lead":
            menu.append("Create Member")
            menu.append("View Member Tasks")

        choice = st.sidebar.radio("Menu", menu)
        logout_button = st.sidebar.button("Logout")

        if logout_button:
            # Reset session state to log out the user
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["role"] = None
            
            # Use JavaScript to refresh the page
            st.success("You have been logged out. The page will refresh shortly.")
            st.rerun()

        if choice == "Task Manager":
            task_manager()  # Navigate to Task Manager
        elif choice == "Create Member" and st.session_state["role"] == "team lead":
            signup()
        elif choice == "View Member Tasks" and st.session_state["role"] == "team lead":
            view_member_tasks()
        elif choice == "Update Password":
            update_password()
    else:
        login()

if __name__ == '__main__':
    main()
