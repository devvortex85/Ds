# Discuss - Social Community Platform

A dynamic Reddit-like social platform that enables community-driven content sharing and intelligent interaction through advanced social features.

## Key Features

- User authentication with AllAuth
- Community creation and management
- Post creation (text and link posts)
- Commenting with nested replies
- Advanced search functionality
- User profiles with reputation system
- Voting system for posts and comments
- Notification system for user interactions
- Private messaging between users
- Donation functionality

## Technologies

- Django web framework
- PostgreSQL database
- Responsive web design with Bootstrap 5
- AJAX-powered interactive features
- django-allauth for authentication
- django-mptt for nested comments
- django-taggit for tagging
- django-watson for search
- django-countries for location data
- django-postman for messaging
- django-payments for donations
- Sentry for error tracking

## Development Environment Setup

1. Clone the repository:
   ```
   git clone https://codeberg.org/Adamcatholic/Ds.git
   cd Ds
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables (create a .env file or export in your shell):
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/discuss
   DJANGO_SECRET_KEY=your_secret_key
   DEBUG=True
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Deployment Guide

### Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- SSH access
- Domain name (optional but recommended)
- Knowledge of Linux, Nginx, PostgreSQL

### 1. Server Setup

1. Update your system packages and install required software:
   ```
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3 python3-pip python3-venv git nginx postgresql postgresql-contrib
   ```

2. Create a dedicated user for the application:
   ```
   sudo adduser discuss
   sudo usermod -aG sudo discuss
   ```

### 2. Database Setup

1. Create a PostgreSQL database and user:
   ```
   sudo -u postgres psql
   CREATE DATABASE discuss;
   CREATE USER discussuser WITH PASSWORD 'secure_password';
   ALTER ROLE discussuser SET client_encoding TO 'utf8';
   ALTER ROLE discussuser SET default_transaction_isolation TO 'read committed';
   ALTER ROLE discussuser SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE discuss TO discussuser;
   \q
   ```

2. Update your environment variables with the database connection information.

### 3. Application Setup

1. Clone the repository:
   ```
   git clone https://codeberg.org/Adamcatholic/Ds.git /home/discuss/app
   cd /home/discuss/app
   ```

2. Set up a Python virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. Create an environment file (.env) with required settings:
   ```
   DEBUG=False
   DJANGO_SECRET_KEY=your_secure_secret_key
   DATABASE_URL=postgresql://discussuser:secure_password@localhost:5432/discuss
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   SENTRY_DSN=your_sentry_dsn_if_using
   ```

5. Run migrations and collect static files:
   ```
   python manage.py migrate
   python manage.py collectstatic
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

### 4. Web Server Configuration

1. Create a systemd service file for Gunicorn:
   ```
   sudo nano /etc/systemd/system/gunicorn_discuss.service
   ```

   Add the following content:
   ```
   [Unit]
   Description=Gunicorn daemon for Discuss
   After=network.target

   [Service]
   User=discuss
   Group=www-data
   WorkingDirectory=/home/discuss/app
   ExecStart=/home/discuss/app/venv/bin/gunicorn \
             --access-logfile - \
             --workers 3 \
             --bind unix:/home/discuss/app/discuss.sock \
             discuss.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start the Gunicorn service:
   ```
   sudo systemctl enable gunicorn_discuss
   sudo systemctl start gunicorn_discuss
   ```

3. Configure Nginx:
   ```
   sudo nano /etc/nginx/sites-available/discuss
   ```

   Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /home/discuss/app;
       }

       location /media/ {
           root /home/discuss/app;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/home/discuss/app/discuss.sock;
       }
   }
   ```

4. Enable the site and restart Nginx:
   ```
   sudo ln -s /etc/nginx/sites-available/discuss /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. Set up SSL with Let's Encrypt:
   ```
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com -d www.your-domain.com
   ```

### 5. Maintenance and Monitoring

1. Set up automatic database backups:
   ```
   cd /home/discuss
   mkdir backups
   nano backup.sh
   ```

   Add the following script:
   ```bash
   #!/bin/bash
   DATE=$(date +%Y-%m-%d)
   PGPASSWORD=secure_password pg_dump -h localhost -U discussuser discuss > /home/discuss/backups/discuss_$DATE.sql
   ```

   Make it executable and set up a cron job:
   ```
   chmod +x backup.sh
   crontab -e
   ```

   Add the line to run daily at 2 AM:
   ```
   0 2 * * * /home/discuss/backup.sh
   ```

2. Monitor logs:
   ```
   sudo journalctl -u gunicorn_discuss
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

3. Update application:
   ```
   cd /home/discuss/app
   source venv/bin/activate
   git pull
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic
   sudo systemctl restart gunicorn_discuss
   ```

## Security Considerations

1. Always use environment variables for sensitive information
2. Keep your server and packages updated
3. Use HTTPS in production
4. Implement IP rate limiting for login attempts
5. Maintain regular database backups

## Contributing

Contributions to Discuss are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
