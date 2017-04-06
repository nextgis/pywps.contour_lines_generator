# Copyright (c) 2016 PyWPS Project Steering Committee
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Alexander Lisovenko'

import os
import zipfile
import logging
import time

from pywps import Process, LiteralInput, BoundingBoxInput, LiteralOutput, ComplexInput, ComplexOutput, Format, FORMATS, UOM
from pywps.validator.complexvalidator import validategml

from pywps.validator.mode import MODE

import pywps.configuration as config


class Lines2Polygones(Process):
    def __init__(self):
        inputs = [
                  ComplexInput('geojson_lines', 'GEOJSON Lines', supported_formats=[Format(FORMATS.GEOJSON.mime_type)]),
                  ComplexInput('geojson_points', 'GEOJSON Points', supported_formats=[Format(FORMATS.GEOJSON.mime_type)]),
                 ]
        outputs = [
                  ComplexOutput('polygones', 'Polygones', supported_formats=[Format(FORMATS.SHP.mime_type)])
                  ]

        super(Lines2Polygones, self).__init__(
            self._handler,
            identifier='lines2polygones',
            version='0.1',
            title="Lines To Polygones",
            abstract='Generate Polygon shape from Lines geojson and Points geojson',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            grass_location="epsg:3857"
        )

    def _handler(self, request, response):
        from grass.pygrass.modules import Module
        
        # print request.inputs["geojson_lines"]
        # print type(request.inputs["geojson_lines"])
        # print dir(request.inputs["geojson_lines"][0])
        # print request.inputs["geojson_lines"][0].file

        Module('v.in.ogr',
              input=request.inputs["geojson_lines"][0].file,
              output="lines"
        )
        Module('v.in.ogr',
              input=request.inputs["geojson_points"][0].file,
              output="points"
        )

        # TODO generate layer 'polygones'
        Module('v.out.ogr', input='lines', output='polygones', format='ESRI_Shapefile')

        shp_zip = zipfile.ZipFile('polygones.zip', 'w')
        for file in os.listdir('polygones'):
            shp_zip.write(os.path.join('polygones', file), file)
        shp_zip.close()
        response.outputs['polygones'].file = 'polygones.zip'

        return response
