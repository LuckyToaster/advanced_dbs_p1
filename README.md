# Advanced-Databases
Project work for the course Advanced Databases (2509_INSG3_ABDS_A) at u-tad in Madrid, Spain.

### Dependencies
- [pymongo](https://pymongo.readthedocs.io/en/stable/)
- [pyyaml](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [geojson](https://geojson.org/)
- [geopy](https://geopy.readthedocs.io/en/stable/)
- [typing](https://docs.python.org/3/library/typing.html)
- [pytest](https://pypi.org/project/pytest/)

Typing is included in versions of python 3.5 or later

### Installing
Install the python package handler [pip](https://pypi.org/project/pip/)
Install [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install#linux-2) (If you do not already have it installed).

### Executing program
* Open the map "Advanced_Databases_Practice1_Ellen_Gemback" in the terminal of your choice.

* Create and activate a Miniconda virtual environment
```
conda create -n mongo python=3.12
conda activate mongo
```

* Download required pyhton libraries inside of the virtual environment.
```
pip install -r requirements.txt
```

* Run the main file
```
python ODM.py
```

## Authors
- Ellen Gemback
- Senén Marqués
