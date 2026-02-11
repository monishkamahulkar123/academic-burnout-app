import streamlit as st

GOOGLE_CALENDAR_ENABLED = False

def initialize_calendar():
    if GOOGLE_CALENDAR_ENABLED:
        pass
    return None

def create_calendar_event(task_title, deadline):
    if GOOGLE_CALENDAR_ENABLED:
        event_id = f"mock_event_{task_title}_{deadline}"
        return event_id
    return None

def update_calendar_event(event_id, task_title, deadline):
    if GOOGLE_CALENDAR_ENABLED:
        pass
    return True

def delete_calendar_event(event_id):
    if GOOGLE_CALENDAR_ENABLED:
        pass
    return True

def sync_task_to_calendar(task_id, title, deadline):
    event_id = create_calendar_event(title, deadline)
    return event_id