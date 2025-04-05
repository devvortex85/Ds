#!/bin/bash

# Set up repository
echo "Setting up repository..."
mkdir -p codeberg_repo
cd codeberg_repo
git clone https://Adamcatholic:$CODEBERG_TOKEN@codeberg.org/Adamcatholic/Ds.git .
git config user.email "discuss-app@example.com"
git config user.name "Discuss App"

# Verify we're on main
git checkout main

# For each branch to merge
for branch in updated-forms updated-views tag-init tags-feature readme-only; do
  echo "Attempting to merge $branch into main..."
  # Create a separate branch for the merge attempt
  git checkout main
  git checkout -b merge-$branch
  
  # Try to merge with --allow-unrelated-histories
  if git merge --allow-unrelated-histories -m "Merge branch '$branch' into main" $branch; then
    echo "Successfully merged $branch"
    git checkout main
    git merge --no-ff merge-$branch -m "Merge branch '$branch' into main"
  else
    echo "Failed to merge $branch - conflicts encountered"
    git merge --abort
    git checkout main
  fi
  
  # Clean up the temporary merge branch
  git branch -D merge-$branch
done

# Push the updated main branch
echo "Pushing changes to main..."
git push origin main

# Delete other branches on origin
echo "Deleting remote branches..."
for branch in updated-forms updated-views tag-init tags-feature readme-only; do
  echo "Deleting remote branch $branch..."
  git push origin --delete $branch
done

echo "Done!"