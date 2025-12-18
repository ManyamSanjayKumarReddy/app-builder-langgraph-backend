import streamlit as st

# Define a function for the login form
def login_form():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.success("Login successful!")
            # Redirect to the main application logic here
            st.write("Welcome to the main application!")
        else:
            st.error("Invalid username or password")

if __name__ == '__main__':
    login_form()