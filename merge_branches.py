import os
import subprocess
import json
import requests
import re

# Get the Codeberg token from environment
token = os.environ.get('CODEBERG_TOKEN')
if not token:
    print("Error: CODEBERG_TOKEN environment variable not set")
    exit(1)

headers = {
    'Authorization': f'token {token}',
    'Content-Type': 'application/json'
}

# Repository information
repo_owner = 'Adamcatholic'
repo_name = 'Ds'
base_url = f'https://codeberg.org/api/v1/repos/{repo_owner}/{repo_name}'

# Function to get all branches
def get_branches():
    response = requests.get(f'{base_url}/branches', headers=headers)
    if response.status_code != 200:
        print(f"Error getting branches: {response.text}")
        return []
    return [branch['name'] for branch in response.json() if branch['name'] != 'main']

# Function to delete a branch
def delete_branch(branch_name):
    response = requests.delete(f'{base_url}/branches/{branch_name}', headers=headers)
    if response.status_code in [200, 204]:
        print(f"Successfully deleted branch: {branch_name}")
    else:
        print(f"Error deleting branch {branch_name}: {response.text}")

# Function to get all pull requests
def get_pull_requests():
    response = requests.get(f'{base_url}/pulls', headers=headers)
    if response.status_code != 200:
        print(f"Error getting pull requests: {response.text}")
        return []
    return response.json()

# Function to find an existing PR for a branch
def find_pr_for_branch(branch, pull_requests):
    for pr in pull_requests:
        if pr['head']['ref'] == branch and pr['base']['ref'] == 'main':
            return pr
    return None

# Function to extract PR ID from error message
def extract_pr_id_from_error(error_text):
    match = re.search(r'\[id: (\d+),', error_text)
    if match:
        return match.group(1)
    return None

# Function to create a pull request
def create_pull_request(head, base, title):
    data = {
        'head': head,
        'base': base,
        'title': title
    }
    response = requests.post(f'{base_url}/pulls', headers=headers, json=data)
    if response.status_code == 201:
        print(f"Successfully created PR from {head} to {base}")
        return response.json()
    else:
        error_text = response.text
        print(f"Error creating PR: {error_text}")
        # Try to extract PR ID from error message if it already exists
        pr_id = extract_pr_id_from_error(error_text)
        if pr_id:
            print(f"Found existing PR ID: {pr_id}")
            # Get the PR details
            pr_response = requests.get(f'{base_url}/pulls/{pr_id}', headers=headers)
            if pr_response.status_code == 200:
                return pr_response.json()
        return None

# Function to merge a pull request
def merge_pull_request(pr_number):
    data = {
        'Do': 'merge',
        'MergeMessageField': f'Merge PR #{pr_number}'
    }
    response = requests.post(f'{base_url}/pulls/{pr_number}/merge', headers=headers, json=data)
    if response.status_code == 200:
        print(f"Successfully merged PR #{pr_number}")
        return True
    else:
        print(f"Error merging PR #{pr_number}: {response.text}")
        return False

# Main function
def main():
    # Get all branches excluding main
    branches = get_branches()
    print(f"Found branches: {branches}")
    
    # Get all existing pull requests
    pull_requests = get_pull_requests()
    print(f"Found {len(pull_requests)} existing pull requests")
    
    # Process each branch
    for branch in branches:
        # Try to find an existing PR for this branch
        existing_pr = find_pr_for_branch(branch, pull_requests)
        
        if existing_pr:
            pr_number = existing_pr['number']
            print(f"Found existing PR #{pr_number} for branch {branch}")
        else:
            # Create a pull request
            print(f"Creating PR for {branch}...")
            pr_result = create_pull_request(branch, 'main', f'Merge {branch} into main')
            if not pr_result:
                print(f"Skipping branch {branch} due to PR creation failure")
                continue
            pr_number = pr_result.get('number')
            
        # Try to merge the PR
        if pr_number:
            print(f"Merging PR #{pr_number}...")
            if merge_pull_request(pr_number):
                # If merge successful, delete the branch
                print(f"Deleting branch {branch}...")
                delete_branch(branch)
        
    print("All operations completed!")

if __name__ == "__main__":
    main()