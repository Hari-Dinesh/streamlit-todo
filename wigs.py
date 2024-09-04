import streamlit as st
import pymongo
from datetime import datetime

# MongoDB setup
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

    # Create two tabs: "Add WIGs" and "View WIGs"
    tab1, tab2 = st.tabs(["Add WIGs", "View WIGs"])

    with tab1:
        # Tab 1: Add WIGs
        if st.session_state.get("role") == "team lead":
            st.header("Add New WIG")

            # Select Year and Semester for WIGs
            selected_year = st.selectbox("Select Year", range(datetime.now().year - 1, datetime.now().year + 5), key="wig_year")
            selected_semester = st.selectbox("Select Semester", ["Sem1", "Sem2"], key="wig_semester")

            # Input fields for adding a new WIG
            wig_name = st.text_input("WIG Name")
            wig_description = st.text_area("Description")
            assigned_member = st.selectbox("Assign to Member", ["All"] + members)

            if st.button("Add WIG"):
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
                else:
                    st.error("Please fill in all the fields to add a WIG.")
        else:
            st.info("Only team leads can add WIGs.")

    with tab2:
        # Tab 2: View WIGs
        st.header("View WIGs")

        # Common elements for both team leads and members
        selected_wig_year = st.selectbox("Select WIG Year", range(datetime.now().year - 1, datetime.now().year + 5), key="view_wig_year")
        selected_wig_semester = st.selectbox("Select WIG Semester", ["Sem1", "Sem2"], key="view_wig_semester")

        if st.session_state.get("role") == "team lead":
            # Team Lead View: Can view and update all WIGs
            wigs = list(wigs_collection.find({"year": selected_wig_year, "semester": selected_wig_semester}))
            if wigs:
                for wig in wigs:
                    st.write(f"**WIG Name:** {wig['name']}")
                    st.write(f"**Description:** {wig['description']}")
                    st.write(f"**Assigned Member:** {wig['assigned_member']}")

                    # Display updates and allow team lead to add new updates
                    st.write("**Updates:**")
                    updates = wig.get("updates", [])
                    for update in updates:
                        st.write(f"- {update['member']}: {update['update']}")

                    st.subheader("Add Update")
                    update_text = st.text_area(f"Update for {wig['name']}", key=f"update_{wig['_id']}")
                    if st.button(f"Add Update for {wig['name']}", key=f"add_update_{wig['_id']}"):
                        if update_text:
                            wigs_collection.update_one(
                                {"_id": wig["_id"]},
                                {"$push": {"updates": {"member": st.session_state["username"], "update": update_text}}}
                            )
                            st.success("Update added successfully!")
                            st.experimental_rerun()
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
                    st.write(f"**WIG Name:** {wig['name']}")
                    st.write(f"**Description:** {wig['description']}")

                    # Display updates for the member
                    st.write("**Updates:**")
                    updates = wig.get("updates", [])
                    for update in updates:
                        st.write(f"- {update['member']}: {update['update']}")

                    st.subheader("Add Update")
                    update_text = st.text_area(f"Update for {wig['name']}", key=f"update_{wig['_id']}")
                    if st.button(f"Add Update for {wig['name']}", key=f"add_update_{wig['_id']}"):
                        if update_text:
                            wigs_collection.update_one(
                                {"_id": wig["_id"]},
                                {"$push": {"updates": {"member": st.session_state["username"], "update": update_text}}}
                            )
                            st.success("Update added successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Please enter an update before submitting.")
            else:
                st.info("No WIGs found for the selected criteria.")

if __name__ == "__main__":
    manage_wigs()
