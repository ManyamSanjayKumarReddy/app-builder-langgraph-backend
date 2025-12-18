import streamlit as st
import pandas as pd

# Function to display the form and table
def main():
    st.title("Streamlit Form and Table Display")

    # Initialize session state for data if it doesn't exist
    if 'data' not in st.session_state:
        st.session_state.data = []

    # Form for user input
    with st.form(key='user_input_form'):
        name = st.text_input("Enter your name:")
        age = st.number_input("Enter your age:", min_value=0)
        country_code = st.selectbox("Select your country code:", options=["+91", "+1", "+44", "+81"])
        status = st.selectbox("Select your status:", options=["Married", "Single"])
        submit_button = st.form_submit_button(label='Submit')

        # Process the form submission
        if submit_button:
            st.session_state.data.append({'Name': name, 'Age': age, 'Country Code': country_code, 'Status': status})
            st.success(f'Added {name}, Age: {age}, Country Code: {country_code}, Status: {status}')

    # Display the data in a table
    if st.session_state.data:
        df = pd.DataFrame(st.session_state.data)
        st.table(df)

if __name__ == '__main__':
    main()