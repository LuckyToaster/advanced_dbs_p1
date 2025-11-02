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
- `scripts` directory, containing some useful bash scripts:
    - `export_collections.sh` - export DB data to `data` directory 
    - `import_collections.sh` - improt JSON data from `data` directory into DB
    - `start_mongo.sh` - start systemd `mongodb` service, which is **critical for running the practice**
    - `populate_db.py` - ORM queries initially used to populate the DB

And some miscellaneous files for documentation and git version control:
- `.gitignore` file 
- `.git` directory
- `README.md` Documentation

## Running the Project
### 1 - Prepare Python Virtual Environment for Execution
Create a python virtual environment and install the dependencies
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 2 - Execution
In order to execute the second practice, we must first popoulate the DB, this can be done by either running 
```
./scripts/import_collections.sh
``` 
or, alternatively
```
python -m scripts.populate_db`
```

After the DB is populated with data, we can run the practice with
```
python aggregate_queries.py
```

Optionally we can verify that the ORM passes the professor's tests with:
```
pytest ODM_tests.py
```


