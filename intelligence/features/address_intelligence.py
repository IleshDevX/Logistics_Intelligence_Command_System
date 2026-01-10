"""
Address Intelligence Module - NLP + Last-Mile Feasibility

Purpose: Convert messy Indian addresses into actionable intelligence
Output: Landmarks, Area Type, Confidence Score, Clarification Flag
Approach: Rule-based NLP (industry-realistic, no heavy ML)

This feeds into:
- Risk Engine (Step 6)
- Pre-Dispatch Alerts (Step 9)
- Hyper-Local Vehicle Selector
"""

import re

# India-specific landmark keywords
LANDMARK_KEYWORDS = [
    "temple", "mandir", "masjid", "church",
    "school", "college", "hospital",
    "metro", "station", "bus stand",
    "market", "bazaar", "mall",
    "bank", "atm", "park"
]

# Low confidence threshold (locked)
LOW_CONFIDENCE_THRESHOLD = 60


def clean_address(text: str) -> str:
    """
    Clean and normalize raw address text.
    
    Parameters:
        text (str): Raw address text from customer
    
    Returns:
        str: Cleaned, lowercase, normalized text
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_landmarks(cleaned_text: str):
    """
    Extract landmark keywords from cleaned address text.
    
    Parameters:
        cleaned_text (str): Cleaned address text
    
    Returns:
        list: List of detected landmarks
    """
    landmarks = []
    for word in LANDMARK_KEYWORDS:
        if word in cleaned_text:
            landmarks.append(word)
    return landmarks


def infer_area_type(cleaned_text: str):
    """
    Infer area type from address keywords (fallback logic).
    
    Parameters:
        cleaned_text (str): Cleaned address text
    
    Returns:
        str: "Old City", "Planned", "Rural", or "Semi-Urban"
    """
    # Check rural first (more specific)
    if any(word in cleaned_text for word in ["village", "gaon"]):
        return "Rural"
    # Check planned areas
    if any(word in cleaned_text for word in ["sector", "phase", "block"]):
        return "Planned"
    # Check old city
    if any(word in cleaned_text for word in ["gali", "lane", "chowk", "old"]):
        return "Old City"
    return "Semi-Urban"


def calculate_address_confidence(
    cleaned_text,
    landmarks,
    area_type,
    road_accessibility
):
    """
    Calculate address confidence score (0-100).
    
    Scoring Logic:
    - Base: 50 points
    - Single landmark: +20
    - Multiple landmarks (2+): +30
    - Old City: -15
    - Rural: -10
    - Narrow roads: -20
    - Vague language: -10
    
    Parameters:
        cleaned_text (str): Cleaned address text
        landmarks (list): Detected landmarks
        area_type (str): Area classification
        road_accessibility (str): Road condition
    
    Returns:
        int: Confidence score 0-100
    """
    score = 50  # base confidence

    # Landmarks
    if len(landmarks) == 1:
        score += 20
    elif len(landmarks) >= 2:
        score += 30

    # Area penalty
    if area_type == "Old City":
        score -= 15
    elif area_type == "Rural":
        score -= 10

    # Road penalty
    if road_accessibility == "Narrow":
        score -= 20

    # Vague language penalty
    if any(word in cleaned_text for word in ["near", "behind", "opposite"]):
        score -= 10

    return max(0, min(100, score))


def needs_clarification(address_confidence_score):
    """
    Determine if address needs clarification before dispatch.
    
    Parameters:
        address_confidence_score (int): Confidence score 0-100
    
    Returns:
        bool: True if clarification needed (score < 60)
    """
    return address_confidence_score < LOW_CONFIDENCE_THRESHOLD


def process_address(raw_address, road_accessibility, existing_area_type=None):
    """
    End-to-end address intelligence processing.
    
    Parameters:
        raw_address (str): Raw address text from customer
        road_accessibility (str): Road condition (Wide/Medium/Narrow)
        existing_area_type (str, optional): Pre-classified area type
    
    Returns:
        dict: Complete address intelligence output
            - cleaned_address: Normalized text
            - landmarks: List of detected landmarks
            - area_type: Classified area type
            - address_confidence_score: 0-100 score
            - needs_clarification: Boolean flag
    """
    cleaned = clean_address(raw_address)
    landmarks = extract_landmarks(cleaned)
    area_type = existing_area_type or infer_area_type(cleaned)
    confidence = calculate_address_confidence(
        cleaned, landmarks, area_type, road_accessibility
    )
    clarification_flag = needs_clarification(confidence)

    return {
        "cleaned_address": cleaned,
        "landmarks": landmarks,
        "area_type": area_type,
        "address_confidence_score": confidence,
        "needs_clarification": clarification_flag
    }
