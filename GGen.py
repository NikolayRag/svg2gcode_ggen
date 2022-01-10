#!/usr/bin/env python

import sys
from . import shapes
from . import simpletransform 



class GGen():
    svg_shapes = ('svg', 'g', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path')


    _root = None
    _tree = None

    xform = [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0]]
    smoothness = 0.02
    precision = 4

    shapePre = ''
    shapeIn = ''
    shapeOut = ''


    templateG = 'X{x}Y{y}'


    nslen = 0



    def iterateTree(self, _el, _matrix=None):
        cTag = _el.tag[self.nslen:]

        if cTag in self.svg_shapes:
            shape_class = getattr(shapes, cTag)
            cShape = shape_class(_el, _matrix)

            yield cShape

            _matrix = cShape.transformation_matrix()


        for cEl in _el:
            yield from self.iterateTree(cEl, _matrix)



    def svgVp(self, _root):
        vbox = _root.get('viewBox', "0 0 1 1").split()

        vx = _root.get('width', None)
        if vx and vx[-1]=='%':
            vx = float(vx[:-1]) *.01 *float(vbox[2])
        else:
            vx = ''.join([ c for c in vx if c.isdigit() or c=='.' ]) if vx else vbox[2]
        vx = int(float(vx)) /float(vbox[2])

        vy = _root.get('height', None)
        if vy and vy[-1]=='%':
            vy = float(vy[:-1]) *.01 *float(vbox[3])
        else:
            vy = ''.join([ c for c in vy if c.isdigit() or c=='.'] ) if vy else vbox[3]
        vy = int(float(vy)) /float(vbox[3])

        return [
            [vx,0,-float(vbox[0])*vx],
            [0,vy,-float(vbox[1])*vy]
        ]



    def __init__(self, _root):
        self._root = _root
        self._tree = []
        self.nslen = len(self._root.tag)-3 if self._root.tag[-3:]=='svg' else 0


        cMatrix = self.svgVp(_root)
        for cEl in self.iterateTree(self._root, cMatrix):
            if cEl.isgeo():
                self._tree.append(cEl)



    def root(self):
        return self._root



    '''
    Stored SVG to be generated over further.
    '''
    def tree(self):
        return self._tree



    def set(self,
        xform = None,
        smoothness = None,
        precision = None,

        shapePre = None,
        shapeIn = None,
        shapeOut = None,
    ):
        if xform != None: self.xform = xform
        if smoothness != None: self.smoothness = smoothness
        if precision != None: self.precision = precision

        if shapePre != None: self.shapePre = shapePre
        if shapeIn != None: self.shapeIn = shapeIn
        if shapeOut != None: self.shapeOut = shapeOut


    
    def generate(self,
        xform = None,
        smoothness = None,
        precision = None,
    ):
        for cShape in self._tree:
            cXform = cShape.transformation_matrix(xform or self.xform)
            pointsA = self.shapeGen(cShape, cXform, smoothness or self.smoothness)

            yield cShape, self.shapeDecorate(cShape, pointsA, precision=precision or self.precision)



    def str(self,
        xform = None,
        smoothness = None,
        precision = None,
    ):
        gFlat = []
        for s, gA in self.generate(xform=xform, smoothness=smoothness, precision=precision):
            for g in gA:
                gFlat += g

        return "\n".join(gFlat)



###private###


    def shapeGen(self, _shape, _xform, _smoothness):
        gShapesA = []

        cGShape = []
        p = _shape.divide(_smoothness, _xform)
        for x,y,start in p:
            if start:
                cGShape = []
                gShapesA.append(cGShape)

            cGShape.append((x, y))


        return gShapesA



    def shapeDecorate(self, _shape, _pointsA, _outCode=None, precision=None):
        if not _outCode: _outCode = []


        injectPre = self.buildInline(self.shapePre, _shape)

        cI = 0
        for cShape in _pointsA:
            if len(cShape):
                injectIn = self.buildInline(self.shapeIn, _shape, cShape[0])
                injectOut = self.buildInline(self.shapeOut, _shape, cShape)

                for g in injectPre:
                    if g == False:
                        return _outCode
                    _outCode.append(g)

                _outCode += self.buildMove(cShape[0], precision)

                for g in injectIn:
                    _outCode.append(g)

                _outCode += self.buildMove(cShape[1:], precision)

                for g in injectOut:
                    _outCode.append(g)

            cI += 1


        return _outCode



    def buildInline(self, _tmpl, _shape, _arg=None):
        if callable(_tmpl):
            if _arg:
                _tmpl = _tmpl(_shape, _arg)
            else:
                _tmpl = _tmpl(_shape)

        if not isinstance(_tmpl, list):
            _tmpl = [_tmpl]

        return _tmpl



    def buildMove(self, _coords, prec=None):
        if not isinstance(_coords[0], tuple):
            _coords = (_coords,)

        return [self.templateG.format(x=round(x,prec), y=round(y,prec)) for x,y in _coords]
