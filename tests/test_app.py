"""Test cases for the NutriVision AI application."""

from typing import Dict

from app import (
    extract_daily_intake_info,
    extract_nutritional_values,
    generate_implicature,
    get_daily_nutrition_requirements,
    percent,
)


def test_percent() -> None:
    """Test the percent calculation function."""
    assert percent(50, 100) == 50.0
    assert percent(0, 100) == 0.0
    assert percent(100, 0) == 0.0


def test_get_daily_nutrition_requirements() -> None:
    """Test the daily nutrition requirements calculation."""
    requirements: Dict[str, float] = get_daily_nutrition_requirements(30, 70, 170, "male")
    assert "calories" in requirements
    assert "protein" in requirements
    assert "carbohydrates" in requirements
    assert "fat" in requirements
    assert all(isinstance(v, float) for v in requirements.values())


def test_generate_implicature() -> None:
    """Test the AI response generation function."""
    response: str = generate_implicature(
        "test_key",
        "test_image",
        30,
        70,
        170,
        "male",
        "breakfast",
    )
    assert isinstance(response, str)


def test_extract_daily_intake_info() -> None:
    """Test the daily intake information extraction."""
    response: str = "This meal provides approximately 1/4 of your daily intake."
    assert extract_daily_intake_info(response) == 0.25


def test_extract_nutritional_values() -> None:
    """Test the nutritional values extraction."""
    response: str = "Calories: 500 kcal, Protein: 20 g, Carbohydrates: 60 g, Fat: 15 g"
    values: Dict[str, float] = extract_nutritional_values(response)
    assert values["calories"] == 500.0
    assert values["protein"] == 20.0
    assert values["carbohydrates"] == 60.0
    assert values["fat"] == 15.0
