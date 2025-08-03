import streamlit as st
import requests

# Set title
st.title("📄 LaTeX TikZ Diagram Generator")

# Input prompt
description = st.text_area("Describe your diagram:", "Draw OSI layers with arrows")

if st.button("Generate LaTeX Code"):
    st.info("⏳ Generating...")

    # Fetch secrets safely
    API_KEY = st.secrets["API_KEY"]
    DEPLOYMENT_ID = st.secrets["DEPLOYMENT_ID"]
    URL = st.secrets["URL"]

    # Step 1: Get IAM Token
    token_response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}"
    )

    if token_response.status_code != 200:
        st.error("❌ Failed to get IAM token.")
        st.json(token_response.json())
        st.stop()

    access_token = token_response.json().get("access_token")
    if not access_token:
        st.error("❌ IAM token not returned.")
        st.json(token_response.json())
        st.stop()

    # Step 2: Query the deployed model
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "parameters": {
            "prompt_variables": {
                "description": description
            }
        }
    }

    endpoint = f"{URL}/ml/v1/deployments/{DEPLOYMENT_ID}/text/generation?version=2021-05-01"
    response = requests.post(endpoint, json=payload, headers=headers)

    if response.status_code != 200:
        st.error(f"❌ IBM API Error: {response.status_code}")
        st.json(response.json())
        st.stop()

    try:
        latex_code = response.json()["results"][0]["generated_text"]
        latex_code = latex_code.replace("-latex'", "-latex")  # 🛠 Fix TikZ arrow error

        st.success("✅ Generated successfully!")
        st.code(latex_code, language="latex")
    except Exception as e:
        st.error("⚠️ Something went wrong parsing the response.")
        st.write(response.json())
