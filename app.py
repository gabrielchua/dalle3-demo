"""
app.py
"""
import streamlit as st
from openai import OpenAI

SIZE_MAPPING = {"Square": "1024x1024", "Landscape": "1792x1024", "Portrait": "1024x1792"}

########################################################
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
        messages=[{"role": "system", "content": "You are an art expert. Transform the given text into a prompt for  DALL·E 3, a text-to-image model. Be descriptive."},
                    {"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=len(prompt)*3
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
  
########################################################
st.set_page_config(page_title="Try DALL·E 3 🎨",
                   page_icon="🎨")

st.title("Try DALL·E 3 🎨")
st.info("""
**About:** This app is a personal project, not affliated with OpenAI.
        
**Is this really free?** I have some OpenAI API credits expiring on 1 March 2024. 

**Contact:** [X](https://www.x.com/gabchuayz) or [LinkedIn](https://www.linkedin.com/in/gabriel-chua)
""")

original_prompt = st.text_input("Describe your picture",
                                max_chars=4000,
                                help="Be as descriptive as possible.")
size = st.radio("Size", ["Square", "Landscape", "Portrait"],
                horizontal=True,
                help="The aspect ratio for the image.")
style = st.radio("Style", ["Natural", "Vivid"],
                 horizontal=True,
                 help="Vivid photos will be less realistic")
prompt_enhancment = st.checkbox("Prompt enhancement",
                                help="This uses GPT-4 to enhance your prompt")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if st.button("Generate Image"):
    original_prompt = original_prompt + f". The aspect ratio for the image will be in {size} style."

    size = SIZE_MAPPING[size]

    if len(original_prompt) == 0:
        st.warning("Please enter a prompt.", icon="🚫")
        st.stop()

    if (moderation_check(original_prompt)) or (zero_shot_nsfw_classifier(original_prompt) == 1):
        st.warning("This prompt has been flagged as NSFW. Please revise it.", icon="🚫")
        st.stop()

    if prompt_enhancment:
        prompt_dalle3 = generate_dalle3_prompt(original_prompt)
    else:
        prompt_dalle3 = original_prompt

    if (moderation_check(prompt_dalle3)) or (zero_shot_nsfw_classifier(prompt_dalle3) == 1):
        st.warning("This prompt has been flagged as NSFW. Please revise it.", icon="🚫")
        st.stop
    
    with st.spinner("Generating your image 🎨 - this can take about 30 seconds..."):
        img_url = generate_dalle3_image_url(prompt_dalle3, size, style)
    st.markdown(f'<img src="{img_url}" alt="Generated Image" width="500"> <br>', unsafe_allow_html=True)
    st.success(f"**Prompt:** {prompt_dalle3}")
