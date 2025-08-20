import re

# Rule-based substitutions
SUBSTITUTIONS = {
    'vegan': {
        'milk': 'almond milk',
        'butter': 'vegan butter',
        'egg': 'flaxseed meal',
        'cheese': 'dairy-free cheese',
        'yogurt': 'soy yogurt',
        'honey': 'maple syrup',
        'chicken': 'tofu or seitan',
        'beef': 'lentils or mushrooms',
        'pork': 'jackfruit',
        # add more as needed
    },
    'healthy': {
        'sugar': 'stevia or maple syrup',
        'white rice': 'brown rice or quinoa',
        'vegetable oil': 'olive oil or coconut oil',
        'all-purpose flour': 'whole wheat flour or almond flour',
        'plain flour': 'whole wheat flour or almond flour',
        'mayonnaise': 'Greek yogurt or avocado',
        'sour cream': 'Greek yogurt',
        'white bread': 'whole wheat bread',
        'pasta': 'whole wheat pasta',
        'potatoes': 'sweet potatoes',
        # add more as needed
    }
}

def modify_ingredients(ingredients, restriction):
    if restriction not in SUBSTITUTIONS:
        return ingredients

    subs = SUBSTITUTIONS.get(restriction)
    modified_list = []

    for ing in ingredients:
        # Special case for vegan egg substitution with unit conversion
        if restriction == 'vegan' and 'egg' in ing.lower():
            # Try to find a number for quantity, default to 1 if not found
            quantity_match = re.search(r'(\d*\.?\d+)', ing)
            quantity = 1.0
            if quantity_match:
                try:
                    quantity = float(quantity_match.group(1))
                except ValueError:
                    pass  # Keep default quantity of 1 if parsing fails
            
            # Conversion rule: 1 egg is substituted with 10 grams of flaxseed meal
            flax_quantity = quantity * 50
            modified_list.append(f"{flax_quantity:.0f}g flaxseed meal")
            continue  # Move to the next ingredient

        # General substitution for all other cases
        found_match = False
        for key, val in subs.items():
            if key in ing.lower():
                modified_list.append(ing.lower().replace(key, val))
                found_match = True
                break  # Apply the first matching substitution
        
        if not found_match:
            modified_list.append(ing) # No substitution found, keep the original

    return modified_list
