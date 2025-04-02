# Response
## A. Required Information
### A.1. Requirement Completion Rate
- [X] Design database schema.
  - Tables are designed as follows:
  `pharmacies`: Stores pharmacy details including opening hours (days X opening/closing time).  
  `masks`: Stores mask information (model + color + # of packs).  
  `pharmacy_masks`: Links masks to pharmacies with price. Extesible for other dependent attributes (e.g., ads) in the futue.  
  `users`: Stores user information.  
  `transactions`: Stores user transaction records.  

- [x] Complete ETL scripts to import given json data to sqlite database.
  - Implemented at pharmacies_etl_script.py and users_etl_script.py.

- [ ] List all pharmacies open at a specific time and on a day of the week if requested.
  - Implemented at xxx API.
- [ ] List all masks sold by a given pharmacy, sorted by mask name or price.
  - Implemented at xxx API.
- [ ] List all pharmacies with more or less than x mask products within a price range.
  - Implemented at xxx API.
- [ ] The top x users by total transaction amount of masks within a date range.
  - Implemented at xxx API.
- [ ] The total number of masks and dollar value of transactions within a date range.
  - Implemented at xxx API.
- [x] Search for pharmacies or masks by name, ranked by relevance to the search term.
  - Implemented at xxx API.
- [x] Process a user purchases a mask from a pharmacy, and handle all relevant data changes in an atomic transaction.
  - Implemented at xxx API.
### A.2. API Document
> Please describe how to use the API in the API documentation. You can edit by any format (e.g., Markdown or OpenAPI) or free tools (e.g., [hackMD](https://hackmd.io/), [postman](https://www.postman.com/), [google docs](https://docs.google.com/document/u/0/), or  [swagger](https://swagger.io/specification/)).

Import [this](#api-document) json file to Postman.

### A.3. Build Tables Commands
Please run the script command to setup tables for the database (phantom_mask_db.sqlite3).

```bash
$ python [PATH_TO_FILE]/db_setup.py
```

### A.4. Import Data Commands
Please run the following script commands to migrate the data into the database (phantom_mask_db.sqlite3).

```bash
$ python [PATH_TO_FILE]/pharmacies_etl_script.py
$ python [PATH_TO_FILE]/users_etl_script.py
```
## B. Bonus Information

>  If you completed the bonus requirements, please fill in your task below.
### B.1. Test Coverage Report

I wrote down the 20 unit tests for the APIs I built. Please check the test coverage report at [here](#test-coverage-report).

You can run the test script by using the command below:

```bash
bundle exec rspec spec
```

### B.2. Dockerized
Please check my Dockerfile / docker-compose.yml at [here](https://github.com/a11031371/phantom_mask/blob/master/Dockerfile).

On the local machine, please follow the commands below to build it.

```bash
$ docker build --build-arg ENV=development -p 80:3000 -t my-project:1.0.0 .  
$ docker-compose up -d

# go inside the container, run the migrate data command.
$ docker exec -it my-project bash
$ rake import_data:pharmacies[PATH_TO_FILE] 
$ rake import_data:user[PATH_TO_FILE]
```

### B.3. Demo Site Url

The demo site is ready on [my AWS demo site](#demo-site-url); you can try any APIs on this demo site.

## C. Other Information

### C.1. ERD

My ERD [erd-link](#erd-link).

### C.2. Technical Document

For frontend programmer reading, please check this [technical document](technical-document) to know how to operate those APIs.

- --