# Food Recipe Optimizer 

The Food Recipe Optimizer is a smart web application designed to make recipes healthier, customizable, and nutrition-aware. Users simply provide a recipe link from any food page, and the application automatically extracts the ingredients and cooking instructions, storing them in a recipe model.

Once fetched, the system integrates with a nutrition analysis API to calculate key nutritional values including fat, carbohydrates, protein, and fiber for that recipe.

A unique feature of this application is dietary restriction optimization:

If the user selects "None", the original recipe remains unchanged.

If the user selects "Vegan", "Healthy", or other dietary preferences, the system intelligently modifies the recipe ingredients to align with the chosen restriction while still keeping the original version available for comparison. Both original and modified ingredient lists are displayed side by side.

Additionally, the application includes a Favorites system (available only to logged-in users).

Logged-in users see a "Favorite" button on each recipe.

Clicking it saves the recipe to their Favorites model.

The Favorites Page then displays all saved recipes along with a nutritional breakdown.

A nutrition pie chart is generated to provide a visual summary of the total nutritional values across all favorite recipes.
