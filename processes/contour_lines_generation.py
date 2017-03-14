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

from pywps import Process, LiteralInput, BoundingBoxInput, LiteralOutput, ComplexInput, ComplexOutput, Format, FORMATS, UOM
from pywps.validator.complexvalidator import validategml

from pywps.validator.mode import MODE

import pywps.configuration as config


class ContourLinesGenerator(Process):
    def __init__(self, grass_location):
        inputs = [
                  BoundingBoxInput('bboxin', 'Box in', ['epsg:4326']),
                  LiteralInput('interval', 'Interval', data_type='positiveInteger')
                 ]
        outputs = [
                 ComplexOutput('contour_lines', 'Contour Lines',
                 supported_formats=[Format(FORMATS.SHP.mime_type)])
                  ]

        super(ContourLinesGenerator, self).__init__(
            self._handler,
            identifier='contour_lines_generator',
            version='0.1',
            title="Contour lines generator",
            abstract='Generate contour lines shp from server SRTM data for given bbox and interval',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            grass_location=grass_location
        )

    def _handler(self, request, response):
        from grass.pygrass.modules import Module
        
        Module('g.region',
              n=request.inputs['bboxin'][0].data[3],
              s=request.inputs['bboxin'][0].data[1],
              e=request.inputs['bboxin'][0].data[2],
              w=request.inputs['bboxin'][0].data[0]
        )
        Module('r.contour',
              input='elevation',
              output='contour_lines',
              step=request.inputs['interval'][0].data
        )
        Module('v.out.ogr', input='contour_lines', output='contour_lines', format='ESRI_Shapefile', type='line')

        shp_zip = zipfile.ZipFile('contour_lines.zip', 'w')
        for file in os.listdir('contour_lines'):
            shp_zip.write(os.path.join('contour_lines', file), file)
        shp_zip.close()
        response.outputs['contour_lines'].file = 'contour_lines.zip'

        return response
