__author__ = 'Senén'
__students__ = 'Senén'

import yaml, time, pytest, pymongo, json
from typing import Generator, Any, Self
from random import randint


from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geojson import Point
from bson.objectid import ObjectId

from pymongo.collection import Collection
from pymongo.command_cursor import CommandCursor
from pymongo.cursor import Cursor
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError


# prettry print 
def format(data):
    return json.dumps(data, indent=4, default=str)


def getLocationPoint(address: str) -> Point:
    location = None
    retries = 0
    while retries < 5:
        retries += 1
        try:
            time.sleep(1)
            # Use a random name for the user_agent
            location = Nominatim(user_agent=f'random-name-{randint(0, 1000)}').geocode(address)
            if location: 
                return Point([location.longitude, location.latitude])
        except GeocoderTimedOut:
            continue
    raise ValueError('No se pudieron obtener coordenadas')


def initApp(definitions_path: str = "./models.yml", mongodb_uri="mongodb://localhost:27017/", db_name="abd", scope=globals()) -> None:
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
    db = client[db_name]
    try:
        with open(definitions_path) as models_file:
            for model_name, model_data  in yaml.safe_load(models_file).items():
                required_vars = model_data['required_vars']
                admissible_vars = model_data['admissible_vars']
                indexes = { 
                    'unique_indexes': model_data['unique_indexes'], 
                    'regular_indexes': model_data['regular_indexes'], 
                    'location_index': f'{model_data['location_index']}_loc'
                }
                model_class = type(model_name, (Model,), {})
                model_class.init_class(db.get_collection(model_name), indexes, required_vars, admissible_vars) 
                scope[model_name] = model_class
    except FileNotFoundError:
        print(f'\'{definitions_path}\' not found') 


class Model:
    _required_vars: set[str]
    _admissible_vars: set[str]
    _location_var: None 
    _db: Collection
    _data: dict[str, str | dict] = {} 

    def __init__(self, **kwargs: dict[str, str | dict]):
        super().__setattr__('_data', {}) # bypass the overriden __setattr__
        # check for unallowed keys
        for key in kwargs.keys():
            if key not in self._required_vars and key not in self._admissible_vars and key != '_id':
                raise AttributeError(f'\'{key}\' not allowed in {self.__class__.__name__}')
        self._data.update(kwargs)


    def __setattr__(self, name: str, value: str | dict) -> None:
        if name not in self._required_vars and name not in self._admissible_vars and name != self._location_var:
            raise AttributeError(f'\'{name}\' not allowed in {self.__class__.__name__}')
        else: self._data[name] = value


    def __getattr__(self, name: str) -> Any:
        # if name is one of these attributes, get it with its parent's __getattribute__
        if name in {'_modified_vars', '_required_vars', '_admissible_vars', '_db', '_data', '_location_var'}:
            return super().__getattribute__(name) 
        # otherwise get it like this
        try: return self._data[name]
        except KeyError: raise AttributeError(f'"{name}" is not a valid attribute for {self.__class__.__name__}')


    def save(self) -> None:
        if '_id' in self._data:
            try: 
                self._db.update_one({'_id': self._data['_id']}, {'$set': self._data})
                print(f'updated => {format(self._data)}\n')
            except DuplicateKeyError: 
                print(f'DuplicateKeyError when updating {format(self._data)}\n')
        else:
            try:
                # get the coordinates for the location_index IF the class has the location_var in its ._data (if an attribute flagged as location_index has been defined / passed in the constructor) 
                if self._location_var[0:-4] in self._data.keys():
                    self._data[self._location_var] = getLocationPoint(self._data[self._location_var[0:-4]])
                self._db.insert_one(self._data)
                print(f'inserted => {format(self._data)}\n')
            except DuplicateKeyError: 
                print(f'DuplicateKeyError when inserting {format(self._data)}\n')


    def delete(self) -> None:
        self._db.delete_one(self._data)


    @classmethod
    def find(cls, filter: dict[str, str | dict]) -> Any:
        cursor = cls._db.find(filter)
        return ModelCursor(cls, cursor)

    @classmethod
    def aggregate(cls, pipeline: list[dict]) -> CommandCursor:
        """
        Returns the result of an aggregate query.
        Nothing needs to be done in this function.
        It will be used for queries requested
        in the second project of the practice.

        Parameters
        ----------
        pipeline : list[dict]
            List of stages in the aggregate query

        Returns
        -------
        pymongo.command_cursor.CommandCursor
            pymongo cursor with the query result
        """
        return cls._db.aggregate(pipeline)


    @classmethod
    def find_by_id(cls, id: str) -> Self | None:
        """
        DO NOT IMPLEMENT UNTIL THE THIRD PROJECT
        Searches for a document by its ID using cache and returns it.
        If not found, returns None.

        Parameters
        ----------
        id : str
            ID of the document to search

        Returns
        -------
        Self | None
            Model of the found document or None if not found
        """
        # TODO
        pass


    @classmethod
    def init_class(cls, db_collection: Collection, indexes: dict[str, str], required_vars: set[str], admissible_vars: set[str]) -> None:
        cls._db = db_collection
        cls._required_vars = required_vars
        cls._admissible_vars = admissible_vars
        cls._location_var = indexes['location_index']

        for index in indexes['unique_indexes']:
            cls._db.create_index([(index, pymongo.ASCENDING)], unique=True, sparse=True)

        # for index in indexes['location_index']:
        #     cls._db.create_index([(index, pymongo.GEOSPHERE)])
        #     print(f'creating location index => {index}')

        for index in indexes['regular_indexes']:
            cls._db.create_index([(index, pymongo.ASCENDING)])

        print(f'creating location index => {indexes['location_index']}')
        cls._db.create_index([(indexes['location_index'], pymongo.GEOSPHERE)])


 

class ModelCursor:
    """
    Cursor to iterate over the documents resulting from a query.
    Documents must be returned as model objects.

    Attributes
    ----------
    model_class : Model
        Class used to create models from the documents being iterated. 'address_loc'}
creating unique index => email
    cursor : pymongo.cursor.Cursor
        Pymongo cursor to iterate

    Methods
    -------
    __iter__() -> Generator
        Returns an iterator that goes through the cursor elements
        and returns the documents as model objects.
    """
    def __init__(self, model_class: Model, cursor: Cursor):
        """
        Initializes the cursor with the model class and pymongo cursor.

        Parameters
        ----------
        model_class : Model
            Class used to create models from the documents being iterated.
        cursor: pymongo.cursor.Cursor
            Pymongo cursor to iterate
        """
        self.model = model_class
        self.cursor = cursor

    def __iter__(self) -> Generator:
        """
        Returns an iterator that goes through the cursor elements
        and returns the documents as model objects.
        Use yield to generate the iterator.
        Use next to get the next document from the cursor.
        Use alive to check if more documents exist.
        """
        for doc in self.cursor:
            yield self.model(**doc) # we unwrap the python dictionary to the constructor

        # TODO: Create generator function and use yield in it
        # TODO: Use alive variable


if __name__ == '__main__':
    initApp() # Initialize database and models with initApp

    upm = EducationalCentre(name='Universidad Politecnica de Madrid', website='upm.es', year_founded=1971, address='Av. Complutense, s/n, Moncloa - Aravaca, 28040 Madrid')
    upm.save()
    uam = EducationalCentre(name='Universidad Autónoma de Madrid', website='uam.es', year_founded=1968, address='C. Francisco Tomás y Valiente, 5, Fuencarral-El Pardo, 28049 Madrid') 
    uam.save()
    ucm = EducationalCentre(name='Universidad Complutense de Madrid', website='ucm.es', year_founded=1293, address='Av. Complutense, s/n, Moncloa - Aravaca, 28040 Madrid')
    ucm.save()
    utad = EducationalCentre(name='U-TAD: Centro Universitario de Tecnologia y Arte Digital', website='u-tad.com', year_founded=2011, address='C. Playa de Liencres, 2 bis, 28290 Las Rozas de Madrid, Madrid')
    utad.save()

    deloitte = Company(name='Deloitte', cif='D45678901', website='deloitte.com/es', address='Torre Picasso Madrid, Madrid 28020 España')
    deloitte.save()
    accenture = Company(name='Accenture', cif='C34567890', website='accenture.com/es', address='P.º de la Castellana, 85, Tetuán, 28046 Madrid')
    accenture.save()
    microsoft = Company(name='Microsoft', cif='B23456789', website='microsoft.com/es-es/')
    microsoft.save()
    startup = Company(name='Custom Solutions SA', cif='C12345678', website='customsolutions.es', address='Avenida de Europa 10, Pozuelo de Alarcón, Madrid, 28223 España')
    startup.save()

    p1 = Person(
            name='alex',
            email='alex@email.com',
            description='I like Software Engineering and AI, did i mention i really love AI?',
            education=[{'name': 'computer science', 'year_graduated': 2026, 'education_centre': upm._id}]) 
    p1.save()
    p2 = Person(
        name='clara', 
        email='clara@email.com', 
        description='I am passionate about programming, Machine Learning and Data Science',
        education=[ {'name': 'computer science', 'year_graduated': 2020, 'education_centre': uam._id}, {'name': 'data science', 'year_graduated': 2024, 'education_centre': utad._id} ]
    )
    p2.save()

    p3 = Person(
        name='lucas',
        email='lucas@email.com',
        description='Software engineer interested in backend systems.',
        education=[ {'name': 'computer engineering', 'year_graduated': 2019, 'education_centre': ucm._id} ]
    )
    p3.save()

    p4 = Person(
        name='maria',
        email='maria@email.com',
        description='Data analyst with experience in machine learning.',
        education=[ {'name': 'data science', 'year_graduated': 2022, 'education_centre': uam._id} ]
    )
    p4.save()

    p5 = Person(
        name='javier',
        email='javier@email.com',
        description='Web developer specialized in frontend frameworks.',
        education=[ {'name': 'multimedia engineering', 'year_graduated': 2021, 'education_centre': utad._id} ]
    )
    p5.save()

    p6 = Person(
        name='sofia',
        email='sofia@email.com',
        description='Cloud computing enthusiast and DevOps engineer.',
        education=[
            {'name': 'computer science', 'year_graduated': 2018, 'education_centre': upm._id},
            {'name': 'information systems', 'year_graduated': 2020, 'education_centre': ucm._id}
        ]
    )
    p6.save()

    # from Practice 1
    # p = Person(name="bob", email="bob@example.com")
    # p.save()
    # try: p.favourite_color = 'blue' 
    # except Exception as e: print(e)
    # p.save()
    # p.address = 'Rda. de Valencia, 2, Centro, 28012 Madrid'
    # p.save()
    # for p in Person.find({'name': 'bob' }): print(f'found: {p.name}')

    pytest.main(["-v", "./"]) # Running the professor's tests

