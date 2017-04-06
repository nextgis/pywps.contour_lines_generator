# PyWPS-4 contour lines generator application

This is a app written using PyWPS 4.

## Installation

1. Install pywps 4.x
2. Install Flask
3. Fill all *.templates files and remove .templates extension
4. Create the directories specified in the configuration file: logs, outputs, workdir

## GRASS requirements

1. GRASS PERMANENT mapset which set in app.py must have whole world SRTM raster with name "elevation"  

## Running  
```python app.py```

## Bags
1. Message: **"Maximum number of parallel running processes reached. Please try later."**  
Sometimes it is not **True**!
Pywps stores all requests (and it statuses) in sqlite logs db.
Sometimes need to clean the database.
If request process fail, pywps does not mark request as finished in db.
