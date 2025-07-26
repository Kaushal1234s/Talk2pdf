import streamlit as st
import pdfplumber
import requests
import os

# Set your Groq API Key here
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Function to extract text from uploaded PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# Function to call Groq API
def query_groq(prompt, model="llama3-70b-8192"):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on uploaded PDFs."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code}\n{response.text}"

# Streamlit UI
st.set_page_config(page_title="GenAI PDF Chatbot", layout="centered")
st.title("📄 Talk2PDF")

pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file:
    text = extract_text_from_pdf(pdf_file)
    st.success("✅ PDF processed successfully!")

    question = st.text_input("💬 Ask a question about the document")

    if st.button("Ask"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                prompt = f"Answer the following question based on this document:\n\n{text[:8000]}\n\nQuestion: {question}"
                answer = query_groq(prompt)
                st.markdown("### 🧠 Answer:")
                st.write(answer)
