import streamlit as st
import pymongo
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import os

# MongoDB setup
client = pymongo.MongoClient("mongodb+srv://dinesh:Asdfg123&()@cluster0.5nxca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_manager"]
goals_collection = db['goals']
users_collection = db["users"]
wigs_collection = db["wigs"]  # Collection for WIGs

def calculate_progress(goals):
    """Calculate progress percentage based on completed and total story points."""
    total_story_points = sum(goal["story_points"] for goal in goals)
    total_completed_points = sum(goal["completed"] for goal in goals)
    progress = (total_completed_points / total_story_points * 100) if total_story_points > 0 else 0
    return progress

def display_wig_progress(member, year, semester):
    """Display WIG progress as a bar chart with WIG names on the X-axis and percentage progress on the Y-axis."""
    # Fetch WIGs for the selected member, year, and semester
    wigs = list(wigs_collection.find({"assigned_member": {"$in": [member, "All"]}, "year": year, "semester": semester}))
    
    if wigs:
        wig_names = [wig["name"] for wig in wigs]
        wig_progress = [wig.get("progress", 0) if wig.get("progress") is not None else 0 for wig in wigs]  # Default to 0 if no progress

        # Create the bar chart with Plotly
        fig = go.Figure(
            data=[
                go.Bar(
                    x=wig_names, 
                    y=wig_progress, 
                    text=[f"{p:.2f}%" for p in wig_progress],  # Hover text shows percentage
                    hoverinfo="text",  # Display hover text on hover
                    marker=dict(color='skyblue')
                )
            ]
        )
        fig.update_layout(
            title=f"WIG Progress of {member} in {year} {semester}",
            xaxis_title="WIG Name",
            yaxis_title="Progress (%)",
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white')
        )
        fig.update_yaxes(range=[0, 100])  # Set y-axis range from 0 to 100%
        st.plotly_chart(fig)

    else:
        st.info(f"No WIGs found for {member} in {year} {semester}.")

def teamlead_dashboard():
    """Dashboard view for team leads."""
    if "username" not in st.session_state:
        st.warning("Please login to access this page")
        return
    
    st.title("Team Lead Dashboard")

    # Fetch members with role 'member'
    members = [user["username"] for user in users_collection.find({"role": "member"})]

    tab1, tab2, tab3 = st.tabs(["Member Progress by Year", "Average Progress", "WIGs Progress"])

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

            # Create a bar chart for monthly progress
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(range(1, 13)), 
                        y=monthly_progress, 
                        text=[f"{p:.2f}%" for p in monthly_progress],  # Hover text shows percentage
                        hoverinfo="text",  # Display hover text on hover
                        marker=dict(color='skyblue')
                    )
                ]
            )
            fig.update_layout(
                title=f"Progress of {selected_member} in {selected_year}",
                xaxis_title="Month",
                yaxis_title="Progress (%)",
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white')
            )
            fig.update_yaxes(range=[0, 100])  # Set y-axis range from 0 to 100%
            fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
            st.plotly_chart(fig)

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

            # Create the bar chart for average progress
            if member_averages:
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=list(member_averages.keys()), 
                            y=list(member_averages.values()), 
                            text=[f"{p:.2f}%" for p in member_averages.values()],  # Hover text shows percentage
                            hoverinfo="text",  # Display hover text on hover
                            marker=dict(color='skyblue')
                        )
                    ]
                )
                fig.update_layout(
                    title=f"Average Progress of Members in {selected_year}",
                    xaxis_title="Members",
                    yaxis_title="Average Progress (%)",
                    plot_bgcolor='black',
                    paper_bgcolor='black',
                    font=dict(color='white')
                )
                fig.update_yaxes(range=[0, 100])  # Set y-axis range from 0 to 100%
                st.plotly_chart(fig)
            else:
                st.info("No goals found for any member for the selected year.")

    # Tab 3: View WIGs Progress
    with tab3:
        st.header("View WIGs Progress")

        selected_member = st.selectbox("Select Member", members, key="wig_member")
        selected_year = st.selectbox("Select Year for WIGs", range(datetime.now().year, datetime.now().year + 5), key="wig_year")
        selected_semester = st.selectbox("Select Semester", ["Sem1", "Sem2"], key="wig_semester")

        if selected_member and selected_year and selected_semester:
            display_wig_progress(selected_member, selected_year, selected_semester)

def member_view_dashboard():
    """Dashboard view for individual members to see their yearly progress."""
    if "username" not in st.session_state or st.session_state.get("role") != "member":
        st.warning("Please login as a member to access this page")
        return
    
    st.title("Member Dashboard")

    tab1, tab2 = st.tabs(["Your Yearly Progress", "Your WIGs Progress"])

    # Tab 1: View Yearly Progress
    with tab1:
        # Select year
        selected_year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="member_progress_year")

        if selected_year:
            monthly_progress = []
            for month in range(1, 13):
                goals = list(goals_collection.find({"member": st.session_state["username"], "year": selected_year, "month": month}))
                progress = calculate_progress(goals)
                monthly_progress.append(progress)

            # Create the bar chart for monthly progress
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=list(range(1, 13)), 
                        y=monthly_progress, 
                        text=[f"{p:.2f}%" for p in monthly_progress],  # Hover text shows percentage
                        hoverinfo="text",  # Display hover text on hover
                        marker=dict(color='skyblue')
                    )
                ]
            )
            fig.update_layout(
                title=f"Your Progress in {selected_year}",
                xaxis_title="Month",
                yaxis_title="Progress (%)",
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white')
            )
            fig.update_yaxes(range=[0, 100])  # Set y-axis range from 0 to 100%
            fig.update_xaxes(tickvals=list(range(1, 13)), ticktext=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])
            st.plotly_chart(fig)

    # Tab 2: View WIGs Progress
    with tab2:
        st.header("Your WIGs Progress")

        selected_year = st.selectbox("Select Year for WIGs", range(datetime.now().year, datetime.now().year + 5), key="member_wig_year")
        selected_semester = st.selectbox("Select Semester", ["Sem1", "Sem2"], key="member_wig_semester")

        if selected_year and selected_semester:
            display_wig_progress(st.session_state["username"], selected_year, selected_semester)

if __name__ == "__main__":
    # Check user role and display the appropriate dashboard
    if st.session_state.get("role") == "team lead":
        teamlead_dashboard()
    elif st.session_state.get("role") == "member":
        member_view_dashboard()
    else:
        st.warning("You need to be logged in to access this content.")
