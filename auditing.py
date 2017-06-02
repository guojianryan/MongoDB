#!/usr/bin/env python

import re
import xml.etree.ElementTree as ET

'''
These three methods are extracted from the quiz.
'''
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def audit_street_type(street_types, street_name):
    expected = ["Street", "Avenue", "Boulevard", "Drive", "Court",
    "Place", "Square", "Lane", "Road", "Trail", "Parkway",
    "Commons", "Way", "Alley"]
    street_type_re = re.compile(r'\b\S+?$', re.IGNORECASE)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types.add(street_name)

if __name__ == "__main__":
    OSM_FILE = "brooklyn_new-york.osm"
    print audit(OSM_FILE)
