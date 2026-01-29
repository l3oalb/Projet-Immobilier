import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_with_ai(raw_text):
    """Extrait le prix, la surface, le type de bien, la ville et l'état d'un texte d'annonce immobilière avec l'API OpenAI."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
    Extrais les informations suivantes du texte de l'annonce immobilière ci-dessous sous format JSON uniquement :
    - prix (entier)
    - surface (entier)
    - type_bien (Maison, Appartement, ou Garage)
    - ville (nom propre)
    - etat (Neuf, Bon état, À rénover)

    Texte : {raw_text[:2000]}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # peu cher et rapide
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )

    json_string = response.choices[0].message.content # Récupère la chaîne JSON renvoyée par l'API
    
    # On la transforme en dictionnaire Python
    try:
        data = json.loads(json_string)
        return data
    except Exception as e:
        print(f"Erreur de décodage JSON : {e}")
        return None