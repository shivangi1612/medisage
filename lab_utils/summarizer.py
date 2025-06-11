from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import json

def summarize_results(interpreted_data):
    summary_input = json.dumps(interpreted_data, indent=2)

    prompt = PromptTemplate(
        input_variables=["structured_data"],
        template="""
Given the following interpreted lab results, summarize them in simple, friendly language a patient can understand.

Structured data:
{structured_data}

Summary:
"""
    )

    llm = ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )

    chain = LLMChain(prompt=prompt, llm=llm)
    return chain.run(structured_data=summary_input)
