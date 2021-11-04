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

    feedRate = 0
    park = False

    preamble = ''
    shapePre = ''
    shapeIn = ''
    shapeOut = ''
    postamble = ''


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
            vx = float(vx[:-1]) *.01
        else:
            vx = ''.join([ c for c in vx if c.isdigit() or c=='.' ]) if vx else vbox[2]
            vx = float(vx) /float(vbox[2])

        vy = _root.get('height', None)
        if vy and vy[-1]=='%':
            vy = float(vy[:-1]) *.01
        else:
            vy = ''.join([ c for c in vy if c.isdigit() or c=='.'] ) if vy else vbox[3]
            vy = float(vy) /float(vbox[3])

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



    def tree(self):
        return self._tree



    def setDevice(self,
        feedRate = None,
        park = None,
    ):
        if feedRate != None: self.feedRate = feedRate
        if park != None: self.park = park



    def set(self,
        xform = None,
        smoothness = None,
        precision = None,

        preamble = None,
        shapePre = None,
        shapeIn = None,
        shapeOut = None,
        postamble = None,
    ):
        if xform != None: self.xform = xform
        if smoothness != None: self.smoothness = smoothness
        if precision != None: self.precision = precision

        if preamble != None: self.preamble = preamble
        if shapePre != None: self.shapePre = shapePre
        if shapeIn != None: self.shapeIn = shapeIn
        if shapeOut != None: self.shapeOut = shapeOut
        if postamble != None: self.postamble = postamble


    
    def generate(self,
        xform = None,
        smoothness = None,
        precision = None,
    ):
        self.set(xform=xform, smoothness=smoothness, precision=precision)


        el = self.buildHead()
        yield el


        matrixAcc = []
        prevDep = 0
        for cShape in self._tree:
            cXform = cShape.transformation_matrix(self.xform)
            pointsA = self.shapeGen(cShape, cXform)

            el = self.shapeDecorate(cShape, pointsA)
            yield el


        el = self.buildTail()
        yield el



    def str(self,
        xform = None,
        smoothness = None,
        precision = None,
    ):
        gFlat = []
        for g in self.generate(xform=xform, smoothness=smoothness, precision=precision):
            gFlat += g

        return "\n".join(gFlat)



###private###


    def shapeGen(self, _shape, _xform):
        gShapesA = []

        cGShape = []
        p = _shape.divide(self.smoothness, _xform)
        for x,y,start in p:
            if start:
                cGShape = []
                gShapesA.append(cGShape)

            cGShape.append((x, y))


        return gShapesA



    def shapeDecorate(self, _shape, _pointsA, _outCode=None):
        if not _outCode: _outCode = []


        injectPre = self.buildInline(self.shapePre, _shape)

        if injectPre == False:
            return _outCode


        cI = 0
        for cShape in _pointsA:
            if len(cShape):
                injectIn = self.buildInline(self.shapeIn, _shape, cShape[0])
                injectOut = self.buildInline(self.shapeOut, _shape, [_pointsA, cI])

                _outCode += [injectPre or '']
                _outCode += self.buildMove(cShape[0])
                _outCode += [injectIn or '']
                _outCode += self.buildMove(cShape[1:])
                _outCode += [injectOut or '']

            cI += 1


        return _outCode



    def buildInline(self, _tmpl, _shape, _arg=None):
        if callable(_tmpl):
            if _arg:
                _tmpl = _tmpl(_shape, _arg)
            else:
                _tmpl = _tmpl(_shape)

        return _tmpl



    def buildMove(self, _coords):
        if not isinstance(_coords[0], tuple):
            _coords = (_coords,)

        p = self.precision
        return [self.templateG.format(x=round(x,p), y=round(y,p)) for x,y in _coords]



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



