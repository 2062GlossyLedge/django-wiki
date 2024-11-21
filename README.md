WikiWard Web Application Setup Instructions

Introduction
Wikiward builds upon the open-source project django-wiki, utilizing the Django framework and SQLite for the backend. It incorporates libraries such as Django Authentication for secure user logins. Django Templates, enhanced with Bootstrap and jQuery, is for frontend design and functionality. Wikiward extends these capabilities with tools like LangChain to provide advanced wiki features. The project is designed to be hosted on AWS.

Installation
Prerequisites
Install Python 3.11 from the official Python website.


Fork the Repository

Clone the Wikiward repository:

git clone https://capstone-cs.eng.utah.edu/wikiward/wikiward.git

Navigate to the project directory

Set up a virtual environment:
python -m venv env
source env/bin/activate  # For Linux/MacOS
env\Scripts\activate     # For Windows
Install required packages:
pip install django
pip install wiki

Configuration
Update settings.py
Add the following to INSTALLED_APPS in your settings.py:

INSTALLED_APPS = [
    'django.contrib.sites.apps.SitesConfig',
    'django.contrib.humanize.apps.HumanizeConfig',
    'django_nyt.apps.DjangoNytConfig',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki.apps.WikiConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig',
    'wiki.plugins.notifications.apps.NotificationsConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.macros.apps.MacrosConfig',
]
Add the required context processors:

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "sekizai.context_processors.sekizai",
            ],
        },
    },
]
Additional django-wiki configuration settings: 
https://django-wiki.readthedocs.io/en/latest/installation.html

Development Setup

Install Hatch 

Hatch is used for environment management:

pip install hatch
hatch env create
hatch shell

Additional Hatch configuration settings:

https://django-wiki.readthedocs.io/en/latest/development/environment.html

Install Required Libraries 

Inside /testproject/testproject/
Install dependencies using:

pip install -r requirements.txt

Tailwind Setup 
Install and configure Tailwind for styling:

python -m pip install django-tailwind[reload]
python manage.py tailwind init
python manage.py tailwind install
python manage.py tailwind start

Additional Tailwind configuration settings:
https://django-tailwind.readthedocs.io/en/latest/installation.html#content-formerly-purge-rules-configuration


Environment Variables
Store API keys in /testproject/testproject/settings/.env:
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
GOOGLE_API_KEY=your_google_api_key


Running the Application
While inside the Hatch shell

Locate folder holding manage.py 

cd /testproject/testproject

Create Database Tables

python manage.py makemigrations
python manage.py migrate

Create a superuser:

python manage.py createsuperuser

Start the development server:

python manage.py runserver
Access the local development at the port 8000 in the url http://localhost:8000/.
Interacting with the Application

Sign in to the website using your credentials used to create the superuser

Create a root wiki

Now you can explore all that WikiWard has to offer!

Deploying the Application
EC2 Instance Setup
Launch an Ubuntu EC2 Instance on AWS 
Follow the above instructions to get WikiWard setup in the instance
Adjust testproject/testproject/settings/base.py, testproject/testproject/settings/demo.py, testproject/testproject/settings/dev.py to have
ALLOWED_HOSTS = [‘your_domain.com’]
And 
SESSION_COOKIE_DOMAIN = “.your_domain.com”
Install Gunicorn and Nginx
sudo apt install nginx -y
sudo apt install gunicorn -y

Setup Gunicorn
Create a gunicorn service file

sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/wikiward/testproject/
ExecStart=path/to/your/gunicorn/bin --workers 3 --bind unix:/home/ubuntu/wikiward/testproject/testproject.sock testproject.wsgi:application
Environment=”SECRET_KEY=yoursecretkey”

[Install]
WantedBy=multi-user.target

Reload the systemd daemon and start Gunicorn

sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

Setup Nginx

Create an Nginx server block
sudo nano /etc/nginx/sites-available/testproject

Server {
	listen 80;
	server_name your_domain.com

	location /static/ {
		Root /home/ubuntu/wikiward/testproject/testproject;
	}

	Location /media/ {
		root /home/ubuntu/wikiward/testproject/testproject;
	}

	Location / {
		Proxy_pass http://unix:/home/ubuntu/wikiward/testproject/testproject.sock;
		proxy_set_header Host $host
		Proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}
}

Link the configuration and remove the default

sudo ln -s /etc/nginx/sites-available/testproject /etc/nginx/sites-enabled

sudo rm /etc/nginx/sites-enabled/default

Restart Nginx

sudo systemctl restart nginx
