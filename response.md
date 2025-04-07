# Response
## A. Required Information
### A.1. Requirement Completion Rate
- [X] Select development tools.
- Key considerations focused on: *development efficiency*, *architectural completeness*, and *ease of prototyping*. To concentrate on core feature implementation, I chose SQLite as the initial database due to its simplicity and adequacy for early-stage development. Given my familiarity with Python, I adopted `Django` along with `Django REST Framework (DRF)`, which enables rapid development of well-structured RESTful APIs and offers robust model management, aligning well with the current needs of the project.
- [X] Design database schema.
- Analysis and design:
  - By analyzing the requirements and the data, we can identify four core entities: `users`, `pharmacies`, `masks`, and `transactions` with the following relationships:
    1. A `user` performs multiple `transactions`.
    2. Each `mask` is characterized by its model, color, and pack size and can be included in multiple `transactions`.
    3. A `pharmacy` processes mutilple `transactions`.
    4. A `pharmacy` can sell multiple types of `masks`, and each type of `mask` can be available at multiple `pharmacies` (N to N).
  - Based on these relationships, the design considerations are that:
    1. The `masks` table should define mask types by distinguishing them through a combination of model, color, and pack size.
    2. The `transaction` table should be normalized to separate information of the three entities and other purchase-related attributes.
    3. A join table is necessary to normalize the N-to-N relationship between `pharmacies` and `masks`, allowing each pharmacy to set different prices for each mask type it offers.
  - Hence, the tables are designed as follows (or see the [ERD](https://drive.google.com/file/d/1TJGQgKH0TNSHkjXInfxpcH3f2wFDlJSp/view?usp=drive_link)):  
`pharmacies`: Stores pharmacy details including opening hours (days X opening/closing time).  
`masks`: Stores mask information (model + color + # of packs).  
`pharmacy_masks`: Links masks to pharmacies with price. Extesible for other dependent attributes (e.g., stock level, ads) in the futue.  
`users`: Stores user information.  
`transactions`: Stores transaction records.   

- [x] Complete ETL scripts to import given json data to sqlite database.
- Given that the system is still in the development phase with manageable data volume, I have chosen to perform the ETL process manually for now. This allows for flexibility in adjusting logic and quickly addressing issues. Automation can be considered when the system becomes stable with consistent data needs.
  - Implemented at `pharmacies_etl_script.py` and `users_etl_script.py`.

- [x] Build ORM models in django and finish migration.

- [x] Complete the API: List all pharmacies open at a specific time and on a day of the week if requested.
  - Implemented at `OpenPharmaciesListView` API.
  - Tested and documented.
- [x] Complete the API: List all masks sold by a given pharmacy, sorted by mask name or price.
  - Implemented at `PharmacyMasksListView` API.
  - Tested and documented.
- [x] Complete the API: List all pharmacies with more or less than x mask products within a price range.
  - Implemented at `PharmaciesMaskCompareListView` API.
  - Tested and documented.
- [x] Complete the API: The top x users by total transaction amount of masks within a date range.
  - Implemented at `ActiveTransactionsUserListView` API.
  - Tested and documented.
- [x] Complete the API: The total number of masks and dollar value of transactions within a date range.
  - Implemented at `MaskTransactionsView` API.
  - Tested and documented.
- [x] Complete the API: Search for pharmacies or masks by name, ranked by relevance to the search term.
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

- [x] Complete an addtional API: Delete the latest transaction record.
  - Implemented at `CancelLatestTransactionView` API.
  - Tested and documented.
  - Simply delete a record. The API needs to be refactored in a more robust way for production.
  
- [x] Refactor the APIs:
- Design concept: There are several queries. The query logic for pharmacies and users is abstracted into the `PharmacyQueryService` and `UserQueryService` modules, respectively, separating it from the view layer. Logic related to masks, due to their dependency on pharmacies, is also handled within the `PharmacyQueryService`. The abstraction simplifies views, enhances maintainability, and makes it easier to extend or reuse query conditions in the future.
  
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

[Here](https://drive.google.com/file/d/1TJGQgKH0TNSHkjXInfxpcH3f2wFDlJSp/view?usp=drive_link) is My ERD design.

### C.2. Technical Document

For frontend programmer reading, please check this [technical document](https://hackmd.io/@LLH/Bk9rZVFaJg) to know how to operate those APIs.

- --