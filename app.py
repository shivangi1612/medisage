import streamlit as st
from dotenv import load_dotenv
import os
import json
import pandas as pd

from lab_utils.ocr_loader import extract_text_from_file
from lab_utils.lab_extractor import extract_lab_data
from lab_utils.interpreter import interpret_lab_results
from lab_utils.summarizer import summarize_results
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Page configuration
st.set_page_config(page_title="🧠 MediSage: AI-Powered Lab Report Analyzer", layout="centered")
st.markdown("""
    <style>
        .centered { text-align: center; }
        .stTextArea > div > textarea {
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            background-color: #f0f8ff;
            color: #003366;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='centered'>🧠 MediSage: AI-Powered Lab Report Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered'>Upload a lab report and let the AI extract, interpret, summarize, and answer your questions.</p>", unsafe_allow_html=True)
st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("📄 Upload Lab Report (PDF / Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    st.markdown("### 🔍 Step 1: Extracting Text from Report")
    with st.spinner("Extracting text..."):
        extracted_text = extract_text_from_file(uploaded_file)

    st.success("✅ Text extracted successfully!")
    st.text_area("📃 Extracted Raw Text", extracted_text, height=300)

    st.markdown("---")
    st.markdown("### 🔬 Step 2: Extracting Lab Test Data")
    with st.spinner("Calling Gemini to extract lab results..."):
        extracted_json_str = extract_lab_data(extracted_text)

    st.success("✅ Lab results extracted!")
    st.code(extracted_json_str, language="json")

    try:
        structured_data = json.loads(extracted_json_str)

        st.markdown("---")
        st.markdown("### 📈 Step 3: Interpreting Lab Results")
        with st.spinner("Interpreting values..."):
            interpreted = interpret_lab_results(json.dumps(structured_data))

        st.success("✅ Lab results interpreted!")

        # Display interpretation table
        df = pd.DataFrame(interpreted)

        def highlight_status(val):
            if val == "High":
                return "background-color: #FFCCCC; color: red;"  # light red
            elif val == "Low":
                return "background-color: #CCE5FF; color: blue;"  # light blue
            elif val == "Normal":
                return "background-color: #D4EDDA; color: green;"  # light green
            return ""

        styled_df = df.style.applymap(highlight_status, subset=["interpretation"])
        st.dataframe(styled_df, use_container_width=True)

        st.markdown("---")
        st.markdown("### 💡 Step 4: Generating Summary")
        with st.spinner("Summarizing for patient..."):
            summary = summarize_results(interpreted)

        st.subheader("📝 AI Summary for Patient")
        st.markdown(summary)

        st.markdown("---")
        st.markdown("### 💬 Step 5: Ask Follow-up Questions")

        user_query = st.text_input("Ask any health-related question based on your report:")
        if user_query:
            def generate_chat_response(question, context):
                prompt = PromptTemplate.from_template("""
                You are a medical assistant. Based on the following lab report interpretation:
                {context}

                Patient question: {question}

                Provide a helpful, medically informed answer.
                """)
                llm = ChatGoogleGenerativeAI(
                    model="models/gemini-1.5-flash",
                    google_api_key=os.getenv("GOOGLE_API_KEY")
                )
                chain = LLMChain(prompt=prompt, llm=llm)
                return chain.run(context=json.dumps(context), question=question)

            with st.spinner("🤖 Thinking..."):
                response = generate_chat_response(user_query, interpreted)
                st.markdown(f"**🤖 AI Response:** {response}")

    except json.JSONDecodeError:
        st.error("❌ Failed to parse lab results. Please check the extraction format.")
        st.code(extracted_json_str)

else:
    st.info("👆 Please upload a PDF or image to begin.")
