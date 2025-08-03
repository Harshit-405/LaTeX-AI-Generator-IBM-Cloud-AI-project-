import streamlit as st
import requests

st.set_page_config(page_title="LaTeX TikZ Generator", layout="centered")
st.title("🧠 AI-powered LaTeX TikZ Diagram Generator")

# User input
description = st.text_area("Describe the diagram you want to generate:", height=150)

# Button to trigger generation
if st.button("Generate LaTeX Code"):
    if not description.strip():
        st.warning("Please enter a description.")
        st.stop()

    # Get token using IBM IAM
    def get_iam_token(api_key):
        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key,
            },
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            st.error("❌ Failed to authenticate with IBM Cloud.")
            st.stop()

    # Load from secrets.toml
    API_KEY = st.secrets["API_KEY"]
    DEPLOYMENT_URL = st.secrets["DEPLOYMENT_URL"]

    token = get_iam_token(API_KEY)

    # Prepare headers and payload
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": description,
        "parameters": {
            "decoding_method": "greedy"
        }
    }

    with st.spinner("Generating LaTeX TikZ code..."):
        response = requests.post(DEPLOYMENT_URL, headers=headers, json=payload)

    if response.status_code == 200:
        tikz_code = response.json().get("results", [{}])[0].get("generated_text", "")
        if tikz_code:
            st.subheader("📄 Generated LaTeX Code")
            st.code(tikz_code, language="latex")
        else:
            st.warning("⚠️ No code was generated.")
    else:
        st.error(f"❌ IBM API Error: {response.status_code}\n{response.text}")
