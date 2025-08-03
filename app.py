from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

app = FastAPI()

# Define input model
class PromptRequest(BaseModel):
    description: str

# IBM Watson config (replace with your actual values or use st.secrets if in Streamlit)
API_KEY = "lOdzajDlVzNo_GBB1AtnU_r8XRRuTwEhXBrTV4e10lFw"
DEPLOYMENT_ID = "8093338b-afee-4cc2-bfb6-3e1d8f87cc8e"
PROJECT_ID = "4a067384-6ab5-4cf8-8230-6bdc655f1cc4"
SPACE_ID = "23585c38-600b-4ed2-8bb8-49c7545ded66"
BASE_URL = "https://us-south.ml.cloud.ibm.com"

def get_iam_token():
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": API_KEY
        }
    )
    return response.json()["access_token"]

@app.post("/generate/")
def generate_latex(req: PromptRequest):
    try:
        # 🔧 Prepend instruction to avoid LaTeX errors
        prompt = (
            "Do not use TikZ styles like '-latex'' or deprecated arrow tips. "
            "Instead, use \\usetikzlibrary{arrows.meta} and define arrows as -{Latex}. "
            "Now draw: " + req.description
        )

        iam_token = get_iam_token()
        headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "parameters": {
                "prompt_variables": {
                    "description": prompt
                }
            }
        }

        endpoint = f"{BASE_URL}/ml/v1/deployments/{DEPLOYMENT_ID}/text/generation?version=2021-05-01"
        response = requests.post(endpoint, headers=headers, json=payload)

        if response.status_code != 200:
            return {"detail": f"IBM API Error: {response.status_code} - {response.text}"}

        output = response.json()
        return {"latex_code": output.get("results", [{}])[0].get("generated_text", "No output")}

    except Exception as e:
        return {"detail": str(e)}
