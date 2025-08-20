from django.contrib import admin
from .models import Recipe, Favorite

admin.site.register(Recipe)
admin.site.register(Favorite)
