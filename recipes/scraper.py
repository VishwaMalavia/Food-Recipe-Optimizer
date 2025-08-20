import requests
from bs4 import BeautifulSoup
import re

def scrape_recipe(url):
    """
    Enhanced scraper for multiple recipe websites with improved data extraction
    Supports: BBC Good Food, AllRecipes, and a variety of Indian recipe sites.
    """

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Enhanced title extraction
        title = extract_title(soup, url)
        
        # Enhanced ingredients extraction
        ingredients = extract_ingredients(soup, url)
        
        # Enhanced instructions extraction
        instructions = extract_instructions(soup, url)
        
        if not title or not ingredients:
            raise Exception("Could not extract recipe data from this URL")
        
        return {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'source_url': url
        }
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Error scraping recipe: {str(e)}")
        
def extract_title(soup, url):
    """Extract recipe title based on website"""
    if 'bbcgoodfood.com' in url:
        # BBC Good Food
        title_elem = soup.find('h1', class_='heading__title')
        if title_elem:
            return title_elem.get_text(strip=True)
        
        # Fallback for BBC Good Food
        title_elem = soup.find('h1')
        if title_elem:
            return title_elem.get_text(strip=True)
    
    elif 'allrecipes.com' in url:
        # AllRecipes
        title_elem = soup.find('h1', class_='recipe-title')
        if title_elem:
            return title_elem.get_text(strip=True)
    
    elif any(site in url for site in [
        'foodfood.com', 'indianhealthyrecipes.com', 'recipes.timesofindia.com', 
        'archanaskitchen.com', 'food.ndtv.com', 'vegrecipesofindia.com',
        'simplyrecipes.com', 'recipetineats.com'
    ]):
        # Common pattern for many recipe sites
        title_elem = soup.find('h1', class_=re.compile(r'title|recipe-title|entry-title', re.IGNORECASE))
        if title_elem:
            return title_elem.get_text(strip=True)
    
    # Generic fallback
    title_elem = soup.find('h1')
    if title_elem:
        return title_elem.get_text(strip=True)
    
    return "Recipe Title Not Found"

def extract_ingredients(soup, url):
    """Extract ingredients list based on website"""
    ingredients = []
    
    if 'bbcgoodfood.com' in url:
        # BBC Good Food - look for ingredients in list items
        ingredient_containers = soup.find_all(['li', 'p'], class_=re.compile(r'ingredient|ingredients'))
        if not ingredient_containers:
            # Try to find ingredients in any list within the recipe section
            recipe_sections = soup.find_all(['section', 'div'], class_=re.compile(r'recipe|ingredients'))
            for section in recipe_sections:
                list_items = section.find_all('li')
                for item in list_items:
                    text = ' '.join(item.stripped_strings)
                    if text and len(text) > 3:  # Filter out empty or very short items
                        ingredients.append(text)
        else:
            for container in ingredient_containers:
                text = ' '.join(container.stripped_strings)
                if text and len(text) > 3:
                    ingredients.append(text)
    
    elif 'allrecipes.com' in url:
        # AllRecipes
        ingredient_elems = soup.find_all('span', class_='ingredients-item-name')
        for elem in ingredient_elems:
            text = ' '.join(elem.stripped_strings)
            if text:
                ingredients.append(text)

    elif any(site in url for site in [
        'foodfood.com', 'indianhealthyrecipes.com', 'recipes.timesofindia.com', 
        'archanaskitchen.com', 'food.ndtv.com', 'simplyrecipes.com', 'recipetineats.com',
        'vegrecipesofindia.com'
    ]):        # Special handling for vegrecipesofindia.com to remove checkboxes
        ingredient_container = soup.find('div', class_=re.compile(r'ingredients', re.IGNORECASE))
        if ingredient_container:
            list_items = ingredient_container.find_all('li')
            for item in list_items:
                text = ' '.join(item.stripped_strings)
                if text:
                    # Use regex to remove leading symbols (like checkboxes, bullets)
                    cleaned_text = re.sub(r'^[\W\s]+', '', text)
                    if cleaned_text:
                        ingredients.append(cleaned_text)
    
    # Generic fallback - look for common ingredient patterns
    if not ingredients:
        # Look for any list items that might contain ingredients
        all_list_items = soup.find_all('li')
        for item in all_list_items:
            text = ' '.join(item.stripped_strings)
            # Simple heuristic: ingredients often contain measurements or food words
            if (text and len(text) > 3 and 
                any(word in text.lower() for word in ['cup', 'tbsp', 'tsp', 'gram', 'ounce', 'pound', 'kg', 'ml', 'g', 'oz', 'lb'])):
                ingredients.append(text)
    
    return ingredients[:]  



def extract_instructions(soup, url):
    """Extract cooking instructions based on website"""
    instructions = []
    
    if 'bbcgoodfood.com' in url:
        # BBC Good Food - look for method/instructions
        method_containers = soup.find_all(['li', 'p'], class_=re.compile(r'method|instruction|step'))
        if not method_containers:
            # Try to find numbered steps
            step_containers = soup.find_all(['li', 'p'], class_=re.compile(r'step'))
            if step_containers:
                method_containers = step_containers
        
        for container in method_containers:
            text = ' '.join(container.stripped_strings)
            if text and len(text) > 10:  # Filter out very short items
                instructions.append(text)

    
    elif 'allrecipes.com' in url:
        # AllRecipes
        instruction_elems = soup.find_all('div', class_='paragraph')
        for elem in instruction_elems:
            text = ' '.join(elem.stripped_strings)
            if text:
                instructions.append(text)

    elif 'simplyrecipes.com' in url:
        instruction_container = soup.find('div', id='structured-project__steps_1-0')
        if instruction_container:
            instruction_elems = instruction_container.find_all('p')
            for elem in instruction_elems:
                text = ' '.join(elem.stripped_strings)
                if text and len(text) > 10:
                    instructions.append(text)

    elif any(site in url for site in [
        'foodfood.com', 'indianhealthyrecipes.com', 'recipes.timesofindia.com', 
        'archanaskitchen.com', 'food.ndtv.com','vegrecipesofindia.com',
        'recipetineats.com'
    ]):

        # Common pattern for many recipe sites
        instruction_container = soup.find(['div', 'ol'], class_=re.compile(r'method|instruction|procedure|recipe-instructions', re.IGNORECASE))

        if instruction_container:
            instruction_elems = instruction_container.find_all(['li', 'p'])
            for elem in instruction_elems:
                text = ' '.join(elem.stripped_strings)
                if text and len(text) > 10:
                    instructions.append(text)
    
    # Generic fallback
    if not instructions:
        # Look for paragraphs that might contain instructions
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = ' '.join(p.stripped_strings)
            if text and len(text) > 20:  # Instructions are usually longer
                instructions.append(text)

    
    return instructions[:]
