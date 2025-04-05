# Response
## A. Required Information
### A.1. Requirement Completion Rate
- [X] Design database schema.
  - Tables are designed as follows:  
`pharmacies`: Stores pharmacy details including opening hours (days X opening/closing time).  
`masks`: Stores mask information (model + color + # of packs).  
`pharmacy_masks`: Links masks to pharmacies with price. Extesible for other dependent attributes (e.g., mask stocks, ads) in the futue.  
`users`: Stores user information.  
`transactions`: Stores user transaction records.  

- [x] Complete ETL scripts to import given json data to sqlite database.
  - Implemented at pharmacies_etl_script.py and users_etl_script.py.

- [x] Build ORM models in django and finish migration.

- [x] Complete task: List all pharmacies open at a specific time and on a day of the week if requested.
  - Implemented at `OpenPharmaciesListView` API.
  - Tested and documented.
- [x] Complete task: List all masks sold by a given pharmacy, sorted by mask name or price.
  - Implemented at `PharmacyMasksListView` API.
  - Tested and documented.
- [x] Complete task: List all pharmacies with more or less than x mask products within a price range.
  - Implemented at `PharmaciesMaskCompareListView` API.
  - Tested and documented.
- [x] Complete task: The top x users by total transaction amount of masks within a date range.
  - Implemented at `ActiveTransactionsUserListView` API.
  - Tested and documented.
- [x] Complete task: The total number of masks and dollar value of transactions within a date range.
  - Implemented at `MaskTransactionsListView` API.
  - Tested and documented.
- [x] Complete task: Search for pharmacies or masks by name, ranked by relevance to the search term.
  - Implemented at `SearchView` API.
  - Tested and documented.
  - Developed a custom mathematical model combining:
    [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance#:~:text=The%20Levenshtein%20distance%20between%20two,defined%20the%20metric%20in%201965.) (edit distance)
    [Jaro-Winkler Distance](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance) (string similarity)
    [Jaccard Similarity](https://en.wikipedia.org/wiki/Jaccard_index) (word overlap)
    Conducted experiments to adjust weighting and improve ranking quality.
  - Wrote `StringRelevance` module incorporating the custom ranking model and integrated it in `SearchView`.
  
- [x] Complete task: Process a user purchases a mask from a pharmacy, and handle all relevant data changes in an atomic transaction.
  - Implemented at `PurchaseMaskView` API.
  - Tested and documented.

- [x] Addtional API: Delete the latest transaction record.
  - Implemented at `CancelLatestTransactionView` API.
  - Tested and documented.
  
### A.2. API Document
Please go [here](https://hackmd.io/@LLH/Bk9rZVFaJg) to refer to the API documentation.

### A.3. Build Tables Commands
Please run the script command to setup tables for the database (phantom_mask_db.db).

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
### B.1. Test Coverage Report

> todo

### B.2. Dockerized
Please check my Dockerfile at [here](https://github.com/a11031371/phantom_mask/blob/master/phantom_mask_api_server/Dockerfile) and docker-compose.yml at [here](https://github.com/a11031371/phantom_mask/blob/master/compose.yaml).

On the local machine, please follow the commands below to build it.

```bash
$ docker-compose build  
$ docker-compose up -d
```

### B.3. Demo Site Url

> todo

## C. Other Information

### C.1. ERD

My ERD [erd-link](#erd-link).

### C.2. Technical Document

For frontend programmer reading, please check this [technical document](https://hackmd.io/@LLH/Bk9rZVFaJg) to know how to operate those APIs.

- --