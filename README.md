#KAINO PROJECT

# KAINO PROJECT

## Overview

KAINO is a web application that allows users to create and manage tasks. It's intended for individuals or teams who need a simple, lightweight way to keep track of their to-do lists.

## Getting Started

In the .env file add CREDENTIALS as given in .envExample file.


To get started with KAINO, follow these steps:

1. Clone this repository to your local machine.
2. Create a virtual environment in your root file.
3. Install dependencies by running `pip install -r requirements.txt`.
4. Create a MYSQL database and update the `DATABASES` credentials in .env file.
5. Run database migrations by running `python manage.py makemigrations`.
6. Run migrate by ruuning  `python manage.py migrate`.
7. Start the server by running `python manage.py runserver 0.0.0.0:8000`.
8. Visit `http://localhost:8000` in your web browser to view the app.

## Technologies Used

KAINO was built using the following technologies:

- Django
- Mysql
