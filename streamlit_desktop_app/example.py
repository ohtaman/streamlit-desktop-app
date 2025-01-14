"""Example Streamlit application demonstrating desktop app capabilities.

This example showcases various Streamlit features and how they work in a desktop window.
It serves as both a demonstration and a template for creating your own desktop apps.

Usage:
    from streamlit_desktop_app import start_desktop_app
    start_desktop_app('path/to/this/example.py')
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Desktop App Demo",
    page_icon="🖥️",
    layout="wide"
)

# Main title and description
st.title("Streamlit Desktop App Example")
st.markdown("""
This example demonstrates how to create interactive desktop applications using Streamlit.
The app showcases various Streamlit components and features:
- Basic text and markdown rendering
- Interactive widgets
- Data display capabilities
- Layout options
""")

# Sidebar with configuration options
with st.sidebar:
    st.header("Settings")
    theme = st.selectbox(
        "Choose theme",
        ["Light", "Dark"],
        help="Select the app's color theme"
    )
    show_data = st.checkbox("Show sample data", True)

# Interactive elements
col1, col2 = st.columns(2)

with col1:
    st.subheader("Interactive Components")
    name = st.text_input("Enter your name", "Guest")
    age = st.slider("Select your age", 0, 100, 25)
    if st.button("Say Hello"):
        st.success(f"Hello {name}! You are {age} years old.")

with col2:
    st.subheader("Data Visualization")
    if show_data:
        import pandas as pd
        import numpy as np
        
        # Create sample data
        data = pd.DataFrame({
            'x': range(10),
            'y': np.random.randn(10)
        })
        
        # Display as chart
        st.line_chart(data.set_index('x'))
        
        # Display as table
        st.dataframe(data)

# Footer
st.markdown("---")
st.markdown("""
### About This Example
This example demonstrates how to create a rich desktop application using Streamlit.
It shows various UI components, layouts, and interactive features that you can use
in your own applications.

For more information, visit the [Streamlit documentation](https://docs.streamlit.io).
""")
