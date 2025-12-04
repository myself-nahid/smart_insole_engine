import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "assets", "templates")
TEMP_DIR = os.path.join(BASE_DIR, "assets", "temp")

# Ensure directories exist
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Weight Logic Rules (Spec Part IV)
INFILL_RULES = {
    "light": {"max_weight": 50, "infill": 20},
    "medium": {"max_weight": 70, "infill": 30},
    "heavy": {"max_weight": 90, "infill": 40},
    "extra_heavy": {"max_weight": 110, "infill": 50},
    "robust": {"max_weight": 999, "infill": 60},
}