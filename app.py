import streamlit as st
from datetime import datetime, timedelta
import calendar as cal_module

from auth import register_user, login_user, logout_user, request_password_reset, reset_password
from tasks import (
    add_task, get_user_tasks, delete_task, update_task,
    detect_deadline_collisions, get_all_user_group_tasks, get_tasks_needing_reminder,
    mark_task_completed  # ADD THIS
)
from groups import (
    create_group, get_user_groups, join_group, get_all_groups,
    add_group_task, get_group_tasks, update_group_task_status,
    delete_group_task, get_group_members, join_group_by_code,
    is_group_head, update_group_task, get_group_analytics
)
from burnout import calculate_burnout_risk, get_burnout_recommendations
from calendar_sync import sync_task_to_calendar
from utils import (
    apply_custom_css, show_logo, create_progress_bar,
    create_task_completion_chart, create_priority_distribution_chart,
    create_workload_timeline, export_tasks_to_excel, export_report_to_pdf,
    show_notification, create_calendar_view
)

st.set_page_config(
    page_title="Academic Burnout Detector",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_css()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'show_reminders' not in st.session_state:
    st.session_state.show_reminders = True

def navigate_to(page):
    st.session_state.page = page

def check_and_show_reminders():
    """Check for upcoming deadlines and show reminders"""
    if not st.session_state.show_reminders:
        return
    
    reminders = get_tasks_needing_reminder(st.session_state.user_id)
    
    if reminders:
        for task in reminders:
            days_left = (task['deadline'] - datetime.now().date()).days
            if days_left == 0:
                show_notification(f"⚠️ URGENT: '{task['title']}' is due TODAY!", "🚨")
            elif days_left == 1:
                show_notification(f"⏰ Reminder: '{task['title']}' is due TOMORROW!", "📅")
            elif days_left <= 3:
                show_notification(f"📌 Upcoming: '{task['title']}' is due in {days_left} days", "🔔")

def welcome_page():
    show_logo()
    
    st.markdown("""
    <div style='background: white; padding: 40px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); margin: 20px 0;'>
        <h2 style='color: #1e3a8a; text-align: center; margin-bottom: 30px;'>Welcome to Academic Burnout Detector</h2>
        <p style='font-size: 16px; color: #64748b; text-align: center; line-height: 1.8;'>
            Your intelligent companion for managing academic workload, preventing burnout, and staying organized.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 8px 16px rgba(102,126,234,0.3);'>
            <h3 style='color: white; border: none; padding: 0;'>📋 Task Management</h3>
            <p>Organize assignments, projects, and deadlines efficiently</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 8px 16px rgba(240,147,251,0.3);'>
            <h3 style='color: white; border: none; padding: 0;'>📊 Analytics</h3>
            <p>Track workload, burnout risk, and productivity trends</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 8px 16px rgba(79,172,254,0.3);'>
            <h3 style='color: white; border: none; padding: 0;'>👥 Collaboration</h3>
            <p>Work together on group projects seamlessly</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔐 Login", use_container_width=True, key="welcome_login"):
            navigate_to('login')
            st.rerun()
    
    with col2:
        if st.button("📝 Register", use_container_width=True, key="welcome_register"):
            navigate_to('register')
            st.rerun()
    
    with col3:
        if st.button("🔑 Reset Password", use_container_width=True, key="welcome_reset"):
            navigate_to('reset_password')
            st.rerun()

def register_page():
    show_logo()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 40px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Create Account</h2>", unsafe_allow_html=True)
        
        with st.form("register_form", clear_on_submit=True):
            username = st.text_input("👤 Username", placeholder="Enter username")
            email = st.text_input("📧 Email", placeholder="Enter email address")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Register", use_container_width=True)
            with col2:
                back = st.form_submit_button("Back", use_container_width=True)
        
        if back:
            navigate_to('welcome')
            st.rerun()
        
        if submit:
            if not username or not email or not password:
                st.error("❌ All fields are required")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                success, message = register_user(username, email, password)
                if success:
                    st.success("✅ " + message)
                    st.info("➡️ Redirecting to login...")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error("❌ " + message)
        
        st.markdown("</div>", unsafe_allow_html=True)

def login_page():
    show_logo()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 40px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Login</h2>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col2:
                back = st.form_submit_button("Back", use_container_width=True)
        
        if back:
            navigate_to('welcome')
            st.rerun()
        
        if submit:
            if not username or not password:
                st.error("❌ Username and password are required")
            else:
                success, user = login_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user['user_id']
                    st.session_state.username = user['username']
                    st.session_state.email = user['email']
                    st.session_state.page = 'dashboard'
                    st.success(f"✅ Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        st.markdown("</div>", unsafe_allow_html=True)

def reset_password_page():
    show_logo()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 40px; border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>Reset Password</h2>", unsafe_allow_html=True)
        
        if 'reset_step' not in st.session_state:
            st.session_state.reset_step = 1
        
        if st.session_state.reset_step == 1:
            with st.form("request_reset_form"):
                email = st.text_input("📧 Enter your email", placeholder="your@email.com")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Send Reset Code", use_container_width=True)
                with col2:
                    back = st.form_submit_button("Back", use_container_width=True)
                
                if back:
                    navigate_to('welcome')
                    st.rerun()
                
                if submit:
                    if email:
                        success, message = request_password_reset(email)
                        if success:
                            st.success("✅ " + message)
                            st.info("📝 Copy the reset code above and use it in the next step")
                            st.session_state.reset_step = 2
                            st.rerun()
                        else:
                            st.error("❌ " + message)
        
        else:
            with st.form("reset_password_form"):
                reset_code = st.text_input("🔑 Reset Code", placeholder="Enter 8-character code")
                new_password = st.text_input("🔒 New Password", type="password", placeholder="Enter new password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm new password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Reset Password", use_container_width=True)
                with col2:
                    back = st.form_submit_button("Back", use_container_width=True)
                
                if back:
                    st.session_state.reset_step = 1
                    st.rerun()
                
                if submit:
                    if not reset_code or not new_password:
                        st.error("❌ All fields are required")
                    elif new_password != confirm_password:
                        st.error("❌ Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        success, message = reset_password(reset_code, new_password)
                        if success:
                            st.success("✅ " + message)
                            st.info("➡️ Redirecting to login...")
                            st.session_state.reset_step = 1
                            navigate_to('login')
                            st.rerun()
                        else:
                            st.error("❌ " + message)
        
        st.markdown("</div>", unsafe_allow_html=True)

def dashboard_page():
    show_logo()
    check_and_show_reminders()
    
    st.markdown(f"""
    <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h2 style='color: #1e3a8a; margin: 0; border: none;'>👋 Welcome back, {st.session_state.username}!</h2>
        <p style='color: #64748b; margin-top: 10px;'>Here's your academic workload overview</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    tasks = get_user_tasks(st.session_state.user_id)
    group_tasks = get_all_user_group_tasks(st.session_state.user_id)
    groups = get_user_groups(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Individual Tasks", len(tasks), delta=None)
    with col2:
        st.metric("👥 Group Tasks", len(group_tasks), delta=None)
    with col3:
        st.metric("🔗 My Groups", len(groups), delta=None)
    with col4:
        completed_tasks = len([t for t in tasks + group_tasks if t.get('task_status') == 'Completed'])
        st.metric("✅ Completed", completed_tasks, delta=None)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Deadline Collisions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🚨 Deadline Collisions")
        collisions = detect_deadline_collisions(st.session_state.user_id)
        
        if collisions:
            for deadline, tasks_list in collisions.items():
                st.warning(f"⚠️ **{len(tasks_list)} tasks** due on **{deadline}**")
                for task in tasks_list:
                    task_type = "Group" if 'group_name' in task else "Individual"
                    st.write(f"   • [{task_type}] {task['title']} ({task['priority']} priority)")
        else:
            st.success("✅ No deadline collisions detected!")
    
    with col2:
        st.markdown("### 🔥 Burnout Risk")
        risk_level, score, total, due_week, hours = calculate_burnout_risk(st.session_state.user_id)
        
        risk_colors = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
        risk_icons = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
        
        st.markdown(f"""
        <div style='background: {risk_colors[risk_level]}; padding: 20px; border-radius: 15px; text-align: center; color: white;'>
            <h2 style='color: white; margin: 0; border: none;'>{risk_icons[risk_level]} {risk_level}</h2>
            <p style='margin: 10px 0 0 0; font-size: 18px;'>Risk Score: {score}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Tasks This Week", due_week)
        st.metric("Hours This Week", hours)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("### 🎯 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add Task", use_container_width=True):
            navigate_to('individual_tasks')
            st.rerun()
    with col2:
        if st.button("👥 Manage Groups", use_container_width=True):
            navigate_to('group_tasks')
            st.rerun()
    with col3:
        if st.button("📅 View Calendar", use_container_width=True):
            navigate_to('calendar')
            st.rerun()
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            navigate_to('reports')
            st.rerun()

# Continue in next message due to length...
def individual_tasks_page():
    show_logo()
    check_and_show_reminders()
    
    st.title("📋 Individual Task Management")
    
    # Get tasks
    all_user_tasks = get_user_tasks(st.session_state.user_id)
    
    # Separate by status
    pending_tasks = [t for t in all_user_tasks if t.get('task_status', 'Pending') != 'Completed']
    completed_tasks = [t for t in all_user_tasks if t.get('task_status') == 'Completed']
    
    # Export buttons at top
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.metric("📋 Active Tasks", len(pending_tasks))
    with col2:
        st.metric("✅ Completed", len(completed_tasks))
    with col3:
        total_hours = sum(t['estimated_hours'] for t in pending_tasks)
        st.metric("⏱️ Total Hours", total_hours)
    with col4:
        if all_user_tasks:
            excel_data = export_tasks_to_excel(all_user_tasks)
            st.download_button(
                label="📥 Export Excel",
                data=excel_data,
                file_name=f"tasks_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add New Task", "📝 Active Tasks", "✅ Completed Tasks"])
    
    with tab1:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        with st.form("add_task_form", clear_on_submit=True):
            st.subheader("Create New Task")
            title = st.text_input("📝 Task Title", placeholder="e.g., Complete Math Assignment")
            
            col1, col2 = st.columns(2)
            with col1:
                deadline = st.date_input("📅 Deadline", min_value=datetime.now().date())
            with col2:
                estimated_hours = st.number_input("⏱️ Estimated Hours", min_value=1, max_value=100, value=2)
            
            submit = st.form_submit_button("➕ Add Task", use_container_width=True)
        
        if submit:
            if not title:
                st.error("❌ Task title is required")
            else:
                task_id = add_task(st.session_state.user_id, title, deadline, estimated_hours)
                if task_id:
                    st.success(f"✅ Task '{title}' added successfully!")
                    sync_task_to_calendar(task_id, title, deadline)
                    st.rerun()
                else:
                    st.error("❌ Failed to add task")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        if not pending_tasks:
            st.info("🎉 No active tasks! All caught up!")
        else:
            st.subheader(f"Active Tasks: {len(pending_tasks)}")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High"], key="filter_active")
            with col2:
                sort_by = st.selectbox("Sort by", ["Deadline", "Priority", "Hours"], key="sort_active")
            with col3:
                view_mode = st.selectbox("View", ["Detailed", "Compact"], key="view_active")
            
            # Apply filters
            filtered_tasks = pending_tasks
            if filter_priority != "All":
                filtered_tasks = [t for t in filtered_tasks if t['priority'] == filter_priority]
            
            # Sort
            if sort_by == "Deadline":
                filtered_tasks = sorted(filtered_tasks, key=lambda x: x['deadline'])
            elif sort_by == "Priority":
                priority_order = {"High": 0, "Medium": 1, "Low": 2}
                filtered_tasks = sorted(filtered_tasks, key=lambda x: priority_order[x['priority']])
            elif sort_by == "Hours":
                filtered_tasks = sorted(filtered_tasks, key=lambda x: x['estimated_hours'], reverse=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            for task in filtered_tasks:
                priority_colors = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
                priority_icons = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                
                if view_mode == "Compact":
                    # Compact view
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{priority_icons[task['priority']]} {task['title']}**")
                    with col2:
                        st.write(f"📅 {task['deadline']}")
                    with col3:
                        st.write(f"⏱️ {task['estimated_hours']}h")
                    with col4:
                        if st.button("✅ Complete", key=f"complete_compact_{task['task_id']}", use_container_width=True):
                            from tasks import mark_task_completed
                            mark_task_completed(task['task_id'])
                            st.success(f"✅ Task '{task['title']}' marked as completed!")
                            st.rerun()
                    
                    st.markdown("---")
                
                else:
                    # Detailed view
                    with st.expander(f"{priority_icons[task['priority']]} {task['title']} - Due: {task['deadline']}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div style='background: white; padding: 15px; border-radius: 10px;'>
                                <p><strong>📅 Deadline:</strong> {task['deadline']}</p>
                                <p><strong>⏱️ Estimated Hours:</strong> {task['estimated_hours']} hours</p>
                                <p><strong>🎯 Priority:</strong> <span style='color: {priority_colors[task['priority']]}'>{task['priority']}</span></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            days_left = (task['deadline'] - datetime.now().date()).days
                            if days_left < 0:
                                st.error(f"⚠️ Overdue by {abs(days_left)} days")
                            elif days_left == 0:
                                st.warning("⏰ Due TODAY!")
                            elif days_left <= 3:
                                st.info(f"📌 {days_left} days left")
                            else:
                                st.success(f"✅ {days_left} days left")
                        
                        st.markdown("---")
                        
                        # Quick Complete Button
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Mark as Completed", key=f"complete_{task['task_id']}", use_container_width=True):
                                from tasks import mark_task_completed
                                mark_task_completed(task['task_id'])
                                st.success(f"✅ Task '{task['title']}' completed!")
                                st.rerun()
                        
                        with col2:
                            pass
                        
                        st.markdown("---")
                        st.subheader("Edit Task")
                        
                        with st.form(f"edit_form_{task['task_id']}", clear_on_submit=False):
                            new_title = st.text_input("Title", value=task['title'], key=f"title_{task['task_id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                new_deadline = st.date_input("Deadline", value=task['deadline'], key=f"deadline_{task['task_id']}")
                            with col2:
                                new_hours = st.number_input("Hours", value=task['estimated_hours'], min_value=1, key=f"hours_{task['task_id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                update_btn = st.form_submit_button("💾 Update", use_container_width=True)
                            with col2:
                                delete_btn = st.form_submit_button("🗑️ Delete", use_container_width=True)
                        
                        if update_btn:
                            update_task(task['task_id'], new_title, new_deadline, new_hours)
                            st.success("✅ Task updated successfully!")
                            st.rerun()
                        
                        if delete_btn:
                            delete_task(task['task_id'])
                            st.success("✅ Task deleted successfully!")
                            st.rerun()
    
    with tab3:
        if not completed_tasks:
            st.info("📭 No completed tasks yet. Keep working!")
        else:
            st.subheader(f"Completed Tasks: {len(completed_tasks)}")
            
            # Stats
            total_completed_hours = sum(t['estimated_hours'] for t in completed_tasks)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Total Completed", len(completed_tasks))
            with col2:
                st.metric("⏱️ Hours Completed", total_completed_hours)
            with col3:
                if all_user_tasks:
                    completion_rate = len(completed_tasks) / len(all_user_tasks) * 100
                    st.metric("📊 Completion Rate", f"{completion_rate:.0f}%")
            
            st.markdown("---")
            
            # Show completed tasks
            for task in sorted(completed_tasks, key=lambda x: x['deadline'], reverse=True):
                priority_icons = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background: #f0fdf4; padding: 15px; border-radius: 10px; border-left: 4px solid #10b981;'>
                        <h4 style='margin: 0; color: #065f46;'>✅ {task['title']}</h4>
                        <p style='margin: 5px 0 0 0; color: #059669;'>
                            {priority_icons[task['priority']]} {task['priority']} Priority | 
                            📅 Completed by: {task['deadline']} | 
                            ⏱️ {task['estimated_hours']}h
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("↩️ Reopen", key=f"reopen_{task['task_id']}", use_container_width=True):
                        execute_query(
                            "UPDATE tasks SET task_status = 'Pending' WHERE task_id = %s",
                            (task['task_id'],)
                        )
                        st.success("Task reopened!")
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Delete", key=f"del_completed_{task['task_id']}", use_container_width=True):
                        delete_task(task['task_id'])
                        st.success("Task deleted!")
                        st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)

def group_tasks_page():
    show_logo()
    check_and_show_reminders()
    
    st.title("👥 Group Task Management")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🆕 Create Group", "🔗 Join Group", "📋 My Groups"])
    
    with tab1:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        st.info("💡 As the creator, you will be the **Group Head** with full management permissions")
        
        with st.form("create_group_form", clear_on_submit=True):
            st.subheader("Create New Group")
            group_name = st.text_input("👥 Group Name", placeholder="e.g., CS Project Team")
            submit = st.form_submit_button("Create Group", use_container_width=True)
        
        if submit:
            if not group_name:
                st.error("❌ Group name is required")
            else:
                group_id, invite_code = create_group(group_name, st.session_state.user_id)
                if group_id:
                    st.success(f"✅ Group '{group_name}' created successfully!")
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 20px 0;'>
                        <h3 style='color: white; margin: 0;'>📋 Invite Code</h3>
                        <h1 style='color: white; margin: 10px 0; font-size: 48px; letter-spacing: 5px; border: none;'>{invite_code}</h1>
                        <p>Share this code with your team members</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("❌ Failed to create group")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        """, unsafe_allow_html=True)
        
        st.info("💡 Enter the invite code shared by the group head")
        
        with st.form("join_group_form", clear_on_submit=True):
            st.subheader("Join with Invite Code")
            invite_code = st.text_input("🔑 Invite Code", max_chars=8, placeholder="Enter 8-character code")
            submit = st.form_submit_button("Join Group", use_container_width=True)
        
        if submit:
            if not invite_code:
                st.error("❌ Invite code is required")
            else:
                invite_code = invite_code.upper().strip()
                success, message = join_group_by_code(invite_code, st.session_state.user_id)
                if success:
                    st.success("✅ " + message)
                    st.rerun()
                else:
                    st.error("❌ " + message)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Browse All Groups")
        
        all_groups = get_all_groups()
        user_groups = get_user_groups(st.session_state.user_id)
        user_group_ids = [g['group_id'] for g in user_groups]
        
        available_groups = [g for g in all_groups if g['group_id'] not in user_group_ids]
        
        if not available_groups:
            st.info("📭 No available groups to join")
        else:
            for group in available_groups:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div style='background: white; padding: 15px; border-radius: 10px; border-left: 4px solid #3b82f6;'>
                        <h4 style='margin: 0; color: #1e3a8a;'>{group['group_name']}</h4>
                        <p style='margin: 5px 0 0 0; color: #64748b;'>Created by: {group['creator_name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Join", key=f"join_{group['group_id']}", use_container_width=True):
                        success, message = join_group(group['group_id'], st.session_state.user_id)
                        if success:
                            st.success("✅ " + message)
                            st.rerun()
                        else:
                            st.error("❌ " + message)
    
    with tab3:
        groups = get_user_groups(st.session_state.user_id)
        
        if not groups:
            st.info("📭 You haven't joined any groups yet")
        else:
            for group in groups:
                is_head = group['member_role'] == 'Head'
                role_badge = "👑 Head" if is_head else "👤 Member"
                role_color = "#f59e0b" if is_head else "#3b82f6"
                
                with st.expander(f"📁 {group['group_name']} - {role_badge}"):
                    # Group Header
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div style='background: white; padding: 15px; border-radius: 10px;'>
                            <p><strong>👤 Created by:</strong> {group['creator_name']}</p>
                            <p><strong>🎯 Your Role:</strong> <span style='color: {role_color}; font-weight: bold;'>{role_badge}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 15px; border-radius: 10px; color: white; text-align: center;'>
                            <p style='margin: 0; font-size: 12px;'>Invite Code</p>
                            <h3 style='color: white; margin: 5px 0; letter-spacing: 3px; border: none;'>{group['invite_code']}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Members
                    members = get_group_members(group['group_id'])
                    st.markdown("---")
                    st.subheader(f"👥 Members ({len(members)})")
                    
                    cols = st.columns(min(len(members), 4))
                    for idx, member in enumerate(members):
                        with cols[idx % 4]:
                            role_emoji = "👑" if member['member_role'] == 'Head' else "👤"
                            st.markdown(f"""
                            <div style='background: #f8f9fa; padding: 10px; border-radius: 8px; text-align: center; margin: 5px 0;'>
                                <div style='font-size: 24px;'>{role_emoji}</div>
                                <div style='font-weight: bold; color: #1e3a8a;'>{member['username']}</div>
                                <div style='font-size: 12px; color: #64748b;'>{member['member_role']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Group Analytics
                    st.markdown("---")
                    st.subheader("📊 Group Analytics")
                    
                    analytics = get_group_analytics(group['group_id'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Tasks", analytics['total_tasks'])
                    with col2:
                        st.metric("Completed", analytics['completed_tasks'])
                    with col3:
                        st.metric("In Progress", analytics['in_progress_tasks'])
                    with col4:
                        st.metric("Pending", analytics['pending_tasks'])
                    
                    # Progress bar
                    if analytics['total_tasks'] > 0:
                        st.markdown(create_progress_bar(analytics['completed_tasks'], analytics['total_tasks']), unsafe_allow_html=True)
                    
                    # Add Task (Head Only)
                    st.markdown("---")
                    
                    if is_head:
                        st.subheader("➕ Add Group Task (Head Only)")
                        
                        with st.form(f"add_group_task_{group['group_id']}", clear_on_submit=True):
                            task_title = st.text_input("📝 Task Title", key=f"gtask_title_{group['group_id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                task_deadline = st.date_input("📅 Deadline", min_value=datetime.now().date(), key=f"gtask_deadline_{group['group_id']}")
                            with col2:
                                task_hours = st.number_input("⏱️ Estimated Hours", min_value=1, value=2, key=f"gtask_hours_{group['group_id']}")
                            
                            member_options = {f"{m['username']} ({m['member_role']})": m['user_id'] for m in members}
                            member_options = {"Unassigned": None, **member_options}
                            
                            assigned_member = st.selectbox("👤 Assign To", list(member_options.keys()), key=f"gtask_assign_{group['group_id']}")
                            
                            add_btn = st.form_submit_button("➕ Add Task", use_container_width=True)
                        
                        if add_btn:
                            if not task_title:
                                st.error("❌ Task title is required")
                            else:
                                assigned_id = member_options[assigned_member]
                                
                                task_id = add_group_task(
                                    group['group_id'],
                                    task_title,
                                    task_deadline,
                                    task_hours,
                                    assigned_id
                                )
                                
                                if task_id:
                                    st.success("✅ Group task added successfully!")
                                    st.rerun()
                    else:
                        st.info("ℹ️ Only the Group Head can add tasks")
                    
                    # Group Tasks List
                    st.markdown("---")
                    st.subheader("📋 Group Tasks")
                    
                    group_tasks = get_group_tasks(group['group_id'])
                    
                    if not group_tasks:
                        st.info("📭 No tasks in this group yet")
                    else:
                        for idx, task in enumerate(group_tasks):
                            status_colors = {"Pending": "#64748b", "In Progress": "#f59e0b", "Completed": "#10b981"}
                            status_icons = {"Pending": "⏳", "In Progress": "🔄", "Completed": "✅"}
                            
                            st.markdown(f"""
                            <div style='background: white; padding: 20px; border-radius: 12px; margin: 10px 0; 
                                        border-left: 5px solid {status_colors[task['task_status']]}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                                <h4 style='margin: 0; color: #1e3a8a;'>{status_icons[task['task_status']]} {task['title']}</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div style='padding: 10px;'>
                                    <p><strong>📅 Due:</strong> {task['deadline']}</p>
                                    <p><strong>⏱️ Hours:</strong> {task['estimated_hours']}h</p>
                                    <p><strong>🎯 Priority:</strong> {task['priority']}</p>
                                    <p><strong>👤 Assigned to:</strong> {task['assigned_name'] if task['assigned_name'] else 'Unassigned'}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                new_status = st.selectbox(
                                    "Update Status",
                                    ["Pending", "In Progress", "Completed"],
                                    index=["Pending", "In Progress", "Completed"].index(task['task_status']),
                                    key=f"status_{task['group_task_id']}"
                                )
                                
                                if new_status != task['task_status']:
                                    if st.button(f"💾 Save", key=f"save_status_{task['group_task_id']}", use_container_width=True):
                                        update_group_task_status(task['group_task_id'], new_status)
                                        st.success("✅ Status updated!")
                                        st.rerun()
                            
                            # Head Actions
                            if is_head:
                                with st.expander("⚙️ Head Actions"):
                                    with st.form(f"edit_task_{task['group_task_id']}", clear_on_submit=False):
                                        edit_title = st.text_input("Title", value=task['title'], key=f"edit_title_{task['group_task_id']}")
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            edit_deadline = st.date_input("Deadline", value=task['deadline'], key=f"edit_deadline_{task['group_task_id']}")
                                        with col2:
                                            edit_hours = st.number_input("Hours", value=task['estimated_hours'], min_value=1, key=f"edit_hours_{task['group_task_id']}")
                                        
                                        member_options = {f"{m['username']} ({m['member_role']})": m['user_id'] for m in members}
                                        member_options = {"Unassigned": None, **member_options}
                                        
                                        current_assigned = "Unassigned"
                                        if task['assigned_to']:
                                            for key, val in member_options.items():
                                                if val == task['assigned_to']:
                                                    current_assigned = key
                                                    break
                                        
                                        edit_assigned = st.selectbox(
                                            "Reassign To",
                                            list(member_options.keys()),
                                            index=list(member_options.keys()).index(current_assigned),
                                            key=f"edit_assign_{task['group_task_id']}"
                                        )
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            update_btn = st.form_submit_button("💾 Update", use_container_width=True)
                                        with col2:
                                            delete_btn = st.form_submit_button("🗑️ Delete", use_container_width=True)
                                    
                                    if update_btn:
                                        assigned_id = member_options[edit_assigned]
                                        update_group_task(task['group_task_id'], edit_title, edit_deadline, edit_hours, assigned_id)
                                        st.success("✅ Task updated!")
                                        st.rerun()
                                    
                                    if delete_btn:
                                        delete_group_task(task['group_task_id'])
                                        st.success("✅ Task deleted!")
                                        st.rerun()
                            
                            st.markdown("<br>", unsafe_allow_html=True)

def calendar_page():
    show_logo()
    
    st.title("📅 Calendar View")
    st.markdown("---")
    
    tasks = get_user_tasks(st.session_state.user_id)
    group_tasks = get_all_user_group_tasks(st.session_state.user_id)
    all_tasks = tasks + group_tasks
    
    if not all_tasks:
        st.info("📭 No tasks to display in calendar")
        return
    
    # Calendar controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        current_year = datetime.now().year
        year = st.selectbox("Year", range(current_year - 1, current_year + 3), index=1)
    
    with col2:
        month = st.selectbox("Month", range(1, 13), index=datetime.now().month - 1, 
                            format_func=lambda x: cal_module.month_name[x])
    
    with col3:
        view_type = st.selectbox("View", ["Month", "Week", "List"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if view_type == "Month":
        # Show monthly calendar
        calendar_html = create_calendar_view(all_tasks, year, month)
        st.markdown(calendar_html, unsafe_allow_html=True)
    
    elif view_type == "Week":
        # Show weekly view
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;'>
            <h3 style='color: #1e3a8a; margin: 0;'>Week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for day_offset in range(7):
            current_day = week_start + timedelta(days=day_offset)
            day_tasks = [t for t in all_tasks if t['deadline'] == current_day]
            
            day_name = cal_module.day_name[current_day.weekday()]
            
            if day_tasks:
                bg_color = "#fee2e2" if len(day_tasks) > 2 else "#fef3c7" if len(day_tasks) > 0 else "white"
                st.markdown(f"""
                <div style='background: {bg_color}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #3b82f6;'>
                    <h4 style='margin: 0; color: #1e3a8a;'>{day_name}, {current_day.strftime('%B %d')}</h4>
                """, unsafe_allow_html=True)
                
                for task in day_tasks:
                    task_type = "Group" if 'group_name' in task else "Individual"
                    st.write(f"   • [{task_type}] {task['title']} - {task['priority']} priority")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    else:  # List view
        st.subheader("📋 All Upcoming Tasks")
        
        # Sort by deadline
        sorted_tasks = sorted(all_tasks, key=lambda x: x['deadline'])
        
        for task in sorted_tasks:
            task_type = "Group" if 'group_name' in task else "Individual"
            days_left = (task['deadline'] - datetime.now().date()).days
            
            if days_left < 0:
                urgency = "🔴 Overdue"
                bg_color = "#fee2e2"
            elif days_left == 0:
                urgency = "🟠 Due Today"
                bg_color = "#fef3c7"
            elif days_left <= 3:
                urgency = f"🟡 {days_left} days left"
                bg_color = "#fef3c7"
            else:
                urgency = f"🟢 {days_left} days left"
                bg_color = "white"
            
            st.markdown(f"""
            <div style='background: {bg_color}; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #3b82f6;'>
                <h4 style='margin: 0; color: #1e3a8a;'>{task['title']}</h4>
                <p style='margin: 5px 0;'>
                    <strong>Type:</strong> {task_type} | 
                    <strong>Due:</strong> {task['deadline']} | 
                    <strong>Priority:</strong> {task['priority']} | 
                    <strong>Hours:</strong> {task['estimated_hours']}h
                </p>
                <p style='margin: 0; font-weight: bold;'>{urgency}</p>
            </div>
            """, unsafe_allow_html=True)

def reports_page():
    show_logo()
    
    st.title("📊 Reports & Analytics")
    st.markdown("---")
    
    tasks = get_user_tasks(st.session_state.user_id)
    group_tasks = get_all_user_group_tasks(st.session_state.user_id)
    all_tasks = tasks + group_tasks
    
    # Export buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if all_tasks:
            excel_data = export_tasks_to_excel(all_tasks)
            st.download_button(
                label="📥 Export Excel",
                data=excel_data,
                file_name=f"all_tasks_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    with col3:
        if all_tasks:
            burnout_data = calculate_burnout_risk(st.session_state.user_id)
            pdf_data = export_report_to_pdf(st.session_state.username, tasks, group_tasks, burnout_data)
            st.download_button(
                label="📄 Export PDF",
                data=pdf_data,
                file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not all_tasks:
        st.info("📭 No data available for analytics")
        return
    
    # Summary metrics
    st.subheader("📈 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(all_tasks))
    with col2:
        completed = len([t for t in all_tasks if t.get('task_status') == 'Completed'])
        st.metric("Completed", completed)
    with col3:
        total_hours = sum(t['estimated_hours'] for t in all_tasks)
        st.metric("Total Hours", total_hours)
    with col4:
        avg_hours = total_hours / len(all_tasks) if all_tasks else 0
        st.metric("Avg Hours/Task", f"{avg_hours:.1f}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Task Completion Status")
        fig = create_task_completion_chart(all_tasks)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Priority Distribution")
        fig = create_priority_distribution_chart(all_tasks)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("📅 Workload Timeline")
    fig = create_workload_timeline(all_tasks)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Weekly/Monthly Reports
    st.subheader("📋 Period Reports")
    
    report_type = st.radio("Select Report Period", ["This Week", "This Month", "Custom Range"], horizontal=True)
    
    today = datetime.now().date()
    
    if report_type == "This Week":
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        period_tasks = [t for t in all_tasks if week_start <= t['deadline'] <= week_end]
        st.info(f"📅 Week: {week_start} to {week_end}")
    
    elif report_type == "This Month":
        month_start = today.replace(day=1)
        next_month = month_start.replace(day=28) + timedelta(days=4)
        month_end = next_month - timedelta(days=next_month.day)
        period_tasks = [t for t in all_tasks if month_start <= t['deadline'] <= month_end]
        st.info(f"📅 Month: {month_start.strftime('%B %Y')}")
    
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=today)
        with col2:
            end_date = st.date_input("End Date", value=today + timedelta(days=30))
        
        period_tasks = [t for t in all_tasks if start_date <= t['deadline'] <= end_date]
    
    if period_tasks:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Period Tasks", len(period_tasks))
        with col2:
            period_hours = sum(t['estimated_hours'] for t in period_tasks)
            st.metric("Period Hours", period_hours)
        with col3:
            completed_period = len([t for t in period_tasks if t.get('task_status') == 'Completed'])
            completion_rate = (completed_period / len(period_tasks) * 100) if period_tasks else 0
            st.metric("Completion Rate", f"{completion_rate:.0f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        for task in sorted(period_tasks, key=lambda x: x['deadline']):
            task_type = "Group" if 'group_name' in task else "Individual"
            status = task.get('task_status', 'Pending')
            status_color = {"Pending": "#64748b", "In Progress": "#f59e0b", "Completed": "#10b981"}
            
            st.markdown(f"""
            <div style='background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {status_color[status]};'>
                <h4 style='margin: 0; color: #1e3a8a;'>{task['title']}</h4>
                <p style='margin: 5px 0; color: #64748b;'>
                    {task_type} | Due: {task['deadline']} | {task['priority']} Priority | {task['estimated_hours']}h | Status: {status}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 No tasks in selected period")

def burnout_page():
    show_logo()
    
    st.title("🔥 Burnout Risk Analysis")
    st.markdown("---")
    
    risk_level, score, total_tasks, tasks_due, total_hours = calculate_burnout_risk(st.session_state.user_id)
    
    risk_colors = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
    risk_icons = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
    
    # Risk Level Banner
    st.markdown(f"""
    <div style='background: {risk_colors[risk_level]}; padding: 40px; border-radius: 15px; text-align: center; color: white; margin-bottom: 30px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 48px; border: none;'>{risk_icons[risk_level]} {risk_level} Risk</h1>
        <h3 style='color: white; margin: 10px 0 0 0; border: none;'>Burnout Risk Score: {score}/10</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Total Tasks", total_tasks)
    with col2:
        st.metric("📅 Due This Week", tasks_due)
    with col3:
        st.metric("⏱️ Hours This Week", total_hours)
    
    st.markdown("---")
    
    # Recommendations
    st.subheader("💡 Personalized Recommendations")
    
    recommendations = get_burnout_recommendations(risk_level)
    
    for idx, rec in enumerate(recommendations, 1):
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 12px; margin: 10px 0; border-left: 4px solid #3b82f6; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <p style='margin: 0; font-size: 16px; color: #1e3a8a;'><strong>{idx}.</strong> {rec}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Task Distribution
    st.subheader("📊 Workload Distribution")
    
    tasks = get_user_tasks(st.session_state.user_id)
    group_tasks = get_all_user_group_tasks(st.session_state.user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        individual_hours = sum(t['estimated_hours'] for t in tasks)
        group_hours = sum(t['estimated_hours'] for t in group_tasks)
        
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h4 style='color: #1e3a8a;'>Individual Tasks</h4>
            <h2 style='color: #3b82f6; margin: 10px 0;'>{individual_hours} hours</h2>
            <p style='color: #64748b;'>{len(tasks)} tasks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h4 style='color: #1e3a8a;'>Group Tasks</h4>
            <h2 style='color: #8b5cf6; margin: 10px 0;'>{group_hours} hours</h2>
            <p style='color: #64748b;'>{len(group_tasks)} tasks</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # High Priority Tasks
    st.subheader("⚠️ High Priority Tasks Requiring Attention")
    
    high_priority_tasks = [t for t in tasks + group_tasks if t['priority'] == 'High']
    
    if not high_priority_tasks:
        st.success("✅ No high priority tasks currently!")
    else:
        for task in sorted(high_priority_tasks, key=lambda x: x['deadline']):
            task_type = "Group" if 'group_name' in task else "Individual"
            days_left = (task['deadline'] - datetime.now().date()).days
            
            urgency_text = "OVERDUE" if days_left < 0 else f"{days_left} days left"
            
            st.markdown(f"""
            <div style='background: #fee2e2; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #ef4444;'>
                <h4 style='margin: 0; color: #991b1b;'>🔴 {task['title']}</h4>
                <p style='margin: 5px 0; color: #7f1d1d;'>
                    [{task_type}] Due: {task['deadline']} | {task['estimated_hours']}h | {urgency_text}
                </p>
            </div>
            """, unsafe_allow_html=True)

def main():
    if not st.session_state.logged_in:
        if st.session_state.page == 'register':
            register_page()
        elif st.session_state.page == 'login':
            login_page()
        elif st.session_state.page == 'reset_password':
            reset_password_page()
        else:
            welcome_page()
    else:
        # Sidebar
        with st.sidebar:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 15px; margin-bottom: 20px;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>👤</div>
                <h3 style='color: white; margin: 0;'>{st.session_state.username}</h3>
                <p style='color: rgba(255,255,255,0.7); margin: 5px 0 0 0;'>Student</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📍 Navigation")
            
            if st.button("🏠 Dashboard", use_container_width=True):
                navigate_to('dashboard')
                st.rerun()
            if st.button("📋 Individual Tasks", use_container_width=True):
                navigate_to('individual_tasks')
                st.rerun()
            if st.button("👥 Group Tasks", use_container_width=True):
                navigate_to('group_tasks')
                st.rerun()
            if st.button("📅 Calendar", use_container_width=True):
                navigate_to('calendar')
                st.rerun()
            if st.button("📊 Reports & Analytics", use_container_width=True):
                navigate_to('reports')
                st.rerun()
            if st.button("🔥 Burnout Analysis", use_container_width=True):
                navigate_to('burnout')
                st.rerun()
            
            st.markdown("---")
            
            st.markdown("### ⚙️ Settings")
            
            st.session_state.show_reminders = st.checkbox("🔔 Show Reminders", value=st.session_state.show_reminders)
            
            st.markdown("---")
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("""
            <div style='text-align: center; color: rgba(255,255,255,0.5); font-size: 12px;'>
                <p>Academic Burnout Detector</p>
                <p>v3.0.0 | © 2024</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Main content
        if st.session_state.page == 'dashboard':
            dashboard_page()
        elif st.session_state.page == 'individual_tasks':
            individual_tasks_page()
        elif st.session_state.page == 'group_tasks':
            group_tasks_page()
        elif st.session_state.page == 'calendar':
            calendar_page()
        elif st.session_state.page == 'reports':
            reports_page()
        elif st.session_state.page == 'burnout':
            burnout_page()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()