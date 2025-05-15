import streamlit as st
import httpx
import base64
import re


# --- Nutrition Calculation ---
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


# --- API Call ---
def generate_implicature(api_key, image_data_uri, age, weight, height, gender, meal_type):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    user_context = (
        "Given this meal: [detailed description], calculate and output the nutritional values using standard nutritional databases. "
        "Use EXACTLY this format, with each value on its own line and no extra text:\n\n"
        "Calories: [value] kcal\n"
        "Protein: [value] g\n"
        "Carbohydrates: [value] g\n"
        "Fats: [value] g\n"
        "Daily Intake Portion: [fraction]\n"
        "Do not summarize, explain, or add any extra text, formatting, or commentary. Output only the five lines above."
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


# --- Extract Portion Info ---
def extract_daily_intake_info(response_text):
    match = re.search(
        r"(approximately\s*)?(about\s*)?(?P<portion>1/4|1/2|1/3|1/5|1/6|1/8|one[-\s]?(fourth|half|third))[^.,]*",
        response_text, re.IGNORECASE
    )
    return match.group(0).strip() if match else "Couldn't extract daily intake portion."


# --- Extract Nutritional Values ---
def extract_nutritional_values(response_text):
    nutrients = {
        "calories": None,
        "protein": None,
        "carbohydrates": None,
        "fat": None
    }
    patterns = {
        "calories": r'(?i)(?:calories|kcal)\D*?(\d+\.?\d*)|(\d+\.?\d*)\s*(?:kcal|calories)',
        "protein": r'(?i)(?:protein|prot)\D*?(\d+\.?\d*)|(\d+\.?\d*)\s*(?:g|grams?)\s*(?:protein|prot)',
        "carbohydrates": r'(?i)(?:carbohydrates|carbs)\D*?(\d+\.?\d*)|(\d+\.?\d*)\s*(?:g|grams?)\s*(?:carbohydrates|carbs)',
        "fat": r'(?i)(?:fat|lipids)\D*?(\d+\.?\d*)|(\d+\.?\d*)\s*(?:g|grams?)\s*(?:fat|lipids)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text)
        if match:
            value = next((float(g) for g in match.groups() if g is not None), None)
            nutrients[key] = value
    return nutrients


# --- Meal Portion and Example Data ---
MEAL_DISTRIBUTION = {
    "Breakfast": 0.25,
    "Lunch": 0.35,
    "Dinner": 0.30,
    "Snack": 0.10
}
MEAL_EXAMPLES = {
    "Breakfast": [
        {"label": "Small", "desc": "Oatmeal (1/2 cup) with berries and almonds", "Calories": 220, "Protein": 7, "Carbs": 38, "Fat": 6},
        {"label": "Large", "desc": "2 eggs, 2 toast, 1 banana", "Calories": 420, "Protein": 20, "Carbs": 55, "Fat": 14}
    ],
    "Lunch": [
        {"label": "Small", "desc": "Grilled chicken salad (100g chicken, greens)", "Calories": 280, "Protein": 25, "Carbs": 10, "Fat": 12},
        {"label": "Large", "desc": "Brown rice bowl (1 cup rice, 100g paneer, veggies)", "Calories": 520, "Protein": 22, "Carbs": 70, "Fat": 14}
    ],
    "Dinner": [
        {"label": "Small", "desc": "Mixed veg stir-fry + tofu (100g)", "Calories": 250, "Protein": 15, "Carbs": 22, "Fat": 10},
        {"label": "Large", "desc": "Fish curry (120g) + 2 rotis + salad", "Calories": 480, "Protein": 28, "Carbs": 50, "Fat": 16}
    ],
    "Snack": [
        {"label": "Small", "desc": "Fruit yogurt (100g)", "Calories": 90, "Protein": 5, "Carbs": 15, "Fat": 1},
        {"label": "Large", "desc": "Peanut butter sandwich (1 slice bread, 1 tbsp PB)", "Calories": 180, "Protein": 6, "Carbs": 20, "Fat": 8}
    ]
}


# --- Main App ---
def main():
    st.set_page_config(page_title="🍲 Food Nutrition Analyzer", layout="centered")
    st.title("🍽️ Smart Food Nutrition Analyzer")
    st.caption("Upload or capture an image of your food to analyze its nutritional impact.")

    api_key = st.secrets["myconnection"]["YOUR_API_KEY"]

    # Sidebar Inputs
    with st.sidebar:
        st.header("👤 Your Information")
        user_name = st.text_input("🧑 Name", value="Parmanand Sahu", placeholder="Enter your full name")
        age = st.number_input("🎂 Age", min_value=1, max_value=120, value=34)
        weight = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=84.6)
        height = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=172.0)
        gender = st.selectbox("⚧️ Gender", ["Male", "Female", "Other"])
        meal_type = st.selectbox("🍽️ Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])

    # Session state for meals (history)
    if "meals" not in st.session_state:
        st.session_state.meals = []

    # Calculate daily needs
    calories, protein, carbs, fats = get_daily_nutrition_requirements(age, weight, height, gender)

    # --- Show meal-type nutrition requirement table ---
    meal_portion = MEAL_DISTRIBUTION.get(meal_type, 0.25)
    meal_targets = {
        "Calories": round(calories * meal_portion, 1),
        "Protein (g)": round(protein * meal_portion, 1),
        "Carbohydrates (g)": round(carbs * meal_portion, 1),
        "Fat (g)": round(fats * meal_portion, 1)
    }
    st.markdown(f"### 🍽️ {meal_type} Nutrition Targets (portion of daily)")
    st.table({
        "Nutrient": list(meal_targets.keys()),
        f"{meal_type} Target": list(meal_targets.values())
    })

    # --- Meal Examples Section ---
    st.markdown(f"### 🥗 {meal_type} Meal Examples")
    examples = MEAL_EXAMPLES[meal_type]
    col1, col2 = st.columns(2)
    for i, ex in enumerate(examples):
        with [col1, col2][i]:
            st.markdown(f"**{ex['label']} Portion**")
            st.markdown(f"{ex['desc']}")
            st.markdown(f"Calories: {ex['Calories']} kcal")
            st.markdown(f"Protein: {ex['Protein']}g | Carbs: {ex['Carbs']}g | Fat: {ex['Fat']}g")

    # --- Main daily nutrient table ---
    st.markdown(f"### 🧮 Recommended Daily Intake for **{user_name}**")
    st.markdown(f"**Age**: {age} | **Weight**: {weight} kg | **Height**: {height} cm")
    recommendation_data = {
        "Nutrient": ["Calories", "Protein (g)", "Carbohydrates (g)", "Fat (g)"],
        "Daily Requirement": [f"{calories} kcal", f"{protein} g", f"{carbs} g", f"{fats} g"]
    }
    # Add meal columns with meal type names
    for i, meal in enumerate(st.session_state.meals):
        meal_name = meal.get("meal_type", f"Meal {i + 1}")
        meal_col = f"{meal_name} (Amount)"
        percent_col = f"{meal_name} (%)"
        def percent(part, whole):
            return f"{round((part / whole) * 100)}%" if part and whole else "N/A"
        recommendation_data[meal_col] = [
            f"{meal['nutrition']['calories']} kcal" if meal["nutrition"]["calories"] else "N/A",
            f"{meal['nutrition']['protein']} g" if meal["nutrition"]["protein"] else "N/A",
            f"{meal['nutrition']['carbohydrates']} g" if meal["nutrition"]["carbohydrates"] else "N/A",
            f"{meal['nutrition']['fat']} g" if meal["nutrition"]["fat"] else "N/A",
        ]
        recommendation_data[percent_col] = [
            percent(meal["nutrition"]["calories"], calories),
            percent(meal["nutrition"]["protein"], protein),
            percent(meal["nutrition"]["carbohydrates"], carbs),
            percent(meal["nutrition"]["fat"], fats),
        ]
    # Add summary row for total intake
    total_intake = {
        "Calories": sum(meal["nutrition"]["calories"] or 0 for meal in st.session_state.meals),
        "Protein": sum(meal["nutrition"]["protein"] or 0 for meal in st.session_state.meals),
        "Carbs": sum(meal["nutrition"]["carbohydrates"] or 0 for meal in st.session_state.meals),
        "Fat": sum(meal["nutrition"]["fat"] or 0 for meal in st.session_state.meals)
    }
    recommendation_data["Total Intake"] = [
        f"{total_intake['Calories']} kcal",
        f"{total_intake['Protein']} g",
        f"{total_intake['Carbs']} g",
        f"{total_intake['Fat']} g"
    ]
    st.table(recommendation_data)

    # --- Progress bars for each nutrient (daily) ---
    st.subheader("🌱 Progress toward Daily Nutrient Goals")
    st.progress(min(1.0, total_intake['Calories'] / calories), text=f"Calories: {total_intake['Calories']} / {calories}")
    st.progress(min(1.0, total_intake['Protein'] / protein), text=f"Protein: {total_intake['Protein']} / {protein}")
    st.progress(min(1.0, total_intake['Carbs'] / carbs), text=f"Carbs: {total_intake['Carbs']} / {carbs}")
    st.progress(min(1.0, total_intake['Fat'] / fats), text=f"Fat: {total_intake['Fat']} / {fats}")

    # --- Progress for current meal type ---
    meal_intake = {"calories": 0, "protein": 0, "carbohydrates": 0, "fat": 0}
    for meal in st.session_state.meals:
        if meal.get("meal_type") == meal_type:
            for k in meal_intake:
                meal_intake[k] += meal["nutrition"].get(k, 0) or 0
    st.markdown(f"### 📊 {meal_type} Progress")
    st.progress(min(1.0, meal_intake['calories'] / meal_targets["Calories"]), text=f"Calories: {meal_intake['calories']} / {meal_targets['Calories']}")
    st.progress(min(1.0, meal_intake['protein'] / meal_targets["Protein (g)"]), text=f"Protein: {meal_intake['protein']} / {meal_targets['Protein (g)']}")
    st.progress(min(1.0, meal_intake['carbohydrates'] / meal_targets["Carbohydrates (g)"]), text=f"Carbs: {meal_intake['carbohydrates']} / {meal_targets['Carbohydrates (g)']}")
    st.progress(min(1.0, meal_intake['fat'] / meal_targets["Fat (g)"]), text=f"Fat: {meal_intake['fat']} / {meal_targets['Fat (g)']}")

    # --- Camera or File Upload ---
    st.markdown("### 📸 Capture or Upload Your Food Image")
    input_method = st.radio("Choose input method:", ["Camera", "File Upload"], horizontal=True)
    image_data_uri = None
    if input_method == "Camera":
        img_file_buffer = st.camera_input("Take a picture of your food")
        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()
            mime_type = getattr(img_file_buffer, "type", "image/jpeg")
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            image_data_uri = f"data:{mime_type};base64,{base64_image}"
    else:
        uploaded_file = st.file_uploader("Upload your food image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            base64_image = base64.b64encode(uploaded_file.read()).decode("utf-8")
            mime_type = uploaded_file.type
            image_data_uri = f"data:{mime_type};base64,{base64_image}"

    if image_data_uri is not None:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(image_data_uri, caption="🍱 Your Meal", use_container_width=True)
        with col2:
            if st.button("🔍 Analyze Nutrition"):
                with st.spinner("🧠 Analyzing nutritional content..."):
                    result = generate_implicature(api_key, image_data_uri, age, weight, height, gender, meal_type)
                    intake_info = extract_daily_intake_info(result)
                    nutrient_vals = extract_nutritional_values(result)
                    # Save to session (limit to 5 meals, with image and meal_type)
                    if len(st.session_state.meals) >= 5:
                        st.session_state.meals.pop()
                    st.session_state.meals.insert(0, {
                        "nutrition": nutrient_vals,
                        "image": image_data_uri,
                        "analysis": result,
                        "meal_type": meal_type
                    })
                    st.success("✅ Analysis Complete!")
                    st.markdown(f"### 🥗 This meal provides **{intake_info}** of your daily intake.")
                    with st.expander("📋 Full Nutritional Analysis"):
                        st.markdown(result)
                    st.rerun()  # Refresh to update progress and history

    # --- Meal History with Images ---
    if st.session_state.meals:
        st.markdown("## 🕘 Meal History (Last 5 Meals)")
        for i, meal in enumerate(st.session_state.meals):
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(meal["image"], use_container_width=True)
            with cols[1]:
                meal_name = meal.get("meal_type", f"Meal {i + 1}")
                st.markdown(f"**{meal_name}:**")
                st.markdown(f"- Calories: {meal['nutrition']['calories'] or 'N/A'} kcal")
                st.markdown(f"- Protein: {meal['nutrition']['protein'] or 'N/A'} g")
                st.markdown(f"- Carbs: {meal['nutrition']['carbohydrates'] or 'N/A'} g")
                st.markdown(f"- Fat: {meal['nutrition']['fat'] or 'N/A'} g")
                with st.expander("Show analysis"):
                    st.markdown(meal["analysis"])
            st.divider()


if __name__ == "__main__":
    main()
