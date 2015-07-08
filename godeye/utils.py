#! /usr/bin/python
# -*- coding: utf-8 -*-
import json
from model import PoiModel
import math

EARTH_RADIUS =  6378.137
PI = 3.1415926535

def rad(d):
    return d * PI / 180.0

def round(d):
    return int(d + 0.5)

def get_distance(lat1, lng1, lat2, lng2):
    """get the distance from 2 posisions set by lats and longs"""
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.sin(a/2)**2 + math.cos(radLat1) * math.cos(radLat2) * math.sin(b/2) **2))
    s = s * EARTH_RADIUS
    return s


def parse_poi_data(data):
    json_data = json.loads(data)
    poi_list = json_data['results']
    next_page_token = json_data.get('next_page_token', None)
    return poi_list, next_page_token

    
def filter_poi_infos(raw_list):
    """parse the raw return data"""
    poi_list = []
    for index, poi_item in enumerate(raw_list):
        location = poi_item['geometry'].get('location', None)
        viewport = poi_item['geometry'].get('viewport', None)
        id = poi_item.get('id', '')
        name = poi_item.get('name', '')
        typ = poi_item.get('types', '')
        near = poi_item.get('vicinity', '')
        reference = poi_item.get('reference', None)
        p = PoiModel(id, name, typ, near, location, viewport, reference)
        poi_list.append(p)
    return poi_list

def calculate_position(poi_list, lat, lng):
    """set the angle between the POIs and user"""
    for p in poi_list:
        a = get_distance(lat, lng, lat, p.get_location()['lng'])
        b = get_distance(lat, lng, p.get_location()['lat'], lng)
        p.set_distance(math.sqrt(a ** 2 + b ** 2))
        angle = math.atan(a/b) / PI * 180
        if lat < p.get_location()['lat']:
            angle += 90
        if lng <  p.get_location()['lng']:
            angle += 180
        p.set_angle(angle)

def generate_result(poi_list):
    """generate the output for the request"""
    p_return = {}
    p_dict_list = []
    for p in poi_list:
        p_dict = {}
        p_dict['id'] = p.get_id()
        p_dict['name'] = p.get_name()
        p_dict['location'] = p.get_location()
        p_dict['angle'] = p.get_angle()
        p_dict['type'] = p.get_type()
        p_dict['distance'] = p.get_distance()
        p_dict['reference'] = p.get_reference()
        p_dict_list.append(p_dict)
    p_dict_list.sort(key=lambda x:x.get('distance'))
    p_return['results'] = p_dict_list

    return p_return