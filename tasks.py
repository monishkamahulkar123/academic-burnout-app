import streamlit as st
from db import execute_query, execute_query_one
from datetime import datetime, timedelta

def calculate_priority(estimated_hours):
    if estimated_hours <= 2:
        return "Low"
    elif estimated_hours <= 4:
        return "Medium"
    else:
        return "High"

def add_task(user_id, title, deadline, estimated_hours):
    priority = calculate_priority(estimated_hours)
    task_id = execute_query(
        "INSERT INTO tasks (user_id, title, deadline, estimated_hours, priority) VALUES (%s, %s, %s, %s, %s)",
        (user_id, title, deadline, estimated_hours, priority)
    )
    return task_id

def get_user_tasks(user_id):
    tasks = execute_query(
        "SELECT * FROM tasks WHERE user_id = %s ORDER BY deadline ASC",
        (user_id,),
        fetch=True
    )
    return tasks or []

def delete_task(task_id):
    execute_query("DELETE FROM tasks WHERE task_id = %s", (task_id,))

def update_task(task_id, title, deadline, estimated_hours):
    priority = calculate_priority(estimated_hours)
    execute_query(
        "UPDATE tasks SET title = %s, deadline = %s, estimated_hours = %s, priority = %s WHERE task_id = %s",
        (title, deadline, estimated_hours, priority, task_id)
    )

def detect_deadline_collisions(user_id):
    tasks = get_user_tasks(user_id)
    group_tasks = get_all_user_group_tasks(user_id)
    
    all_tasks = tasks + group_tasks
    deadline_dict = {}
    
    for task in all_tasks:
        deadline = task['deadline']
        if deadline not in deadline_dict:
            deadline_dict[deadline] = []
        deadline_dict[deadline].append(task)
    
    collisions = {k: v for k, v in deadline_dict.items() if len(v) > 1}
    return collisions

def get_all_user_group_tasks(user_id):
    query = """
        SELECT gt.*, sg.group_name 
        FROM group_tasks gt
        JOIN group_members gm ON gt.group_id = gm.group_id
        JOIN student_groups sg ON gt.group_id = sg.group_id
        WHERE gm.user_id = %s
        ORDER BY gt.deadline ASC
    """
    tasks = execute_query(query, (user_id,), fetch=True)
    return tasks or []

def get_tasks_needing_reminder(user_id):
    """Get tasks that need reminders (within 3 days and not yet reminded)"""
    today = datetime.now().date()
    reminder_date = today + timedelta(days=3)
    
    # Individual tasks
    individual_query = """
        SELECT task_id, title, deadline, priority, estimated_hours
        FROM tasks 
        WHERE user_id = %s 
        AND deadline BETWEEN %s AND %s
        AND (reminder_sent = FALSE OR reminder_sent IS NULL)
        ORDER BY deadline ASC
    """
    individual_tasks = execute_query(individual_query, (user_id, today, reminder_date), fetch=True) or []
    
    # Group tasks
    group_query = """
        SELECT gt.group_task_id as task_id, gt.title, gt.deadline, gt.priority, gt.estimated_hours, sg.group_name
        FROM group_tasks gt
        JOIN group_members gm ON gt.group_id = gm.group_id
        JOIN student_groups sg ON gt.group_id = sg.group_id
        WHERE gm.user_id = %s 
        AND gt.deadline BETWEEN %s AND %s
        AND (gt.reminder_sent = FALSE OR gt.reminder_sent IS NULL)
        ORDER BY gt.deadline ASC
    """
    group_tasks = execute_query(group_query, (user_id, today, reminder_date), fetch=True) or []
    
    return individual_tasks + group_tasks

def mark_reminder_sent(task_id, is_group_task=False):
    """Mark a task as having reminder sent"""
    if is_group_task:
        execute_query("UPDATE group_tasks SET reminder_sent = TRUE WHERE group_task_id = %s", (task_id,))
    else:
        execute_query("UPDATE tasks SET reminder_sent = TRUE WHERE task_id = %s", (task_id,))

def mark_task_completed(task_id):
    """Mark an individual task as completed"""
    execute_query(
        "UPDATE tasks SET task_status = 'Completed' WHERE task_id = %s",
        (task_id,)
    )

def get_completed_tasks(user_id):
    """Get all completed tasks for a user"""
    tasks = execute_query(
        "SELECT * FROM tasks WHERE user_id = %s AND task_status = 'Completed' ORDER BY deadline DESC",
        (user_id,),
        fetch=True
    )
    return tasks or []