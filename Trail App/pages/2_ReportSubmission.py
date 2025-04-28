import streamlit as st
import datetime
import pandas as pd
import random
import unicodedata
from openai import OpenAI
from fpdf import FPDF
from PIL import Image
import base64
import io

# Initialize OpenAI client
api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=api_key)


# Function to clean text for PDF
def clean_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

# Function to load trail locations from CSV
@st.cache_data
def load_locations():
    df = pd.read_csv('Trail App/trail_info.csv')
    return df['location'].tolist()

# Load location list
locations = load_locations()

# Streamlit app setup
st.title("🌿 EcoTrail AI – Report Submission for Santa Clara Valley Water")
st.write("Learn about your trail, upload issue photos, and generate a formal report.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a trail issue photo (JPEG, PNG)", type=["jpg", "jpeg", "png"])

# 📷 Show image preview
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image Preview", use_column_width=True)

# ⚠️ Ethical Upload Guideline
st.caption("⚠️ Please upload images related to trail issues only. Avoid uploading images with identifiable people or private property.")

# --- Location Selection ---
selected_location = st.selectbox("Where was this photo taken?", locations)

# --- Optional User Comment ---
user_input = st.text_input("Additional Comments (optional)", 
                            help="Provide more context if the AI might misunderstand your image.")

# --- Consent Checkbox ---
consent = st.checkbox("📄 Consent to Share", 
                      help="By submitting, you agree to allow your report and uploaded image to be shared with Santa Clara Valley Water officials.")
# --- Ethics Disclaimer ---
st.markdown(
    "<small>📢 <i>Note: This report is AI-assisted and should be reviewed by Santa Clara Valley Water officials for accuracy.</i></small>",
    unsafe_allow_html=True
)

# --- Submit Button ---
if st.button("Submit Report"):
    if not uploaded_file:
        st.error("Please upload an image before submitting.")
    elif not consent:
        st.error("You must agree to the Consent to Share before submitting.")
    else:
        with st.spinner('Generating your report...'):
            try:
                # Step 1: Process uploaded image into base64 URL-style
                image = Image.open(uploaded_file)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()

                # Create a data URL
                image_data_url = f"data:image/jpeg;base64,{img_base64}"

                # Step 2: Send to OpenAI with detailed prompt
                prompt = f"""
                Describe the trail issue shown in the uploaded photo.
                Location: {selected_location}
                Include:
                - What the problem is
                - 2–3 possible solutions
                - What potential dangers could occur if this issue is not addressed.
                User Additional Comments: {user_input}.
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": image_data_url}}
                            ]
                        }
                    ],
                    max_tokens=500
                )
                description = response.choices[0].message.content

                # Clean any Unicode characters not supported by latin-1
                description = clean_text(description)
                user_input = clean_text(user_input)

                # Generate PDF Report
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Title
                pdf.cell(0, 10, "Santa Clara Valley Water Report", ln=True, align="C")
                pdf.ln(10)

                # Date and Location
                pdf.multi_cell(0, 10, f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}")
                pdf.multi_cell(0, 10, f"Location: {selected_location}")
                pdf.ln(5)

                # Description
                pdf.multi_cell(0, 10, "Trail Issue, Solutions, and Potential Dangers:")
                pdf.multi_cell(0, 10, description)

                # Optional User Comment
                if user_input:
                    pdf.ln(5)
                    pdf.multi_cell(0, 10, f"Additional User Comments: {user_input}")

                # Footer divider line
                pdf.set_y(-30)
                pdf.set_draw_color(169, 169, 169)  # Light gray
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())

                # Footer text
                pdf.set_y(-20)
                pdf.set_font("Arial", size=8)
                pdf.cell(0, 10, "Generated by EcoTrail AI - Empowering Trail Preservation", align="C")

                # Save PDF to bytes
                pdf_output = io.BytesIO()
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                pdf_output.write(pdf_bytes)
                pdf_output.seek(0)

                # Generate downloadable filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Santa_Clara_Water_Report_{timestamp}.pdf"

                # 📄 Offer download
                st.success("Report generated successfully!")
                st.download_button(
                    label="📄 Download Your Report",
                    data=pdf_output,
                    file_name=filename,
                    mime='application/pdf'
                )

                # 📄 Display PDF preview inside the app
                base64_pdf = base64.b64encode(pdf_output.getvalue()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Failed to generate report. Error: {str(e)}")
                st.stop()
