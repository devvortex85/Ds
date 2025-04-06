#!/bin/bash

# This script cleans up the Git repository to match the desired structure

echo "Starting repository cleanup..."

# Add .gitignore and .gitattributes
git add .gitignore .gitattributes

# Remove unwanted directories from Git tracking
echo "Removing unwanted directories from Git tracking..."
git rm -r --cached discuss-package/ 2>/dev/null || echo "discuss-package/ not found in Git index"
git rm -r --cached discuss_core/ 2>/dev/null || echo "discuss_core/ not found in Git index"
git rm -r --cached temp_repo/ 2>/dev/null || echo "temp_repo/ not found in Git index"
git rm -r --cached temp_extract/ 2>/dev/null || echo "temp_extract/ not found in Git index"
git rm -r --cached temp_push/ 2>/dev/null || echo "temp_push/ not found in Git index"
git rm -r --cached minimal_repo/ 2>/dev/null || echo "minimal_repo/ not found in Git index"
git rm -r --cached fresh_clone/ 2>/dev/null || echo "fresh_clone/ not found in Git index"

# Remove __pycache__ directories
echo "Removing __pycache__ directories from Git tracking..."
find . -type d -name "__pycache__" | while read dir; do
  git rm -r --cached "$dir" 2>/dev/null || echo "$dir not found in Git index"
done

# Commit the changes
echo "Committing changes..."
git commit -m "Clean up repository structure"

# Push to remote
echo "Pushing changes to remote..."
git push origin main

echo "Repository cleanup complete!"