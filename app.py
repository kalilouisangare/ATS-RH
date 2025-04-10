import streamlit as st
import google.generativeai as genai
import docx2txt
import PyPDF2 as pdf
import json  # Ajout de l'import JSON

# Configuration de l'API Google via Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ... (generation_config et safety_settings restent identiques) ...

def generate_response_from_gemini(input_text):
    llm = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    output = llm.generate_content(input_text)
    return output.text

# ... (les fonctions d'extraction de texte restent identiques) ...

# Nouveau prompt template avec instructions strictes
input_prompt_template = """
Je veux une réponse STRICTEMENT dans ce format JSON (sans texte supplémentaire) :
{{
    "Job Description Match": "X%",
    "Mots manquants": ["mot1", "mot2", ...],
    "Resume candidat": "texte concis",
    "Experience": "analyse détaillée"
}}

Vous êtes un expert ATS. Analysez ce CV :
resume : {text}
description: {job_description}
"""

# ... (configuration Streamlit reste identique jusqu'au bouton) ...

if submit_button:
    if uploaded_file is not None:
        try:
            # Extraction du texte
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf_file(uploaded_file)
            else:
                resume_text = extract_text_from_docx_file(uploaded_file)
            
            # Génération de la réponse
            response_text = generate_response_from_gemini(
                input_prompt_template.format(
                    text=resume_text, 
                    job_description=job_description
                )
            )

            # Nettoyage de la réponse
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "")
            
            # Parsing JSON sécurisé
            response_data = json.loads(cleaned_response)
            
            # Extraction des valeurs
            match_percentage = float(response_data["Job Description Match"].strip('%'))
            
            # Affichage formaté
            st.subheader("Résultat Evaluation ATS:")
            st.json(response_data)

            # Logique de décision
            decision_message = "✅ Poursuivre l'embauche" if match_percentage >= 80 else "❌ Vous ne correspondez pas au poste"
            st.markdown(f"**Décision:** {decision_message}")

        except json.JSONDecodeError:
            st.error("Erreur de format de réponse. Voici la réponse brute:")
            st.code(response_text)
        except KeyError as e:
            st.error(f"Champ manquant dans la réponse: {str(e)}")
            st.code(response_text)
        except Exception as e:
            st.error(f"Erreur inattendue: {str(e)}")
