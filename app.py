import streamlit as st
import requests

st.set_page_config(page_title="LaTeX TikZ Generator 💡", layout="centered")
st.title("🧠 AI-Powered LaTeX Diagram Generator")
description = st.text_area("Enter a description of the diagram:")

if st.button("Generate TikZ Code") and description:
    with st.spinner("Generating..."):
        api_key = st.secrets["API_KEY"]
        deployment_id = st.secrets["DEPLOYMENT_ID"]
        url = st.secrets["URL"]

        # Step 1: Get IAM token
        token_response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key,
            },
        )
        access_token = token_response.json()["access_token"]

        # Step 2: Create prompt with a fix
        prompt = (
            "Do not use TikZ styles like '-latex'' or deprecated arrow tips. "
            "Use \\usetikzlibrary{arrows.meta} and -{Latex} instead. "
            "Now draw: " + description
        )

        # Step 3: Make request to Watsonx
        response = requests.post(
            f"{url}/ml/v1/deployments/{deployment_id}/text/generation?version=2021-05-01",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "parameters": {
                    "prompt_variables": {
                        "description": prompt
                    }
                }
            },
        )

        if response.status_code == 200:
            result = response.json()
            latex_code = result["results"][0]["generated_text"]
            st.code(latex_code, language="latex")
        else:
            st.error(f"❌ IBM API Error: {response.status_code} - {response.text}")
