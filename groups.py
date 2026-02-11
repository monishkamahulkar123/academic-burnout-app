import streamlit as st
import random
import string
from db import execute_query, execute_query_one
from tasks import calculate_priority

def generate_invite_code():
    """Generate a random 8-character invite code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_group(group_name, created_by):
    invite_code = generate_invite_code()
    
    # Ensure unique invite code
    while execute_query_one("SELECT group_id FROM student_groups WHERE invite_code = %s", (invite_code,)):
        invite_code = generate_invite_code()
    
    group_id = execute_query(
        "INSERT INTO student_groups (group_name, created_by, invite_code) VALUES (%s, %s, %s)",
        (group_name, created_by, invite_code)
    )
    
    if group_id:
        # Add creator as Group Head
        execute_query(
            "INSERT INTO group_members (group_id, user_id, member_role) VALUES (%s, %s, %s)",
            (group_id, created_by, 'Head')
        )
    
    return group_id, invite_code

def get_user_groups(user_id):
    query = """
        SELECT sg.*, u.username as creator_name, gm.member_role
        FROM student_groups sg
        JOIN group_members gm ON sg.group_id = gm.group_id
        JOIN users u ON sg.created_by = u.user_id
        WHERE gm.user_id = %s
        ORDER BY sg.created_at DESC
    """
    groups = execute_query(query, (user_id,), fetch=True)
    return groups or []

def join_group_by_code(invite_code, user_id):
    # Find group by invite code
    group = execute_query_one(
        "SELECT group_id, group_name FROM student_groups WHERE invite_code = %s",
        (invite_code,)
    )
    
    if not group:
        return False, "Invalid invite code"
    
    # Check if already a member
    existing = execute_query_one(
        "SELECT membership_id FROM group_members WHERE group_id = %s AND user_id = %s",
        (group['group_id'], user_id)
    )
    
    if existing:
        return False, "Already a member of this group"
    
    # Add as member
    membership_id = execute_query(
        "INSERT INTO group_members (group_id, user_id, member_role) VALUES (%s, %s, %s)",
        (group['group_id'], user_id, 'Member')
    )
    
    if membership_id:
        return True, f"Successfully joined '{group['group_name']}'"
    return False, "Failed to join group"

def join_group(group_id, user_id):
    existing = execute_query_one(
        "SELECT membership_id FROM group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id)
    )
    
    if existing:
        return False, "Already a member"
    
    membership_id = execute_query(
        "INSERT INTO group_members (group_id, user_id, member_role) VALUES (%s, %s, %s)",
        (group_id, user_id, 'Member')
    )
    
    if membership_id:
        return True, "Joined successfully"
    return False, "Failed to join"

def get_all_groups():
    groups = execute_query(
        "SELECT sg.*, u.username as creator_name FROM student_groups sg JOIN users u ON sg.created_by = u.user_id ORDER BY sg.created_at DESC",
        fetch=True
    )
    return groups or []

def add_group_task(group_id, title, deadline, estimated_hours, assigned_to=None):
    priority = calculate_priority(estimated_hours)
    task_id = execute_query(
        "INSERT INTO group_tasks (group_id, title, deadline, estimated_hours, priority, assigned_to) VALUES (%s, %s, %s, %s, %s, %s)",
        (group_id, title, deadline, estimated_hours, priority, assigned_to)
    )
    return task_id

def get_group_tasks(group_id):
    query = """
        SELECT gt.*, u.username as assigned_name
        FROM group_tasks gt
        LEFT JOIN users u ON gt.assigned_to = u.user_id
        WHERE gt.group_id = %s
        ORDER BY gt.deadline ASC
    """
    tasks = execute_query(query, (group_id,), fetch=True)
    return tasks or []

def update_group_task_status(task_id, status):
    execute_query(
        "UPDATE group_tasks SET task_status = %s WHERE group_task_id = %s",
        (status, task_id)
    )

def delete_group_task(task_id):
    execute_query("DELETE FROM group_tasks WHERE group_task_id = %s", (task_id,))

def get_group_members(group_id):
    query = """
        SELECT u.user_id, u.username, u.email, gm.member_role, gm.joined_at
        FROM users u
        JOIN group_members gm ON u.user_id = gm.user_id
        WHERE gm.group_id = %s
        ORDER BY 
            CASE gm.member_role 
                WHEN 'Head' THEN 1 
                ELSE 2 
            END,
            gm.joined_at ASC
    """
    members = execute_query(query, (group_id,), fetch=True)
    return members or []

def is_group_head(group_id, user_id):
    member = execute_query_one(
        "SELECT member_role FROM group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id)
    )
    return member and member['member_role'] == 'Head'

def get_group_by_id(group_id):
    return execute_query_one(
        "SELECT * FROM student_groups WHERE group_id = %s",
        (group_id,)
    )

def assign_task_to_member(task_id, user_id):
    execute_query(
        "UPDATE group_tasks SET assigned_to = %s WHERE group_task_id = %s",
        (user_id, task_id)
    )

def update_group_task(task_id, title, deadline, estimated_hours, assigned_to):
    priority = calculate_priority(estimated_hours)
    execute_query(
        "UPDATE group_tasks SET title = %s, deadline = %s, estimated_hours = %s, priority = %s, assigned_to = %s WHERE group_task_id = %s",
        (title, deadline, estimated_hours, priority, assigned_to, task_id)
    )

def get_group_analytics(group_id):
    """Get analytics for a specific group"""
    tasks = get_group_tasks(group_id)
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['task_status'] == 'Completed'])
    in_progress_tasks = len([t for t in tasks if t['task_status'] == 'In Progress'])
    pending_tasks = len([t for t in tasks if t['task_status'] == 'Pending'])
    
    total_hours = sum(t['estimated_hours'] for t in tasks)
    completed_hours = sum(t['estimated_hours'] for t in tasks if t['task_status'] == 'Completed')
    
    return {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'total_hours': total_hours,
        'completed_hours': completed_hours,
        'completion_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }