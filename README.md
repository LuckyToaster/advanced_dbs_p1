# Advanced-Databases 2nd Project
Project work for the course Advanced Databases (2509_INSG3_ABDS_A) 

### Authors
- Ellen Gemback
- Senén Marqués

## Project structure
We have included the mandatory files which are the following:
- `ODM.py` - Our ORM library
- `models.yml` - Collection definitions for the practice
- `ODM_test.py` - Tests provided by the teacher for the previous practice
- `model_test.yml` - Collection definitions for the tests 

In addition, we have included:
- `aggregate_queries.py` - aggregate queries for this practice
- `data` - directory with DB data in JSON format
- `requirements.txt` - python dependencies
- `scripts` directory, containing some useful bash scripts:
    - `export_collections.sh` - export DB data to `data` directory 
    - `import_collections.sh` - improt JSON data from `data` directory into DB
    - `start_mongo.sh` - start systemd `mongodb` service, which is **critical for running the practice**
    - `populate_db.py` - ORM queries initially used to populate the DB

And some miscellaneous files for documentation and git version control:
- `.gitignore`
- `.git`
- `README.md` 

## Running the Practice
1. Create python virtual environment, activate it and install the dependencies
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

3. Populate the DB and execute the code
```
./scripts/import_collections.sh # or alternatively: python -m scripts.populate_db
python aggregate_queries.py
pytest ODM_test.py
```


2. Practice execution
    1. Populate the DB
    ```
    ./scripts/import_collections.sh
    ``` 
    or, alternatively 
    ```
    python -m scripts.populate_db
    ```
    2. Run the practice
    ```
    python aggregate_queries.py
    ```
3. Optionally, verify the professor's tests pass
```
pytest ODM_tests.py
```
