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
2. Populate the DB, execute the code and run the tests
```
./scripts/import_collections.sh # or alternatively: python -m scripts.populate_db
python aggregate_queries.py
pytest ODM_test.py
```

## Aggregate Queries Documentation
What follows is some documentation for the aggregated queries found in `aggregated_queries.py`

### 1 - List of all people who have studied at the UPM or UAM.
First, we do a **match** to obtain the 2 EducationalCentres we are interested in.

Then, we do a **lookup** with the Person collection, where we will obtain 2 documents, one for each university, each with an array of Person documents called 'students_who_went_there'.

We then use **unwind** to flatten our result, which results in an array of EducationalCentre documents each with a 'students_who_went_there' field with a single Person Document, so this operation is like a flatten.

Because we want to obtain a list of students as a result, we use **replaceRoot** 

Finally, we use **project** to obtain only a list of Person documents containing only an ObjectId and name field

```
db.EducationalCentre.aggregate([
    { $match: { name: { $in: [ "Universidad Autónoma de Madrid", "Universidad Politecnica de Madrid" ] } } },
    { 
        $lookup: { 
            from: "Person", 
            localField: "_id", 
            foreignField: "education.education_centre",
            as: "students_who_went_there" 
        } 
    },
    { $unwind: "$students_who_went_there" },
    { $replaceRoot: { newRoot: "$students_who_went_there" } },
    { $project: { name: 1 } }
])
```

### 2 - List of the different universities in which people residing in Madrid have studied
First we **match** all the people with 'Madrid' in their address field.
Then we populate their education field with universities in a new field using **lookup**
Then we flatten by 'education' field using **unwind**
Then we get rid of everything that isn't a list of universities with **replaceRoot**
Finally a **group** by name gives us the names of the universities in which all persons residing in madrid have attended.
```
db.Person.aggregate([
    { $match: { address: /Madrid/ } },
    { 
        $lookup: {
            from: 'EducationalCentre',
            localField: 'education.education_centre',
            foreignField: '_id',
            as: 'education'
        }
    },
    { $unwind: '$education' },
    { $replaceRoot: { newRoot: '$education' } },
    { $group: { _id: '$name' } }
])
```

### 3 - People who, in their profile description, include the terms "Big Data" or "Artificial Ingeligence"
Here we match for people who have theese two terms in their description using the **or** operator and **regex**
```
db.Person.aggregate([
    {
        $match: {
            $or: [
                    { description: { $regex: "Big Data", $options: "i" } },
                    { description: { $regex: "Artificial Intelligence", $options: "i" } }
            ]
        }
    },
    { $project: { name: 1, description: 1 } }
])
```

### 4 - Save in a new table the list of people who have completed one of their studies in 2017 or later

```
db.Person.aggregate([
    { $match: { "education.year_graduated": { $gte: 2017 } } },
    { $out: "people_graduated_in_2017_or_later" }
])
```
