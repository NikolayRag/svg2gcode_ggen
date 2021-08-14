#!/usr/bin/env python

import sys
from . import shapes as shapes_pkg
from .shapes import point_generator



class GGen():
    svg_shapes = ('rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path')


    rootET = None
    smoothness = 0.02
    feedRate = 0
    park = False
    maxX = 200
    maxY = 300

    precision = 4
    preamble = ''
    shapePre = ''
    shapeIn = ''
    shapePost = ''
    postamble = ''


    scale = 1.



    def __init__(self, _rootET):
        self.rootET = _rootET



    def set(self,
        smoothness = None,
        feedRate = None,
        park = None,
        maxX = None,
        maxY = None,

        precision = None,
        preamble = None,
        shapePre = None,
        shapeIn = None,
        shapePost = None,
        postamble = None
    ):
        if smoothness != None: self.smoothness = smoothness
        if feedRate != None: self.feedRate = feedRate
        if park != None: self.park = park
        if maxX != None: self.maxX = maxX
        if maxY != None: self.maxY = maxY

        if precision != None: self.precision = precision
        if preamble != None: self.preamble = preamble
        if shapePre != None: self.shapePre = shapePre
        if shapeIn != None: self.shapeIn = shapeIn
        if shapePost != None: self.shapePost = shapePost
        if postamble != None: self.postamble = postamble


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
#            self.scale = min(scale_x, scale_y)

        else:
            print("Unable to get width and height for the svg")


    
    def build(self, join=False):
        out = (
            self.gHead()
            + [self.preamble]
            + self.gCode()
            + [self.postamble]
            + self.gTail()
        )

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
                shapesA = self.gShape(shape_class(elem))

                self.shapeDecorate(elem, shapesA, outGCode)


        return outGCode



    def gShape(self, _shape):
        d = _shape.d_path()
        m = _shape.transformation_matrix()

        if not d:
            return []


        gShapesA = []

        cGShape = []
        p = point_generator(d, m, self.smoothness)
        for x,y,start in p:
            if start:
                cGShape = []
                gShapesA.append(cGShape)

            cGShape.append( (self.scale*x, self.scale*y) )


        return gShapesA



    def shapeDecorate(self, _cEl, _shapes, outGShapeCode=[]):
        injectPre = self.buildInline(self.shapePre, _cEl)
        injectPost = self.buildInline(self.shapePost, _cEl, _shapes)


        for cShape in _shapes:
            if len(cShape):
                injectIn = self.buildInline(self.shapeIn, _cEl, cShape[0])

                outGShapeCode += [injectPre]
                outGShapeCode += self.gMove(cShape[0])
                outGShapeCode += [injectIn]
                outGShapeCode += self.gMove(cShape[1:])
                outGShapeCode += [injectPost]


        return outGShapeCode



    def buildInline(self, _tmpl, _el, _arg=None):
        if callable(_tmpl):
            if arg:
                _tmpl = _tmpl(_el, _arg)
            else:
                _tmpl = _tmpl(_el)

        if not isinstance(_tmpl, str):
            _tmpl = ''

        return _tmpl



    def gMove(self, _coords):
        if not isinstance(_coords[0], tuple):
            _coords = (_coords,)

        p = self.precision
        return [f"X{_xy[0]:.{p}f}Y{_xy[1]:.{p}f}" for _xy in _coords]



    def gHead(self):
        out = []
        if self.feedRate:
            out.append( f'F{self.feedRate}' )

        return out



    def gTail(self):
        out = []

        if self.park:
            out.append( self.gMove((0,0)) )


        return out



