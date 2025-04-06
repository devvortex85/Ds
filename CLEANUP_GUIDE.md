# Repository Cleanup Guide

Follow these steps to clean up your Git repository structure and synchronize it with Codeberg:

## 1. Ensure .gitignore is properly set up

Your .gitignore should include entries to exclude the following:
- Temporary directories (temp_repo, temp_extract, temp_push, minimal_repo, fresh_clone)
- Duplicate project directories (discuss-package, discuss_core)
- Cache files (__pycache__, .pytest_cache)
- Database files (db.sqlite3)
- IDE files (.idea, .vscode)

## 2. Remove unwanted directories from Git tracking

Run these commands one by one:

```bash
# Add .gitignore and .gitattributes first
git add .gitignore .gitattributes

# Remove directories from tracking (but keep them on disk)
git rm -r --cached discuss-package/
git rm -r --cached discuss_core/
git rm -r --cached temp_repo/
git rm -r --cached temp_extract/
git rm -r --cached temp_push/
git rm -r --cached minimal_repo/
git rm -r --cached fresh_clone/

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec git rm -r --cached {} \; 2>/dev/null || true
```

## 3. Commit and push the changes

```bash
git commit -m "Clean up repository structure"
git push origin main
```

## 4. Verify the cleanup

Check the remote repository structure:

```bash
git ls-tree -r --name-only origin/main | sort
```

## 5. Optional: Clean local disk

If you want to also clean up your local disk (not just the Git repository):

```bash
# BE CAREFUL with these commands as they will delete files from disk
rm -rf discuss-package/
rm -rf discuss_core/
rm -rf temp_repo/
rm -rf temp_extract/
rm -rf temp_push/
rm -rf minimal_repo/
rm -rf fresh_clone/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
```

## 6. Final project structure

Your final structure should look like:

```
.
├── .gitattributes
├── .gitignore
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── static/
│   ├── templates/
│   ├── templatetags/
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── discuss/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
├── manage.py
└── requirements.txt
```

This guide should help you clean up your repository while avoiding any destructive operations.