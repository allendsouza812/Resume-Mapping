import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx
from dotenv import load_env

load_env() # Save api key in .env as GOOGLE_API_KEY

# 🔹 Configure Google Gemini API  # Replace with your actual API Key
genai.configure()

MODEL_NAME = "gemini-2.0-flash"  # Free-tier Gemini model
model = genai.GenerativeModel(MODEL_NAME)

def extract_keywords_from_gemini(job_description):
    """
    Extracts relevant keywords from a job description using Google Gemini AI.
    """
    try:
        response = model.generate_content(
            f"Extract the most important skills, tools, and technologies "
            f"from the following job description:\n\n{job_description}\n\n"
            f"Return only the keywords as a comma-separated list."
        )

        if response and hasattr(response, "text"):
            return [kw.strip() for kw in response.text.strip().split(",")]
        else:
            return ["Error extracting keywords."]
    except Exception as e:
        return [f"API Error: {str(e)}"]

def extract_text_from_file(uploaded_file):
    """
    Extracts text from an uploaded resume file (PDF or DOCX).
    """
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            return text.strip()
        elif uploaded_file.name.endswith(".docx"):
            doc = docx.Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs]).strip()
        else:
            return "Unsupported file format. Please upload a PDF or DOCX file."
    return None

def analyze_resume_with_gemini(job_keywords, resume_text):
    """
    Asks Google Gemini to compare the resume against job keywords and provide a score.
    """
    try:
        prompt = (
            f"The following are job-relevant keywords extracted from a job description:\n\n"
            f"{', '.join(job_keywords)}\n\n"
            f"Analyze the following resume text and determine how well it matches these keywords:\n\n"
            f"{resume_text}\n\n"
            f"Provide:\n"
            f"1. A similarity percentage (0-100%) based on how well the resume matches.\n"
            f"2. A short feedback summary on what improvements can be made to better match the job description.\n"
            f"3. Give a final numerical score out of 10 (considering the job match, relevance, and clarity of the resume)."
        )

        response = model.generate_content(prompt)

        if response and hasattr(response, "text"):
            return response.text.strip()
        else:
            return "Error analyzing resume."
    except Exception as e:
        return f"API Error: {str(e)}"

# 🔹 Streamlit UI
st.title("📄 AI-Powered Resume Matcher ")
st.write("Compare multiple resumes against a job description and get AI-powered analysis.")

# User Input (Job Description)
job_description = st.text_area("✍️ Enter Job Description:", height=200)

# Multiple File Upload Option (Resumes)
uploaded_files = st.file_uploader("📂 Upload Resumes (PDF/DOCX):", type=["pdf", "docx"], accept_multiple_files=True)

if st.button("🔎 Analyze Resumes"):
    if job_description and uploaded_files:
        # Extract keywords from the job description using Gemini
        job_keywords = extract_keywords_from_gemini(job_description)
        st.subheader("📌 Extracted Job Keywords:")
        st.write(", ".join(job_keywords))

        # Process each uploaded resume
        for uploaded_file in uploaded_files:
            st.subheader(f"📄 Analyzing {uploaded_file.name}...")
           
            # Extract text from the resume
            resume_text = extract_text_from_file(uploaded_file)

            # Analyze resume with Gemini AI
            analysis_result = analyze_resume_with_gemini(job_keywords, resume_text)

            st.subheader(f"📊 Gemini Resume Analysis for {uploaded_file.name}:")
            st.write(analysis_result)

    else:
        st.error("❌ Please enter a job description and upload at least one resume.")


# Run this using: `streamlit run resume_matcher.py`
