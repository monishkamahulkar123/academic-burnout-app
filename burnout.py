from datetime import datetime, timedelta
from tasks import get_user_tasks, get_all_user_group_tasks

def calculate_burnout_risk(user_id):
    individual_tasks = get_user_tasks(user_id)
    group_tasks = get_all_user_group_tasks(user_id)
    
    all_tasks = individual_tasks + group_tasks
    
    total_tasks = len(all_tasks)
    
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    tasks_next_week = [t for t in all_tasks if today <= t['deadline'] <= next_week]
    tasks_due_count = len(tasks_next_week)
    
    total_hours = sum(t['estimated_hours'] for t in tasks_next_week)
    
    risk_score = 0
    
    if total_tasks >= 10:
        risk_score += 2
    elif total_tasks >= 5:
        risk_score += 1
    
    if tasks_due_count >= 5:
        risk_score += 2
    elif tasks_due_count >= 3:
        risk_score += 1
    
    if total_hours >= 20:
        risk_score += 3
    elif total_hours >= 10:
        risk_score += 2
    elif total_hours >= 5:
        risk_score += 1
    
    if risk_score >= 5:
        return "High", risk_score, total_tasks, tasks_due_count, total_hours
    elif risk_score >= 3:
        return "Medium", risk_score, total_tasks, tasks_due_count, total_hours
    else:
        return "Low", risk_score, total_tasks, tasks_due_count, total_hours

def get_burnout_recommendations(risk_level):
    if risk_level == "High":
        return [
            "⚠️ You have a high burnout risk. Consider postponing non-urgent tasks.",
            "🧘 Take regular breaks every 50 minutes.",
            "👥 Delegate group tasks if possible.",
            "💤 Ensure you get 7-8 hours of sleep.",
            "🆘 Reach out to professors for deadline extensions if needed."
        ]
    elif risk_level == "Medium":
        return [
            "⚡ You have a moderate workload. Stay organized.",
            "📅 Prioritize tasks by deadline and difficulty.",
            "🔄 Break large tasks into smaller chunks.",
            "🚶 Include physical activity in your daily routine."
        ]
    else:
        return [
            "✅ Your workload is manageable.",
            "📚 Keep up the good work!",
            "🎯 Stay consistent with your schedule."
        ]