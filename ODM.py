__author__ = 'Ellen Gemback'
__students__ = 'Ellen Gemback'

#Imports
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from random import randint

import time
from typing import Generator, Any, Self
from geojson import Point
from bson.objectid import ObjectId
import yaml
import json

#Pymongo and DB connection
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#Testing
import pytest

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
            # TODO
            # A user_agent is required to use the API
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
    _location_var: None
    _db: pymongo.collection.Collection
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
        #Initialize data with an empty dictionary
        super().__setattr__('_data', {})
        
        #Make sure the object is not created if required fields are missing
        missing = [var for var in self._required_vars if var not in kwargs]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")            
        
        # Handle location geocoding 
        if hasattr(self, '_location_var') and self._location_var:
            #Get the original location index value (keyname) (without the added _coordinates)
            address_field = self._location_var.replace("_coordinates", "")
            
            #Check if the field is in the received kwargs
            if address_field in kwargs and self._location_var not in kwargs:
                try:
                    point = getLocationPoint(kwargs[address_field])
                    
                    if point:
                        # Store coordinates in location_var
                        # This adds a NEW field that's not in kwargs originally
                        # Convert Point to MongoDB GeoJSON dict format
                        kwargs[self._location_var] = {
                            "type": "Point",
                            "coordinates": list(point.coordinates)
                        }
                        
                except Exception as e:
                    print(f"\nCould not geocode address '{kwargs[address_field]}'")
                    print(f"Error: {e}")
        
        # validate all provided attributes (including the newly added location field)
        #Let "_id" bypass as this is assigned by mongodb and not by the python program
        #Let _location_var pass because this is created from the adress but is not required
        for key_name in kwargs:
            if key_name == "_id":
                continue
            
            if (hasattr(self, '_location_var') and key_name == self._location_var):
                continue
            
            if hasattr(self, '_location_var') and self._location_var and key_name == self._location_var.replace("_coordinates", ""):
                continue

            #Check so that no non required nor non admissible vars are added to _data
            if key_name.lower() not in self._admissible_vars and key_name.lower() not in self._required_vars:
                raise ValueError(f"Invalid field for this model: {key_name}")
        
        # Assign allowed values to _data attribute
        self._data.update(kwargs)

    def __setattr__(self, name: str, value: str | dict) -> None:
        """
        Overrides the attribute assignment method to control
        which attributes are modified and when.
        """        
        if name == "_data":
            #Making sure the value is a dictionary and not something else as _data is going to store key value pairs
            if not isinstance(value, dict):
                raise TypeError("_data must be a dictionary")
            
                #Uses settattr method from the parent class
                #Accessing the original functionality of the setter
                
            super().__setattr__(name, value)
                
        else:
            # Accept allowed attributes
            if hasattr(self, "_admissible_vars") and (name in self._admissible_vars or name in self._required_vars or name == "_location_var"):
                self._data[name] = value
                
            else:
                # Ignore disallowed attributes
                print(f"{name} is not an admissible attribute. The value-key pair will not be stored in the database.")

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
        """
        Saves the model to the database.
        If the model does not exist in the database, a new
        document is created with the model's values. Otherwise,
        the existing document is updated with the new values.
        """            
        # Auto-geocode address
        if self._location_var:
            #Get org fieldname (key)
            coordinates_field = self._location_var.replace("_coordinates", "")
            #See if the key is present
            if coordinates_field in self._data:
                try:
                    #Try to get coordinates for adress
                    coordinates = getLocationPoint(self._data[coordinates_field])
                    
                    #GeoJSON formatting
                    if coordinates:
                        self._data[self._location_var] = {
                            "type": "Point",
                            "coordinates": list(coordinates.coordinates)
                        }
                    
                except Exception as e:
                    print(f"Could not geocode address. Will only save address not coordinates")
                    print(f"Error: {e}")
        
        # Prepare data to save (avoid DuplicateKeyError on _id)
        data_to_save = self._data.copy()
        data_to_save.pop("_id", None)
        
        if "_id" in self._data and self._data["_id"]:
            query = {"_id": self._data["_id"]}
        else:
            query = {"name": self._data.get("name")}  # since 'name' is unique for User
            
        result = self._db.update_one(query, {"$set": data_to_save}, upsert=True)

        if result.upserted_id:
            self._data["_id"] = result.upserted_id
            print("Inserted new user.")
        else:
            doc = self._db.find_one(query)
            if doc:
                self._data["_id"] = doc["_id"]
            print("Updated existing user.")

    def delete(self) -> None:
        """
        Deletes the model from the database.
        """
        #In the save method it has been made sure that the id is stored in _data
        #If the _id cannot be found in the object _data attribute, then raise error
        if "_id" not in self._data or not self._data["_id"]:
            raise ValueError("Cannot delete: _id not set. Save the object first.")

        #If error was not raised then build a query based on the _id from _data to use in deletion
        query = {"_id": self._data["_id"]}

        try:
            #Try to delete the object based on the previously created query
            result = self._db.delete_one(query)
            
            #If the deletion occurred
            if result.deleted_count > 0:
                print("The document was successfully deleted from the database")
                
                # Clear _id from _data attribute in the Python object. 
                #If the user tries to delete the object again, they will reach the ValueError above, informing them about having to save the object again before being able to delete it.
                self._data["_id"] = None
            
            #If the deletion did not occurr
            else:
                print("Error. No document could be deleted from the database.")
                
        #Catch exceptions upon deletion 
        except Exception as e:
            print(f"\nException occurred while deleting: {e}") 
            
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
        #Filter search
        pymongo_cursor = cls._db.find(filter)
        
        #Return a model cursor
        return ModelCursor(cls, pymongo_cursor)

    @classmethod
    def aggregate(cls, pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor:
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
        return cls.db.aggregate(pipeline)

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
    def init_class(cls, db_collection: pymongo.collection.Collection, indexes: dict[str, str], required_vars: set[str], admissible_vars: set[str]) -> None:
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
        
        # Loop through each type of index in dict of indexes
        # Create indexes in the db based on the received information
        # create_index() both initializes and ensures the index (meaning that if the index does not exist, it creates it but if it is already there, it does nothing)      
        for key in indexes.get("unique_indexes", []):
            cls._db.create_index([(key, 1)], unique=True)

        for key in indexes.get("regular_indexes", []):
            cls._db.create_index([(key, 1)], unique=False)
        
        # Geolocation
        if indexes.get("location_index"):           
            # Store the name of the coordinates field in the class
            cls._location_var = indexes["location_index"] + "_coordinates"

            # Create 2dsphere index on the coordinates field
            cls._db.create_index([(cls._location_var, pymongo.GEOSPHERE)])
         
        else:
            cls._location_var = None
         
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
    
    def __init__(self, model_class: Model, cursor: pymongo.cursor.Cursor):
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
        #Loop through the information recieved as long as the cursor has the potential to return more data
        while self.cursor.alive:
            #This "try" is used in order to check if there is more documents to fetch
            try: 
                doc = next(self.cursor)
                #This "try" is used in trying to create an model object out of the document fetched
                try:
                    #The ** operator converts the dictionary keys into keyword arguments.
                    model_instance = self.model(**doc)
                    
                    #The return value will be a list of values, one for each yield.
                    #The yield keyword is used to return a list of values from a function.
                    yield model_instance
                
                #Error handling upon error with creation of model objects
                except (TypeError, ValueError) as e:
                    print(f"Could not create {self.model.__name__}: {e}")
                    return None
                
            # StopIteration is raised when the cursor has no more documents to fetch.
            except StopIteration:
                break
    
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
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
    db = client[db_name]

    #load the blueprint from models.yml
    with open(definitions_path, 'r') as file:
        models_config = yaml.safe_load(file)
        
    #loop through the blueprint
    for model_name, model_config in models_config.items():
        
        #Model declaration 
        #Dynamically create python classes based on collection_name (from models.yml)
        #(Model,) defines that the class should inherit from the abstract class: Model
        #scope=globals() (see args) the models will be globally accessable
        scope[model_name] = type(model_name, (Model,), {})
        
        scope[model_name].init_class(
            #Create a collection in the db Social_Network
            db_collection = db[model_name],
             
            indexes = {
            'unique_indexes': model_config.get('unique_indexes', []),
            'regular_indexes': model_config.get('regular_indexes', []),
            'location_index': model_config.get('location_index')
            },
            
            #Create sets of vars based on the blueprint in models.yml
            required_vars = set(model_config.get('required_vars', [])),
            admissible_vars = set(model_config.get('admissible_vars', []))
        )
    
if __name__ == '__main__':
    # Initialize database and models with initApp
    initApp()
    
    #Load the example data
    print("Loading the example data into the database...")
    try:
        json_files = {
        "User": "./data/users.json",
        "Company": "./data/companies.json",
        "Educational_center": "./data/Educational_centers.json"
        }
        
        for model_name, file_path in json_files.items():
            model_class = globals().get(model_name)
            if not model_class:
                print(f"Model {model_name} not found in globals()")
                continue

            # Load JSON data
            with open(file_path, "r", encoding="utf-8") as f:
                documents = json.load(f)
            
            # Insert documents
            for document in documents:
                try:
                    instance = model_class(**document)
                    instance.save()
                    
                except Exception as e:
                    print(f"\nCould not save {model_name} document: {document}")
                    print(f"Error: {e}")
                    
    except Exception as e:
        print(f"Error: {e}")
    
    # Inform the user
    print("Running ODM.py main program...")

    # Automaticall running of tests (to verify the model works correctly)
    print("Running tests provided by teacher...")
    pytest.main(["-v", "./"])

    print("Trying out the project...")
    
    # Create model
    try:
        print("Creating a model object...")
        clara = User(
            name="Clara",
            email="clara.karlsson@example.com",
            address="Drottninggatan 10, Stockholm, Sweden")
        
        # Assign new value to allowed variable of the object
        print("Value assigned to OK attribute...")
        clara.age = 29
        
        # Assign new value to disallowed variable of the object
        print("Value assigned to NOT OK attribute...")
        clara.hair_color = "Blonde"
        
        # Save
        print("Trying to save...")
        clara.save()
        
        # Assign new value to allowed variable of the object
        print("Value assigned to OK attribute...")
        clara.age = 28
        
        # Save
        print("Trying to save...")
        clara.save()

        # Search for new document with find
        print("Search for newly saved document...")
        cursor = User.find({"name": clara.name})
        
        # Get first document
        print("Get first document...")
        first_user_found = next(iter(cursor), None)
        
        if first_user_found.address_coordinates:
            print("Found:", first_user_found.name, first_user_found.email, first_user_found.address, first_user_found.address_coordinates['coordinates'])
            
        else:
            print("Found:", first_user_found.name, first_user_found.email, first_user_found.address, first_user_found.address_coordinates)
            
        # Modify value of allowed variable
        print("Changing value of OK attribute...")
        clara.age = 30
        
        # Save
        clara.save()
        
    except Exception as e:
        print(f"\n\nOBS Error: {e}")