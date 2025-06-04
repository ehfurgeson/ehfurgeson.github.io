#!/usr/bin/env python3
"""
Flask Recipe Generator Web Application

A web interface for generating recipe HTML files using the existing recipe_generator.py logic.
Provides a form for inputting recipe details and generates downloadable HTML files.

Usage:
    python app.py

Then navigate to http://localhost:5000 in your web browser.
"""

from flask import Flask, render_template_string, request, send_file, flash, redirect, url_for, jsonify
import os
import tempfile
import zipfile
from datetime import datetime
import json
import re
from pathlib import Path

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # Change this to a secure secret key

# Import the functions from your existing recipe_generator.py
def parse_ingredients(ingredients_str):
    """Parse ingredients string into a list of tuples (ingredient, amount)."""
    if not ingredients_str:
        return []
    
    ingredients = []
    for item in ingredients_str.split("\n"):
        item = item.strip()
        if not item:
            continue
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
    
    return [step.strip() for step in directions_str.split("\n") if step.strip()]

def parse_categories(categories_str):
    """Parse categories string into a list."""
    if not categories_str:
        return []
    
    return [category.strip() for category in categories_str.split(",") if category.strip()]

def generate_id(title):
    """Generate a URL-friendly ID from the title."""
    return re.sub(r"[^a-z0-9-]", "", title.lower().replace(" ", "-"))

def highlight_ingredients_in_step(step, ingredients):
    """Add highlighting to ingredients mentioned in a step."""
    sorted_ingredients = sorted(ingredients, key = lambda x: len(x[0]), reverse = True)
    
    for ingredient, amount in sorted_ingredients:
        ingredient_escaped = re.escape(ingredient.lower())
        pattern = rf"\b{ingredient_escaped}s?\b"
        
        if amount:
            replacement = f'<span class="ingredient-used">{ingredient} ({amount})</span>'
        else:
            replacement = f'<span class="ingredient-used">{ingredient}</span>'
        
        step = re.sub(pattern, replacement, step, flags = re.IGNORECASE)
    
    return step

def generate_html(title, description, difficulty, prep_time, cook_time, servings, categories, ingredients, directions, notes):
    """Generate the HTML content for the recipe."""
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
    for category in categories:
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

# HTML template for the web form
FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recipe Generator - Eli's Kitchen</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Georgia', serif;
            background-color: #121212;
            background-image: linear-gradient(to bottom right, #121212, #1a1a2e);
            color: #f5f5f5;
            line-height: 1.6;
            min-height: 100vh;
        }
        
        .form-container {
            background-color: #1e1e1e;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #e0e0e0;
        }
        
        .form-input, .form-textarea, .form-select {
            width: 100%;
            padding: 0.75rem;
            background-color: #2a2a2a;
            border: 1px solid #444;
            border-radius: 8px;
            color: #f5f5f5;
            transition: border-color 0.3s;
        }
        
        .form-input:focus, .form-textarea:focus, .form-select:focus {
            outline: none;
            border-color: #4a5568;
            box-shadow: 0 0 0 3px rgba(74, 85, 104, 0.1);
        }
        
        .form-textarea {
            resize: vertical;
            min-height: 120px;
        }
        
        .btn-primary {
            background: linear-gradient(90deg, #4a5568, #2d3748);
            color: white;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-primary:hover {
            background: linear-gradient(90deg, #2d3748, #1a202c);
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: linear-gradient(90deg, #2f855a, #276749);
            color: white;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-secondary:hover {
            background: linear-gradient(90deg, #276749, #22543d);
            transform: translateY(-2px);
        }
        
        .flash-message {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        
        .flash-success {
            background-color: rgba(72, 187, 120, 0.1);
            border: 1px solid #48bb78;
            color: #68d391;
        }
        
        .flash-error {
            background-color: rgba(245, 101, 101, 0.1);
            border: 1px solid #f56565;
            color: #fc8181;
        }
        
        .help-text {
            font-size: 0.875rem;
            color: #a0aec0;
            margin-top: 0.25rem;
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        @media (max-width: 768px) {
            .two-column {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container mx-auto px-6 py-12 max-w-4xl">
        <header class="mb-12 text-center">
            <h1 class="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-400">Recipe Generator</h1>
            <div class="w-24 h-1 mx-auto bg-gradient-to-r from-gray-500 to-gray-700 mb-8"></div>
            <p class="text-gray-300 text-lg">Create beautiful recipe pages with our simple form</p>
        </header>

        <main>
            <div class="form-container p-8">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash-message flash-{{ category }}">
                                {{ message }}
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                <form method="POST" action="/generate">
                    <!-- Basic Recipe Information -->
                    <h2 class="text-2xl font-bold mb-6 text-gray-200">Basic Information</h2>
                    
                    <div class="form-group">
                        <label for="title" class="form-label">Recipe Title *</label>
                        <input type="text" id="title" name="title" class="form-input" required 
                               placeholder="e.g., Chocolate Chip Cookies" value="{{ request.form.title }}">
                    </div>
                    
                    <div class="form-group">
                        <label for="description" class="form-label">Description *</label>
                        <textarea id="description" name="description" class="form-textarea" required 
                                  placeholder="Brief description of your recipe...">{{ request.form.description }}</textarea>
                        <div class="help-text">This will appear in search results and recipe cards</div>
                    </div>
                    
                    <div class="two-column">
                        <div class="form-group">
                            <label for="difficulty" class="form-label">Difficulty *</label>
                            <select id="difficulty" name="difficulty" class="form-select" required>
                                <option value="easy" {{ 'selected' if request.form.difficulty == 'easy' else '' }}>Easy</option>
                                <option value="medium" {{ 'selected' if request.form.difficulty == 'medium' else '' }}>Medium</option>
                                <option value="hard" {{ 'selected' if request.form.difficulty == 'hard' else '' }}>Hard</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="servings" class="form-label">Servings *</label>
                            <input type="number" id="servings" name="servings" class="form-input" required 
                                   min="1" placeholder="4" value="{{ request.form.servings }}">
                        </div>
                    </div>
                    
                    <div class="two-column">
                        <div class="form-group">
                            <label for="prep_time" class="form-label">Prep Time *</label>
                            <input type="text" id="prep_time" name="prep_time" class="form-input" required 
                                   placeholder="15 mins" value="{{ request.form.prep_time }}">
                        </div>
                        
                        <div class="form-group">
                            <label for="cook_time" class="form-label">Cook Time *</label>
                            <input type="text" id="cook_time" name="cook_time" class="form-input" required 
                                   placeholder="25 mins" value="{{ request.form.cook_time }}">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="categories" class="form-label">Categories</label>
                        <input type="text" id="categories" name="categories" class="form-input" 
                               placeholder="dinner, italian, pasta" value="{{ request.form.categories }}">
                        <div class="help-text">Separate multiple categories with commas</div>
                    </div>
                    
                    <!-- Ingredients -->
                    <h2 class="text-2xl font-bold mb-6 mt-8 text-gray-200">Ingredients</h2>
                    
                    <div class="form-group">
                        <label for="ingredients" class="form-label">Ingredients *</label>
                        <textarea id="ingredients" name="ingredients" class="form-textarea" required 
                                  style="min-height: 200px;" placeholder="Enter each ingredient on a new line in format:
ingredient name: amount

Example:
all-purpose flour: 2 cups
baking soda: 1 tsp
salt: 1/2 tsp
butter: 1 cup (softened)">{{ request.form.ingredients }}</textarea>
                        <div class="help-text">Enter one ingredient per line in format: "ingredient name: amount"</div>
                    </div>
                    
                    <!-- Directions -->
                    <h2 class="text-2xl font-bold mb-6 mt-8 text-gray-200">Directions</h2>
                    
                    <div class="form-group">
                        <label for="directions" class="form-label">Instructions *</label>
                        <textarea id="directions" name="directions" class="form-textarea" required 
                                  style="min-height: 250px;" placeholder="Enter each step on a new line:

Preheat oven to 375°F (190°C).
Mix dry ingredients in a large bowl.
In another bowl, cream butter and sugars.
Add eggs one at a time.
Gradually mix in dry ingredients.
Bake for 10-12 minutes.">{{ request.form.directions }}</textarea>
                        <div class="help-text">Enter one step per line. Steps will be automatically numbered.</div>
                    </div>
                    
                    <!-- Notes -->
                    <h2 class="text-2xl font-bold mb-6 mt-8 text-gray-200">Additional Notes</h2>
                    
                    <div class="form-group">
                        <label for="notes" class="form-label">Recipe Notes</label>
                        <textarea id="notes" name="notes" class="form-textarea" 
                                  placeholder="Any additional tips, storage instructions, variations, or serving suggestions...">{{ request.form.notes }}</textarea>
                        <div class="help-text">Optional: Add any helpful tips or variations</div>
                    </div>
                    
                    <!-- Submit Buttons -->
                    <div class="flex flex-wrap gap-4 mt-8">
                        <button type="submit" name="action" value="preview" class="btn-primary">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                            Preview Recipe
                        </button>
                        
                        <button type="submit" name="action" value="download" class="btn-secondary">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            Download HTML
                        </button>
                    </div>
                </form>
            </div>
        </main>

        <footer class="mt-12 mb-8 text-center text-gray-400">
            <p>&copy; 2025 Eli Furgeson - Recipe Generator</p>
        </footer>
    </div>

    <script>
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });
        
        // Flash message auto-hide
        setTimeout(() => {
            document.querySelectorAll('.flash-message').forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                setTimeout(() => msg.remove(), 300);
            });
        }, 5000);
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(FORM_TEMPLATE)

@app.route("/generate", methods = ["POST"])
def generate_recipe():
    try:
        # Get form data
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        difficulty = request.form.get("difficulty", "easy")
        prep_time = request.form.get("prep_time", "").strip()
        cook_time = request.form.get("cook_time", "").strip()
        servings = request.form.get("servings", "4")
        categories_str = request.form.get("categories", "").strip()
        ingredients_str = request.form.get("ingredients", "").strip()
        directions_str = request.form.get("directions", "").strip()
        notes = request.form.get("notes", "").strip()
        action = request.form.get("action", "preview")
        
        # Validate required fields
        if not all([title, description, prep_time, cook_time, ingredients_str, directions_str]):
            flash("Please fill in all required fields.", "error")
            return render_template_string(FORM_TEMPLATE)
        
        # Parse the form data
        try:
            servings = int(servings)
        except ValueError:
            servings = 4
            
        categories = parse_categories(categories_str)
        ingredients = parse_ingredients(ingredients_str)
        directions = parse_directions(directions_str)
        
        if not ingredients:
            flash("Please enter at least one ingredient.", "error")
            return render_template_string(FORM_TEMPLATE)
            
        if not directions:
            flash("Please enter at least one instruction step.", "error")
            return render_template_string(FORM_TEMPLATE)
        
        # Generate the HTML
        html_content = generate_html(
            title, description, difficulty, prep_time, cook_time,
            servings, categories, ingredients, directions, notes
        )
        
        if action == "preview":
            # Return the generated HTML for preview
            return html_content
        
        elif action == "download":
            # Create a temporary file for download
            recipe_id = generate_id(title)
            filename = f"{recipe_id}.html"
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode = "w", suffix = ".html", delete = False, encoding = "utf-8")
            temp_file.write(html_content)
            temp_file.close()
            
            def remove_file(response):
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass
                return response
            
            # Send file and clean up
            return send_file(
                temp_file.name,
                as_attachment = True,
                download_name = filename,
                mimetype = "text/html"
            )
        
        else:
            flash("Invalid action specified.", "error")
            return render_template_string(FORM_TEMPLATE)
            
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return render_template_string(FORM_TEMPLATE)

@app.route("/api/validate", methods = ["POST"])
def validate_form():
    """API endpoint to validate form data without generating the full recipe."""
    try:
        data = request.get_json()
        
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ["title", "description", "prep_time", "cook_time", "ingredients", "directions"]
        for field in required_fields:
            if not data.get(field, "").strip():
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate ingredients format
        if data.get("ingredients"):
            ingredients = parse_ingredients(data["ingredients"])
            if len(ingredients) == 0:
                errors.append("Please enter at least one ingredient")
            elif len(ingredients) < 3:
                warnings.append("Recipes with fewer than 3 ingredients might be too simple")
        
        # Validate directions
        if data.get("directions"):
            directions = parse_directions(data["directions"])
            if len(directions) == 0:
                errors.append("Please enter at least one instruction step")
            elif len(directions) < 3:
                warnings.append("Consider adding more detailed steps for clarity")
        
        # Validate servings
        try:
            servings = int(data.get("servings", 0))
            if servings <= 0:
                errors.append("Servings must be a positive number")
            elif servings > 50:
                warnings.append("That's a lot of servings! Double-check if this is correct")
        except ValueError:
            errors.append("Servings must be a valid number")
        
        # Check for common time format issues
        time_fields = ["prep_time", "cook_time"]
        for field in time_fields:
            time_val = data.get(field, "").strip()
            if time_val and not re.search(r"\d+\s*(min|hour|hr)", time_val, re.IGNORECASE):
                warnings.append(f"{field.replace('_', ' ').title()} should include units (e.g., '30 mins', '1 hour')")
        
        return jsonify({
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        })
        
    except Exception as e:
        return jsonify({"valid": False, "errors": [f"Validation error: {str(e)}"]})

if __name__ == "__main__":
    print("Starting Recipe Generator Web App...")
    print("Navigate to http://localhost:5000 in your web browser")
    print("Press Ctrl+C to stop the server")
    app.run(debug = True, host = "0.0.0.0", port = 5000)