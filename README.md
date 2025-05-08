```markdown
# 🥗 Food Nutrition Analyzer from Image

Analyze the nutritional content of your meals directly from an image! This Streamlit app uses AI to assess whether a meal is appropriate for you based on your age, weight, height, gender, and meal type.

---

Live App: [Food Nutrition Analyzer](https://foodnutrition-bedw5i7pctwrb9zuvu3jzg.streamlit.app/)  
GitHub Repo: [github.com/tula8891/food_nutrition](https://github.com/tula8891/food_nutrition)

---

## Features

- Upload a food image and get nutritional analysis using AI.
- Personalized results based on user details (age, weight, height, gender, meal type).
- Estimates what portion of your recommended daily nutritional intake the meal provides.
- Simple, interactive web interface powered by Streamlit.

---

## How to Use

1. Open the App: Visit the [live app link](https://foodnutrition-bedw5i7pctwrb9zuvu3jzg.streamlit.app/).
2. Enter Details: Use the sidebar to input your age, weight, height, gender, and select the meal type.
3. Upload Image: Upload a photo of your meal (jpg, jpeg, or png).
4. Analyze: Click "Analyze Nutrition" to get instant feedback on the meal’s nutritional value and suitability for you.
5. View Results: The app will display a summary, including how much of your daily nutritional needs this meal covers.

---

## Installation (For Local Use)

1. Clone the repository:
    ```
    git clone https://github.com/tula8891/food_nutrition.git
    cd food_nutrition
    ```
2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Set up your API key in `.streamlit/secrets.toml`:
    ```
    [myconnection]
    YOUR_API_KEY = "your_perplexity_api_key_here"
    ```
4. Run the app:
    ```
    streamlit run app.py
    ```

---

## How It Works

- The app collects your personal details and meal image.
- The image is encoded and sent to an AI API along with your details.
- The AI analyzes the food, estimates nutritional content, and considers your physical characteristics and meal context.
- Results are displayed in an easy-to-read format within the app.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request via the [GitHub repository](https://github.com/tula8891/food_nutrition).

---

## License

This project is open-source. See the [GitHub repo](https://github.com/tula8891/food_nutrition) for details.

---
```

---
