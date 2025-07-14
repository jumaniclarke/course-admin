import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

def logout():
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.rerun()
    
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "course_admin_app.py", title="Dashboard", icon=":material/dashboard:", default=True
)
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Dashboard": [dashboard],
            "Logout": [logout_page]   
        }
    )
else:
    pg = st.navigation(
        {
            "Login": [login_page]
        }
    )
    
pg.run()