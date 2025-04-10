import streamlit as st
import google.generativeai as genai
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configure the generative AI model with the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]


def generate_response_from_gemini(input_text):
     # Create a GenerativeModel instance with 'gemini-pro' as the model type
    llm = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
    )
    # Generate content based on the input text
    output = llm.generate_content(input_text)
    # Return the generated text
    return output.text

def extract_text_from_pdf_file(uploaded_file):
    # Use PdfReader to read the text content from a PDF file
    pdf_reader = pdf.PdfReader(uploaded_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content

def extract_text_from_docx_file(uploaded_file):
    # Use docx2txt to extract text from a DOCX file
    return docx2txt.process(uploaded_file)

# Prompt Template
input_prompt_template = """
Vous êtes un expert en ressources humaines et en technologie, avec une expertise en systèmes de suivi des candidats (ATS).
En tant qu'analyste expérimenté du système de suivi des candidats (ATS),
avec des connaissances approfondies en technologie, ingénierie logicielle, science des données, 
et ingénierie des big data, votre rôle consiste à évaluer les CV par rapport aux descriptions de postes.
Conscient de la compétitivité du marché de l'emploi, vous fournissez une assistance de premier ordre pour l'amélioration des CV.
Votre objectif est d'analyser le CV par rapport à la description de poste donnée, 
d'attribuer un pourcentage de correspondance basé sur des critères clés, et d'identifier avec précision les mots clés manquants.
resume : {text}
description:{job_description}
Je souhaite que la réponse se présente en français et sous la forme d'une seule chaîne de caractères ayant la structure suivante

{{  "Job Description Match":"%",
    "Missing Keywords":"",
    "Candidate Summary":"",
    "Experience":""}}
"""

# Streamlit app
# Initialize Streamlit app
st.title("Analyser votre CV avec Intelligent ATS")
st.markdown('<style>h1{color: orange; text-align: center;}</style>', unsafe_allow_html=True)
job_description = st.text_area("Copier-Coller ici la description du poste",height=300)
uploaded_file = st.file_uploader("Charger votre CV ici", type=["pdf", "docx"], help="Document autorise PDF ou Word")

submit_button = st.button("Analyser le CV")

if submit_button:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf_file(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx_file(uploaded_file)
        response_text = generate_response_from_gemini(input_prompt_template.format(text=resume_text, job_description=job_description))

        # Extract Job Description Match percentage from the response
        match_percentage_str = response_text.split('"Job Description Match":"')[1].split('"')[0]

        # Remove percentage symbol and convert to float
        match_percentage = float(match_percentage_str.rstrip('%'))

        st.subheader("Résultat Evaluation ATS:")
        st.write(response_text)
        #st.write(f'{{\n"Job Description Match": "{match_percentage}%",\n"Missing Keywords": "",\n"Candidate Summary": "",\n"Experience": ""\n}}')

        # Display message based on Job Description Match percentage
        if match_percentage >= 80:
            st.text("✅ Poursuivre l'embauche")
        else:
            st.text("❌ Vous ne correspondez pas au poste")
            
