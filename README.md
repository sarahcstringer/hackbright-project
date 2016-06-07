# Locography
Locography is a location-based journal that creates concrete views of where users have spent their time. 
![Login Page](/static/img/login.png)

### Table of Contents
- [Technologies Used](#tech-used)
- [How To Run Locally](#run-local)
- [Features](#features)

## <a name="tech-used"></a>Technologies Used
- Python
- Flask
- PostgresSQL
- Javascript/jQuery
- AJAX/JSON
- Jinja2
- Chart.js
- Bootstrap
- Google Maps API
- Google Locations API

Dependencies are listed in requirements.txt

## <a name="run-local"></a>How To Run Locally
Locography is not deployed.

- Create a python virtual environment and install all dependencies
```sh
$ pip install -r requirements.txt
```
- Have PostgreSQL running. Create a database called _locations_:
```sh
$ psql
# CREATE DATABASE locations
```
- Create the tables in the database:
```sh
$ python model.py
```
- Start Flask server:
```sh
$ python server.py
```
- Access the web app at localhost:5000

## <a name='features'></a>Features
- Account setup and user login
- Add a log/location (uses Google Locations API to collect information about the location -- lat, long, address, phone, website -- and save it in the locations database)
- View logs:
    * On home page load, browser receives a JSON object of any logs a user has already created for the current date.
    * User can scroll through day by day (using << and >> buttons) or select a date on the dropdown datepicker menu to jump to that specific day's logs.
    * Ways to interact with logs on homepage:

![Homepage](/static/img/homepage1.png)
    
- View a directory of all locations a user has visited and search directory
    * View details about each location, including any logs about that location
- Edit username and home location

Author: [Sarah Stringer](https://www.linkedin.com/in/sarahstringer)