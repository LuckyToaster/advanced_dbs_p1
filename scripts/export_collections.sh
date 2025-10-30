#!/bin/bash

mongoexport --db abd --collection Person --out data/Person.json --jsonArray
mongoexport --db abd --collection Company --out data/Company.json --jsonArray
mongoexport --db abd --collection EducationalCentre --out data/EducationalCentre.json --jsonArray

