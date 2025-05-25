"""NutriVision AI - An AI-powered nutrition assistant application.

This Streamlit application helps users analyze their food intake and provides
nutritional insights using AI-powered image analysis.
"""

import base64

# import io
# import os
import re
from typing import Dict, List, Optional, TypedDict  # Union

import httpx

# import openai
import pandas as pd
import streamlit as st

# from PIL import Image


class Meal(TypedDict):
    """Type definition for a meal entry."""

    nutrition: Dict[str, float]
    image: str
    analysis: str
    meal_type: str


class SessionState(TypedDict, total=False):
    """Type definition for session state."""

    authenticated: bool
    page: str
    meals: List[Meal]


def percent(part: float, whole: float) -> float:
    """Calculate percentage.

    Args:
        part: The part value.
        whole: The whole value.

    Returns:
        The percentage value.
    """
    return (part / whole) * 100 if whole != 0 else 0


def img_to_base64(img_path: str) -> str:
    """Convert an image file to base64 string.

    Args:
        img_path: Path to the image file.

    Returns:
        Base64 encoded string of the image.
    """
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


img_base64 = img_to_base64("test4.png")
img_html = f"""
<div style="display:flex;align-items:center;gap:0.5rem;">
    <img src="data:image/jpeg;base64,{img_base64}" width="1200", height="500"/>
</div>
"""
img_base64 = img_to_base64("3.jpeg")
img2_html = f"""
<div style="display:flex;align-items:center;gap:0.5rem;">
    <img src="data:image/jpeg;base64,{img_base64}" width="1200", height="500"/>
</div>
"""


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="🍽️ NutriVision AI",
    page_icon="🍽️",
)

# --- DUMMY CREDENTIALS ---
DUMMY_EMAIL = "test@example.com"
DUMMY_PASSWORD = "test123"

# Initialize session state with proper types
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "home"

if "meals" not in st.session_state:
    st.session_state.meals = []

# --- MODERN CARD CSS ---
st.markdown(
    """
<style>
body {
    background: #f7f9fa;
}
.card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08), 0 1.5px 6px rgba(0,0,0,0.05);
    padding: 2rem 2.5rem;
    margin: 1.5rem auto;
    max-width: 420px;
}
.card-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.card-sub {
    color: #666;
    font-size: 1.1rem;
    margin-bottom: 1.2rem;
}
.feature-row {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
@media (min-width: 650px) {
    .feature-row {
        flex-direction: row;
        justify-content: space-between;
    }
}
.feature-card {
    background: #f4f7fb;
    border-radius: 10px;
    padding: 1rem;
    flex: 1;
    min-width: 120px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.how-card {
    background: #f9fafb;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-top: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.login-card {
    margin-top: 2rem;
    background: #fff;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.login-demo {
    color: #222;
    font-size: 1.13rem;
    margin-bottom: 0.7rem;
}
/* Custom button styling */
.stButton > button {
    padding: .2rem 1rem;
    border: 1px solid #4CAF50;
    background-color: #4CAF50;
    color: white;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s ease;
    border-radius: 8px;
    width: 100%;
}

.stButton > button:hover {
    background-color: #45a049;
}

.btn-group {
    display: flex;
    gap: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)


def show_login_page() -> None:
    """Display the login page with email and password inputs."""
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <img src="https://img.icons8.com/color/96/000000/healthy-food.png" width="48"/>
            <span style="font-size:1.5rem;font-weight:600;">NutriVision AI</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
            <div style="font-size:0.9rem;color:gray;">
                Snap. Analyze. Eat Smarter.<br>
                Your AI-powered nutrition assistant.
            </div>
            """,
        unsafe_allow_html=True,
    )

    # st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("### 🔐 Login")
    st.markdown(f"<div class='login-demo'>Demo: <b>{DUMMY_EMAIL}</b> / <b>{DUMMY_PASSWORD}</b></div>", unsafe_allow_html=True)
    email = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

    st.markdown('<div class="btn-group">', unsafe_allow_html=True)
    if st.button("Login", key="login_button"):
        if email == DUMMY_EMAIL and password == DUMMY_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials. Use the demo login above.")
    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def show_landing_page() -> None:
    """Display the landing page with features and how it works sections."""
    # Create two columns
    col1, col2 = st.columns([2, 1])  # Adjust the ratio if needed

    with col1:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:0.5rem;">
                <img src="https://img.icons8.com/color/96/000000/healthy-food.png" width="48"/>
                <span style="font-size:1.5rem;font-weight:600;">NutriVision AI</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="font-size:1rem;color:gray;">
                Snap. Analyze. Eat Smarter.<br>
                Your AI-powered nutrition assistant.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown('<div class="btn-group">', unsafe_allow_html=True)
        if st.button("Login"):
            st.session_state.page = "login"
            st.rerun()
        if st.button("Sign Up"):
            st.info("Sign up functionality coming soon!")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Features Card ---
    st.markdown('<div class="feature-row">', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="feature-card"><b>📸 Instant Analysis</b><br>Photo to insights</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="feature-card"><b>📊 Smart Tracking</b><br>Personalized daily goals</div>', unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="feature-card"><b>🎯 Simple & Secure</b><br>Private and easy to use</div>', unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(img_html, unsafe_allow_html=True)

    # --- How it works Card ---
    st.markdown('<div class="feature-row">', unsafe_allow_html=True)
    st.markdown(
        """
     <div class="how-card" style="font-size:36px; font-weight:bold; text-align:center;">
        How it works ?
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(img2_html, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="how-card" style="font-size:36px; font-weight:bold; text-align:center;">
            Why You'll Love It
        </div>
        """,
        unsafe_allow_html=True,
    )
    # --- Features Card ---
    st.markdown('<div class="feature-row">', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="feature-card"><b>⏰ Time Saving</b><br>No manual <br> calorie <br> tracking needed</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="feature-card"><b>📊 Informed Choices</b><br>Make smart <br>dietary <br>decisions</div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            '<div class="feature-card"><b>📱 Device Friendly</b><br>Use on<br> any<br> device</div>', unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="how-card" style="font-size:36px; font-weight:bold; text-align:center;">
        Who Needs This?
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Features Card ---
    st.markdown('<div class="feature-row">', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="feature-card"><b>🏃 Health Enthusiasts</b><br>Track macros <br>effortlessly</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="feature-card"><b>🏋️ Fitness Pros</b><br>Advise clients with <br> precision</div>', unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="feature-card"><b>👨‍👩‍👧‍👦 Parents</b><br>Plan balanced meals for <br> kids</div>', unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # footer
    st.markdown(
        """
    <hr style="margin-top: 50px;">
    <div style="text-align: center; color: gray; font-size: 14px;">
        &copy; 2025 All rights reserved.<br>
        Developed by <a href="https://parmanandsahu.com/" target="_blank" style="color: blue;">Parmanand Sahu</a>
        & <a href="https://in.linkedin.com/in/tula-ram-sahu-003226104" target="_blank" style="color: blue;">Tula Ram Sahu</a>
    </div>
    """,
        unsafe_allow_html=True,
    )


def get_daily_nutrition_requirements(age: int, weight: float, height: float, gender: str) -> Dict[str, float]:
    """Calculate daily nutrition requirements based on user metrics.

    Args:
        age: User's age in years.
        weight: User's weight in kg.
        height: User's height in cm.
        gender: User's gender ('male' or 'female').

    Returns:
        Dictionary containing daily nutrition requirements.
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity factor (moderate activity)
    tdee = bmr * 1.55

    # Macronutrient distribution
    protein = weight * 2.2  # 2.2g per kg of body weight
    fat = (tdee * 0.25) / 9  # 25% of calories from fat
    carbs = (tdee - (protein * 4) - (fat * 9)) / 4  # Remaining calories from carbs

    return {
        "calories": tdee,
        "protein": protein,
        "carbohydrates": carbs,
        "fat": fat,
    }


def get_perplexity_response(
    api_key: str,
    image_data_uri: str,
    age: int,
    weight: float,
    height: float,
    gender: str,
    meal_type: str,
) -> str:
    """Generate nutritional analysis using Perplexity AI.

    Args:
        api_key: API key for the Perplexity AI service.
        image_data_uri: Base64 encoded image data.
        age: User's age in years.
        weight: User's weight in kg.
        height: User's height in cm.
        gender: User's gender ('male' or 'female').
        meal_type: Type of meal being analyzed.

    Returns:
        str: AI-generated nutritional analysis text.
    """
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    user_context = (
        "Given this meal: [detailed description], calculate and output the nutritional values "
        "using standard nutritional databases. Use EXACTLY this format, with each value on its "
        "own line and no extra text:\n\n"
        "Calories: [value] kcal\n"
        "Protein: [value] g\n"
        "Carbohydrates: [value] g\n"
        "Fats: [value] g\n"
        "Daily Intake Portion: [fraction]\n"
        "Do not summarize, explain, or add any extra text, formatting, or commentary. "
        "Output only the five lines above."
        "after analyzing the image, give me complete nutrient of food other than above mentioned"
    )
    data = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_context},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_uri},
                    },
                ],
            },
        ],
    }
    try:
        timeout = httpx.Timeout(30.0, read=30.0)
        response = httpx.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return ""


def extract_daily_intake_info(response_text: str) -> float:
    """Extract daily intake information from AI response text.

    Args:
        response_text: AI response text containing daily intake information

    Returns:
        float: Portion of daily intake (0.0 to 1.0)
    """
    patterns = [
        r"(\d+)/(\d+)\s+of your daily",
        r"(\d+)%\s+of your daily",
        r"(\d+)\s+percent\s+of your daily",
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            if "/" in pattern:
                return float(match.group(1)) / float(match.group(2))
            return float(match.group(1)) / 100
    return 0.0


def extract_nutritional_values(response_text: str) -> Dict[str, float]:
    """Extract nutritional values from AI response text.

    Args:
        response_text: AI response text containing nutritional information

    Returns:
        Dict[str, float]: Dictionary of nutritional values
    """
    patterns = {
        "calories": r"Calories:\s*(\d+(?:\.\d+)?)\s*(?:kcal|calories)?",
        "protein": r"Protein:\s*(\d+(?:\.\d+)?)\s*(?:g|grams)?",
        "carbohydrates": r"Carbohydrates:\s*(\d+(?:\.\d+)?)\s*(?:g|grams)?",
        "fat": r"(?:Fat|Fats):\s*(\d+(?:\.\d+)?)\s*(?:g|grams)?",
    }

    values = {}
    for nutrient, pattern in patterns.items():
        match = re.search(pattern, response_text, re.IGNORECASE)
        values[nutrient] = float(match.group(1)) if match else 0.0
    return values


def main() -> None:
    """Run the main application."""
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if not st.session_state.authenticated:
        if st.session_state.page == "login":
            show_login_page()
        else:
            show_landing_page()
        return

    st.title("🍽️ Smart Food Nutrition Analyzer")
    st.caption("Upload or capture an image of your food to analyze its nutritional impact.")

    api_key = st.secrets["myconnection"]["YOUR_API_KEY"]

    with st.sidebar:
        st.header("👤 Your Information")
        user_name = st.text_input(
            "🧑 Name",
            value="Parmanand Sahu",
            placeholder="Enter your full name",
        )
        age = st.number_input("🎂 Age", min_value=1, max_value=120, value=34)
        weight = st.number_input(
            "⚖️ Weight (kg)",
            min_value=10.0,
            max_value=300.0,
            value=84.6,
        )
        height = st.number_input(
            "📏 Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=172.0,
        )
        gender = st.selectbox("⚧️ Gender", ["Male", "Female", "Other"])
        meal_type = st.selectbox(
            "🍽️ Meal Type",
            ["Breakfast", "Lunch", "Dinner", "Snack"],
        )

        st.markdown("---")
        if st.button("🚪 Logout", key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.page = "login"
            st.rerun()

    daily_requirements = get_daily_nutrition_requirements(age, weight, height, gender)

    st.markdown(f"### 🧮 Recommended Daily Intake for **{user_name}**")
    st.markdown(f"**Age**: {age} | **Weight**: {weight} kg | **Height**: {height} cm")

    # Create the base data structure
    table_data = {
        "Nutrient": ["Calories", "Protein (g)", "Carbohydrates (g)", "Fat (g)"],
        "Daily Requirement": [
            f"{daily_requirements['calories']} kcal",
            f"{daily_requirements['protein']} g",
            f"{daily_requirements['carbohydrates']} g",
            f"{daily_requirements['fat']} g",
        ],
    }

    # Process each meal
    for i, meal in enumerate(st.session_state.meals):
        meal_name = meal.get("meal_type", f"Meal {i + 1}")
        nutritional_values = extract_nutritional_values(meal["analysis"])
        meal["nutrition"] = nutritional_values

        # Add meal amounts
        table_data[f"{meal_name} (Amount)"] = [
            f"{nutritional_values['calories']} kcal" if nutritional_values["calories"] else "N/A",
            f"{nutritional_values['protein']} g" if nutritional_values["protein"] else "N/A",
            f"{nutritional_values['carbohydrates']} g" if nutritional_values["carbohydrates"] else "N/A",
            f"{nutritional_values['fat']} g" if nutritional_values["fat"] else "N/A",
        ]

        # Add meal percentages
        table_data[f"{meal_name} (%)"] = [
            (
                f"{percent(nutritional_values['calories'], daily_requirements['calories'])}%"
                if nutritional_values["calories"]
                else "N/A"
            ),
            (
                f"{percent(nutritional_values['protein'], daily_requirements['protein'])}%"
                if nutritional_values["protein"]
                else "N/A"
            ),
            (
                f"{percent(nutritional_values['carbohydrates'], daily_requirements['carbohydrates'])}%"
                if nutritional_values["carbohydrates"]
                else "N/A"
            ),
            f"{percent(nutritional_values['fat'], daily_requirements['fat'])}%" if nutritional_values["fat"] else "N/A",
        ]

    # Display the table
    df = pd.DataFrame(table_data)
    st.table(df)

    # Calculate total intake
    total_intake = {
        "calories": sum(float(meal["nutrition"]["calories"] or 0) for meal in st.session_state.meals),
        "protein": sum(float(meal["nutrition"]["protein"] or 0) for meal in st.session_state.meals),
        "carbohydrates": sum(float(meal["nutrition"]["carbohydrates"] or 0) for meal in st.session_state.meals),
        "fat": sum(float(meal["nutrition"]["fat"] or 0) for meal in st.session_state.meals),
    }

    st.subheader("🌱 Progress toward Daily Nutrient Goals")
    st.progress(
        min(1.0, total_intake["calories"] / daily_requirements["calories"]),
        text=f"Calories: {total_intake['calories']:.0f} / {daily_requirements['calories']} kcal",
    )
    st.progress(
        min(1.0, total_intake["protein"] / daily_requirements["protein"]),
        text=f"Protein: {total_intake['protein']:.0f} / {daily_requirements['protein']} g",
    )
    st.progress(
        min(1.0, total_intake["carbohydrates"] / daily_requirements["carbohydrates"]),
        text=f"Carbs: {total_intake['carbohydrates']:.0f} / {daily_requirements['carbohydrates']} g",
    )
    st.progress(
        min(1.0, total_intake["fat"] / daily_requirements["fat"]),
        text=f"Fat: {total_intake['fat']:.0f} / {daily_requirements['fat']} g",
    )

    st.markdown("### 📸 Capture or Upload Your Food Image")
    input_method = st.radio(
        "Choose input method:",
        ["Camera", "File Upload"],
        horizontal=True,
    )

    image_data_uri: Optional[str] = None
    if input_method == "Camera":
        img_file_buffer = st.camera_input("Take a picture of your food")
        if img_file_buffer is not None:
            bytes_data = img_file_buffer.getvalue()
            mime_type = getattr(img_file_buffer, "type", "image/jpeg")
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            image_data_uri = f"data:{mime_type};base64,{base64_image}"
    else:
        uploaded_file = st.file_uploader(
            "Upload your food image",
            type=["jpg", "jpeg", "png"],
        )
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
                    result = get_perplexity_response(
                        api_key,
                        image_data_uri,
                        age,
                        weight,
                        height,
                        gender,
                        meal_type,
                    )
                    intake_info = extract_daily_intake_info(result)
                    nutrient_vals = extract_nutritional_values(result)
                    if len(st.session_state.meals) >= 5:
                        st.session_state.meals.pop()
                    st.session_state.meals.insert(
                        0,
                        {
                            "nutrition": nutrient_vals,
                            "image": image_data_uri,
                            "analysis": result,
                            "meal_type": meal_type,
                        },
                    )
                    st.success("✅ Analysis Complete!")
                    st.markdown(f"### 🥗 This meal provides **{intake_info * 100:.1f}%** of your daily intake.")
                    with st.expander("📋 Full Nutritional Analysis"):
                        st.markdown(result)
                    st.rerun()

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
