import os
import flask
from flask import request
from pywps import Service

import configuration

from processes.contour_lines_generation import ContourLinesGenerator
from processes.lines2polygones import Lines2Polygones
from processes.value_from_raster import ValueFromRaster
processes = [
    Lines2Polygones(),
    ValueFromRaster(configuration.grass_db_location),
    ContourLinesGenerator(configuration.grass_db_location),
]
service = Service(processes, ['pywps.cfg'])

app = flask.Flask(__name__)

@app.route('/wps/', methods=['GET', 'POST'])
def wps():
    return service

@app.route('/wps/outputs/'+'<filename>')
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

@app.route('/static/'+'<filename>')
def staticfile(filename):
    targetfile = os.path.join('static', filename)
    if os.path.isfile(targetfile):
        file_ext = os.path.splitext(targetfile)[1]
        with open(targetfile, mode='rb') as f:
            file_bytes = f.read()
        mime_type = None
        return flask.Response(file_bytes, content_type=mime_type)
    else:
        flask.abort(404)


def make_wps_request(xml):
    import requests
    import xml.etree.ElementTree as ET

    headers = {'Content-Type': 'application/xml'}
    resp = requests.post('http://0.0.0.0:5001/wps/', data=xml, headers=headers)

    if resp.status_code == requests.codes.ok:
# <!-- PyWPS 4.0.0 -->
# <wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US" serviceInstance="http://176.9.38.120/wps/?service=WPS&amp;request=GetCapabilities" statusLocation="http://176.9.38.120/wps/outputs/c0325248-e4a0-11e6-aaa3-00163e5cdd44.xml">
#   <wps:Process wps:processVersion="0.1">
#     <ows:Identifier>contour_lines_generator</ows:Identifier>
#     <ows:Title>Contour lines generator</ows:Title>
#     <ows:Abstract>Generate contour lines shp from server SRTM data for given bbox and interval</ows:Abstract>
#   </wps:Process>
#   <wps:Status creationTime="2017-01-27T17:56:15Z">
#     <wps:ProcessAccepted>PyWPS Process contour_lines_generator accepted</wps:ProcessAccepted>
#   </wps:Status>
# </wps:ExecuteResponse>
        try:
            root = ET.fromstring(resp.text)
            statusLocation = root.attrib.get("statusLocation")
            # return statusLocation.split('/')[-1].split('.')[0]
            # return statusLocation
            response = app.response_class(
                response='{"type":"success", "data":"%s"}' % statusLocation.split('/')[-1].split('.')[0],
                mimetype="application/json"
            )
            return response
        except Exception as e:
            response = app.response_class(
                response='{"type":"error", "data":"%s"}' % unicode(e),
                mimetype="application/json"
            )
            return response

    elif resp.status_code == 400:
# <?xml version="1.0" encoding="UTF-8"?>
# <ows:ExceptionReport xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/ows/1.1 ../../../ows/1.1.0/owsExceptionReport.xsd" version="1.0.0">
#     <ows:Exception exceptionCode="ServerBusy">
#         <ows:ExceptionText>Maximum number of parallel running processes reached. Please try later.</ows:ExceptionText>
#     </ows:Exception>
# </ows:ExceptionReport>
        ns = {
            "ows":"http://www.opengis.net/ows/1.1"
        }
        root = ET.fromstring(resp.text)
        exception_text_element = root.find("ows:Exception/ows:ExceptionText", ns)

        response = app.response_class(
            response='{"type":"error", "data":"%s"}' % exception_text_element.text,
            mimetype="application/json"
        )
        return response

    else:
        response = app.response_class(
            response='{"type":"error", "data":"Internal server error"}',
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

@app.route("/wps/simple/contour_lines/check") # delete only after fix http://176.9.38.120/wps/isoline GUI
@app.route("/wps/simple/check_result")
def contour_lines_check():
    import requests
    import xml.etree.ElementTree as ET

    uuid = request.args.get("uuid", "")

    resp = requests.get('http://0.0.0.0:5001/wps/outputs/%s.xml' % uuid)

    ns = {
        "wps":"http://www.opengis.net/wps/1.0.0",
        "xlink": "http://www.w3.org/1999/xlink",
        "ows": "http://www.opengis.net/ows/1.1",
    }
    if resp.status_code == requests.codes.ok:
        try:
            t = resp.text
            root = ET.fromstring(t)

            process_accepted_tag = root.find("wps:Status/wps:ProcessAccepted", ns)
            if process_accepted_tag is not None:
# <wps:ExecuteResponse xmlns:wps="http://www.opengis.net/wps/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" xsi:schemaLocation="http://www.opengis.net/wps/1.0.0 http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd" service="WPS" version="1.0.0" xml:lang="en-US" serviceInstance="http://176.9.38.120/wps/?service=WPS&amp;request=GetCapabilities" statusLocation="http://176.9.38.120/wps/outputs/a34ed56a-e4a1-11e6-b711-00163e5cdd44.xml">
#   <wps:Process wps:processVersion="0.1">
#     <ows:Identifier>contour_lines_generator</ows:Identifier>
#     <ows:Title>Contour lines generator</ows:Title>
#     <ows:Abstract>Generate contour lines shp from server SRTM data for given bbox and interval</ows:Abstract>
#   </wps:Process>
#   <wps:Status creationTime="2017-01-27T18:02:36Z">
#     <wps:ProcessAccepted>PyWPS Process contour_lines_generator accepted</wps:ProcessAccepted>
#   </wps:Status>
# </wps:ExecuteResponse>
                response = app.response_class(
                    response='{"type":"warning", "data":"Task in process"}',
                    mimetype="application/json"
                )
                return response

            process_succeeded_tag = root.find("wps:Status/wps:ProcessSucceeded", ns)
            if process_succeeded_tag is not None:
#   <wps:ProcessOutputs>
#     <wps:Output>
#       <ows:Identifier>contour_lines</ows:Identifier>
#       <ows:Title>Contour Lines</ows:Title>
#       <wps:Reference xlink:href="http://176.9.38.120/wps/outputs/contour_linesRuN7Qo.zip" mimeType="application/x-zipped-shp"/>
#     </wps:Output>
#   </wps:ProcessOutputs>
                output_ref = root.find("wps:ProcessOutputs/wps:Output/wps:Reference", ns)
                if output_ref is not None:
                    rez_ref = output_ref.attrib.get("{%s}href" % ns.get("xlink"))
                    response = app.response_class(
                        response='{"type":"success", "data":"%s"}' % rez_ref,
                        mimetype="application/json"
                    )
                    return response

# <wps:ProcessOutputs>
#     <wps:Output>
#         <ows:Identifier>value</ows:Identifier>
#         <ows:Title>Raster value</ows:Title>
#         <wps:Data>
#             <wps:LiteralData dataType="urn:ogc:def:dataType:OGC:1.1:float">90.0</wps:LiteralData>
#         </wps:Data>
#     </wps:Output>
# </wps:ProcessOutputs>                
                output_ref = root.find("wps:ProcessOutputs/wps:Output/wps:Data/wps:LiteralData", ns)
                if output_ref is not None:
                    response = app.response_class(
                        response='{"type":"success", "data":"%s"}' % output_ref.text,
                        mimetype="application/json"
                    )
                    return response

            process_failed_tag = root.find("wps:Status/wps:ProcessFailed", ns)
            if process_failed_tag is not None:
# <wps:Status creationTime="2017-04-07T10:48:35Z">
#     <wps:ProcessFailed>
#         <wps:ExceptionReport>
#             <ows:Exception exceptionCode="NoApplicableCode" locater="None">
#                 <ows:ExceptionText>Process error: value_from_raster.py._handler Line 86 No value!</ows:ExceptionText>
#             </ows:Exception>
#         </wps:ExceptionReport>
#     </wps:ProcessFailed>
# </wps:Status>
                err_msg = root.find("wps:Status/wps:ProcessFailed/wps:ExceptionReport/ows:Exception/ows:ExceptionText", ns)
                if err_msg is None:
                    err_msg = "Unknown error"
                else:
                    err_msg = err_msg.text

                response = app.response_class(
                    response='{"type":"error", "data":"%s"}' % err_msg,
                    mimetype="application/json"
                )
                return response

        except Exception as e:
            response = app.response_class(
                response='{"type":"error", "data":"%s"}' % unicode(e),
                mimetype="application/json"
            )
            return response

        response = app.response_class(
            response='{"type":"error", "data":"Unknown task id"}',
            mimetype="application/json"
        )
        return response

    elif resp.status_code == 400:
        ns = {
            "ows":"http://www.opengis.net/ows/1.1"
        }
        root = ET.fromstring(resp.text)
        exception_text_element = root.find("ows:Exception/ows:ExceptionText", ns)

        response = app.response_class(
            response='{"type":"error", "data":"%s"}' % exception_text_element,
            mimetype="application/json"
        )
        return response

    elif resp.status_code == 404:
        response = app.response_class(
            response='{"type":"error", "data":"Unknown task id"}',
            mimetype="application/json"
        )
        return response

    else:
        response = app.response_class(
            response='{"type":"error", "data":"Internal server error"}',
            mimetype="application/json"
        )
        return response


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

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=5001, threaded=True)
