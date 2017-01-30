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
