#!/usr/bin/env python

from pymongo import MongoClient
from pprint import pprint
import bson
import re

def get_collection():
    client = MongoClient("mongodb://localhost:27017")
    return client.osm.nyb

def find_basic_info():
    '''list basic facts:'''
    c = get_collection()
    print "documents:", c.find().count()
    print "nodes:",c.find({"type":"node"}).count()
    print "ways:",c.find({"type":"way"}).count()
    print "relations:",c.find({"type":"relation"}).count()
    print "unique users:", len(c.distinct("created.user"))
    print "number of cafes:", c.find({"amenity":"cafe"}).count()
    print "number of schools:", len(c.distinct("name",{"amenity":"school"}))
    print "number of shops:", len(c.distinct("name",{"shop":{"$exists":1}}))
    print "number of parks:", c.find({"leisure":"park"}).count()
    print "number of parks (using park tag):", c.find({"park":{"$exists":1}}).count()
    print "number of buildings:", c.find({"building":"yes"}).count()
    print "unique postcodes", c.distinct("addr.postcode",{"addr.postcode":{"$exists":1}})
    print "facbook:", c.find({"contact.facebook":{"$exists":1}}).count()
    print "twitter:", c.find({"contact.twitter":{"$exists":1}}).count()
    print "instagram:", c.find({"contact.instagram":{"$exists":1}}).count()
    print "google_plus:", c.find({"contact.google_plus":{"$exists":1}}).count()
    print "yelp:", c.find({"contact.yelp":{"$exists":1}}).count()

def aggregate(pipeline, allow_disk_use=True):
    '''helper function to perform aggregation'''
    c = get_collection()
    results = c.aggregate(pipeline,allowDiskUse = allow_disk_use)
    for record in results:
        pprint(record)

def find_street_with_most_addresses():
    '''find the biggest street'''
    pipeline = [
        {"$match":{"addr.street":{"$exists":1}}},
        {"$group": {"_id": "$addr.street", "count": {"$sum": 1}}},
        {"$sort":{"count":-1}},
        {"$limit":1}
        ]
    print "Street with most addresses:"
    aggregate(pipeline, True)

def find_street_with_most_parking_lots():
    '''find the street with most parking losts'''
    pipeline = [
        {"$match":{"amenity":"parking"}},
        {"$match":{"addr.street":{"$exists":1}}},
        {"$group": {"_id": "$addr.street", "count": {"$sum": 1}}},
        {"$sort":{"count":-1}},
        {"$limit":1}
    ]
    print "Street with most parking lots:"
    aggregate(pipeline, True)

def find_highest_building():
    '''find the highest building'''
    pipeline = [
        {"$match":{"height":{"$exists":1}}},
        {"$match":{"building.building":"yes"}},
        {"$sort":{"height":-1}},
        {"$limit":1}
        ]
    print "The tallest building:"
    aggregate(pipeline, True)

def find_top_3_sports():
    '''find the top 3 sports facilities'''
    pipeline = [
        {"$match":{"sport":{"$exists":1}}},
        {"$group": {"_id": "$sport", "count": {"$sum": 1}}},
        {"$sort":{"count":-1}},
        {"$limit":3}
    ]
    print "Top 3 sports:"
    aggregate(pipeline, True)

def update_postcode():
    '''clean up postcode field'''
    c = get_collection()
    for item in c.find({"addr.postcode":{"$exists":1}}):
        code = re.findall("[0-9]{5}-{1}[0-9]{4}|[0-9]{5}",item["addr"]["postcode"])
        if code == []:
            code = None
        item["addr"]["postcode"] = code
        c.save(item)

if __name__ == "__main__":
    find_basic_info()
    find_street_with_most_addresses()
    find_street_with_most_parking_lots()
    find_highest_building()
    find_top_3_sports()
