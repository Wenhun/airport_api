# airport_api

API service for airport management.

## Features

- JWT authenticated
- Admin panel available at `/admin/`
- API documentation available at `/api/doc/swagger/`
- Managing users and authentication
- Managing airports, cities, and countries
- Creating and managing routes
- Managing airplanes and airplane types
- Scheduling flights
- Managing orders and tickets
- Filtering and searching for flights, airports, and routes

## Installing using GitHub

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd airport_api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   set DB_HOST=<your_db_host>
   set DB_NAME=<your_db_name>
   set DB_USER=<your_db_user>
   set DB_PASSWORD=<your_db_password>
   set DJANGO_SECRET_KEY=<your_secret_key>
   set ACCESS_TOKEN_LIFETIME=<token_lifetime_in_minutes>
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Run the server:
   ```bash
   python manage.py runserver
   ```

## Run with Docker

1. Ensure Docker is installed on your system.

2. Build and run the containers:
   ```bash
   docker-compose build
   docker-compose up
   ```

## Getting access

- Create a user via `/api/user/register/`
- Get an access token via `/api/user/token/`