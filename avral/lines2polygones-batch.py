"""
Usage:
    python lines2poligones.py - for generate polygones for all available periods
    python lines2poligones.py year1 year2 ... yearN - for generate polygones only for periods with year1 OR year2 OR ... OR yearN inside
"""

import sys
import csv
import json
import time
import urllib
import urllib2
import subprocess

webgis = 'histgeo'
lines_id = '609'
points_id = '607'


url_template = "http://213.248.47.89/api/resource/%s/geojson"

lines_json_url = url_template % lines_id
points_json_url = url_template % points_id

print "Download lines START"
#urllib.urlretrieve(lines_json_url, "lines.geojson")
request = urllib2.urlopen(lines_json_url, timeout=500)
with open("lines.geojson", 'wb') as f:
    try:
        f.write(request.read())
    except:
        print("Download lines ERROR")
print "Download lines FINISH"

print "Convert to CSV START"
# ogr2ogr -f CSV -select UpperDat,LwDate lines.csv lines.geojson
subprocess.check_call(["ogr2ogr", "-f", "CSV", "-select", "UpperDat,LwDate", "lines.csv", "lines.geojson"])
print "Convert to CSV FINISH"

years = set()
with open('lines.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    reader.next()
    for row in reader:
        for val in row:
            if int(val[:4]) >= 1462:
                years.add(int(val[:4]))
years = list(years)
years.sort()

periods = [ (years[i], years[i+1]) for i in xrange(len(years) - 1)]
print "Available number of periods: ", len(periods)
print "All periods: ", periods

args = sys.argv[1:]
if len(args) != 0:
    selected_periods = []
    for yl, yu in periods:
        for year in args:
            y = int(year)
            if y <= yu and y >= yl:
                selected_periods.append((yl, yu))
                continue
    print "Use only next periods:"
    print selected_periods
    periods = selected_periods

failed_generations_periods = []

def gen_polygones(year_l, year_u):
    print "Generate polygones for period %04d...%04d START" % (year_l, year_u)

    year = int( (year_u + year_l)/2 )
    url = "http://dev.nextgis.com/wps/simple/lines2polygones/book?" \
           + "lines=%s&" % lines_json_url \
           + "points=%s&" % points_json_url \
           + "year=%s" % year
    print url
    response = urllib2.urlopen(url).read()
    data = json.loads(response)

    if data["type"] != "success":
        print "    WPS server return error: ", data["data"]
        print "Generate polygones FAILED!"
        failed_generations_periods.append((year_l, year_u))
        return

    sys.stdout.write("    wait end of wps process...")
    url = "http://dev.nextgis.com/wps/simple/check_result?uuid=%s" % data["data"]
    response = urllib2.urlopen(url).read()
    data = json.loads(response)
    while data["type"] == "warning":
        time.sleep(1)
        sys.stdout.write('.')
        sys.stdout.flush()
        response = urllib2.urlopen(url).read()
        data = json.loads(response)
    print ""

    if data["type"] == "success":
        urllib.urlretrieve (data["data"], "from_%s_to_%s.zip" % (year_l, year_u) )
        print "Generate polygones SUCCESS"
    else:
        failed_generations_periods.append((year_l, year_u))
        print "Generate polygones FAILED! - ", data["data"]

for l, u in periods:
    gen_polygones( l, u )

if len(failed_generations_periods) > 0:
    print "WARNING! ----------------------"
    print "Polygones for some periods do not generate:"
    print failed_generations_periods
    print "-------------------------------"
else:
    print "SUCCESS!"
