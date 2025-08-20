from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    source_url = models.URLField(unique=True, blank=True, null=True)
    ingredients = models.JSONField(default=list)

    def __str__(self):
        return self.title

    # def formatted_ingredients(self):
    #     """Return ingredients as a newline-separated string for admin display."""
    #     return "\n".join(self.ingredients) if isinstance(self.ingredients, list) else str(self.ingredients).replace('[', '').replace(']', '')

    # formatted_ingredients.short_description = "Ingredients"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} - {self.recipe.title}"
