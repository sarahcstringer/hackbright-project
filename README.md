# Locography
Locography is a location-based journal that creates concrete views of where users have spent their time. 

### Table of Contents
- [Technologies Used](#tech-used)
- How To Run Locally

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

### How To Run Locally
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

Author: [Sarah Stringer](https://github.com/sarahcstringer)