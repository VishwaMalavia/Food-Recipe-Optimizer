from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache

from .scraper import scrape_recipe
from .ml_utils import modify_ingredients
from .nutrition import analyze_nutrition
from .models import Recipe, Favorite

import traceback

def index(request):
    # On POST, process the recipe and redirect to the recipe page
    if request.method == 'POST':
        url = request.POST.get('url')
        restriction = request.POST.get('restriction', '')

        # Create a unique cache key and try to get data from cache
        cache_key = f"recipe_{url}_restriction_{restriction}"
        recipe_context = cache.get(cache_key)

        if not recipe_context:
            try:
                # Scrape the recipe
                recipe = scrape_recipe(url)
                
                # Modify ingredients based on dietary restriction
                modified_ingredients = recipe['ingredients']
                if restriction:
                    modified_ingredients = modify_ingredients(recipe['ingredients'], restriction)
                
                # Analyze nutrition (using API)
                nutrition = analyze_nutrition(modified_ingredients)
                
                # Create or get recipe with all necessary data
                recipe_obj, created = Recipe.objects.update_or_create(
                    source_url=url,
                    defaults={
                        'title': recipe['title'],
                        'instructions': '\n'.join(recipe['instructions']) if recipe['instructions'] else 'Instructions not found',
                        'ingredients': modified_ingredients,
                    }
                )
                                
                # Prepare context for session and cache
                recipe_context = {
                    'title': recipe['title'],
                    'original_ingredients': recipe['ingredients'],
                    'modified_ingredients': recipe_obj.ingredients,
                    'instructions': '\n'.join(recipe['instructions']) if recipe['instructions'] else 'Instructions not found',
                    'nutrition': nutrition,
                    'restriction': restriction,
                    'recipe_id': recipe_obj.id,
                    'success': True
                }
                
                # Cache the result for 1 hour
                cache.set(cache_key, recipe_context, 3600)

            except Exception as e:
                recipe_context = {
                    'error': f"Error processing recipe: {str(e)}",
                    'url': url,
                    'restriction': restriction,
                    'success': False
                }
                print(f"Error in recipe processing: {traceback.format_exc()}")
        
        # Store context in session and redirect
        request.session['recipe_context'] = recipe_context
        return redirect('recipe')

    # On GET, just show the form
    context = {}

    if request.user.is_authenticated:
        favorite_count = Favorite.objects.filter(user=request.user).count()
        context['favorite_count'] = favorite_count
    
    return render(request, 'index.html', context)


                
def recipe_view(request):
    """Display a single recipe."""
    context = request.session.pop('recipe_context', {})
    
    # If no context (e.g., direct access or after session expiry), redirect to home
    if not context:
        return redirect('index')
        
    # Check favorite status if user is logged in and there is a recipe
    if request.user.is_authenticated and context.get('success'):
        context['is_favorite'] = Favorite.objects.filter(
            user=request.user,
            recipe_id=context['recipe_id']
        ).exists()
        
        favorite_count = Favorite.objects.filter(user=request.user).count()
        context['favorite_count'] = favorite_count
        
    return render(request, 'recipes/recipe.html', context)
                
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('index')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            login(request, user)
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
@require_POST
def toggle_favorite(request):
    """Toggle favorite status for a recipe"""
    recipe_id = request.POST.get('recipe_id')
    
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        
        if not created:
            # If favorite already exists, remove it
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        favorite_count = Favorite.objects.filter(user=request.user).count()

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'favorite_count': favorite_count,
            'message': 'Recipe added to favorites' if is_favorite else 'Recipe removed from favorites'
        })

        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def favorite_list(request):
    """Display user's favorite recipes"""
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    context = {
        'favorites': favorites
    }
    return render(request, 'recipes/favorite.html', context)
