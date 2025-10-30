#!/bin/bash

mongoimport --db abd --collection Person --file data/Person.json --jsonArray
mongoimport --db abd --collection Company --file data/Company.json --jsonArray
mongoimport --db abd --collection EducationalCentre --file data/EducationalCentre.json --jsonArray
