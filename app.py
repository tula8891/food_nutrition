import streamlit as st
import httpx
import base64


def generate_implicature(api_key, image_data_uri, age, weight, height, gender, meal_type):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # user_context = (
    #     f"This image is from a {meal_type}. The person consuming this food is {age} years old, "
    #     f"weighs {weight} kg, is {height} cm tall, and is {gender}. "
    #     "Please analyze the nutritional content of the food shown in the image and determine if it is appropriate "
    #     "for the person considering their physical characteristics and meal context."
    # )
    user_context = (
        f"This image is from a {meal_type}. The person consuming this food is {age} years old, "
        f"weighs {weight} kg, is {height} cm tall, and is {gender}. "
        "Please analyze the nutritional content of the food shown in the image and determine if it is appropriate "
        "for this person, considering their physical characteristics and the meal context. "
        "Additionally, indicate approximately what portion of their recommended daily nutritional intake "
        "this meal provides (e.g., 1/4, 1/2, etc.)."
    )

    data = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_context},
                    {"type": "image_url", "image_url": {"url": image_data_uri}}
                ]
            }
        ]
    }

    try:
        timeout = httpx.Timeout(30.0, read=30.0)
        response = httpx.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API Error: {e}"


def main():
    st.set_page_config(page_title="Food Nutrition Analyzer", layout="centered")
    st.title("🥗 Food Nutrition Analyzer from Image")

    try:
        api_key = st.secrets["myconnection"]["YOUR_API_KEY"]
    except Exception as e:
        st.error("Failed to load API key from secrets.")
        return

    # User inputs for health and context
    st.sidebar.header("User Details")
    age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)
    weight = st.sidebar.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)
    height = st.sidebar.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    meal_type = st.sidebar.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

    uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Image", width=200)

        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
        mime_type = uploaded_file.type
        image_data_uri = f"data:{mime_type};base64,{base64_image}"

        if st.button("Analyze Nutrition"):
            with st.spinner("Analyzing..."):
                result = generate_implicature(api_key, image_data_uri, age, weight, height, gender, meal_type)
                st.markdown("### Nutrition Information")
                st.markdown(result)


if __name__ == "__main__":
    main()
