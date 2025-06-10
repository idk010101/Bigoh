import streamlit as st
import bcrypt
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime
import re

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Page configuration
st.set_page_config(
    page_title="BigOh Tech Club",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        margin: 1rem 0;
    }
    .announcement-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

# Helper functions
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_member(full_name, email, phone, student_id, year_of_study, branch, skills, password):
    try:
        # Check if email already exists
        existing_user = supabase.table('members').select('email').eq('email', email).execute()
        if existing_user.data:
            return False, "Email already registered!"
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert new member
        result = supabase.table('members').insert({
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'student_id': student_id,
            'year_of_study': year_of_study,
            'branch': branch,
            'skills': skills,
            'password_hash': password_hash
        }).execute()
        
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def login_user(email, password):
    try:
        # Check member login
        result = supabase.table('members').select('*').eq('email', email).execute()
        if result.data:
            user = result.data[0]
            if verify_password(password, user['password_hash']):
                st.session_state.logged_in = True
                st.session_state.user_id = user['id']
                st.session_state.user_name = user['full_name']
                st.session_state.is_admin = False
                return True, "Login successful!"
        
        # Check admin login
        admin_result = supabase.table('admins').select('*').eq('email', email).execute()
        if admin_result.data:
            admin = admin_result.data[0]
            if verify_password(password, admin['password_hash']):
                st.session_state.logged_in = True
                st.session_state.user_id = admin['id']
                st.session_state.user_name = "Admin"
                st.session_state.is_admin = True
                return True, "Admin login successful!"
        
        return False, "Invalid email or password!"
    except Exception as e:
        return False, f"Login failed: {str(e)}"

def get_announcements():
    try:
        result = supabase.table('announcements').select('*, members(full_name)').eq('is_active', True).order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        st.error(f"Error fetching announcements: {str(e)}")
        return []

def add_announcement(title, content):
    try:
        result = supabase.table('announcements').insert({
            'title': title,
            'content': content,
            'author_id': st.session_state.user_id if not st.session_state.is_admin else None
        }).execute()
        return True, "Announcement added successfully!"
    except Exception as e:
        return False, f"Failed to add announcement: {str(e)}"

# Main header
st.markdown("""
<div class="main-header">
    <h1>⚡ BigOh Tech Club</h1>
    <p>Empowering the next generation of tech innovators</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("### Navigation")
    
    if not st.session_state.logged_in:
        page = st.radio("Choose a page:", ["Home", "Register", "Login"])
    else:
        welcome_msg = f"Welcome, {st.session_state.user_name}!"
        st.success(welcome_msg)
        
        if st.session_state.is_admin:
            page = st.radio("Choose a page:", ["Announcements", "Add Announcement", "Member List"])
        else:
            page = st.radio("Choose a page:", ["Announcements", "Profile"])
        
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Main content area
if not st.session_state.logged_in:
    if page == "Home":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## Welcome to BigOh Tech Club! 🚀
            
            **About Us:**
            BigOh is a vibrant community of tech enthusiasts, programmers, and innovators. We focus on:
            
            - 💻 **Programming & Development**
            - 🤖 **AI & Machine Learning**
            - 🌐 **Web Development**
            - 📱 **Mobile App Development**
            - 🔒 **Cybersecurity**
            - 🎯 **Competitive Programming**
            
            **What We Offer:**
            - Regular workshops and seminars
            - Coding competitions and hackathons
            - Project collaboration opportunities
            - Industry expert sessions
            - Networking events
            
            **Join us today** and be part of the tech revolution! 🌟
            """)
            
            st.info("👈 Use the sidebar to register as a new member or login to your account.")

    elif page == "Register":
        st.markdown("## 📝 Member Registration")
        
        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name *", placeholder="Enter your full name")
                email = st.text_input("Email *", placeholder="your.email@example.com")
                phone = st.text_input("Phone Number", placeholder="+91 9876543210")
                student_id = st.text_input("Student ID", placeholder="Your student ID")
            
            with col2:
                year_of_study = st.selectbox("Year of Study", [1, 2, 3, 4, 5])
                branch = st.selectbox("Branch", [
                    "Computer Science", "Information Technology", "Electronics", 
                    "Mechanical", "Civil", "Electrical", "Other"
                ])
                skills = st.text_area("Skills & Interests", placeholder="Programming languages, frameworks, interests...")
                password = st.text_input("Password *", type="password", placeholder="Minimum 6 characters")
            
            submitted = st.form_submit_button("Register", use_container_width=True)
            
            if submitted:
                if not all([full_name, email, password]):
                    st.error("Please fill all required fields marked with *")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif not validate_email(email):
                    st.error("Please enter a valid email address")
                else:
                    success, message = register_member(
                        full_name, email, phone, student_id, 
                        year_of_study, branch, skills, password
                    )
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials!")
                    else:
                        st.error(message)

    elif page == "Login":
        st.markdown("## 🔐 Member Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your.email@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    if not all([email, password]):
                        st.error("Please enter both email and password")
                    else:
                        success, message = login_user(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            st.markdown("---")
            st.info("**Demo Admin Login:**\nEmail: admin@bigoh.com\nPassword: admin123")

else:
    # Logged in pages
    if page == "Announcements":
        st.markdown("## 📢 Club Announcements")
        
        announcements = get_announcements()
        
        if announcements:
            for announcement in announcements:
                with st.container():
                    st.markdown(f"""
                    <div class="announcement-card">
                        <h3>{announcement['title']}</h3>
                        <p>{announcement['content']}</p>
                        <small>
                            Posted by: {announcement.get('members', {}).get('full_name', 'Admin') if announcement.get('members') else 'Admin'} | 
                            {datetime.fromisoformat(announcement['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No announcements available at the moment.")
    
    elif page == "Add Announcement" and st.session_state.is_admin:
        st.markdown("## ➕ Add New Announcement")
        
        with st.form("announcement_form"):
            title = st.text_input("Announcement Title *", placeholder="Enter announcement title")
            content = st.text_area("Content *", placeholder="Enter announcement content...", height=200)
            submitted = st.form_submit_button("Post Announcement", use_container_width=True)
            
            if submitted:
                if not all([title, content]):
                    st.error("Please fill all required fields")
                else:
                    success, message = add_announcement(title, content)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    elif page == "Member List" and st.session_state.is_admin:
        st.markdown("## 👥 Registered Members")
        
        try:
            members = supabase.table('members').select('*').eq('is_active', True).order('created_at', desc=True).execute()
            
            if members.data:
                st.markdown(f"**Total Members: {len(members.data)}**")
                
                for member in members.data:
                    with st.expander(f"{member['full_name']} - {member['email']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Phone:** {member.get('phone', 'N/A')}")
                            st.write(f"**Student ID:** {member.get('student_id', 'N/A')}")
                            st.write(f"**Year:** {member.get('year_of_study', 'N/A')}")
                        with col2:
                            st.write(f"**Branch:** {member.get('branch', 'N/A')}")
                            st.write(f"**Joined:** {datetime.fromisoformat(member['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y')}")
                        
                        if member.get('skills'):
                            st.write(f"**Skills:** {member['skills']}")
            else:
                st.info("No members registered yet.")
        except Exception as e:
            st.error(f"Error fetching members: {str(e)}")
    
    elif page == "Profile" and not st.session_state.is_admin:
        st.markdown("## 👤 My Profile")
        
        try:
            user_data = supabase.table('members').select('*').eq('id', st.session_state.user_id).execute()
            
            if user_data.data:
                user = user_data.data[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Personal Information")
                    st.write(f"**Name:** {user['full_name']}")
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Phone:** {user.get('phone', 'Not provided')}")
                    st.write(f"**Student ID:** {user.get('student_id', 'Not provided')}")
                
                with col2:
                    st.markdown("### Academic Information")
                    st.write(f"**Year of Study:** {user.get('year_of_study', 'Not provided')}")
                    st.write(f"**Branch:** {user.get('branch', 'Not provided')}")
                    st.write(f"**Member Since:** {datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y')}")
                
                if user.get('skills'):
                    st.markdown("### Skills & Interests")
                    st.write(user['skills'])
                
        except Exception as e:
            st.error(f"Error fetching profile: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>© 2024 BigOh Tech Club | Empowering Innovation | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
