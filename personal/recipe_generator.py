#!/usr/bin/env python3
"""
Recipe HTML Generator

This script generates an HTML recipe file based on the provided template.
It takes command line arguments for recipe details, ingredients, and directions.

Usage:
    python recipe_generator.py --title "Recipe Title" --description "Recipe description" 
                              --difficulty easy|medium|hard --prep-time "10 mins" --cook-time "20 mins"
                              --servings 4 --categories "dinner,italian"
                              --ingredients "ingredient1:amount1,ingredient2:amount2,..."
                              --directions "Step 1,Step 2,..."
                              --notes "Optional notes"
                              --output "recipe-filename.html"

Example:
    python recipe_generator.py --title "Chocolate Chip Cookies" 
                                --description "Classic homemade chocolate chip cookies with a soft center and crispy edges." 
                                --difficulty easy 
                                --prep-time "15 mins" 
                                --cook-time "10 mins" 
                                --servings 24 
                                --categories "dessert,snack,baking" 
                                --ingredients "all-purpose flour:2 1/4 cups,baking soda:1 tsp,salt:1 tsp,butter:1 cup (softened),brown sugar:3/4 cup,granulated sugar:3/4 cup,vanilla extract:1 tsp,eggs:2 large,chocolate chips:2 cups" 
                                --directions "Preheat oven to 375°F (190°C).,Combine flour, baking soda, and salt in a small bowl.,Beat butter, brown sugar, granulated sugar, and vanilla in large mixer bowl.,Add eggs one at a time, beating well after each addition.,Gradually beat in flour mixture.,Stir in chocolate chips.,Drop by rounded tablespoon onto ungreased baking sheets.,Bake for 9 to 11 minutes or until golden brown.,Cool on baking sheets for 2 minutes; remove to wire racks to cool completely." 
                                --notes "For softer cookies, bake for 8-9 minutes. For crispier cookies, bake for 11-12 minutes. Store in an airtight container for up to 5 days." 
                                --output "recipes/chocolate-chip-cookies.html" 
                                --update-json
"""

import argparse
import os
import json
import re
from datetime import datetime


def parse_ingredients(ingredients_str):
    """Parse ingredients string into a list of tuples (ingredient, amount)."""
    if not ingredients_str:
        return []
    
    ingredients = []
    for item in ingredients_str.split(","):
        parts = item.split(":")
        if len(parts) >= 2:
            ingredient = parts[0].strip()
            amount = parts[1].strip()
            ingredients.append((ingredient, amount))
        else:
            # If no amount is specified
            ingredients.append((item.strip(), ""))
    
    return ingredients


def parse_directions(directions_str):
    """Parse directions string into a list of steps."""
    if not directions_str:
        return []
    
    return [step.strip() for step in directions_str.split(",")]


def parse_categories(categories_str):
    """Parse categories string into a list."""
    if not categories_str:
        return []
    
    return [category.strip() for category in categories_str.split(",")]


def generate_id(title):
    """Generate a URL-friendly ID from the title."""
    # Convert to lowercase, replace spaces with hyphens, remove non-alphanumeric chars
    return re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))


def highlight_ingredients_in_step(step, ingredients):
    """Add highlighting to ingredients mentioned in a step."""
    # Sort ingredients by length (longest first) to avoid partial matches
    sorted_ingredients = sorted(ingredients, key=lambda x: len(x[0]), reverse=True)
    
    for ingredient, amount in sorted_ingredients:
        # Escape special characters for regex
        ingredient_escaped = re.escape(ingredient.lower())
        # Look for the ingredient name with word boundaries
        pattern = rf"\b{ingredient_escaped}s?\b"
        
        # Create the replacement with highlighting and amount
        if amount:
            replacement = f'<span class="ingredient-used">{ingredient} ({amount})</span>'
        else:
            replacement = f'<span class="ingredient-used">{ingredient}</span>'
        
        # Replace case-insensitively
        step = re.sub(pattern, replacement, step, flags=re.IGNORECASE)
    
    return step


def generate_html(args, ingredients, directions):
    """Generate the HTML content for the recipe."""
    # Set default values
    title = args.title or "Recipe Title"
    description = args.description or "Recipe description."
    difficulty = args.difficulty or "easy"
    prep_time = args.prep_time or "10 mins"
    cook_time = args.cook_time or "20 mins"
    servings = args.servings or 4
    notes = args.notes or ""
    
    difficulty_class = f"difficulty-{difficulty}"
    
    # Generate ingredients HTML
    ingredients_html = ""
    for ingredient, amount in ingredients:
        ingredients_html += f"""
                            <div class="ingredient-item">
                                <div class="mr-3 mt-1">
                                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                </div>
                                <div><span class="ingredient-amount">{amount}</span> {ingredient}</div>
                            </div>"""
    
    # Generate directions HTML
    directions_html = ""
    for index, step in enumerate(directions, 1):
        # Highlight ingredients in the step
        highlighted_step = highlight_ingredients_in_step(step, ingredients)
        
        directions_html += f"""
                            <li class="instruction-step">
                                <div class="flex">
                                    <div class="flex-shrink-0 mr-4">
                                        <div class="flex items-center justify-center w-8 h-8 bg-gray-700 rounded-full text-white font-bold instruction-step-number">{index}</div>
                                    </div>
                                    <div>
                                        <p>{highlighted_step}</p>
                                    </div>
                                </div>
                            </li>"""
    
    # Generate categories meta tags
    categories_meta = ""
    for category in parse_categories(args.categories):
        categories_meta += f'    <meta name="recipe-category" content="{category}">\n'
    
    # Format the HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Recipe status: "live" makes the recipe appear in the index, anything else hides it -->
    <meta name="recipe-status" content="live">
    
    <!-- Recipe description (optional but recommended) -->
    <meta name="description" content="{description}">
    
    <!-- Recipe categories (can add multiple) -->
{categories_meta}
    <!-- Rest of <head> -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Eli Furgeson's Recipes</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: 'Georgia', serif;
            background-color: #121212;
            background-image: linear-gradient(to bottom right, #121212, #1a1a2e);
            color: #f5f5f5;
            line-height: 1.6;
            min-height: 100vh;
        }}
        
        .nav-link {{
            position: relative;
            text-decoration: none;
            transition: color 0.3s;
            color: #e0e0e0;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        .nav-link:hover {{
            color: #ffffff;
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        .nav-link::after {{
            content: '';
            position: absolute;
            width: 100%;
            height: 2px;
            bottom: -2px;
            left: 0;
            background: linear-gradient(90deg, #4a5568, #a0aec0);
            transform: scaleX(0);
            transform-origin: bottom right;
            transition: transform 0.3s;
        }}
        
        .nav-link:hover::after {{
            transform: scaleX(1);
            transform-origin: bottom left;
        }}
        
        .content-card {{
            background-color: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .section-title {{
            display: inline-block;
            position: relative;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            width: 100%;
            height: 2px;
            bottom: -6px;
            left: 0;
            background: linear-gradient(90deg, #4a5568, transparent);
        }}
        
        .ingredient-item {{
            display: flex;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            border-radius: 8px;
            transition: background-color 0.2s;
        }}
        
        .ingredient-item:hover {{
            background-color: #2a2a2a;
        }}
        
        .instruction-step {{
            margin-bottom: 1.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #333;
        }}
        
        .instruction-step:last-child {{
            border-bottom: none;
        }}
        
        .difficulty-tag {{
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
        }}
        
        .difficulty-easy {{
            background-color: #2f855a;
            color: #e0e0e0;
        }}
        
        .difficulty-medium {{
            background-color: #dd6b20;
            color: #e0e0e0;
        }}
        
        .difficulty-hard {{
            background-color: #c53030;
            color: #e0e0e0;
        }}
        
        .time-tag {{
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            background-color: #2c5282;
            color: #e0e0e0;
        }}
        
        .notes-section {{
            background-color: #252525;
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 2rem;
            border-left: 4px solid #4a5568;
        }}
        
        /* Subtle grain overlay */
        .grain {{
            position: fixed;
            top: 0;
            left: 0;
            height: 100%;
            width: 100%;
            pointer-events: none;
            opacity: 0.3;
            z-index: 100;
        }}
        
        /* Mobile responsiveness improvements */
        @media (max-width: 768px) {{
            .container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            
            h1 {{
                font-size: 2.5rem;
            }}
            
            h2 {{
                font-size: 1.75rem;
            }}
            
            .nav-link {{
                padding: 4px 8px;
                font-size: 0.9rem;
            }}
            
            .ingredient-amount {{
                font-weight: 600;
                display: inline-block;
                min-width: 80px;
            }}
            
            .instruction-step-number {{
                min-width: 32px;
                height: 32px;
                font-size: 0.9rem;
            }}
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            
            .content-card {{
                background: white;
                box-shadow: none;
                border: 1px solid #ddd;
            }}
            
            .nav-link, .header, footer {{
                display: none;
            }}
            
            .grain {{
                display: none;
            }}
        }}
        
        /* Ingredient styling for better mobile display */
        .ingredient-amount {{
            font-weight: 600;
            color: #a0aec0;
            display: inline-block;
            min-width: 100px;
        }}
        
        /* Ingredient used in current step highlight */
        .ingredient-used {{
            background-color: rgba(76, 81, 191, 0.2);
            border-radius: 4px;
            padding: 0 3px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="grain" style="background-image: url('data:image/png;base64,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');"></div>
    
    <div class="container mx-auto px-4 sm:px-6 py-8 sm:py-12 max-w-4xl">
        <header class="mb-8 sm:mb-12 text-center">
            <h1 class="text-4xl sm:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-400">Eli</h1>
            <div class="w-24 h-1 mx-auto bg-gradient-to-r from-gray-500 to-gray-700 mb-6 sm:mb-8"></div>
            <nav class="flex flex-wrap justify-center space-x-2 sm:space-x-8 p-2 rounded-full bg-gray-800 bg-opacity-50 inline-flex">
                <a href="../index.html" class="nav-link font-medium">Home</a>
                <a href="../prob.html" class="nav-link font-medium">Probability</a>
                <a href="../recipes.html" class="nav-link font-medium">Recipes</a>
            </nav>
        </header>

        <main>
            <section class="mb-12">
                <div class="content-card p-4 sm:p-8">
                    <!-- Recipe Header -->
                    <div class="flex flex-col sm:flex-row justify-between items-start mb-6 sm:mb-8">
                        <h2 class="text-2xl sm:text-3xl font-semibold mb-3 sm:mb-0">{title}</h2>
                        <div class="flex items-center space-x-3">
                            <span class="difficulty-tag {difficulty_class}">{difficulty}</span>
                            <button onclick="window.print()" class="text-gray-400 hover:text-white transition-colors duration-300">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Recipe Overview -->
                    <div class="mb-8">
                        <p class="text-gray-300 mb-4">{description}</p>
                        <div class="flex flex-wrap gap-4">
                            <div class="flex items-center text-gray-300">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <span><strong>Prep:</strong> {prep_time}</span>
                            </div>
                            <div class="flex items-center text-gray-300">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <span><strong>Cook:</strong> {cook_time}</span>
                            </div>
                            <div class="flex items-center text-gray-300">
                                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                                </svg>
                                <span><strong>Serves:</strong> {servings}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Ingredients -->
                    <div class="mb-8">
                        <h3 class="text-xl sm:text-2xl section-title">Ingredients</h3>
                        <div class="grid md:grid-cols-2 gap-4">
{ingredients_html}
                        </div>
                    </div>
                    
                    <!-- Instructions -->
                    <div class="mb-8">
                        <h3 class="text-xl sm:text-2xl section-title">Instructions</h3>
                        <ol class="list-none pl-0 space-y-6">
{directions_html}
                        </ol>
                    </div>
                    
                    <!-- Notes (Optional) -->
                    <div class="notes-section">
                        <h3 class="text-xl font-semibold mb-3">Notes</h3>
                        <p>{notes}</p>
                    </div>
                </div>
            </section>
        </main>

        <footer class="mt-12 mb-8 text-center text-gray-400">
            <p>&copy; 2025 Eli Furgeson</p>
        </footer>
    </div>
</body>
</html>
"""
    return html_template


def update_json(recipe_id, title, description, difficulty, time, servings, categories):
    """Update the recipes.json file with the new recipe."""
    json_path = "recipes.json"
    
    # Load existing JSON if it exists
    recipes = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                recipes = json.load(f)
        except json.JSONDecodeError:
            # If JSON is invalid, start with an empty list
            recipes = []
    
    # Check if recipe already exists
    recipe_exists = False
    for i, recipe in enumerate(recipes):
        if recipe.get("id") == recipe_id:
            # Update existing recipe
            recipes[i] = {
                "id": recipe_id,
                "title": title,
                "description": description,
                "difficulty": difficulty,
                "time": time,
                "servings": servings,
                "categories": categories,
                "display": True
            }
            recipe_exists = True
            break
    
    # Add new recipe if it doesn't exist
    if not recipe_exists:
        new_recipe = {
            "id": recipe_id,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "time": time,
            "servings": servings,
            "categories": categories,
            "display": True
        }
        recipes.append(new_recipe)
    
    # Write updated JSON
    with open(json_path, "w") as f:
        json.dump(recipes, f, indent=2)
    
    return recipe_exists


def main():
    parser = argparse.ArgumentParser(description="Generate an HTML recipe file")
    
    # Recipe metadata
    parser.add_argument("--title", help="Recipe title")
    parser.add_argument("--description", help="Recipe description")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="easy", help="Recipe difficulty")
    parser.add_argument("--prep-time", help="Preparation time (e.g., '10 mins')")
    parser.add_argument("--cook-time", help="Cooking time (e.g., '20 mins')")
    parser.add_argument("--servings", type=int, help="Number of servings")
    parser.add_argument("--categories", help="Comma-separated list of categories")
    
    # Recipe content
    parser.add_argument("--ingredients", help="Comma-separated list of 'ingredient:amount' pairs")
    parser.add_argument("--directions", help="Comma-separated list of directions")
    parser.add_argument("--notes", help="Additional notes for the recipe")
    
    # Output options
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--update-json", action="store_true", help="Update recipes.json file")
    
    args = parser.parse_args()
    
    # Parse ingredients and directions
    ingredients = parse_ingredients(args.ingredients)
    directions = parse_directions(args.directions)
    
    # Generate HTML
    html_content = generate_html(args, ingredients, directions)
    
    # Generate recipe ID if not provided
    recipe_id = generate_id(args.title) if args.title else "unnamed-recipe"
    
    # Determine output file path
    output_path = args.output if args.output else f"{recipe_id}.html"
    
    # Write HTML to file
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Recipe HTML written to {output_path}")
    
    # Update recipes.json if requested
    if args.update_json:
        # Calculate total time
        prep_time = args.prep_time or "0 mins"
        cook_time = args.cook_time or "0 mins"
        
        # Extract minutes from time strings
        prep_mins = int(re.search(r"(\d+)", prep_time).group(1)) if re.search(r"(\d+)", prep_time) else 0
        cook_mins = int(re.search(r"(\d+)", cook_time).group(1)) if re.search(r"(\d+)", cook_time) else 0
        
        # Calculate total time
        total_mins = prep_mins + cook_mins
        total_time = f"{total_mins} mins"
        
        # Get categories as list
        categories = parse_categories(args.categories)
        
        # Update JSON
        exists = update_json(
            recipe_id,
            args.title,
            args.description,
            args.difficulty,
            total_time,
            args.servings,
            categories
        )
        
        if exists:
            print(f"Updated existing recipe '{args.title}' in recipes.json")
        else:
            print(f"Added new recipe '{args.title}' to recipes.json")


if __name__ == "__main__":
    main()