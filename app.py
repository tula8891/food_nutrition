import streamlit as st
import httpx
import base64
from openai import OpenAI


# Load parameters from YAML file
# @st.cache_data
# def load_params_from_yaml(yaml_file="params_new.yaml"):
#     with open(yaml_file, 'r') as file:
#         params = yaml.safe_load(file)
#     return params


# Function to generate nutrition table from image
# def generate_implicature(api_key, image_data_uri):
#     client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
#
#     try:
#         response = client.chat.completions.create(
#             model="sonar-pro",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         {"type": "text", "text": "Can you describe this image food nutrition in table?"},
#                         {"type": "image_url", "image_url": {"url": image_data_uri}}
#                     ]
#                 }
#             ]
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"API Error: {e}"


def generate_implicature(api_key, image_data_uri):
    url = "https://api.perplexity.ai/chat/completions"  # Corrected URL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Can you describe this image's food nutrition in table format?"},
                    {"type": "image_url", "image_url": {"url": image_data_uri}}
                ]
            }
        ]
    }

    try:
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API Error: {e}"


# Streamlit UI
def main():
    st.set_page_config(page_title="Food Nutrition Analyzer", layout="centered")
    st.title("🥗 Food Nutrition Analyzer from Image")

    # Load API key
    try:
        # params = load_params_from_yaml()
        # api_key = params['YOUR_API_KEY']
        api_key = st.secrets["myconnection"]["YOUR_API_KEY"]
    except Exception as e:
        st.error("Failed to load API key from YAML. Please check 'params_new.yaml'.")
        return

    # File uploader
    uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Convert image to base64
        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
        mime_type = uploaded_file.type  # Automatically gets MIME type like 'image/jpeg'
        image_data_uri = f"data:{mime_type};base64,{base64_image}"

        if st.button("Analyze Nutrition"):
            with st.spinner("Analyzing..."):
                result = generate_implicature(api_key, image_data_uri)
                st.markdown("### Nutrition Information")
                st.markdown(result)


if __name__ == "__main__":
    main()
