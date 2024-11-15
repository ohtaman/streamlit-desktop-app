# app.py
import streamlit as st

st.title("Streamlit Desktop App Example")
st.write("Hello, this is a simple example running in a desktop window!")
st.write("Feel free to interact with this Streamlit app.")
if st.button("Click me!"):
    st.write("Clicked!")
