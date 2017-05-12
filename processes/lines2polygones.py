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
                  LiteralInput('year', "Year")
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

        os.environ["SHAPE_ENCODING"] = "UTF8"

        year = int(request.inputs['year'][0].data)

        Module('v.in.ogr',
              input=request.inputs["geojson_lines"][0].file,
              output="lines_orign",
              encoding="UTF8"
        )
        Module('v.in.ogr',
              input=request.inputs["geojson_points"][0].file,
              output="points_orign",
              encoding="UTF8"
        )

        condition = "date(UpperDat)>date('%d-01-01') and date(LwDate)<date('%d-01-01')" % (year, year)
        Module('v.extract',
              input="lines_orign",
              flags=["t"],
              output="lines",
              where=condition
        )
        Module('v.extract',
              input="points_orign",
              output="points",
              where=condition
        )

        # TODO generate layer 'polygones'
        # Module('v.out.ogr', input='lines', output='polygones', format='ESRI_Shapefile')
        # v.clean in=test out=test_clean -c tool=snap,break,rmsa,break,rmdupl,rmline,rmdangle threshold=0,0,0,0,1,0,10 --o
        Module('v.clean',
              input="lines",
              output="lines_clean",
              tool=["snap","break","rmsa","break","rmdupl","rmline","rmdangle"],
              threshold=[0,0,0,0,1,0,10],
              overwrite=True,
              flags=["c"],
        )
        # v.type input=test_clean output=test_clean1 from_type=line to_type=boundary --o
        Module('v.type',
              input="lines_clean",
              output="test_clean1",
              from_type="line",
              to_type="boundary",
              overwrite=True,
        )
        
        # v.patch in=point_map,test_clean1 out=test_clean2 --o
        Module('v.patch',
              input=["points","test_clean1"],
              output="test_clean2",
              overwrite=True,
        )
        # v.type test_clean2 out=test_clean3 from=point to=centroid --o
        Module('v.type',
              input="test_clean2",
              output="test_clean3",
              from_type="point",
              to_type="centroid",
              overwrite=True,
        )

        # v.db.connect test_clean3 table=point_map
        Module('v.db.connect',
              map="test_clean3",
              table="points",
        )

        # v.out.ogr test_clean2 out=test_clean2 type=area --o
        Module('v.out.ogr',
              input="test_clean3",
              output="polygones",
              type="area",
              overwrite=True,
        )

        shp_zip = zipfile.ZipFile('polygones.zip', 'w')
        for file in os.listdir('polygones'):
            shp_zip.write(os.path.join('polygones', file), file)
        shp_zip.close()
        response.outputs['polygones'].file = 'polygones.zip'

        return response
