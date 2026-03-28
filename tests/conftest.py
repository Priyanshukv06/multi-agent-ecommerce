import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()


# ── Shared state fixtures ───────────────────────────────────────────────────

@pytest.fixture
def base_state():
    """Minimal valid EcommerceState for testing."""
    return {
        "user_query":             "I want a machine learning book under ₹1000",
        "conversation_history":   [],
        "intent":                 "",
        "plan":                   [],
        "budget":                 1000.0,
        "category":               "machine learning",
        "product_list":           [],
        "research_data":          [],
        "comparison_result":      None,
        "final_answer":           "",
        "recommended_product_id": None,
        "validation_score":       0.0,
        "validation_feedback":    None,
        "retry_count":            0,
        "order_status":           None,
        "order_id":               None,
        "error":                  None,
        "current_node":           "start"
    }


@pytest.fixture
def mock_products():
    """Sample products for testing without DB calls."""
    return [
        {
            "id": 1,
            "title": "Hands-On Machine Learning",
            "author": "Aurélien Géron",
            "price": 899.0,
            "rating": 4.9,
            "category": "machine learning",
            "description": "Practical ML book covering full pipeline.",
            "reviews": [
                "Best ML book ever. Very practical.",
                "Covers everything from basics to neural networks.",
                "Perfect for hands-on learners."
            ]
        },
        {
            "id": 2,
            "title": "Python Machine Learning",
            "author": "Sebastian Raschka",
            "price": 750.0,
            "rating": 4.7,
            "category": "machine learning",
            "description": "Comprehensive ML with Python.",
            "reviews": [
                "Great balance of theory and practice.",
                "Sebastian explains concepts clearly.",
                "Good for intermediate learners."
            ]
        },
        {
            "id": 3,
            "title": "Introduction to ML with Python",
            "author": "Andreas Müller",
            "price": 649.0,
            "rating": 4.5,
            "category": "machine learning",
            "description": "Beginner-friendly ML with Scikit-Learn.",
            "reviews": [
                "Perfect for beginners.",
                "No scary math, clean code.",
                "Great first ML book."
            ]
        }
    ]


@pytest.fixture
def mock_research_data():
    """Sample research data for testing."""
    return [
        {
            "product_id": 1,
            "title": "Hands-On Machine Learning",
            "pros": ["Very practical", "Full pipeline coverage", "Exercises in each chapter"],
            "cons": ["Slightly advanced for beginners"],
            "difficulty_level": "intermediate",
            "use_cases": ["Python developers learning ML", "Hands-on learners"],
            "summary": "Best practical ML book available."
        },
        {
            "product_id": 2,
            "title": "Python Machine Learning",
            "pros": ["Balance of theory and code", "Clear explanations", "NLP coverage"],
            "cons": ["Dense chapters", "Better for intermediate"],
            "difficulty_level": "intermediate",
            "use_cases": ["Intermediate Python developers", "Theory + practice seekers"],
            "summary": "Comprehensive ML with solid theory."
        },
        {
            "product_id": 3,
            "title": "Introduction to ML with Python",
            "pros": ["Beginner friendly", "Clean code examples", "Scikit-Learn focused"],
            "cons": ["Not very deep", "Limited advanced topics"],
            "difficulty_level": "beginner",
            "use_cases": ["Absolute beginners", "Non-math learners"],
            "summary": "Best first ML book for beginners."
        }
    ]


@pytest.fixture
def mock_comparison_result():
    return {
        "ranked_products": [
            {"rank": 1, "product_id": 1, "title": "Hands-On Machine Learning",
             "total_score": 34, "price_value": 7, "beginner_friendly": 6,
             "content_depth": 11, "rating_score": 10}
        ],
        "best_choice_id": 1,
        "scoring_table":  [],
        "reasoning": "Best combination of rating, depth and practical approach."
    }
