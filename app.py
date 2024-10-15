from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import fitz  # PyMuPDF (alternative to pdf2image)
import google.generativeai as genai

# Set page configuration first
st.set_page_config(page_title="Cover Letter AI")

# Load environment variables
load_dotenv()

# Configure the Generative AI model with the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    """
    Generates a response using the Google Gemini Generative AI model.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Converts the uploaded PDF to an image using PyMuPDF and returns the first page as a base64-encoded JPEG.
    """
    if uploaded_file is not None:
        try:
            # Open the uploaded PDF with PyMuPDF
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            # Extract the first page as an image
            first_page = pdf_document.load_page(0)  # Load the first page
            pix = first_page.get_pixmap()  # Convert the page to an image
            
            # Convert the image to bytes
            img_byte_arr = io.BytesIO(pix.tobytes("jpeg"))
            
            # Convert the image to base64
            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr.getvalue()).decode()  # Encode to base64
                }
            ]
            return pdf_parts
        except Exception as e:
            st.error(f"Error processing the PDF file: {str(e)}")
            return None
    else:
        raise FileNotFoundError("No file uploaded")

# Custom CSS to hide Streamlit branding and buttons
hide_st_style = """
            <style>
            /* Hide Streamlit's default hamburger menu */
            #MainMenu {visibility: hidden;}
            
            /* Hide Streamlit's footer (the "Made with Streamlit" footer) */
            footer {visibility: hidden;}
            
            /* Hide Streamlit's "Deploy" button */
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

## Streamlit App

st.header("Cover Letter AI")

# File uploader to upload a PDF resume
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Button to create the cover letter
submit1 = st.button("Create Cover Letter")

# Input prompt for generating the cover letter
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume and create a cover letter based on the resume content.
"""

# When the button is pressed, generate the cover letter using the resume
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            response = get_gemini_response(input_prompt1, pdf_content, input_prompt1)
            st.subheader("The Response is:")
            st.write(response)
    else:
        st.write("Please upload the resume")
