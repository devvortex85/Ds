import os
import requests

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
    print(f"Attempting to delete branch {branch_name}...")
    # Need to use actual Git reference format
    git_ref = f"heads/{branch_name}"
    response = requests.delete(f'{base_url}/git/refs/{git_ref}', headers=headers)
    if response.status_code in [200, 204]:
        print(f"Successfully deleted branch: {branch_name}")
        return True
    else:
        print(f"Error deleting branch {branch_name}: {response.text} (Status: {response.status_code})")
        return False

# Main function
def main():
    # Get all branches excluding main
    branches = get_branches()
    print(f"Found branches to delete: {branches}")
    
    # Delete each branch
    successful_deletions = 0
    for branch in branches:
        if delete_branch(branch):
            successful_deletions += 1
    
    print(f"Deleted {successful_deletions} of {len(branches)} branches")
    print("Operation completed!")

if __name__ == "__main__":
    main()