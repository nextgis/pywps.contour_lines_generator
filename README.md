# PyWPS-4 contour lines generator application

This is a app written using PyWPS 4.

## Installation

1. Install pywps 4.x  
2. Fill all *.templates files and remove .templates extension  

## GRASS requirements

1. GRASS PERMANENT mapset which set in py_wps_app.py must have whole world SRTM raster with name "elevation"  

## Running  

1. With uwsgi:  
```uwsgi --ini uwsgi.cfg```
