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
    shapeOut = ''
    shapeFinal = ''
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
        shapeOut = None,
        shapeFinal = None,
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
        if shapeOut != None: self.shapeOut = shapeOut
        if shapeFinal != None: self.shapeFinal = shapeFinal
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


    
    def generate(self, join=False):
        outGCode = self.buildHead()


        for elem in self.rootET.iter():
            try:
                _, tag_suffix = elem.tag.split('}')
            except ValueError:
                print('Skip tag:', elem.tag)
                continue

            if tag_suffix in self.svg_shapes:
                shape_class = getattr(shapes_pkg, tag_suffix)
                shapesA = self.shapeGen(shape_class(elem))

                self.shapeDecorate(elem, shapesA, outGCode)


        outGCode += self.buildTail()


        return "\n".join(outGCode) if join else outGCode



    def shapeGen(self, _shape):
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



    def shapeDecorate(self, _cEl, _shapes, _outCode=[]):
        injectPre = self.buildInline(self.shapePre, _cEl)
        injectFinal = self.buildInline(self.shapeFinal, _cEl, _shapes)


        for cShape in _shapes:
            if len(cShape):
                injectIn = self.buildInline(self.shapeIn, _cEl, cShape[0])
                injectOut = self.buildInline(self.shapeOut, _cEl, cShape)

                if injectPre: _outCode += [injectPre]
                _outCode += self.buildMove(cShape[0])
                if injectIn: _outCode += [injectIn]
                _outCode += self.buildMove(cShape[1:])
                if injectOut: _outCode += [injectOut]

        if injectFinal: _outCode += [injectFinal]


        return _outCode



    def buildInline(self, _tmpl, _el, _arg=None):
        if callable(_tmpl):
            if _arg:
                _tmpl = _tmpl(_el, _arg)
            else:
                _tmpl = _tmpl(_el)

        if not isinstance(_tmpl, str):
            _tmpl = ''

        return _tmpl



    def buildMove(self, _coords):
        if not isinstance(_coords[0], tuple):
            _coords = (_coords,)

        p = self.precision
        return [f"X{round(_x,p)}Y{round(_y,p)}" for _x,_y in _coords]



    def buildHead(self):
        out = []

        out.append(self.preamble)

        if self.feedRate:
            out.append( f'F{self.feedRate}' )

        return out



    def buildTail(self):
        out = []

        if self.park:
            out.append( self.buildMove((0,0)) )

        out.append(self.postamble)

        return out



