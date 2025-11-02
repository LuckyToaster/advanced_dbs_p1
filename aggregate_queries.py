from ODM import initApp
import re

initApp(scope=globals())


print('Exercise 1')
res = EducationalCentre.aggregate([
    { '$match': { 'name': { '$in': [ "Universidad Autónoma de Madrid", "Universidad Politecnica de Madrid" ] } } },
    { 
        '$lookup': { 
            'from': "Person", 
            'localField': "_id", 
            'foreignField': "education.education_centre",
            'as': "students_who_went_there" 
        } 
    },
    { '$unwind': "$students_who_went_there" },
    { '$replaceRoot': { 'newRoot': "$students_who_went_there" } },
    { '$project': { 'name': 1 } }
])
for r in res: print(r)


print('Exercise 2')
res = Person.aggregate([
    {
        '$lookup': {
            'from': "EducationalCentre",
            'localField': "education.education_centre",
            'foreignField': "_id",
            'as': "education_details"
        }
    },
    { '$unwind': "$education_details" },
    { '$match': { "education_details.address": re.compile('Madrid', re.IGNORECASE) } },
    { '$group': { '_id': "$education_details.name" } },
    { '$project': { 'university': "$_id", '_id': 0 } }
])
for r in res: print(r)


print('Exercise 3')
res = Person.aggregate([
    {
        '$match': {
            '$or': [
                    { 'description': { '$regex': "Big Data", '$options': "i" } },
                    { 'description': { '$regex': "Artificial Intelligence", '$options': "i" } }
            ]
        }
    },
    { '$project': { 'name': 1, 'description': 1 } }
])
for r in res: print(r)


print('Exercise 4')
Person.aggregate([
    { '$match': { 'education.year_graduated': { '$gte': 2017 } } },
    { '$out': 'people_graduated_in_2017_or_later' }
])
print('Seemed to run successfully, check in the DB if the collection \'people_graduated_in_2017_or_later\' exists')


print('Exercise 5')
res = Person.aggregate([
    {
        '$lookup': {
            'from': 'Company',
            'localField': 'company',
            'foreignField': '_id',
            'as': 'the_company'
        }
    },
    { '$unwind': '$the_company' },
    { '$match': { 'the_company.name': 'Microsoft' } },
    { '$project': { 'n_studies': { '$size': '$education' } } },
    {
        '$group': {
            '_id': None,
            'avg_studies': { '$avg': '$n_studies' }
        }
    }
])
for r in res: print(r)


print('Exercise 6')
res = Person.aggregate([
    {
        '$geoNear': {
            'near': { 'type': 'Point', 'coordinates': [-3.692602, 40.456426] },
            'distanceField': 'distance_to_office',
            'spherical': True
        }
    },
    {
        '$lookup': {
            'from': 'Company',
            'localField': 'company',
            'foreignField': '_id',
            'as': 'company_data'
        }
    },
    { '$unwind': '$company_data' },
    { '$match': { 'company_data.name': 'Google' } },
    {
        '$group': {
            '_id': None,
            'avg_distance': { '$avg': '$distance_to_office' }
        }
    }
])
for r in res: print(r)
