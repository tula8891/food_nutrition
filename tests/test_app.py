"""Test cases for the NutriVision AI application."""

import base64
import os
from typing import Dict
from unittest.mock import Mock, patch

from app import (
    extract_daily_intake_info,
    extract_nutritional_values,
    get_daily_nutrition_requirements,
    get_perplexity_response,
    img_to_base64,
    main,
    percent,
    show_landing_page,
    show_login_page,
)

# Removed unused imports


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


def test_img_to_base64() -> None:
    """Test the image to base64 conversion function."""
    # Create a temporary test image
    test_img_path = "test_img.png"
    with open(test_img_path, "wb") as f:
        f.write(b"fake image data")
    try:
        result = img_to_base64(test_img_path)
        assert isinstance(result, str)
        # Verify it's a valid base64 string
        base64.b64decode(result)
    finally:
        os.remove(test_img_path)


@patch("httpx.post")
def test_get_perplexity_response(mock_post: Mock) -> None:
    """Test the Perplexity API response function."""
    mock_response = Mock()
    mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    result = get_perplexity_response("test_key", "test_image", 30, 70, 170, "male", "breakfast")
    assert result == "Test response"


@patch("streamlit.markdown")
def test_show_login_page(mock_markdown: Mock) -> None:
    """Test the login page display function."""
    show_login_page()
    assert mock_markdown.call_count >= 1  # At least one markdown call is made


@patch("streamlit.markdown")
def test_show_landing_page(mock_markdown: Mock) -> None:
    """Test the landing page display function."""
    show_landing_page()
    assert mock_markdown.call_count >= 1  # At least one markdown call is made


@patch("streamlit.session_state")
def test_main(mock_session_state: Mock) -> None:
    """Test the main function."""
    main()
    # Verify that the main function runs without errors
    assert True  # If we get here, the function ran successfully
