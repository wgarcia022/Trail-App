import streamlit as st

# Set the page configuration
st.set_page_config(
    page_title="EcoTrail App",
    page_icon="🌿",
    layout="wide"
)

# Main page content
st.title("🌍 Welcome to the EcoTrail App")
st.markdown(
    """
**EcoTrail App** is your all-in-one solution for exploring trails, submitting reports about environmental issues, and tracking eco-friendly actions. 
    
Use the sidebar to navigate between the following features:  
1. **Virtual Trails**: Explore AI-generated trail overviews with stops and trail information.  
2. **Report Submission**: Submit trail issue reports, including photos, and download them as professional PDFs.  
3. **Eco Actions Tracker**: Log your eco-friendly actions and earn badges by protecting the environment.  


----



### How to Navigate
- Click on the **pages** in the sidebar (on the left) to start exploring each feature.
- Each feature is designed to give you an interactive and educational experience. Engage and enjoy!
    """
)

# Footer
st.markdown("---")
st.markdown (
    """
#### About EcoTrail App  
Built with 💚 by Coral & the help of ChatGPT. This app uses AI to educate, engage, and empower users to preserve our trails while staying eco-friendly.
"""



)