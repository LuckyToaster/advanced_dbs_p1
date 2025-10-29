__author__ = 'Senén'
__students__ = 'Senén'

from typing import Generator, Any, Self

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geojson import Point
from bson.objectid import ObjectId

import yaml, time
from random import randint

import pymongo
from pymongo.collection import Collection
from pymongo.command_cursor import CommandCursor
from pymongo.cursor import Cursor
from pymongo import MongoClient
from pymongo.server_api import ServerApi


def getLocationPoint(address: str) -> Point:
    """
    Gets the coordinates of an address in geojson.Point format.
    Uses the geopy API to obtain the coordinates of the address.
    Be careful, the API is public and has a request limit, use sleeps.

    Parameters
    ----------
    address : str
        Full address from which to obtain coordinates

    Returns
    -------
    geojson.Point
        Coordinates of the address point
    """
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



class Model:
    """
    Abstract model class.
    Create as many classes inheriting from this class as
    collections/models desired in the database.

    Attributes
    ----------
    required_vars : set[str]
        Set of attributes required by the model
    admissible_vars : set[str]
        Set of attributes allowed by the model
    db : pymongo.collection.Collection
        Connection to the database collection

    Methods
    -------
    __setattr__(name: str, value: str | dict) -> None
        Overrides the attribute assignment method to control
        which attributes are modified and when.
    __getattr__(name: str) -> Any
        Overrides the attribute access method
    save() -> None
        Saves the model to the database
    delete() -> None
        Deletes the model from the database
    find(filter: dict[str, str | dict]) -> ModelCursor
        Performs a read query in the DB.
        Returns a ModelCursor of models
    aggregate(pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor
        Returns the result of an aggregate query.
    find_by_id(id: str) -> dict | None
        Searches for a document by its ID using cache and returns it.
        If not found, returns None.
    init_class(db_collection: pymongo.collection.Collection, required_vars: set[str], admissible_vars: set[str]) -> None
        Initializes class variables during system initialization.
    """
    _required_vars: set[str]
    _admissible_vars: set[str]
    _location_var: None # initialize this
    _db: Collection
    _data: dict[str, str | dict] = {} 

    def __init__(self, **kwargs: dict[str, str | dict]):
        """
        Initializes the model with values provided in kwargs.
        Checks that the values provided in kwargs are allowed
        by the model and that required attributes are provided.

        Parameters
        ----------
        kwargs : dict[str, str | dict]
            Dictionary with the model's attribute values
        """
        super().__setattr__('_data', {}) # bypass the overriden __setattr__
        
        # check for unallowed keys
        for key in kwargs.keys():
            required = key in self._required_vars
            admissible = key in self._admissible_vars
            id = key != '_id'
            location = key != self._location_var

            if not required and not admissible and not id and not location:
                raise AttributeError(f'\'{key}\' not allowed in {self.__class__.__name__}')


        self._data.update(kwargs)
        # TODO: If _location_var set, get location and assign it

    def __setattr__(self, name: str, value: str | dict) -> None:
        """
        Overrides the attribute assignment method to control
        which attributes are modified and when.
        """
        if name not in self._required_vars and name not in self._admissible_vars and name != self._location_var:
            raise AttributeError(f'\'{name}\' not allowed in {self.__class__.__name__}')
        else:
            self._data[name] = value
        # Perform necessary checks and handling
        # before assignment.
        # Assign the value to the variable name


    def __getattr__(self, name: str) -> Any:
        """
        Overrides the attribute access method.
        __getattr__ is only called when the attribute
        is not found in the object.
        """
        if name in {'_modified_vars', '_required_vars', '_admissible_vars', '_db', '_data', '_location_var'}:
            return super().__getattribute__(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError


    def save(self) -> None:
        if '_id' in self._data:
            self._db.update_one({'_id': self._data['_id']}, {'$set': self._data})
            print(f'updated: {self._data}')
        else:
            self._db.insert_one(self._data)
            print(f'inserted: {self._data}')


    def delete(self) -> None:
        self._db.delete_one(self._data)

    @classmethod
    def find(cls, filter: dict[str, str | dict]) -> Any:
        """
        Uses pymongo's find method to perform a read query
        in the database.
        find should return a ModelCursor of models.

        Parameters
        ----------
        filter : dict[str, str | dict]
            Dictionary with the search criteria

        Returns
        -------
        ModelCursor
            Cursor of models
        """
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
        """
        Initializes class attributes during system initialization.
        Here, indexes should be initialized or ensured. Additional
        initialization/checks or changes may also be made
        as deemed necessary by the student.

        Parameters
        ----------
        db_collection : pymongo.collection.Collection
            Connection to the database collection
        indexes: Dict[str, str]
            Set of indexes and index types for the collection
        required_vars : set[str]
            Set of attributes required by the model
        admissible_vars : set[str]
            Set of attributes allowed by the model
        """
        cls._db = db_collection
        cls._required_vars = required_vars
        cls._admissible_vars = admissible_vars
        cls._location_var = indexes['location_index']

        for index in indexes['unique_indexes']:
            cls._db.create_index([(index, pymongo.ASCENDING)], unique=True, sparse=True)

        for index in indexes['location_index']:
            cls._db.create_index([(indexes['location_index'], pymongo.GEOSPHERE)])

        # TODO
        # what to do with indexes?
        # TODO: Add regular index
        # TODO: Check if location index has been added properly
        

class ModelCursor:
    """
    Cursor to iterate over the documents resulting from a query.
    Documents must be returned as model objects.

    Attributes
    ----------
    model_class : Model
        Class used to create models from the documents being iterated.
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



def initApp(definitions_path: str = "./models.yml", mongodb_uri="mongodb://localhost:27017/", db_name="abd", scope=globals()) -> None:
    """
    Declares the classes that inherit from Model for each of the
    models of the collections defined in definitions_path.
    Initializes the model classes by providing the indexes and
    allowed and required attributes for each of them, and the connection to the
    database collection.

    Parameters
    ----------
    definitions_path : str
        Path to the model definitions file
    mongodb_uri : str
        URI for connecting to the database
    db_name : str
        Name of the database
    """
    # Initialize database
    # Declare as many model classes as there are collections in the database
    # Read the model definitions file to get the collections, indexes, and the allowed and required attributes for each of them.
    # Example of model declaration for a collection called MyModel
    # scope["MyModel"] = type("MyModel", (Model,), {})
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
                # indexes, required_vars and admissible_vars are the kwargs
                model_class.init_class(db.get_collection(model_name), indexes, required_vars, admissible_vars) 
                scope[model_name] = model_class
    except FileNotFoundError:
        print(f'\'{definitions_path}\' not found') 
    # TODO: Check if variable exists before adding it to list (with indexes)


if __name__ == '__main__':
    # Initialize database and models with initApp
    initApp()

    # Example
    # m = MyModel(name="Pablo", surname="Ramos", age=18)
    # m.save()
    # m.name = "Pedro"
    # print(m.name)

    # Create model
    p = Person(name="bob", dni='06637264Q', email="bob@example.com", age=24)
    p.save()
    # Assign new value to allowed variable of the object
    p.age = 26
    # Assign new value to disallowed variable of the object
    try:
        p.favourite_color = 'blue'
    except AttributeError:
        print('favourite color was not allowed and the Attribute error was caught')
    # Save
    p.save()
    # Assign new value to allowed variable of the object
    #p.address = 'C. de Sta. Isabel, 52, Centro, 28012 Madrid'
    p.address = 'Rda. de Valencia, 2, Centro, 28012 Madrid'
    # Save
    p.save()
    # Search for new document with find
    for p in Person.find({'name': 'bob' }):
        print(f'found: {p.name}')

    # Get first document
    # Modify value of allowed variable
    # Save
