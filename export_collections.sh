#!/bin/bash

mongoexport --db abd --collection Person --out data/person.json --jsonArray
mongoexport --db abd --collection Company --out data/company.json --jsonArray
mongoexport --db abd --collection EducationalCentre --out data/person.json --jsonArray
