import streamlit as st
import pymongo
from datetime import datetime
import os
import time
# MongoDB setup
# if os.getenv("DB_URL"):
#     # Use environment variable (for local development)
#     mongo_url = os.getenv("DB_URL")
# else:
#     # Use Streamlit secrets (for Streamlit Cloud)
#     mongo_url = st.secrets["db_url"]
client = pymongo.MongoClient("mongodb+srv://dinesh:Asdfg123&()@cluster0.5nxca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["task_manager"]
users_collection = db["users"]
wigs_collection = db["wigs"]  # Collection for WIGs

def manage_wigs():
    """Function to manage WIGs for team leads and members."""
    if "username" not in st.session_state:
        st.warning("Please login to access this page.")
        return

    st.title("WIGs Management")

    # Fetch members with role 'member'
    members = [user["username"] for user in users_collection.find({"role": "member"})]

    # Check if the logged-in user is a team lead
    is_team_lead = st.session_state.get("role") == "team lead"

    # Create two tabs: "Add WIGs" (only for team leads) and "View WIGs" (for both team leads and members)
    if is_team_lead:
        tab1, tab2 = st.tabs(["Add WIGs", "View WIGs"])
    else:
        tab2, = st.tabs(["View WIGs"])  # Only "View WIGs" for members

    if is_team_lead:
        with tab1:
            # Tab 1: Add WIGs (only for team leads)
            st.header("Add New WIG")

            # Select Year and Semester for WIGs
            col1, col2 = st.columns([1, 1])
            with col1:
                selected_year = st.selectbox("Select Year", range(datetime.now().year - 1, datetime.now().year + 5), key="wig_year")
            with col2:
                selected_semester = st.selectbox("Select Semester", ["Sem1", "Sem2"], key="wig_semester")

            # Input fields for adding a new WIG
            wig_name = st.text_input("WIG Name")
            wig_description = st.text_area("Description")
            assigned_member = st.selectbox("Assign to Member", ["All"] + members)

            if st.button("Add WIG",disabled=wig_name.strip()==""):
                if wig_name and wig_description:
                    new_wig = {
                        "name": wig_name,
                        "description": wig_description,
                        "year": selected_year,
                        "semester": selected_semester,
                        "assigned_member": assigned_member,
                        "updates": []
                    }
                    wigs_collection.insert_one(new_wig)
                    st.success("WIG added successfully!")
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error("Please fill in all the fields to add a WIG.")
                    time.sleep(2)
                    st.rerun()
    
    with tab2:
        # Tab 2: View WIGs (for both team leads and members)
        st.header("View WIGs")

        # Common elements for both team leads and members
        col1, col2 = st.columns([1, 1])
        with col1:
            selected_wig_year = st.selectbox("Select WIG Year", range(datetime.now().year - 1, datetime.now().year + 5), key="view_wig_year")
        with col2:
            selected_wig_semester = st.selectbox("Select WIG Semester", ["Sem1", "Sem2"], key="view_wig_semester")

        if is_team_lead:
            # Team Lead View: Can view and update all WIGs
            wigs = list(wigs_collection.find({"year": selected_wig_year, "semester": selected_wig_semester}))
            if wigs:
                for wig in wigs:
                    name_col, update_col = st.columns([2, 1])
                    with name_col:
                        st.write(f"**WIG Name:** {wig['name']}")
                        st.write(f"**Description:** {wig['description']}")
                        st.write(f"**Assigned Member:** {wig['assigned_member']}")
                        # Progress Bar
                        progress = st.slider(f"Progress for {wig['name']}", 0, 100, wig.get("progress", 0))
                        if st.button(f"Update Progress for {wig['name']}", key=f"update_progress_{wig['_id']}"):
                            wigs_collection.update_one(
                                {"_id": wig["_id"]},
                                {"$set": {"progress": progress}}
                            )
                            st.success("Progress updated successfully!")
                            st.rerun()
                        # Display updates and allow team lead to add new updates
                        st.write("**Updates:**")
                        updates = wig.get("updates", [])
                        for update in updates:
                            st.write(f"- {update['member']}: {update['update']}")
                    with update_col:
                        st.subheader("Add Update")
                        update_text = st.text_area(f"Update for {wig['name']}", key=f"update_{wig['_id']}")
                        if st.button(f"Add Update for {wig['name']}", key=f"add_update_{wig['_id']}"):
                            if update_text:
                                wigs_collection.update_one(
                                    {"_id": wig["_id"]},
                                    {"$push": {"updates": {"member": st.session_state["username"], "update": update_text}}}
                                )
                                st.success("Updates added successfully!")
                                time.sleep(3)
                                st.rerun()
                            else:
                                st.error("Please enter an update before submitting.")
            else:
                st.info("No WIGs found for the selected criteria.")
        else:
            # Member View: Can view and update only assigned WIGs
            wigs = list(wigs_collection.find({
                "assigned_member": {"$in": [st.session_state["username"], "All"]},
                "year": selected_wig_year,
                "semester": selected_wig_semester
            }))

            if wigs:
                for wig in wigs:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**WIG Name:** {wig['name']}")
                        st.write(f"**Description:** {wig['description']}")

                        # Display updates for the member
                        st.write("**Updates:**")
                        updates = wig.get("updates", [])
                        for update in updates:
                            st.write(f"- {update['member']}: {update['update']}")
                    with col2:
                        st.subheader("Add Update")
                        update_text = st.text_area(f"Update for {wig['name']}", key=f"update_{wig['_id']}", value=st.session_state.get(f"update_{wig['_id']}", ""))
                        if st.button(f"Add Update for {wig['name']}", key=f"add_update_{wig['_id']}"):
                            if update_text:
                                wigs_collection.update_one(
                                    {"_id": wig["_id"]},
                                    {"$push": {"updates": {"member": st.session_state["username"], "update": update_text}}}
                                )
                                
                                st.success("Update added successfully!")
                                st.session_state[f"update_{wig['_id']}"] = ""
                                st.rerun()
                            else:
                                st.error("Please enter an update before submitting.")
            else:
                st.info("No WIGs found for the selected criteria.")

if __name__ == "__main__":
    manage_wigs()
