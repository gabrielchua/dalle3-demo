"""
utils.py
"""
import json
from datetime import datetime

import gspread
import streamlit as st
from google.oauth2 import service_account
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def append_to_sheet(prompt, generated):
    """
    Add to GSheet
    """
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(st.secrets["GCP_SERVICE_ACCOUNT"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url(st.secrets["PRIVATE_GSHEETS_URL"])
    worksheet = sh.get_worksheet(0) # Assuming you want to write to the first sheet
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([current_time, prompt, generated])

def moderation_check(text):
    """Check if the given text is safe for work using openai's moderation endpoint."""
    response = client.moderations.create(input=text)
    return response.results[0].flagged

def zero_shot_nsfw_classifier(text):
    """Check if the given text is safe for work using gpt4 zero-shot classifer."""
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "system", "content": "Is the given text NSFW? If yes, return `1`, else return `0`"},
                  {"role": "user", "content": text}],
        max_tokens=1,
        temperature=0,
        seed=0,
        logit_bias={"15": 100,
                    "16": 100}
    )

    return int(response.choices[0].message.content)

def generate_dalle3_prompt(prompt):
    """Enhance the given prompt using GPT-4. Return the enhanced prompt."""
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[{"role": "system", "content": "You are an art expert. You will receive an image description, and your task is to make it much more detailed. Furnish additional details that would make the final image more aesthetically pleasing. Your description should be around 100 words."},
                    {"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content

def generate_dalle3_image_url(prompt, size, style):
    """Generate an image using DALL·E 3 and return the URL."""
    img_response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        style=style.lower(),
        n=1,
        size=size
    )

    return img_response.data[0].url
