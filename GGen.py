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



    def set(self,
        smoothness = 0.02,
        feedRate = 0,
        maxX = 200,
        maxY = 300,

        preamble = '',
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


    
    def build(self, join=True):
        out = self.head() +self.gCode() +self.tail()

        if join:
            out = "\n".join(out)


        return out




    def gCode(self):
        outGCode = []

        for elem in self.rootET.iter():
            try:
                _, tag_suffix = elem.tag.split('}')
            except ValueError:
                print('Skip tag:', elem.tag)
                continue

            if tag_suffix in self.svg_shapes:
                shape_class = getattr(shapes_pkg, tag_suffix)

                outGCode += self.gShape( shape_class(elem) )


        return outGCode



    def gShape(self, _shape):
        d = _shape.d_path()
        m = _shape.transformation_matrix()

        if not d:
            return []


        injectPre = self.shapePreamble
        if callable(injectPre):
            injectPre = injectPre(_shape.__str__())
        if not isinstance(injectPre, str):
            injectPre = ''


        outGShape = []

        p = point_generator(d, m, self.smoothness)
        for x,y in p:
            if x > 0 and x < self.maxX and y > 0 and y < self.maxY:  
                outGShape.append( self.gcMove(self.scale*x, self.scale*y) )


        injectPost = self.shapePostamble
        if callable(injectPost):
            injectPost = injectPost(_shape.__str__(), outGShape)
        if not isinstance(injectPost, str):
            injectPost = ''


        return [injectPre] +outGShape +[injectPost]



    def gcMove(self, _x, _y, _pre="G1"):
            return f"{_pre} X{_x} Y{_y}"



    def head(self):
        out = []
        if self.feedRate:
            out.append( f'F{self.feedRate}' )

        out.append( self.preamble )

        return out



    def tail(self):
        return [self.postamble, self.gcMove(0,0)]



