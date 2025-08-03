import streamlit as st
import requests

API_KEY = st.secrets["API_KEY"]
DEPLOYMENT_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/deployments/8093338b-afee-4cc2-bfb6-3e1d8f87cc8e/text/generation?version=2021-05-01"

def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "apikey": api_key,
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
    }
    res = requests.post(url, headers=headers, data=data)
    return res.json()["access_token"]

st.title("LaTeX TikZ Generator ✏️")
description = st.text_area("Describe your diagram")
if st.button("Generate"):
    with st.spinner("Contacting IBM Watsonx..."):
        token = get_iam_token(API_KEY)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {
            "prompt_variables": {
                "description": description
            }
        }
        response = requests.post(DEPLOYMENT_URL, headers=headers, json=body)
        try:
            output = response.json()["results"][0]["generated_text"]
            st.code(output, language="latex")
        except Exception as e:
            st.error(f"❌ IBM API Error: {response.text}")
