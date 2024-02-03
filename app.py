import sys
from logger import logging

import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap
from dotenv import load_dotenv

# API Key Configure
env_loaded = load_dotenv() # take environment variables from .env.
if env_loaded:
    logging.info("Environment variables loaded.")
else:
    logging.error("Environment variables not loaded.")

api_key = os.getenv("GOOGLE_API_KEY")
# api_key = st.secrets["GOOGLE_API_KEY"]
if api_key:
    genai.configure(api_key=api_key)
else:
    logging.error("API key not found or empty.")
    

def to_markdown(text):
  # Remove the indentation from the text
  text = textwrap.dedent(text)
  # Add the markdown syntax manually
  # text = "\n" + text.replace("•", "*")
#   text = text.replace("•", " ")
  text = text.replace("*", " ")
#   text = text.replace("-", " ")
  # Return the markdown-formatted string
  return text
    
# Data extarction function
def extract_transcript_data(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[-1]

        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        transcript_text = ""
        for i in transcript:
            transcript_text += " " + i["text"]
            
        logging.info("Extract data from the video.")
        return transcript_text
    except Exception as e:
        logging.error(e)
        # print(f"Error extracting transcript: {e}")
        return None

# Define the Subjects and the predefined text prompt
subjects = ["","Biology", "Chemistry","Computer Science","Data Science & Statistics","Economics","History","Literature","Mathematics","Philosophy","Psychology",
            "Sociology","Environmental Science","Political Science","Geography","Art History","Music Theory","Astronomy","Nutrition and Dietetics","Film Studies","Physical Education"]
text_prompt = {
    "":"",
    "Biology": "As a biology expert, analyze the YouTube video transcript, providing detailed notes like a student. Cover key concepts like complex biological processes, cellular functions, and anatomical structures. Break down scientific terms and explain their significance in medicine, environment, and daily life. Use examples to illustrate practical applications.",
    "Chemistry": "Assume the role of a chemistry expert analyzing a YouTube video transcript. Generate detailed notes capturing key concepts like chemical reactions, properties, and molecular structures. Explain reaction mechanisms, theories, and their real-world applications in industry, environment, and daily life. Include examples and case studies to demonstrate practical uses.",
    "Computer Science": "Analyze a YouTube video transcript as a computer science expert. Craft detailed notes like a student, covering fundamental concepts like programming, algorithms, and data structures. Break down technical terms and discuss real-world applications in software development, artificial intelligence, and cybersecurity. Use examples and case studies to illustrate practical aspects.",
    "Data Science & Statistics" : "As a data science and statistics expert, analyze a YouTube video transcript. Create detailed notes resembling a student's, encompassing data science topics like data collection, cleaning, analysis, and visualization. Discuss machine learning techniques, real-world applications, and data ethics. For statistics, cover core concepts, hypothesis testing, and regression analysis, highlighting their importance and practical use with examples.",
    "Economics" : "Assume the role of an economics expert analyzing a YouTube video transcript. Generate detailed notes like a student, covering economic theories, models, and principles. Break down complex concepts and discuss their real-world implications in finance, international trade, and public policy. Use examples and case studies to illustrate practical applications.",
    "History" : "Analyze a YouTube video transcript as a history expert. Craft detailed notes like a student, covering historical events, figures, and movements in their context. Analyze causes, consequences, and different perspectives on events, along with their interpretations over time. Use examples and case studies to illustrate their significance.",
    "Literature" : "As a literature expert, analyze a YouTube video transcript. Create detailed notes resembling a student's, covering literary texts, characters, and themes. Explain literary devices and techniques used by authors, and discuss the historical and cultural context of works. Use examples and case studies to illustrate their significance.",
    "Mathematics" : "Assume the role of a mathematics expert analyzing a YouTube video transcript. Generate detailed notes like a student, covering mathematical concepts, formulas, and problem-solving techniques. Provide step-by-step explanations for solving problems, clarify theoretical foundations, and include relevant examples or practice problems for reinforcement.",
    "Philosophy" : "As a philosophy expert, analyze a YouTube video transcript. Craft detailed notes like a student, covering philosophical concepts, arguments, and schools of thought. Explain complex ideas in understandable terms and discuss their historical and contemporary relevance. Use examples and case studies to illustrate different philosophical perspectives.",
    "Psychology" : "Assume the role of a psychology expert analyzing a YouTube video transcript. Generate detailed notes like a student, covering psychological concepts, theories, and research findings. Explain complex mental processes and behaviors in understandable terms and discuss their real-world applications. Use examples and case studies to illustrate practical implications.",
    "Sociology" : "As a sociology expert, analyze a YouTube video transcript. Create detailed notes resembling a student's, covering social structures, institutions, and processes. Explain complex sociological concepts in understandable terms and discuss their impact on individuals and societies. Use examples and case studies to illustrate real-world applications.",
    "Environmental Science" : "As an environmental science expert, analyze a YouTube video transcript on climate change. Generate detailed notes like a student, explaining key concepts like greenhouse gases, global warming, and its impacts. Discuss climate change mitigation and adaptation strategies, highlighting real-world examples and their effectiveness. Analyze ethical considerations and the role of individual action.",
    "Political Science" : "Assume the role of a political science expert analyzing a documentary on political systems. Craft detailed notes like a student, covering different types of governments, their structures, and functions. Explain key concepts like democracy, authoritarianism, and communism, comparing and contrasting their strengths and weaknesses. Analyze the role of citizens, political parties, and elections in various systems.",
    "Geography" : "Assume the role of a geography expert analyzing a video on a specific geographical region. Generate detailed notes like a student, covering the region's physical features, climate, and ecosystems. Explain the impact of human activities on the region, discussing issues like sustainability and conservation. Analyze the cultural and historical significance of the region, using examples of landmarks and local traditions.",
    "Art History" : "As an art history expert, analyze a video lecture on a specific art movement. Create detailed notes resembling a student's, covering the movement's historical context, key artists, and styles. Explain the movement's philosophical and social influences, analyzing its impact on subsequent art forms. Use examples of iconic artworks and their interpretations to illustrate the movement's essence.",
    "Music Theory" : "As a music theory expert, analyze a video tutorial on a specific musical concept. Create detailed notes resembling a student's, explaining the concept in simple terms and using musical notation for clarity. Discuss the historical development of the concept and its application in different musical styles. Provide examples of iconic compositions that utilize the concept effectively, demonstrating its impact on music creation.",
    "Physical Education" : "Assume the role of a physical education expert analyzing a video on a specific fitness principle. Generate detailed notes like a student, explaining the principle's importance for overall health and well-being. Discuss different exercises that target the principle, providing clear instructions and modifications for different fitness levels. Analyze the benefits and potential risks of the exercises, emphasizing safety and proper form.",
    "Astronomy" : "As an astronomy expert, analyze a video documentary on a specific astronomical phenomenon. Create detailed notes resembling a student's, explaining the phenomenon's scientific principles and its significance in understanding the universe. Discuss the latest research and discoveries related to the phenomenon, using images and diagrams for visualization. Analyze the philosophical and cultural implications of the phenomenon, sparking curiosity and wonder about the cosmos.",
    "Nutrition and Dietetics" : "As a nutrition and dietetics expert, analyze a video on a specific dietary concept or nutritional guideline. Create detailed notes resembling a student's, explaining the concept in clear language and providing relevant scientific evidence. Discuss the impact of the concept on overall health and well-being, addressing common misconceptions and myths. Include practical tips and meal planning strategies for incorporating the concept into daily life, promoting healthy eating habits.",
    "Film Studies" : "Assume the role of a film studies expert analyzing a specific film scene or technique. Generate detailed notes like a student, explaining the scene's composition, symbolism, and narrative significance. Discuss the director's stylistic choices and their impact on the viewer's interpretation. Analyze the scene's connection to broader film movements and genres, highlighting its historical and cultural context."
}
language = ["English","Hindi", "Bengali", "Telugu", "Marathi", "Tamil",
    "Urdu", "Gujarati", "Malayalam", "Kannada", "Odia",
    "Punjabi", "Assamese", "Maithili", "Santali", "Nepali",
    "Konkani", "Dogri", "Kashmiri", "Manipuri", "Sindhi",
    "Bodo", "Khasi", "Mizo", "Garo", "Tulu",
    "Kokborok", "Angika", "Kurukh", "Meitei", "Khasi",
    "Gondi", "Toda", "Nihali", "Bhil", "Kolami",
    "Bhili", "Kumaoni", "Kodava", "Kui", "Mundari",
    "Rajasthani", "Saurashtra", "Tangkhul", "Toda",
    "Kodava", "Kui", "Mundari", "Rajasthani", "Saurashtra",
    "Tangkhul"]

# initialize our streamlit app
st.set_page_config(page_title="Notes Craft Pro")
logging.info("Streamlit app initialized.")
st.header("Notes Craft Pro")
st.write("An application that effortlessly transcribes your YouTube videos into detailed notes.")

# Create a sidebar
sidebar = st.sidebar

# Create the text area for video link
video_url = st.text_input("Enter YouTube Video Link:",key="input")

# Create the dropdown menu
dropdown = sidebar.selectbox("Select Subject :", subjects, key="dropdown",index=0)

prompt_value =text_prompt[dropdown]
# Create the text area 
text_area = sidebar.text_area("Write your text prompt :", value=prompt_value , key="text")

# Create the dropdown menu for language
language_data = sidebar.selectbox("Select language :", language, key="language_data",index=0)
language_prompt = f"And language will be{language_data}"

# Check if the file is not None
if video_url is not None:
    if "=" in video_url:
        st.video(video_url)
    else:
        st.write("Please upload your YouTube video link.")
else:
    st.write("Please upload your YouTube video link.")

# Create an animated button with an emoji
button_css = st.markdown("""
<style>
@keyframes pulse {
  0% {
    transform: scale(0.95);
  }
  70% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(0.95);
  }
}
.stButton>button {
  animation: pulse 2s infinite;
  font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

submit=st.sidebar.button("📝Get Detailed Notes..", key="submit")


if submit:
    if video_url !="" and text_area != "":
        try:
            with st.spinner('Generating notes...'):
                transcript_data = extract_transcript_data(video_url)
                if transcript_data is not None: # check if transcript data is not None
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(text_area + transcript_data +language_prompt)
                    final_response = response.text
                    st.subheader("Generated Notes:")
                    st.write(final_response)
                    logging.info("Notes generated.")
                    # Create a download button
                    sidebar.download_button(
                    label="Download the response",
                    data=to_markdown(final_response),
                    file_name="note.txt",
                    mime="ttext/plain")
                else:
                    st.write("No transcript data found for the video.")
        except Exception as e:
            logging.error(e)
            st.error(f"An error occurred: {e}")
    else:
        st.write("Please enter the video link and text prompt correctly.")

# Add a footer with your name
footer_css = st.sidebar.markdown("""
<style>
.footer {
  position: fixed;
  bottom: 0;
  right: 0;
  padding: 10px;
  color: white;
  font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

footer = st.sidebar.markdown("""
<div class="footer">
Created by : Adrit Pal
</div>
""", unsafe_allow_html=True)