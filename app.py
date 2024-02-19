"""
app.py
"""
import streamlit as st
from openai import OpenAI

from utils import (
    append_to_sheet,
    generate_dalle3_image_url,
    generate_dalle3_prompt,
    moderation_check,
    zero_shot_nsfw_classifier
)

SIZE_MAPPING = {"Square": "1024x1024", "Landscape": "1792x1024"}

st.set_page_config(page_title="DALL·E 3 🎨",
                   page_icon="🎨")

st.title("DALL·E 3 🎨")
with st.expander("About this app"):
    st.info("""
    This is a personal project, not affliated with OpenAI.
            
    **Is this really free?** I have some OpenAI API credits expiring on 1 March 2024. So... yes :)
    
    **Contact:** [X](https://www.x.com/gabchuayz) or [LinkedIn](https://www.linkedin.com/in/gabriel-chua)
    """)
    
original_prompt = st.text_area("Describe your picture",
                                max_chars=4000,
                                value=
                                help="Be as descriptive as possible.")
size = st.radio("Size", ["Square", "Landscape"],
                horizontal=True,
                help="The aspect ratio for the image.")
style = st.radio("Style", ["Natural", "Vivid"],
                 horizontal=True,
                 help="Vivid photos will be less realistic")
prompt_enhancment = st.checkbox("Prompt enhancement",
                                help="This uses GPT-4 to enhance your prompt")

if st.button("Generate Image"):
    size = SIZE_MAPPING[size]

    if len(original_prompt) == 0:
        st.warning("Please enter a prompt.", icon="🚫")
        append_to_sheet(original_prompt, False)
        st.stop()

    if (moderation_check(original_prompt)) or (zero_shot_nsfw_classifier(original_prompt) == 1):
        st.warning("This prompt has been flagged as NSFW. Please revise it.", icon="🚫")
        append_to_sheet(original_prompt, False)
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
        append_to_sheet(prompt_dalle3, True)

    st.markdown(f'<img src="{img_url}" alt="Generated Image" width="500"> <br>', unsafe_allow_html=True)
    st.success(f"**Prompt:** {prompt_dalle3}")
