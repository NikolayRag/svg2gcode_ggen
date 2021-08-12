#!/usr/bin/env python

import sys
from . import shapes as shapes_pkg
from .shapes import point_generator



class GGen():
    svg_shapes = ('rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path')


    rootET = None
    smoothness = 1
    feedRate = 0
    maxX = 0
    maxY = 0

    preamble = ''
    shapePreamble = None
    shapePostamble = None
    postamble = ''


    scale = 1.



    def __init__(self, _rootET):
        self.rootET = _rootET



    def generate(self,
        smoothness = 0.02,
        feedRate = 10000,
        maxX = 200,
        maxY = 300,

        preamble = 'G90',
        shapePreamble = None,
        shapePostamble = None,
        postamble = ''
    ):
        self.smoothness = smoothness
        self.feedRate = feedRate
        self.maxX = maxX
        self.maxY = maxY

        self.preamble = preamble
        self.shapePreamble = shapePreamble
        self.shapePostamble = shapePostamble
        self.postamble = postamble


        width = self.rootET.get('width')
        height = self.rootET.get('height')
        if width == None or height == None:
            viewbox = self.rootET.get('viewBox')
            if viewbox:
                _, _, width, height = viewbox.split()                

        if width != None and height != None:
            width = float(width)
            height = float(height)

            scale_x = self.maxX / max(width, height)
            scale_y = self.maxY / max(width, height)
            self.scale = min(scale_x, scale_y)

        else:
            print("Unable to get width and height for the svg")


        return (
            [f'F{self.feedRate}']
            + self.gCode()
            + [self.gcMove(0,0)]
        )




    def gCode(self):
        outGCode = []

        outGCode.append(self.preamble)

        for elem in self.rootET.iter():
            try:
                _, tag_suffix = elem.tag.split('}')
            except ValueError:
                print('Skip tag:', elem.tag)
                continue

            if tag_suffix in self.svg_shapes:
                shape_class = getattr(shapes_pkg, tag_suffix)

                outGCode += self.gShape( shape_class(elem) )


        outGCode.append(self.postamble)

        return outGCode



    def gShape(self, _shape):
        outGShape = []


        d = _shape.d_path()
        m = _shape.transformation_matrix()

        if not d:
            return outGShape


        cInject = self.shapePreamble
        if cInject:
            if callable(cInject):
                cInject = cInject(_shape.__str__())

            outGShape.append(cInject if isinstance(cInject, str) else '')


        p = point_generator(d, m, self.smoothness)
        for x,y in p:
            if x > 0 and x < self.maxX and y > 0 and y < self.maxY:  
                outGShape.append( self.gcMove(self.scale*x, self.scale*y) )


        cInject = self.shapePostamble
        if cInject:
            if callable(cInject):
                cInject = cInject(_shape.__str__())

            outGShape.append(cInject if isinstance(cInject, str) else '')


        return outGShape



    def gcMove(self, _x, _y, _pre="G1"):
            return f"{_pre} X{_x} Y{_y}"
