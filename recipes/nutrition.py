import requests
import os
import time

USDA_API_KEY = os.getenv('27m65Xj0sxPMfSg3Zsbd1FmDo4nawgel2vLHnmlq')
# SEARCH_URL = 'https://api.nal.usda.gov/fdc/v1/foods/search'
# DETAIL_URL = 'https://api.nal.usda.gov/fdc/v1/food/'

# def get_fdc_id(ingredient):
#     params = {
#         'api_key': USDA_API_KEY,
#         'query': ingredient,
#         'pageSize': 1
#     }
#     resp = requests.get(SEARCH_URL, params=params)
#     if resp.status_code == 200:
#         foods = resp.json().get('foods', [])
#         if foods:
#             return foods[0]['fdcId']
#     return None

# def get_nutrition(fdc_id):
#     params = {'api_key': USDA_API_KEY}
#     resp = requests.get(f"{DETAIL_URL}{fdc_id}", params=params)
#     if resp.status_code == 200:
#         data = resp.json()
#         nutrients = {}
#         for n in data.get('foodNutrients', []):
#             # Some entries may not have 'nutrientName'
#             name = n.get('nutrientName') or n.get('name')
#             if not name:
#                 continue
#             nutrients[name] = n.get('value', 0)
#         return {
#             'calories': nutrients.get('Energy', 0),
#             'protein': nutrients.get('Protein', 0),
#             'fat': nutrients.get('Total lipid (fat)', 0),
#             'carbs': nutrients.get('Carbohydrate, by difference', 0)
#         }
#     return {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

# def analyze_nutrition(ingredients):
#     total = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
#     for ing in ingredients:
#         fdc_id = get_fdc_id(ing)
#         if fdc_id:
#             nut = get_nutrition(fdc_id)
#             total['calories'] += nut['calories']
#             total['protein'] += nut['protein']
#             total['fat'] += nut['fat']
#             total['carbs'] += nut['carbs']
#     return total
SEARCH_URL = 'https://api.nal.usda.gov/fdc/v1/foods/search'
DETAIL_URL = 'https://api.nal.usda.gov/fdc/v1/food/'

# Fallback nutrition data for common ingredients
FALLBACK_NUTRITION = {
    'milk': {'calories': 42, 'protein': 3.4, 'fat': 1.0, 'carbs': 5.0, 'fiber': 0.0},
    'flour': {'calories': 364, 'protein': 10.0, 'fat': 1.0, 'carbs': 76.0, 'fiber': 2.7},
    'egg': {'calories': 68, 'protein': 6.0, 'fat': 5.0, 'carbs': 1.0, 'fiber': 0.0},
    'butter': {'calories': 102, 'protein': 0.1, 'fat': 12.0, 'carbs': 0.0, 'fiber': 0.0},
    'sugar': {'calories': 387, 'protein': 0.0, 'fat': 0.0, 'carbs': 100.0, 'fiber': 0.0},
    'salt': {'calories': 0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0, 'fiber': 0.0},
    'oil': {'calories': 884, 'protein': 0.0, 'fat': 100.0, 'carbs': 0.0, 'fiber': 0.0},
    'water': {'calories': 0, 'protein': 0.0, 'fat': 0.0, 'carbs': 0.0, 'fiber': 0.0},
    'almond milk': {'calories': 17, 'protein': 0.6, 'fat': 1.2, 'carbs': 0.3, 'fiber': 0.0},
    'almond flour': {'calories': 570, 'protein': 21.0, 'fat': 50.0, 'carbs': 21.0, 'fiber': 10.0},
    'vegan butter': {'calories': 90, 'protein': 0.0, 'fat': 10.0, 'carbs': 0.0, 'fiber': 0.0},
    'flaxseed meal': {'calories': 37, 'protein': 1.3, 'fat': 3.0, 'carbs': 2.0, 'fiber': 2.8},
}

def get_fdc_id(ingredient):
    """Get FDC ID for an ingredient from USDA API"""
    try:
        # Clean ingredient name - remove measurements and common words
        clean_ingredient = clean_ingredient_name(ingredient)
        
        params = {
            'api_key': USDA_API_KEY,
            'query': clean_ingredient,
            'pageSize': 1,
            'dataType': ['Foundation', 'SR Legacy']
        }
        
        resp = requests.get(SEARCH_URL, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            foods = data.get('foods', [])
            if foods:
                return foods[0]['fdcId']
        
        return None
    except Exception as e:
        print(f"Error getting FDC ID for {ingredient}: {e}")
        return None

def clean_ingredient_name(ingredient):
    """Clean ingredient name by removing measurements and common words"""
    import re
    
    # Remove common measurements
    measurements = r'\d+(?:\.\d+)?\s*(?:cup|tbsp|tsp|gram|g|ounce|oz|pound|lb|ml|l|kg|teaspoon|tablespoon|pound|pounds|cups?|tablespoons?|teaspoons?)'
    cleaned = re.sub(measurements, '', ingredient, flags=re.IGNORECASE)
    
    # Remove common words
    common_words = ['fresh', 'dried', 'ground', 'chopped', 'sliced', 'minced', 'large', 'small', 'medium']
    words = cleaned.split()
    words = [word for word in words if word.lower() not in common_words]
    
    return ' '.join(words).strip()

def get_nutrition_from_api(fdc_id):
    """Get nutrition data from USDA API"""
    try:
        params = {'api_key': USDA_API_KEY}
        resp = requests.get(f"{DETAIL_URL}{fdc_id}", params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            nutrients = {}
            
            for n in data.get('foodNutrients', []):
                # Handle different possible key names
                name = n.get('nutrientName') or n.get('name') or n.get('nutrient', {}).get('name')
                if not name:
                    continue
                value = n.get('value', 0)
                nutrients[name] = value
            
            return {
                'calories': nutrients.get('Energy', 0),
                'protein': nutrients.get('Protein', 0),
                'fat': nutrients.get('Total lipid (fat)', 0),
                'carbs': nutrients.get('Carbohydrate, by difference', 0),
                'fiber': nutrients.get('Fiber, total', 0)
            }
        
        return None
    except Exception as e:
        print(f"Error getting nutrition from API for FDC ID {fdc_id}: {e}")
        return None

def get_fallback_nutrition(ingredient):
    """Get nutrition data from fallback dictionary"""
    ingredient_lower = ingredient.lower()
    
    # Try exact match first
    if ingredient_lower in FALLBACK_NUTRITION:
        return FALLBACK_NUTRITION[ingredient_lower]
    
    # Try partial matches
    for key, value in FALLBACK_NUTRITION.items():
        if key in ingredient_lower or ingredient_lower in key:
            return value
    
    # Return default values if no match found
    return {'calories': 50, 'protein': 2.0, 'fat': 1.0, 'carbs': 5.0, 'fiber': 2.0}

def analyze_nutrition(ingredients):
    """Analyze nutrition for a list of ingredients"""
    total = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0 , 'fiber': 0}
    
    for ingredient in ingredients:
        nutrition = None
        
        # Try API first
        fdc_id = get_fdc_id(ingredient)
        if fdc_id:
            nutrition = get_nutrition_from_api(fdc_id)
        
        # If API fails, use fallback
        if not nutrition:
            nutrition = get_fallback_nutrition(ingredient)
        
        # Add to totals
        total['calories'] += nutrition['calories']
        total['protein'] += nutrition['protein']
        total['fat'] += nutrition['fat']
        total['carbs'] += nutrition['carbs']
        total['fiber'] += nutrition['fiber']
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.1)
    
    # Round the values
    total['calories'] = round(total['calories'], 1)
    total['protein'] = round(total['protein'], 1)
    total['fat'] = round(total['fat'], 1)
    total['carbs'] = round(total['carbs'], 1)
    total['fiber'] = round(total['fiber'], 1)

    return total
