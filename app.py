import streamlit as st
import requests

st.set_page_config(page_title="LaTeX TikZ Diagram Generator", layout="wide")
st.title("🧠 AI-Powered LaTeX TikZ Diagram Generator")

# Let user input prompt
description = st.text_area("📝 Describe your diagram idea below:", placeholder="e.g. Draw a flowchart with Start → Process → End", height=150)

# Only show button if there's a prompt
if st.button("⚡ Generate LaTeX Code") and description.strip() != "":
    st.info("⏳ Contacting Watsonx.ai...")

    # 1. Get credentials
    API_KEY = st.secrets["API_KEY"]
    DEPLOYMENT_ID = st.secrets["DEPLOYMENT_ID"]
    URL = st.secrets["URL"]

    # 2. Get IAM token
    token_response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}"
    )

    if token_response.status_code != 200:
        st.error("❌ Could not get IAM token.")
        st.json(token_response.json())
        st.stop()

    access_token = token_response.json().get("access_token")
    if not access_token:
        st.error("❌ IAM token missing.")
        st.json(token_response.json())
        st.stop()

    # 3. Make inference call
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "parameters": {
            "prompt_variables": {
                "description": description.strip()
            }
        }
    }

    endpoint = f"{URL}/ml/v1/deployments/{DEPLOYMENT_ID}/text/generation?version=2021-05-01"

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code != 200:
        st.error(f"❌ Error: {response.status_code}")
        st.json(response.json())
        st.stop()

    # 4. Process model response
    try:
        latex_code = response.json()["results"][0]["generated_text"]
        latex_code = latex_code.replace("-latex'", "-latex")  # fix arrow error
        st.success("✅ LaTeX code generated!")
        st.code(latex_code, language="latex")
    except Exception as e:
        st.error("⚠️ Could not extract LaTeX code from the model response.")
        st.json(response.json())

else:
    st.warning("✍️ Please enter a diagram description to generate LaTeX.")
