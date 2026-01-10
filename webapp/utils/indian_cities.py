"""
Comprehensive Indian Cities and States Data
Complete list of Indian states, cities, and postal codes
"""

from typing import Dict, List, Tuple

# Indian States and Union Territories
INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh", 
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
]

INDIAN_UNION_TERRITORIES = [
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry"
]

# Major cities by state
CITIES_BY_STATE = {
    "Andhra Pradesh": [
        "Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", 
        "Rajahmundry", "Kadapa", "Kakinada", "Anantapur", "Tirupati",
        "Vizianagaram", "Eluru", "Ongole", "Chittoor", "Machilipatnam"
    ],
    "Arunachal Pradesh": [
        "Itanagar", "Naharlagun", "Pasighat", "Tezpur", "Bomdila",
        "Ziro", "Along", "Basar", "Khonsa", "Tezu"
    ],
    "Assam": [
        "Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon",
        "Tinsukia", "Tezpur", "Bongaigaon", "Karimganj", "Sivasagar"
    ],
    "Bihar": [
        "Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia",
        "Darbhanga", "Bihar Sharif", "Arrah", "Begusarai", "Katihar",
        "Munger", "Chhapra", "Danapur", "Saharsa", "Hajipur"
    ],
    "Chhattisgarh": [
        "Raipur", "Bhilai", "Korba", "Bilaspur", "Durg",
        "Rajnandgaon", "Jagdalpur", "Raigarh", "Ambikapur", "Mahasamund"
    ],
    "Delhi": [
        "New Delhi", "Delhi", "North Delhi", "South Delhi", "East Delhi",
        "West Delhi", "Central Delhi", "North East Delhi", "North West Delhi",
        "South East Delhi", "South West Delhi", "Shahdara"
    ],
    "Goa": [
        "Panaji", "Vasco da Gama", "Margao", "Mapusa", "Ponda",
        "Bicholim", "Curchorem", "Sanquelim", "Cuncolim", "Quepem"
    ],
    "Gujarat": [
        "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar",
        "Jamnagar", "Junagadh", "Gandhinagar", "Anand", "Navsari",
        "Morbi", "Nadiad", "Surendranagar", "Bharuch", "Mehsana"
    ],
    "Haryana": [
        "Gurugram", "Faridabad", "Panipat", "Ambala", "Yamunanagar",
        "Rohtak", "Hisar", "Karnal", "Sonipat", "Panchkula",
        "Bhiwani", "Sirsa", "Bahadurgarh", "Jind", "Thanesar"
    ],
    "Himachal Pradesh": [
        "Shimla", "Dharamshala", "Solan", "Mandi", "Palampur",
        "Baddi", "Nahan", "Paonta Sahib", "Sundarnagar", "Chamba"
    ],
    "Jammu and Kashmir": [
        "Srinagar", "Jammu", "Baramulla", "Anantnag", "Sopore",
        "KathuaKathua", "Udhampur", "Punch", "Rajauri", "Kupwara"
    ],
    "Jharkhand": [
        "Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar",
        "Phusro", "Hazaribagh", "Giridih", "Ramgarh", "Medininagar"
    ],
    "Karnataka": [
        "Bangalore", "Mysore", "Hubli-Dharwad", "Mangalore", "Belgaum",
        "Gulbarga", "Davanagere", "Bellary", "Bijapur", "Shimoga",
        "Tumkur", "Raichur", "Bidar", "Hospet", "Hassan"
    ],
    "Kerala": [
        "Thiruvananthapuram", "Kochi", "Kozhikode", "Kollam", "Thrissur",
        "Alappuzha", "Palakkad", "Malappuram", "Kannur", "Kasaragod",
        "Kottayam", "Pathanamthitta", "Idukki", "Wayanad", "Ernakulam"
    ],
    "Ladakh": [
        "Leh", "Kargil", "Drass", "Zanskar", "Nubra"
    ],
    "Madhya Pradesh": [
        "Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain",
        "Sagar", "Dewas", "Satna", "Ratlam", "Rewa",
        "Murwara", "Singrauli", "Burhanpur", "Khandwa", "Bhind"
    ],
    "Maharashtra": [
        "Mumbai", "Pune", "Nagpur", "Thane", "Nashik",
        "Aurangabad", "Solapur", "Amravati", "Kolhapur", "Sangli",
        "Malegaon", "Akola", "Latur", "Dhule", "Ahmednagar",
        "Chandrapur", "Parbhani", "Jalgaon", "Bhiwandi", "Nanded"
    ],
    "Manipur": [
        "Imphal", "Thoubal", "Bishnupur", "Churachandpur", "Ukhrul"
    ],
    "Meghalaya": [
        "Shillong", "Tura", "Jowai", "Nongstoin", "Baghmara"
    ],
    "Mizoram": [
        "Aizawl", "Lunglei", "Saiha", "Champhai", "Kolasib"
    ],
    "Nagaland": [
        "Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha"
    ],
    "Odisha": [
        "Bhubaneswar", "Cuttack", "Rourkela", "Brahmapur", "Sambalpur",
        "Puri", "Balasore", "Bhadrak", "Baripada", "Jharsuguda"
    ],
    "Punjab": [
        "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda",
        "Mohali", "Firozpur", "Batala", "Pathankot", "Moga",
        "Abohar", "Malerkotla", "Khanna", "Phagwara", "Muktsar"
    ],
    "Rajasthan": [
        "Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer",
        "Udaipur", "Bhilwara", "Alwar", "Bharatpur", "Sikar",
        "Pali", "Tonk", "Kishangarh", "Beawar", "Hanumangarh"
    ],
    "Sikkim": [
        "Gangtok", "Namchi", "Gyalshing", "Mangan", "Soreng"
    ],
    "Tamil Nadu": [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
        "Tirunelveli", "Tiruppur", "Vellore", "Erode", "Thoothukkudi",
        "Dindigul", "Thanjavur", "Ranipet", "Sivakasi", "Karur"
    ],
    "Telangana": [
        "Hyderabad", "Warangal", "Nizamabad", "Khammam", "Karimnagar",
        "Mahbubnagar", "Nalgonda", "Adilabad", "Suryapet", "Miryalaguda"
    ],
    "Tripura": [
        "Agartala", "Udaipur", "Dharmanagar", "Kailasahar", "Belonia"
    ],
    "Uttar Pradesh": [
        "Lucknow", "Kanpur", "Ghaziabad", "Agra", "Meerut",
        "Varanasi", "Allahabad", "Bareilly", "Aligarh", "Moradabad",
        "Saharanpur", "Gorakhpur", "Noida", "Firozabad", "Jhansi",
        "Muzaffarnagar", "Mathura", "Rampur", "Shahjahanpur", "Farrukhabad"
    ],
    "Uttarakhand": [
        "Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rudrapur",
        "Kashipur", "Rishikesh", "Pithoragarh", "Jaspur", "Manglaur"
    ],
    "West Bengal": [
        "Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri",
        "Malda", "Bardhaman", "Barasat", "Raiganj", "Kharagpur",
        "Haldia", "Nabadwip", "Medinipur", "Jalpaiguri", "Balurghat"
    ]
}

# Union Territory Cities
UNION_TERRITORY_CITIES = {
    "Andaman and Nicobar Islands": [
        "Port Blair", "Bambooflat", "Garacharma", "Dignabad", "Haddo"
    ],
    "Chandigarh": [
        "Chandigarh", "Sector 17", "Sector 22", "Sector 35", "Mani Majra"
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        "Daman", "Diu", "Silvassa", "Vapi", "Dadra"
    ],
    "Lakshadweep": [
        "Kavaratti", "Agatti", "Minicoy", "Amini", "Andrott"
    ],
    "Puducherry": [
        "Puducherry", "Karaikal", "Yanam", "Mahe", "Villianur"
    ]
}

# Combine all cities for easy access
ALL_CITIES_BY_STATE = {**CITIES_BY_STATE, **UNION_TERRITORY_CITIES}

# Top 50 major cities for logistics
TOP_INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Surat", "Jaipur",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Vadodara", "Firozabad", "Ludhiana",
    "Rajkot", "Agra", "Siliguri", "Nashik", "Faridabad",
    "Patiala", "Ghaziabad", "Ludhiana", "Amritsar", "Allahabad",
    "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior",
    "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota",
    "Guwahati", "Chandigarh", "Solapur", "Hubli-Dharwad", "Tiruchirappalli",
    "Bareilly", "Mysore", "Tiruppur", "Gurgaon", "Aligarh"
]

# Postal code patterns by state
POSTAL_CODE_PATTERNS = {
    "Andhra Pradesh": {"start": "515", "end": "535"},
    "Arunachal Pradesh": {"start": "790", "end": "792"},
    "Assam": {"start": "781", "end": "788"},
    "Bihar": {"start": "800", "end": "855"},
    "Chhattisgarh": {"start": "490", "end": "497"},
    "Delhi": {"start": "110", "end": "110"},
    "Goa": {"start": "403", "end": "403"},
    "Gujarat": {"start": "360", "end": "396"},
    "Haryana": {"start": "121", "end": "136"},
    "Himachal Pradesh": {"start": "171", "end": "177"},
    "Jammu and Kashmir": {"start": "180", "end": "194"},
    "Jharkhand": {"start": "813", "end": "835"},
    "Karnataka": {"start": "560", "end": "591"},
    "Kerala": {"start": "670", "end": "695"},
    "Ladakh": {"start": "194", "end": "194"},
    "Madhya Pradesh": {"start": "450", "end": "488"},
    "Maharashtra": {"start": "400", "end": "445"},
    "Manipur": {"start": "795", "end": "795"},
    "Meghalaya": {"start": "793", "end": "794"},
    "Mizoram": {"start": "796", "end": "796"},
    "Nagaland": {"start": "797", "end": "798"},
    "Odisha": {"start": "751", "end": "770"},
    "Punjab": {"start": "140", "end": "160"},
    "Rajasthan": {"start": "301", "end": "345"},
    "Sikkim": {"start": "737", "end": "737"},
    "Tamil Nadu": {"start": "600", "end": "643"},
    "Telangana": {"start": "500", "end": "509"},
    "Tripura": {"start": "799", "end": "799"},
    "Uttar Pradesh": {"start": "201", "end": "285"},
    "Uttarakhand": {"start": "246", "end": "263"},
    "West Bengal": {"start": "700", "end": "743"}
}

# Popular landmarks for address confidence
COMMON_LANDMARKS = [
    "Metro Station", "Railway Station", "Bus Stand", "Airport",
    "Hospital", "School", "College", "University", "Temple",
    "Mosque", "Church", "Gurudwara", "Market", "Mall",
    "Shopping Center", "Police Station", "Post Office", "Bank",
    "ATM", "Petrol Pump", "Gas Station", "Park", "Garden",
    "Stadium", "Cinema Hall", "Restaurant", "Hotel", "Office Complex"
]

def get_cities_by_state(state: str) -> List[str]:
    """Get list of cities for a given state"""
    return ALL_CITIES_BY_STATE.get(state, [])

def get_all_states() -> List[str]:
    """Get list of all Indian states and union territories"""
    return INDIAN_STATES + INDIAN_UNION_TERRITORIES

def get_all_cities() -> List[str]:
    """Get list of all cities across India"""
    all_cities = []
    for cities in ALL_CITIES_BY_STATE.values():
        all_cities.extend(cities)
    return sorted(list(set(all_cities)))

def get_state_for_city(city: str) -> str:
    """Find state for a given city"""
    for state, cities in ALL_CITIES_BY_STATE.items():
        if city in cities:
            return state
    return "Unknown"

def validate_postal_code(postal_code: str, state: str) -> bool:
    """Validate postal code for a given state"""
    if len(postal_code) != 6 or not postal_code.isdigit():
        return False
    
    pattern = POSTAL_CODE_PATTERNS.get(state)
    if not pattern:
        return True  # Allow if pattern not defined
    
    code_prefix = postal_code[:3]
    start_prefix = pattern["start"]
    end_prefix = pattern["end"]
    
    return start_prefix <= code_prefix <= end_prefix

def get_city_suggestions(partial_name: str, limit: int = 10) -> List[str]:
    """Get city suggestions based on partial name"""
    all_cities = get_all_cities()
    suggestions = []
    
    partial_lower = partial_name.lower()
    
    # Exact match first
    for city in all_cities:
        if city.lower().startswith(partial_lower):
            suggestions.append(city)
            if len(suggestions) >= limit:
                break
    
    # Partial match if not enough exact matches
    if len(suggestions) < limit:
        for city in all_cities:
            if partial_lower in city.lower() and city not in suggestions:
                suggestions.append(city)
                if len(suggestions) >= limit:
                    break
    
    return suggestions

def get_nearby_cities(city: str, state: str = None) -> List[str]:
    """Get nearby cities (simplified - same state cities)"""
    if not state:
        state = get_state_for_city(city)
    
    if state == "Unknown":
        return []
    
    cities = get_cities_by_state(state)
    return [c for c in cities if c != city]

def is_major_city(city: str) -> bool:
    """Check if city is a major logistics hub"""
    return city in TOP_INDIAN_CITIES

def get_city_tier(city: str) -> str:
    """Get city tier classification"""
    city_index = None
    try:
        city_index = TOP_INDIAN_CITIES.index(city)
    except ValueError:
        pass
    
    if city_index is not None:
        if city_index < 8:
            return "Tier 1"
        elif city_index < 20:
            return "Tier 2"
        else:
            return "Tier 3"
    else:
        # Check if it's a state capital or major city
        state = get_state_for_city(city)
        if state != "Unknown":
            state_cities = get_cities_by_state(state)
            if state_cities and city == state_cities[0]:  # Usually capital is first
                return "Tier 2"
        
        return "Tier 4"

# Export data for easy import
__all__ = [
    'INDIAN_STATES', 'INDIAN_UNION_TERRITORIES', 'CITIES_BY_STATE',
    'TOP_INDIAN_CITIES', 'COMMON_LANDMARKS', 'get_cities_by_state',
    'get_all_states', 'get_all_cities', 'get_state_for_city',
    'validate_postal_code', 'get_city_suggestions', 'get_nearby_cities',
    'is_major_city', 'get_city_tier'
]