from math import log
from operator import is_
import streamlit as st
#from google.oauth2 import id_token
#from google_auth_oauthlib.flow import Flow


def login():
    st.title("Login Page")

    if not st.user.is_logged_in:
        if st.button("Login in with google"):
            st.login("google")
            if st.user.is_logged_in:
                st.success("Logged in successfully!")
                st.rerun()
    else:
        st.success("You are already logged in as " + st.user.name)
        if st.button("Logout"):
            st.logout()
            #st.rerun()       
        


def logout():
    st.logout()
    st.success("Logged out successfully!")
    #st.rerun()
    
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "course_admin_app.py", title="Dashboard", icon=":material/dashboard:", default=True
)
if st.user.is_logged_in:
    pg = st.navigation(
        {
            "Login": [logout_page], 
            "Dashboard": [dashboard]
        }
    )
else:
    pg = st.navigation(
        {
            "Login": [login_page]
        }
    )
    
pg.run()

