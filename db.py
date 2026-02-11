import mysql.connector
from mysql.connector import Error
import streamlit as st

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '@Shravani123',
    'database': 'academic_burnout_db'
}

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    conn = get_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        else:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
    except Error as e:
        st.error(f"Query execution error: {e}")
        if conn:
            conn.close()
        return None

def execute_query_one(query, params=None):
    conn = get_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        st.error(f"Query execution error: {e}")
        if conn:
            conn.close()
        return None