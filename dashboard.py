import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
# MongoDB setup
if os.getenv("DB_URL"):
    # Use environment variable (for local development)
    mongo_url = os.getenv("DB_URL")
else:
    # Use Streamlit secrets (for Streamlit Cloud)
    mongo_url = st.secrets["db_url"]
client = pymongo.MongoClient(mongo_url)
db = client["task_manager"]
goals_collection = db['goals']
users_collection = db["users"]

def calculate_progress(goals):
    """Calculate progress percentage based on completed and total story points."""
    total_story_points = sum(goal["story_points"] for goal in goals)
    total_completed_points = sum(goal["completed"] for goal in goals)
    progress = (total_completed_points / total_story_points * 100) if total_story_points > 0 else 0
    return progress

def teamlead_dashboard():
    """Dashboard view for team leads."""
    if "username" not in st.session_state:
        st.warning("Please login to access this page")
        return
    
    st.title("Team Lead Dashboard")

    # Fetch members with role 'member'
    members = [user["username"] for user in users_collection.find({"role": "member"})]

    tab1, tab2 = st.tabs(["Member Progress by Year", "Average Progress"])

    # Tab 1: View Member Progress by Year
    with tab1:
        st.header("View Member Progress by Year")
        
        # Select member and year
        selected_member = st.selectbox("Select Member", members, key="progress_member")
        selected_year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="progress_year")

        if selected_member and selected_year:
            monthly_progress = []
            for month in range(1, 13):
                goals = list(goals_collection.find({"member": selected_member, "year": selected_year, "month": month}))
                progress = calculate_progress(goals)
                monthly_progress.append(progress)

            # Display progress chart with dark background
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('black')
            ax.set_facecolor('black')
            ax.bar(range(1, 13), monthly_progress, color='skyblue')
            ax.set_xlabel("Month", color='white')
            ax.set_ylabel("Progress (%)", color='white')
            ax.set_title(f"Progress of {selected_member} in {selected_year}", color='white')
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'], color='white')
            ax.tick_params(axis='y', colors='white')
            st.pyplot(fig)

    # Tab 2: View Average Progress for All Members
    with tab2:
        st.header("Average Progress for All Members")

        selected_year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="avg_progress_year")

        if selected_year:
            member_averages = {}

            for member in members:
                # Fetch all goals for the selected member and year
                yearly_goals = list(goals_collection.find({"member": member, "year": selected_year}))

                if yearly_goals:
                    overall_progress = calculate_progress(yearly_goals)
                    member_averages[member] = overall_progress

            # Plotting the average progress for all members as a bar graph with dark background
            if member_averages:
                fig, ax = plt.subplots()
                fig.patch.set_facecolor('black')
                ax.set_facecolor('black')
                ax.bar(member_averages.keys(), member_averages.values(), color='skyblue')
                ax.set_xlabel("Members", color='white')
                ax.set_ylabel("Average Progress (%)", color='white')
                ax.set_title(f"Average Progress of Members in {selected_year}", color='white')
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                st.pyplot(fig)
            else:
                st.info("No goals found for any member for the selected year.")

def member_view_dashboard():
    """Dashboard view for individual members to see their yearly progress."""
    if "username" not in st.session_state or st.session_state.get("role") != "member":
        st.warning("Please login as a member to access this page")
        return
    
    st.title("Member Dashboard")

    # Select year
    selected_year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="member_progress_year")

    if selected_year:
        monthly_progress = []
        for month in range(1, 13):
            goals = list(goals_collection.find({"member": st.session_state["username"], "year": selected_year, "month": month}))
            progress = calculate_progress(goals)
            monthly_progress.append(progress)

        # Display progress chart with dark background
        fig, ax = plt.subplots()
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        ax.bar(range(1, 13), monthly_progress, color='skyblue')
        ax.set_xlabel("Month", color='white')
        ax.set_ylabel("Progress (%)", color='white')
        ax.set_title(f"Your Progress in {selected_year}", color='white')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'], color='white')
        ax.tick_params(axis='y', colors='white')
        st.pyplot(fig)

if __name__ == "__main__":
    # Check user role and display the appropriate dashboard
    if st.session_state.get("role") == "team lead":
        member_dashboard()
    elif st.session_state.get("role") == "member":
        member_view_dashboard()
    else:
        st.warning("You need to be logged in to access this content.")
