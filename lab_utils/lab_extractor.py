from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import re
import json

def extract_lab_data(text):
    prompt = PromptTemplate(
        input_variables=["report_text"],
        template="""
You are an expert medical assistant.

From the following lab report text, extract all lab test results into a **JSON array** where each object has:

- test_name (string)
- value (string or float)
- unit (string or null)
- reference_range (string or null)

Only return valid JSON output without any explanation or markdown.

Report:
{report_text}
"""
    )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    chain = LLMChain(prompt=prompt, llm=llm)
    response = chain.run(report_text=text)

    # Optional: Strip non-JSON text if Gemini wraps the output
    json_start = response.find("[")
    json_end = response.rfind("]") + 1
    json_str = response[json_start:json_end]

    # Debug print
    print("🔎 Gemini Raw Output:", response)

    return json_str
