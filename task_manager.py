import streamlit as st
import pymongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import time
import os
# from utils import send_email_notification

# MongoDB Client Setup (use your Atlas connection string here)
client = pymongo.MongoClient(os.getenv('DB_URL'))
db = client["task_manager"]
tasks_collection = db["tasks"]
users_collection = db["users"]

def task_manager():
    if "username" not in st.session_state:
        st.warning("Please login to access this page")
        return

    tab1, tab2 = st.tabs(["Today's Tasks", "Task History"])

    # Tab 1: Adding Today's Tasks
    with tab1:
        st.header("Today's Tasks")
        task = st.text_area("What did you work on today?", key="add_task_textarea")
        if st.button("Add Task", disabled=task.strip()=="", key="add_task_button"):
            if task.strip()=="":
                st.error("empty task cannot be added")
            else:
                task_document = {
                    "user": st.session_state["username"],
                    "task": task,
                    "date": datetime.now()  # Save as a datetime.datetime object
                }
                tasks_collection.insert_one(task_document)
                st.success("Task added!")
                time.sleep(3)
                st.rerun()
            
        # Display today's tasks
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_tasks = tasks_collection.find({
            "user": st.session_state["username"],
            "date": {"$gte": today_start}  # Query tasks from the start of today
        })

        st.subheader("Tasks added today:")
        for task in today_tasks:
            st.write(f"- {task['task']}")

    # Tab 2: Viewing Task History with Date Range
    with tab2:
        st.header("Task History")
        st.write("Select a date range to view tasks:")
        start_date = st.date_input("Start Date", key="history_start_date")
        end_date = st.date_input("End Date", key="history_end_date", value=datetime.now().date())

        # Convert selected dates to datetime
        start_of_day = datetime.combine(start_date, datetime.min.time())
        end_of_day = datetime.combine(end_date, datetime.max.time())

        # Query tasks for the selected date range
        tasks = list(tasks_collection.find({
            "user": st.session_state["username"],
            "date": {"$gte": start_of_day, "$lt": end_of_day}
        }))

        if tasks:
            for task in tasks:
                if st.button(task["task"][:10]+".....", key=f"history_task_button_{task['_id']}"):
                    st.text_area("Task Details", value=task["task"], key=f"history_task_textarea_{task['_id']}", disabled=True)
        else:
            st.write("No tasks found for this date range.")

# def send_end_of_day_notification():
#     users = users_collection.find({})
#     for user in users:
#         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         tasks = list(tasks_collection.find({
#             "user": user["username"],
#             "date": {"$gte": today_start}
#         }))

#         if not tasks:
#             send_email_notification(user["email"], "You have not updated your tasks for today!")
