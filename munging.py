#!/usr/bin/env python

from bson import json_util
import xml.etree.ElementTree as ET
import re
from collections import defaultdict
from pprint import pprint
import json
import datetime

def parse(osm_file):
    '''Parse the osm document and dump the data as json format.'''
    context = ET.iterparse(osm_file)
    with open('data_ny.json', 'w') as fp:
        for event, elem in context:
            node = shape_element(elem)
            if node is not None:
                json.dump(node, fp, default=json_util.default)


def update_street_name(name):
    '''Update street name to standardize street types. '''
    mapping = {
            "\s+St.$": " Street",
            "\s+Rd.$":" Road",
            "\s+Ave.$":" Avenue",
            "\s+BLVD$":" Boulevard",
            "\s+St$": " Street",
            "\s+Rd$":" Road",
            "\s+Ave$":" Avenue",
            }
    for key, item in mapping.items():
        if re.search(key, name, re.IGNORECASE)!=None:
            insensitive = re.compile(key, re.IGNORECASE)
            return insensitive.sub(item, name)

    return name

def shape_element(element):
    '''Shape each element of way, node, or relation and return a dict.'''
    PROBLEM_CHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

    node = {}
    if element.tag == "way" or element.tag == "node" or element.tag=="relation":
        node["id"] = element.attrib["id"];

        #visible
        if element.get("visible"):
            node["visible"] = element.get("visible");

        node["id"] = element.attrib["id"];
        node["type"]  = element.tag

        #position
        #Convert lat and lon to floating numbers
        lat = element.get("lat", None)
        lon = element.get("lon", None)
        if lat is not None and lon is not None:
            node["pos"] = [float(lat),float(lon)]

        #created
        #convert timestamp to datetime object
        node["created"] = {
                "version":element.attrib["version"],
                "changeset":element.attrib["changeset"],
                "timestamp":datetime.datetime.strptime(element.attrib["timestamp"],
                                                       "%Y-%m-%dT%H:%M:%SZ"),
                "user":element.attrib["user"],
                "uid":element.attrib["uid"]
            }

        tags = defaultdict(dict)
        for tag in element.iter('tag'):
            key = tag.attrib["k"]
            value = tag.attrib["v"]
            m = PROBLEM_CHARS.search(key)
            if m is None: # No problem
                if key.find(":")!=-1:
                    #deal with multi-level keys
                    key_items = key.split(":")

                    if key_items[1]=="street" or key_items[1]=="street_2":
                        value = update_street_name(value)

                    temp = tags
                    for key_item in key_items[0:-1]:
                        item = temp.get(key_item,None)
                        if item==None: #does not exists; create a new dictionary
                            temp[key_item] = defaultdict(dict)
                        elif type(item)!=type(defaultdict(dict)): #exists but wrong data type
                            item_value = temp[key_item]
                            temp[key_item] = defaultdict(dict)
                            temp[key_item][key_item] = item_value
                        #go to the next level
                        temp = temp[key_item]
                    #set the value of the lowest key item.
                    temp[key_items[-1]] = value
                else:
                    #convert height to floating numbers.
                    if key == "height":
                        tags[key] = extract_number(value)
                    else:
                        tags[key] = value

        #merge node dict.
        node.update(tags)

        #reference nodes
        refs = []
        for tag in element.iter('nd'):
            refs.append(tag.attrib["ref"])
        if len(refs)>0:
            node["node_refs"] = refs

        #members for relations
        members = []
        for tag in element.iter('member'):
            members.append(
                            {"member":
                             {"type":tag.attrib["type"],
                              "ref":tag.attrib["ref"],
                              "role":tag.attrib["role"]}
                            }
                          )

        if len(members)>0:
            node["members"] = members

        return node
    else:
        return None

def extract_number(s):
    '''Extract a floating point number for a string.'''
    num = re.compile("[0-9]*\.?[0-9]*")
    m = num.search(s)
    return float(m.group())

if __name__ == "__main__":
    OSM_FILE = "brooklyn_new-york.osm"
    parse(OSM_FILE)
