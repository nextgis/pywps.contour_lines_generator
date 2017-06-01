import os
import ConfigParser

from owslib.wps import WebProcessingService, WPSExecution, monitorExecution
from owslib.wps import WPSReader, Process
from owslib.util import ServiceException

import flask
from flask import request

app = flask.Flask("avral_simple")

pywps_configs = ['pywps.cfg']

config = ConfigParser.ConfigParser()
config.read(pywps_configs)

pywps_url = config.get('server', 'url')
pywps_outputurl = config.get('server', 'outputurl')


def get_wps():
    print ">>> pywps_url: ", pywps_url
    return WebProcessingService(pywps_url, verbose=True, skip_caps=True)


def make_wps_request(xml):
    import xml.etree.ElementTree as ET

    try:
        execution = get_wps().execute(None, [], request=str(xml))
    except ServiceException as e:
        ns = {
            "ows":"http://www.opengis.net/ows/1.1"
        }
        root = ET.fromstring(str(e))
        exception_text_element = root.find("ows:Exception/ows:ExceptionText", ns)

        response = app.response_class(
            response='{"type":"error", "data":"%s"}' % str(exception_text_element.text),
            mimetype="application/json"
        )
        return response
    except Exception as e:
        response = app.response_class(
            response='{"type":"error", "data":"Unknown exeption: %s"}' % str(e),
            mimetype="application/json"
        )
        return response
    # monitorExecution(execution)

    # print execution
    # print dir(execution)

    # print "isSucceded: ", execution.isSucceded()
    # print "isComplete: ", execution.isComplete()
    # print "getStatus: ", execution.getStatus()
    # print "statusLocation: ", execution.statusLocation

    if execution.statusLocation is not None:
        response = app.response_class(
            response='{"type":"success", "data":"%s"}' % execution.statusLocation.split('/')[-1].split('.')[0],
            mimetype="application/json"
        )
        return response
    else:
        response = app.response_class(
            response='{"type":"error", "data":"%s"}' % execution.getStatus(),
            mimetype="application/json"
        )
        return response


@app.route("/wps/simple/contour_lines/book")
def contour_lines_book():
    minx = request.args.get("minx", "")
    maxx = request.args.get("maxx", "")
    miny = request.args.get("miny", "")
    maxy = request.args.get("maxy", "")
    interval = request.args.get("interval", "")
    xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
    <ows:Identifier>contour_lines_generator</ows:Identifier>
    <wps:DataInputs>
        <wps:Input>
            <ows:Identifier>bboxin</ows:Identifier>
            <ows:Title>Box in</ows:Title>
            <wps:Data>
<wps:BoundingBoxData>
                <ows:LowerCorner>%s %s</ows:LowerCorner>
                <ows:UpperCorner>%s %s</ows:UpperCorner>
</wps:BoundingBoxData>
            </wps:Data>
        </wps:Input>
        <wps:Input>
            <ows:Identifier>interval</ows:Identifier>
            <ows:Title>Interval</ows:Title>
            <wps:Data>
                <wps:LiteralData>%s</wps:LiteralData>
            </wps:Data>
        </wps:Input>
    </wps:DataInputs>
    <wps:ResponseForm>
       <wps:ResponseDocument status="true" storeExecuteResponse="true">
         <wps:Output asReference="true">
           <ows:Identifier>contour_lines</ows:Identifier>
         </wps:Output>
       </wps:ResponseDocument>
    </wps:ResponseForm>
</wps:Execute>
""" % (minx, miny, maxx, maxy, interval)

    return make_wps_request(xml)


@app.route("/wps/simple/lines2polygones/book")
def lines2polygones_book():
    lines_geojson = request.args.get("lines", "")
    points_geojson = request.args.get("points", "")
    year = request.args.get("year", "")

    xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
    <ows:Identifier>lines2polygones</ows:Identifier>
    <wps:DataInputs>
        <wps:Input>
            <ows:Identifier>geojson_lines</ows:Identifier>
            <ows:Title>GEOJSON Lines</ows:Title>
            <wps:Reference xlink:href="%s"/>
        </wps:Input>
        <wps:Input>
            <ows:Identifier>geojson_points</ows:Identifier>
            <ows:Title>GEOJSON Points</ows:Title>
            <wps:Reference xlink:href="%s"/>
        </wps:Input>
        <wps:Input>
            <ows:Identifier>year</ows:Identifier>
            <ows:Title>Year</ows:Title>
            <wps:Data>
                <wps:LiteralData>%s</wps:LiteralData>
            </wps:Data>
        </wps:Input>
    </wps:DataInputs>
    <wps:ResponseForm>
       <wps:ResponseDocument status="true" storeExecuteResponse="true">
         <wps:Output asReference="true">
           <ows:Identifier>polygones</ows:Identifier>
         </wps:Output>
       </wps:ResponseDocument>
    </wps:ResponseForm>
</wps:Execute>
""" % (lines_geojson, points_geojson, year)

    return make_wps_request(xml)


@app.route("/wps/simple/value_from_raster/book")
def value_from_raster_book():
    x = request.args.get("x", "")
    y = request.args.get("y", "")

    xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 ../wpsExecute_request.xsd">
    <ows:Identifier>value_from_raster</ows:Identifier>
    <wps:DataInputs>
        <wps:Input>
            <ows:Identifier>x</ows:Identifier>
            <ows:Title>X</ows:Title>
            <wps:Data>
                <wps:LiteralData>%s</wps:LiteralData>
            </wps:Data>
        </wps:Input>
        <wps:Input>
            <ows:Identifier>y</ows:Identifier>
            <ows:Title>Y</ows:Title>
            <wps:Data>
                <wps:LiteralData>%s</wps:LiteralData>
            </wps:Data>
        </wps:Input>
    </wps:DataInputs>
    <wps:ResponseForm>
       <wps:ResponseDocument status="true" storeExecuteResponse="true">
         <wps:Output asReference="true">
           <ows:Identifier>value</ows:Identifier>
         </wps:Output>
       </wps:ResponseDocument>
    </wps:ResponseForm>
</wps:Execute>
""" % (x, y)

    return make_wps_request(xml)


@app.route("/wps/simple/contour_lines/check") # delete only after fix http://176.9.38.120/wps/isoline GUI
@app.route("/wps/simple/check_result")
def check_result():
    uuid = request.args.get("uuid", "")

    execution = WPSExecution()

    try:
        execution.checkStatus("%s%s.xml" % (pywps_outputurl, uuid), sleepSecs=0)
    except:
        response = app.response_class(
            response='{"type":"error", "data":"Unknown task id"}',
            mimetype="application/json"
        )
        return response

    if execution.isNotComplete():
        response = app.response_class(
            response='{"type":"warning", "data":"Task in process"}',
            mimetype="application/json"
        )
        return response

    if execution.isSucceded():        
        for output in execution.processOutputs:
            if output.reference is not None:
                response = app.response_class(
                    response='{"type":"success", "data":"%s"}' % output.reference,
                    mimetype="application/json"
                )
                return response

            else:
                response = app.response_class(
                    response='{"type":"success", "data":"%s"}' % output.data,
                    mimetype="application/json"
                )
                return response

        response = app.response_class(
            response='{"type":"error", "data":"%s"}' % "Cannot proccess pywps output",
            mimetype="application/json"
        )

        return response

    else:
        errors = [wpsexception.text for wpsexception in execution.errors]
            
        response = app.response_class(
            response='{"type":"error", "data":"%s"}' % errors,
            mimetype="application/json"
        )

        return response


@app.route("/wps/simple/ping")
def ping():
    response = app.response_class(
        response='{"type":"suceess", "data":"Pong"}',
        mimetype="application/json"
    )

    return response

application = app
