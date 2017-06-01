import os

import flask

import pywps
from pywps.app import Service

from avral.contour_lines_generation import ContourLinesGenerator
from avral.lines2polygones import Lines2Polygones
from avral.value_from_raster import ValueFromRaster

import configuration

processes = [
    Lines2Polygones(),
    ValueFromRaster(configuration.grass_db_location),
    ContourLinesGenerator(configuration.grass_db_location),
]

service = Service(processes, ['pywps.cfg'])

application = flask.Flask("avral")


@application.route('/wps/', methods=['GET', 'POST'])
def wps():
    return service


@application.route('/wps/outputs/'+'<filename>')
def outputfile(filename):
    targetfile = os.path.join('outputs', filename)
    if os.path.isfile(targetfile):
        file_ext = os.path.splitext(targetfile)[1]
        with open(targetfile, mode='rb') as f:
            file_bytes = f.read()
        mime_type = None
        if 'xml' in file_ext:
            mime_type = 'text/xml'
        elif 'zip' in file_ext:
            mime_type = 'application/zip'
        return flask.Response(file_bytes, content_type=mime_type)
    else:
        flask.abort(404)
