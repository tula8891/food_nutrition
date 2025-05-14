import streamlit as st
import httpx
import base64
import re


def get_daily_nutrition_requirements(age, weight, height, gender):
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee = bmr * 1.55  # Moderate activity
    calories = tdee
    protein = (0.15 * calories) / 4
    carbs = (0.50 * calories) / 4
    fats = (0.35 * calories) / 9

    return round(calories, 1), round(protein, 1), round(carbs, 1), round(fats, 1)


def generate_implicature(api_key, image_data_uri, age, weight, height, gender, meal_type):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    user_context = (
        f"This image is from a {meal_type}. The person consuming this food is {age} years old, "
        f"weighs {weight} kg, is {height} cm tall, and is {gender}. "
        "Please analyze the nutritional content of the food like calories, Proteins, carbohydrates and fats shown in the image and determine if it is appropriate "
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


def extract_daily_intake_info(response_text):
    match = re.search(
        r"(approximately\s*)?(about\s*)?(?P<portion>1/4|1/2|1/3|1/5|1/6|1/8|one[-\s]?(fourth|half|third))[^.,]*",
        response_text, re.IGNORECASE
    )
    return match.group(0).strip() if match else "Couldn't extract daily intake portion."


def extract_nutritional_values(response_text):
    nutrients = {
        "calories": None,
        "protein": None,
        "carbohydrates": None,
        "fat": None
    }

    patterns = {
        "calories": r"(?i)(?:\bcalories\b.*?)(\d{2,5})\s*k?cal",
        "protein": r"(?i)(?:\bprotein\b.*?)(\d{1,3}(?:\.\d+)?)\s*g",
        "carbohydrates": r"(?i)(?:\bcarbs?\b.*?)(\d{1,3}(?:\.\d+)?)\s*g",
        "fat": r"(?i)(?:\bfat\b.*?)(\d{1,3}(?:\.\d+)?)\s*g"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, response_text)
        if match:
            try:
                nutrients[key] = float(match.group(1))
            except:
                nutrients[key] = None

    return nutrients


def main():
    st.set_page_config(page_title="🍲 Food Nutrition Analyzer", layout="centered")

    st.title("🍽️ Smart Food Nutrition Analyzer")
    st.caption("Upload an image of your food to analyze its nutritional impact.")

    # API Key
    api_key = st.secrets["myconnection"]["YOUR_API_KEY"]

    # Sidebar Inputs
    with st.sidebar:
        st.header("👤 Your Information")
        user_name = st.text_input("Name", value="Parmanand Sahu")
        age = st.number_input("Age", min_value=1, max_value=120, value=34)
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=84.6)
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=172.0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

    # Initialize session state
    if "meals" not in st.session_state:
        st.session_state.meals = []

    # Calculate daily needs
    calories, protein, carbs, fats = get_daily_nutrition_requirements(age, weight, height, gender)

    # 🧮 Nutrient comparison table (Dynamic Columns)
    recommendation_data = {
        "Nutrient": ["Calories", "Protein (g)", "Carbohydrates (g)", "Fat (g)"],
        "Daily Requirement": [f"{calories} kcal", f"{protein} g", f"{carbs} g", f"{fats} g"]
    }

    # Add dynamic meal columns
    for i, meal in enumerate(st.session_state.meals):
        meal_col = f"Meal {i + 1} (Amount)"
        percent_col = f"Meal {i + 1} (%)"

        def percent(part, whole):
            return f"{round((part / whole) * 100)}%" if part and whole else "N/A"

        recommendation_data[meal_col] = [
            f"{meal['calories']} kcal" if meal["calories"] else "N/A",
            f"{meal['protein']} g" if meal["protein"] else "N/A",
            f"{meal['carbohydrates']} g" if meal["carbohydrates"] else "N/A",
            f"{meal['fat']} g" if meal["fat"] else "N/A",
        ]

        recommendation_data[percent_col] = [
            percent(meal["calories"], calories),
            percent(meal["protein"], protein),
            percent(meal["carbohydrates"], carbs),
            percent(meal["fat"], fats),
        ]

    # Add summary row for total intake
    total_intake = {
        "Calories": sum(meal["calories"] if meal["calories"] else 0 for meal in st.session_state.meals),
        "Protein": sum(meal["protein"] if meal["protein"] else 0 for meal in st.session_state.meals),
        "Carbs": sum(meal["carbohydrates"] if meal["carbohydrates"] else 0 for meal in st.session_state.meals),
        "Fat": sum(meal["fat"] if meal["fat"] else 0 for meal in st.session_state.meals)
    }

    recommendation_data["Total Intake"] = [
        f"{total_intake['Calories']} kcal",
        f"{total_intake['Protein']} g",
        f"{total_intake['Carbs']} g",
        f"{total_intake['Fat']} g"
    ]

    st.markdown(f"### 🧮 Recommended Daily Intake for **{user_name}**")
    st.markdown(f"**Age**: {age} | **Weight**: {weight} kg | **Height**: {height} cm")
    st.table(recommendation_data)

    # Show progress bars for each nutrient
    st.subheader("🌱 Progress toward Daily Nutrient Goals")
    st.progress(min(1.0, total_intake['Calories'] / calories), text=f"Calories: {total_intake['Calories']} / {calories}")
    st.progress(min(1.0, total_intake['Protein'] / protein), text=f"Protein: {total_intake['Protein']} / {protein}")
    st.progress(min(1.0, total_intake['Carbs'] / carbs), text=f"Carbs: {total_intake['Carbs']} / {carbs}")
    st.progress(min(1.0, total_intake['Fat'] / fats), text=f"Fat: {total_intake['Fat']} / {fats}")

    # Upload and analyze
    uploaded_file = st.file_uploader("📤 Upload your food image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
        mime_type = uploaded_file.type
        image_data_uri = f"data:{mime_type};base64,{base64_image}"

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_file, caption="🍱 Uploaded Meal", use_container_width=True)

        with col2:
            if st.button("🔍 Analyze Nutrition"):
                with st.spinner("🧠 Analyzing nutritional content..."):
                    result = generate_implicature(api_key, image_data_uri, age, weight, height, gender, meal_type)
                    intake_info = extract_daily_intake_info(result)
                    nutrient_vals = extract_nutritional_values(result)

                    # Save to session (limit to 3 meals)
                    if len(st.session_state.meals) >= 3:
                        st.session_state.meals.pop()
                    st.session_state.meals.insert(0, nutrient_vals)

                    st.success("✅ Analysis Complete!")
                    st.markdown(f"### 🥗 This meal provides **{intake_info}** of your daily intake.")

                    with st.expander("📋 Full Nutritional Analysis"):
                        st.markdown(result)

    # Optional: Meal History Summary
    if st.session_state.meals:
        st.markdown("## 🕘 Meal History")
        for i, meal in enumerate(st.session_state.meals):
            st.markdown(f"**Meal {i + 1}:**")
            st.markdown(f"- Calories: {meal['calories']} kcal")
            st.markdown(f"- Protein: {meal['protein']} g")
            st.markdown(f"- Carbs: {meal['carbohydrates']} g")
            st.markdown(f"- Fat: {meal['fat']} g")
            st.markdown("---")


if __name__ == "__main__":
    main()
