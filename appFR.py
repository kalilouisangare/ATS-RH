import streamlit as st
import google.generativeai as genai
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configurer le modèle d'IA générative avec la clé API Google
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configuration du modèle pour la génération de texte
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Définir les paramètres de qualité pour le suivi-évaluation
safety_settings = [
    {
        "category": f"ME_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["PERTINENCE", "EFFICACITÉ", "EFFICIENCE", "IMPACT", "DURABILITÉ"]
]


def generate_response_from_gemini(input_text):
    # Créer une instance de GenerativeModel avec 'gemini-pro' comme type de modèle
    llm = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    # Générer le contenu en fonction du texte d'entrée
    output = llm.generate_content(input_text)
    # Retourner le texte généré
    return output.text

def extract_text_from_pdf_file(uploaded_file):
    # Utiliser PdfReader pour extraire le texte d'un fichier PDF
    pdf_reader = pdf.PdfReader(uploaded_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content

def extract_text_from_docx_file(uploaded_file):
    # Utiliser docx2txt pour extraire le texte d'un fichier DOCX
    return docx2txt.process(uploaded_file)

# Modèle de prompt
input_prompt_template = """
En tant qu'analyste expérimenté du système de suivi des candidats (ATS),
avec des connaissances approfondies en technologie, ingénierie logicielle, science des données, 
et ingénierie des big data, votre rôle consiste à évaluer les CV par rapport aux descriptions de postes.
Conscient de la compétitivité du marché de l'emploi, vous fournissez une assistance de premier ordre pour l'amélioration des CV.
Votre objectif est d'analyser le CV par rapport à la description de poste donnée, 
d'attribuer un pourcentage de correspondance basé sur des critères clés, et d'identifier avec précision les mots clés manquants.
resume : {text}
description: {job_description}

Je souhaite que la réponse se présente toujours en français et sous la forme d'une seule chaîne de caractères ayant la structure suivante 

{{  "Correspondance, description du poste":"%",

    "Mots clés manquants":"",

    "Résumé du candidat":"",

    "Expérience":""}}

"""

# Application Streamlit
st.title("ATS Intelligent - Améliorez Votre CV")
st.markdown('<style>h1{color: orange; text-align: center;}</style>', unsafe_allow_html=True)

job_description = st.text_area("Collez la description du poste", height=300)
uploaded_file = st.file_uploader("Téléchargez votre CV", type=["pdf", "docx"], help="Veuillez télécharger un fichier PDF ou DOCX")

submit_button = st.button("Valider")

if submit_button:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf_file(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx_file(uploaded_file)
        response_text = generate_response_from_gemini(input_prompt_template.format(text=resume_text, job_description=job_description))

        # Extraire le pourcentage de correspondance à partir de la réponse
        match_percentage_str = response_text.split('"Job Description Match":"')[1].split('"')[0]

        # Supprimer le symbole de pourcentage et convertir en float
        match_percentage = float(match_percentage_str.rstrip('%'))

        st.subheader("Résultat de l'évaluation ATS :")
        st.write(response_text)

        # Afficher un message en fonction du pourcentage de correspondance
        if match_percentage >= 80:
            st.text("Poursuivre l'embauche")
        else:
            st.text("Pas de correspondance")
