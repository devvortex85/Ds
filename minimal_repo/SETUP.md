# Discuss Platform Setup Instructions

This repository contains the complete source code for the Discuss social platform. 
To set up the project locally, follow these steps:

## Using the included tar.gz file

1. Extract the tar.gz file:
   ```
   tar -xzvf discuss-essential.tar.gz
   ```

2. Install the dependencies from requirements.txt

3. Configure your database settings in discuss/settings.py

4. Run migrations

5. Start the development server

## Key Components

- Core app: Contains all models, views, and templates
- discuss: Main project settings and configuration
- Templates: All HTML templates are in core/templates/core/
- Static files: CSS and JavaScript are in core/static/core/

## Database Migration

If you need to migrate from SQLite to PostgreSQL, use the included migrate_data.py script.
