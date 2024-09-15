import streamlit as st
import pymongo
from datetime import datetime
import pandas as pd
from bson import ObjectId
import os
# MongoDB setup
# if os.getenv("DB_URL"):
#     # Use environment variable (for local development)
#     mongo_url = os.getenv("DB_URL")
# else:
#     # Use Streamlit secrets (for Streamlit Cloud)
#     mongo_url = st.secrets["db_url"]
client = pymongo.MongoClient("mongodb+srv://dinesh:Asdfg123&()@cluster0.5nxca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_manager"]
goals_collection = db['goals']
users_collection = db["users"]

def goal_manager():
    if "username" not in st.session_state:
        st.warning("Please login to access this page")
        return

    tab1, tab2 = st.tabs(["Add and Manage Monthly Goals", "View Member Goals"])

    # Fetch members with role 'member'
    members = [user["username"] for user in users_collection.find({"role": "member"})]

    # Tab 1: Add and Manage Monthly Goals
    with tab1:
        st.header("Add and Manage Monthly Goals")

        # Select member, month, and year
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            member = st.selectbox("Select Member", members, key="manage_member")
        with col2:
            month = st.selectbox("Select Month", range(1, 13), format_func=lambda x: datetime(2022, x, 1).strftime('%B'), key="manage_month")
        with col3:
            year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="manage_year")

        # Form for adding new goals
        st.subheader("Add a New Goal")
        with st.form("add_goal_form"):
            goal = st.text_input("Goal")
            story_points = st.number_input("Story Points", min_value=0.0, step=0.1, format="%.1f")
            goal_type = st.selectbox("Type", ["Personal", "Team", "Project"])
            comments = st.text_area("Comments")

            submit_goal = st.form_submit_button("Add Goal")
        
        # On form submission, add a new goal
        if submit_goal:
            new_goal = {
                "member": member,
                "month": month,
                "year": year,
                "goal": goal,
                "story_points": story_points,
                "type": goal_type,
                "comments": comments,
                "completed": 0.0
            }
            goals_collection.insert_one(new_goal)
            st.success("Goal added successfully!")
            time.sleep(3)
            st.rerun()

        # Fetch goals for the selected member, month, and year
        selected_criteria = {"member": member, "month": month, "year": year}
        all_goals = list(goals_collection.find(selected_criteria))

        # Display goals if available
        if all_goals:
            goal_data = pd.DataFrame(all_goals)
            goal_data = goal_data[["goal", "story_points", "type", "comments", "_id"]]
            goal_data.columns = ["Goal", "Story Points", "Type", "Comments", "ID"]

            # Display goals with editable fields
            edited_df = st.data_editor(
                goal_data.drop(columns=["ID"]),
                num_rows="fixed"
            )

            # Update button to save changes
            if st.button("Update Goals"):
                for idx, row in edited_df.iterrows():
                    goal_id = all_goals[idx]["_id"]
                    updated_data = {
                        "goal": row["Goal"],
                        "story_points": row["Story Points"],
                        "type": row["Type"],
                        "comments": row["Comments"]
                    }
                    goals_collection.update_one({"_id": goal_id}, {"$set": updated_data})
                st.success("Goals updated successfully!")
                st.rerun()

            # Add a delete button for each row
            # for i, row in goal_data.iterrows():
            #     if st.button(f"Delete {row['Goal']}", key=f"delete_{row['ID']}"):
            #         goal_id = ObjectId(row["ID"])
            #         goals_collection.delete_one({"_id": goal_id})
            #         st.success("Goal deleted successfully!")
            #         st.rerun()

        else:
            st.info("No goals found for the selected criteria.")

    # Tab 2: View Member Goals
    with tab2:
        st.header("View and Update Member Goals")

        # Select member, month, and year to view goals
        col1,col2,col3=st.columns([1,1,1])
        with col1:
            selected_member = st.selectbox("Select Member to View Goals", members, key="view_member")
        with col2:
            selected_month = st.selectbox("Select Month", range(1, 13), format_func=lambda x: datetime(2022, x, 1).strftime('%B'), key="view_month")
        with col3:
            selected_year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), key="view_year")

        # Fetch goals for the selected member, month, and year
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
                column_config={
                    "Completed Points": st.column_config.NumberColumn(
                        "Completed Points",
                        help="Edit completed points",
                        min_value=0.0,
                        step=0.1,
                        format="%.1f"
                    )
                },
                disabled=["Goal", "Story Points", "Type", "Comments"],  # Disable editing for these columns
                num_rows="fixed"  # Prevent adding new rows
            )

            # Update button to save changes
            if st.button("Update Completed Points"):
                for idx, row in edited_df.iterrows():
                    goal_id = goals[idx]['_id']
                    new_completed = row["Completed Points"]

                    if goals[idx]['completed'] != new_completed:
                        goals_collection.update_one(
                            {"_id": goal_id},
                            {"$set": {"completed": new_completed}}
                        )
                st.success("Completed points updated successfully!")
                time.sleep(3)
                st.rerun()

        else:
            st.info("No goals found for the selected criteria.")

# Run the goal manager function
if __name__ == "__main__":
    goal_manager()
