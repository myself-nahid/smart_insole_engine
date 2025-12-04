from app.config import INFILL_RULES

def calculate_infill(weight_kg):
    """
    Spec Part IV: Intelligent Infill Calculation
    """
    if weight_kg < INFILL_RULES["light"]["max_weight"]:
        return INFILL_RULES["light"]["infill"]
    elif weight_kg < INFILL_RULES["medium"]["max_weight"]:
        return INFILL_RULES["medium"]["infill"]
    elif weight_kg < INFILL_RULES["heavy"]["max_weight"]:
        return INFILL_RULES["heavy"]["infill"]
    elif weight_kg < INFILL_RULES["extra_heavy"]["max_weight"]:
        return INFILL_RULES["extra_heavy"]["infill"]
    else:
        return INFILL_RULES["robust"]["infill"]