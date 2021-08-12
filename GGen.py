#!/usr/bin/env python

import sys
from . import shapes as shapes_pkg
from .shapes import point_generator



class GGen():
    svg_shapes = set(['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path']),


    rootET = None
    smoothness = 1
    feedRate = 0
    maxX = 0
    maxY = 0

    preamble = ''
    shapePreamble = ''
    shapePostamble = ''
    postamble = ''


    scale = 1.



    def __init__(self,
        _rootET,
        _smoothness = 0.02,
        _feedRate = 10000,
        _maxX = 200,
        _maxY = 300,

        _preamble = 'G90',
        _shapePreamble = '',
        _shapePostamble = '',
        _postamble = ''
    ):
        self.rootET = _rootET
        self.smoothness = _smoothness
        self.feedRate = _feedRate
        self.maxX = _maxX
        self.maxY = _maxY

        self.preamble = _preamble
        self.shapePreamble = _shapePreamble
        self.shapePostamble = _shapePostamble
        self.postamble = _postamble


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



    def generate(self):
        outGCode = [f'F{self.feedRate}']

        outGCode.append(self.preamble)
        
        for elem in self.rootET.iter():
            try:
                _, tag_suffix = elem.tag.split('}')
            except ValueError:
                print('Skip tag:', elem.tag)
                continue

            if tag_suffix in self.svg_shapes:
                shape_class = getattr(shapes_pkg, tag_suffix)
                outGCode += gShape( shape_class(elem), self.scale )

        outGCode.append(self.postamble)


        return outGCode



    def gShape(self, _shape, _scale=1):
        outGShape = []


        d = _shape.d_path()
        m = _shape.transformation_matrix()

        if not d:
            return outGShape


        outGShape.append(self.shapePreamble)

        p = point_generator(d, m, self.smoothness)
        for x,y in p:
            if x > 0 and x < self.maxX and y > 0 and y < self.maxY:  
                outGShape.append( gcMove(_scale*x, _scale*y) )

        outGShape.append(self.shapePostamble)


        return outGShape



    def gcMove(_x, _y, _pre="G1"):
            return f"{_pre} X{_x} Y{_y}"
