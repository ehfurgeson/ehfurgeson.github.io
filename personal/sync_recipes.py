#!/usr/bin/env python3
"""
Recipe JSON Synchronizer

This script scans the recipes directory for HTML files and updates the recipes.json file
to ensure all "live" recipes are included and any "dead" recipes or non-existent files
are removed from the JSON.

Usage:
    python sync_recipes.py
"""

import os
import json
import re
import argparse
from bs4 import BeautifulSoup
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Synchronize recipe HTML files with recipes.json")
    parser.add_argument("--recipes-dir", default="recipes", help="Directory containing recipe HTML files (relative to script location)")
    parser.add_argument("--json-file", default="recipes.json", help="Path to recipes.json file (relative to script location)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed information")
    parser.add_argument("--dry-run", action="store_true", help="Don't modify files, just show what would be done")
    return parser.parse_args()

def extract_recipe_metadata(html_path):
    """Extract recipe metadata from HTML file."""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "html.parser")
    
    # Check for recipe status meta tag
    status_meta = soup.find("meta", attrs={"name": "recipe-status"})
    if not status_meta:
        return None  # Recipe has no status meta tag
    
    status = status_meta.get("content", "").lower()
    if status != "live":
        return None  # Recipe is marked as non-live
    
    # Extract basic metadata
    title = soup.title.string if soup.title else Path(html_path).stem.replace("-", " ").title()
    
    # Try to extract description
    description = ""
    desc_meta = soup.find("meta", attrs={"name": "description"})
    if desc_meta:
        description = desc_meta.get("content", "")
    
    # Extract difficulty
    difficulty = "easy"  # Default
    difficulty_tag = soup.find(class_=lambda c: c and c.startswith("difficulty-"))
    if difficulty_tag:
        difficulty_class = difficulty_tag.get("class", [])
        for cls in difficulty_class:
            if cls.startswith("difficulty-"):
                difficulty = cls.replace("difficulty-", "")
                break
    
    # Extract time information
    time = "30 mins"  # Default
    time_elements = soup.find_all(text=re.compile(r"(Prep|Cook|Total).*time", re.IGNORECASE))
    if time_elements:
        time_text = time_elements[0].parent.get_text()
        time_match = re.search(r"(\d+\s*(?:min|hour|hr|minute|sec|second)[s]?(?:\s+\d+\s*(?:min|hour|hr|minute|sec|second)[s]?)?)", time_text, re.IGNORECASE)
        if time_match:
            time = time_match.group(1)
    
    # Extract servings
    servings = 4  # Default
    servings_elements = soup.find_all(text=re.compile(r"Serves|Servings", re.IGNORECASE))
    if servings_elements:
        servings_text = servings_elements[0].parent.get_text()
        servings_match = re.search(r"(\d+)(?:-(\d+))?\s*(?:serving|serve)", servings_text, re.IGNORECASE)
        if servings_match:
            servings = int(servings_match.group(1))
    
    # Try to determine categories
    categories = []
    
    # First check for category meta tags
    category_meta = soup.find_all("meta", attrs={"name": "recipe-category"})
    if category_meta:
        for meta in category_meta:
            cat = meta.get("content", "").lower().strip()
            if cat and cat not in categories:
                categories.append(cat)
    
    # If no categories found, make a best guess based on title and content
    if not categories:
        # Common category keywords and their associated categories
        category_keywords = {
            "breakfast": ["breakfast", "pancake", "waffle", "omelette", "egg", "muffin", "cereal"],
            "lunch": ["lunch", "sandwich", "wrap", "salad"],
            "dinner": ["dinner", "supper", "entrée", "entree", "main course", "main dish"],
            "dessert": ["dessert", "cake", "cookie", "pie", "ice cream", "sweet"],
            "snack": ["snack", "appetizer", "finger food"],
            "vegetarian": ["vegetarian", "veggie", "no meat"],
            "vegan": ["vegan", "plant-based", "no animal products"]
        }
        
        # Check title and content for category keywords
        page_text = title.lower() + " " + soup.get_text().lower()
        for category, keywords in category_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                categories.append(category)
    
    # If still no categories, use "other"
    if not categories:
        categories = ["other"]
    
    return {
        "id": Path(html_path).stem,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "time": time,
        "servings": servings,
        "categories": categories,
        "display": True
    }

def load_current_recipes(json_path):
    """Load the current recipes.json file or create an empty list if it doesn't exist."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_recipes_json(recipes, json_path, dry_run=False):
    """Save the updated recipes to the JSON file."""
    if dry_run:
        print(f"Would save {len(recipes)} recipes to {json_path}")
        return
    
    # Create directory if it doesn't exist
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2)

def main():
    args = parse_args()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Resolve paths relative to the script location
    recipes_dir = script_dir / args.recipes_dir
    json_path = script_dir / args.json_file
    
    if args.verbose:
        print(f"Script directory: {script_dir}")
        print(f"Scanning directory: {recipes_dir}")
        print(f"JSON file: {json_path}")
    
    # Load current recipes
    current_recipes = load_current_recipes(json_path)
    if args.verbose:
        print(f"Loaded {len(current_recipes)} existing recipes")
    
    # Create a dictionary of current recipes by ID for easy lookup
    current_recipe_dict = {recipe["id"]: recipe for recipe in current_recipes}
    
    # Keep track of recipe template if it exists in the JSON
    template_recipe = None
    if "recipe-template" in current_recipe_dict:
        template_recipe = current_recipe_dict["recipe-template"]
        template_recipe["display"] = False  # Always ensure template is hidden
    
    # Scan for HTML files in the recipes directory
    recipe_files = list(recipes_dir.glob("*.html"))
    
    if args.verbose:
        print(f"Found {len(recipe_files)} HTML files")
    
    # Dictionary to track which recipes are new or updated
    discovered_recipes = {}
    new_count = 0
    updated_count = 0
    unchanged_count = 0
    removed_count = 0
    
    # Process each recipe file
    for recipe_file in recipe_files:
        recipe_id = recipe_file.stem
        
        # Skip the template file but make sure it stays in JSON
        if recipe_id == "recipe-template":
            if not template_recipe:
                # Create template entry if it doesn't exist
                template_recipe = {
                    "id": "recipe-template",
                    "title": "Recipe Template",
                    "description": "Template for creating new recipes.",
                    "difficulty": "easy",
                    "time": "0 mins",
                    "servings": 0,
                    "categories": [],
                    "display": False
                }
            
            if args.verbose:
                print(f"Found template file: {recipe_file}")
            continue
        
        metadata = extract_recipe_metadata(recipe_file)
        
        if metadata:
            discovered_recipes[recipe_id] = metadata
            
            if recipe_id not in current_recipe_dict:
                if args.verbose:
                    print(f"New recipe found: {recipe_id}")
                new_count += 1
            else:
                # Check if any metadata has changed
                current = current_recipe_dict[recipe_id]
                differences = []
                
                for key, value in metadata.items():
                    if key in current and current[key] != value:
                        differences.append((key, current[key], value))
                
                if differences:
                    if args.verbose:
                        print(f"Updated recipe: {recipe_id}")
                        for key, old_val, new_val in differences:
                            print(f"  - {key}: {old_val} -> {new_val}")
                    updated_count += 1
                else:
                    if args.verbose:
                        print(f"Unchanged recipe: {recipe_id}")
                    unchanged_count += 1
        elif args.verbose:
            print(f"Skipping non-live recipe: {recipe_file}")
    
    # Check for recipes in JSON but not in HTML files or marked as dead
    invalid_recipes = []
    for recipe_id, recipe in current_recipe_dict.items():
        if recipe_id != "recipe-template":
            # Check if recipe exists in the filesystem
            recipe_file = recipes_dir / f"{recipe_id}.html"
            if not recipe_file.exists():
                if args.verbose:
                    print(f"Recipe in JSON but file not found: {recipe_id}")
                invalid_recipes.append(recipe_id)
                removed_count += 1
            elif recipe_id not in discovered_recipes:
                # File exists but wasn't discovered (marked as non-live or has no status)
                if args.verbose:
                    print(f"Recipe in JSON but marked as dead or has no status: {recipe_id}")
                invalid_recipes.append(recipe_id)
                removed_count += 1
    
    # Update the list of recipes
    updated_recipes = list(discovered_recipes.values())
    
    # Sort recipes alphabetically by title
    updated_recipes.sort(key=lambda x: x["title"])
    
    # Always include the template in the JSON if it exists
    if template_recipe:
        updated_recipes.append(template_recipe)
    
    # Print summary
    print("\nSummary:")
    print(f"- New recipes: {new_count}")
    print(f"- Updated recipes: {updated_count}")
    print(f"- Unchanged recipes: {unchanged_count}")
    print(f"- Removed recipes: {removed_count}")
    print(f"- Total live recipes: {len(updated_recipes) - (1 if template_recipe else 0)}")
    
    if invalid_recipes:
        print("\nRemoved the following recipes from JSON:")
        for recipe_id in invalid_recipes:
            print(f"- {recipe_id}")
    
    # Save the updated recipes
    save_recipes_json(updated_recipes, json_path, args.dry_run)
    
    if not args.dry_run:
        print(f"\nSuccessfully updated {json_path}")
    else:
        print("\nDry run completed. No files were modified.")
    
    print("\nDon't forget to add a meta tag to your recipe HTML files to mark them as live:")
    print('<meta name="recipe-status" content="live">')

if __name__ == "__main__":
    main()