# main.py
import os
import pdfplumber
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI()

def reformat_text(text):
    system_prompt = """You are a text reformatter. Reformat the text with proper spacing and 
    punctuations. The contents of the text should not be changed and should remain as is."""
    
    user_prompt = f"Reformat this text: \n{text} with proper spacing and punctuations."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while reformatting: {e}"

def summarize_text(text):
    system_prompt = """You are a research summarizer. Summarize the content of the research paper in no more than 
    1000 words. Including but not limited to the following sub headings:
    Title and Authors,
    Objective/Problem,
    Background,
    Methods,
    Key Findings,
    Conclusion,
    Future Directions,
    Limitations,
    Potential Applications"""
    
    user_prompt = f"Summarize the content of the research paper: \n{text}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        stream = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True
        )
        for chunk in stream:
            yield chunk.choices[0].delta.content or ""
    except Exception as e:
        yield f"An error occurred while summarizing: {e}"

def extract_content_and_summarize_text(file):
    extracted_text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            left_bbox = (0, 0, page.width / 2, page.height)
            right_bbox = (page.width / 2, 0, page.width, page.height)
            left_text = page.within_bbox(left_bbox).extract_text() or ""
            right_text = page.within_bbox(right_bbox).extract_text() or ""
            full_text = page.extract_text() or ""
            
            if len(left_text) + len(right_text) < 0.8 * len(full_text):
                extracted_text += full_text + "\n"
            else:
                extracted_text += left_text + "\n" + right_text + "\n"
    
    formatted_text = reformat_text(extracted_text)
    for chunk in summarize_text(formatted_text):
        yield chunk
