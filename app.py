import streamlit as st
import pymongo
from datetime import datetime
from auth import login, signup
from screens.task_manager import task_manager
from screens.Goals import goal_manager
from screens.utils import hash_password, verify_password
from screens.wigs import manage_wigs
from screens.dashboard import member_view_dashboard,teamlead_dashboard
import pandas as pd
import os
import time
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
tasks_collection = db["tasks"]
goals_collection = db['goals']

# Function to view member tasks (Team Lead only)
def view_member_tasks():
    st.title("View Member Tasks")
    
    # Select a member
    members = users_collection.find({"role": "member"})
    member_usernames = [member["username"] for member in members]
    col1,col2,col3=st.columns([1,1,1])
    with col1:
        selected_member = st.selectbox("Select a member", member_usernames)
    # Select a date range
    with col2:
        start_date = st.date_input("Start Date", key="start_date")
    with col3:
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

def view_goals():
    st.title("View Member Goals")
    selected_month = st.selectbox("Select Month", range(1, 13), format_func=lambda x: datetime(2022, x, 1).strftime('%B'), key="view_month")
    selected_year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="view_year")
    selected_member=st.session_state["username"]
    view_criteria = {"member": selected_member, "month": selected_month, "year": selected_year}
    goals = list(goals_collection.find(view_criteria))
    if goals:
            # Convert goals to DataFrame for display
            goal_data = pd.DataFrame(goals)
            goal_data = goal_data[["goal", "story_points", "type", "comments", "completed", "_id"]]
            goal_data.columns = ["Goal", "Story Points", "Type", "Comments", "Completed Points", "ID"]

            # Display progress calculation
            total_story_points = goal_data["Story Points"].sum()
            total_completed_points = goal_data["Completed Points"].sum()
            progress = (total_completed_points / total_story_points * 100) if total_story_points > 0 else 0
            st.markdown(f"### Progress: {progress:.2f}%")

            # Display 'Completed Points' editable field
            edited_df = st.data_editor(
                goal_data.drop(columns=["ID"]),
                # column_config={
                #     "Completed Points": st.column_config.NumberColumn(
                #         "Completed Points",
                #         help="Edit completed points",
                #         min_value=0.0,
                #         step=0.1,
                #         format="%.1f"
                #     )
                # },
                disabled=["Goal", "Story Points", "Type", "Comments","Completed Points"],  # Disable editing for these columns
                num_rows="fixed"  # Prevent adding new rows
            )

            
            
        

# Function to update password
def update_password():
    st.title("Update Password")
    
    current_password = st.text_input("Current Password", type='password', key="current_password")
    new_password = st.text_input("New Password", type='password', key="new_password")
    confirm_new_password = st.text_input("Confirm New Password", type='password', key="confirm_new_password")
    
    # Define the button without the on_click callback
    if st.button("Update Password", 
                 disabled=current_password.strip() == "" or new_password.strip() == "" or confirm_new_password.strip() == ""):
        
        # Perform database check and password update
        user = users_collection.find_one({"username": st.session_state["username"]})
        
        if user and verify_password(current_password, user["password"]):
            if new_password == confirm_new_password:
                new_hashed_password = hash_password(new_password)
                users_collection.update_one(
                    {"username": st.session_state["username"]},
                    {"$set": {"password": new_hashed_password}}
                )
                st.success("Your password has been updated successfully!")
                # Optional: Add a small delay and rerun the app to clear the fields visually
                time.sleep(3)
                st.rerun()

            else:
                st.error("New passwords do not match.")
        else:
            st.error("Current password is incorrect.")

# Main Application Function
def get_menu(role):
    base_menu = []
    if role == "team lead":
        base_menu.extend(["Dashboard","Task Manager", "View Member Tasks","wigs", "Add Monthly Goals","Create Member" ])
    elif role == "member":
        base_menu.extend(["Your DashBoard","Task Manager","wigs" ,"view monthly goals"])
    return base_menu

# Function to handle user logout
def handle_logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["logged_in"] = False
    st.success("You have been logged out. The page will refresh shortly.")
    st.rerun()

# Main function
def main():
    # Initialize session state if not already done
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None

    if st.session_state["logged_in"]:
        # Display welcome message in the sidebar
        st.sidebar.title(f"Welcome, {st.session_state['username']}")

        # Generate the menu based on the user role
        menu = get_menu(st.session_state["role"])
        choice = st.sidebar.selectbox("Menu", menu)
        col1,col2=st.columns([1,1])
        with col2:
            Update_Password=st.sidebar.button("Change Password")
        with col1:
            
            logout_button = st.sidebar.button("Logout")

       
        if Update_Password:
            update_password()  # Call the function to update the password
        if logout_button:
            handle_logout()
        # Route the user to the corresponding function based on their choice
        if choice == "Task Manager":
            task_manager()  # Call task manager
        elif choice == "Create Member" and st.session_state["role"] == "team lead":
            signup()  # Call the function to create a new member
        elif choice == "View Member Tasks" and st.session_state["role"] == "team lead":
            view_member_tasks()  # Call the function to view member tasks
       
        elif choice == "Add Monthly Goals" and st.session_state["role"] == "team lead":
            goal_manager()  # Call the function to add monthly goals
        elif choice == "view monthly goals" and st.session_state["role"] == "member":
            view_goals()  # Call the function to view monthly goals
        elif choice == "wigs":
            manage_wigs()  # Call the function to manage WIGs
        elif choice == "Dashboard" and st.session_state["role"] == "team lead":
            teamlead_dashboard()  # Call the function for the team lead dashboard
        elif choice == "Your DashBoard" and st.session_state["role"] == "member":
            member_view_dashboard()  # Call the function for the member's dashboard
    else:
        login() 
if __name__ == '__main__':
    main()
