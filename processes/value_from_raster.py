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
from pywps.app.WPSResponse import STATUS
from pywps.exceptions import NoApplicableCode

import pywps.configuration as config

LOGGER = logging.getLogger("PYWPS")

class ValueFromRaster(Process):
    def __init__(self, grass_location):
        inputs = [
                  LiteralInput('x', 'X coordinate', data_type='float'),
                  LiteralInput('y', 'Y coordinate', data_type='float'),
                 ]
        outputs = [
                 LiteralOutput('value', 'Raster value', data_type='float'),
                  ]

        super(ValueFromRaster, self).__init__(
            self._handler,
            identifier='value_from_raster',
            version='0.1',
            title="Value From Raster",
            abstract='Get raster value by X Y coordiantes',
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True,
            grass_location=grass_location
        )

    def _handler(self, request, response):
        from grass.pygrass.modules import Module
        
        x = request.inputs['x'][0].data
        y = request.inputs['y'][0].data

        #r.what map=name coordinates=east,north
        m =  Module('r.what',
              map="elevation",
              coordinates=[x, y],
              output="result.txt",
              flags="n"
        )

        identify_result = {}
        with open("result.txt", 'r') as f:
          headers = f.readline().strip().split('|')
          LOGGER.warning("[ValueFromRaster] headers: " + str(headers))
          values = f.readline().strip().split('|')
          LOGGER.warning("[ValueFromRaster] values: " + str(values))

        if len(values) == len(headers):
          for i in range(len(headers)):
            identify_result[headers[i]] = values[i]
          
          value = identify_result.get("elevation",None)
          if value is not None:
            response.outputs['value'].data = value

        return response
