import streamlit as st
import requests

st.set_page_config(page_title="LaTeX Diagram Generator")
st.title("🧠 LaTeX Diagram Generator with IBM watsonx")

description = st.text_area("Describe your diagram", height=150)

if st.button("Generate LaTeX"):
    if not description:
        st.warning("Enter something first.")
        st.stop()

    api_key = st.secrets["API_KEY"]
    deployment_url = st.secrets["DEPLOYMENT_URL"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt_variables": {
            "description": description
        }
    }

    with st.spinner("Generating..."):
        res = requests.post(deployment_url, headers=headers, json=payload)

    if res.status_code == 200:
        try:
            output = res.json()["results"][0]["generated_text"]
            st.success("LaTeX Code:")
            st.code(output, language="latex")
        except:
            st.error("⚠️ Unexpected response.")
            st.json(res.json())
    else:
        st.error("❌ Error:")
        st.json(res.json())
