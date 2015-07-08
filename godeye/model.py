#! /usr/bin/python
# -*- coding: utf-8 -*-

class PoiModel(object):
    def __init__(self, id, name, typ, near, location, viewport, reference):
        self._id = id
        self._name = name
        self._type = typ
        self._near = near
        self._location = location
        self._viewport = viewport
        self._angle = -1
        self._dis = 0
        self._reference = reference

    def get_reference(self):
        return self._reference

    def get_location(self):
        return self._location

    def get_name(self):
        return self._name

    def get_viewport(self):
        return self._viewport

    def get_id(self):
        return self._id

    def set_angle(self, angle):
        self._angle = angle

    def get_angle(self):
        return self._angle

    def get_type(self):
        return self._type

    def set_distance(self, distance):
        self._dis = distance

    def get_distance(self):
        return self._dis