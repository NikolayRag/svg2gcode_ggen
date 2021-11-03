#!/usr/bin/env python

import sys
from . import shapes
from . import simpletransform 



class GGen():
    svg_shapes = ('g', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path')


    tree = None

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



    def iterateTree(self, _el, _dep=0,):
        try:
            _, cTag = _el.tag.split('}')
        except ValueError:
            print('Skip tag:', _el.tag)
            return


        if cTag in self.svg_shapes:
            shape_class = getattr(shapes, cTag)
            cShape = shape_class(_el)

            yield [_dep, cShape]

        else:
            _dep -= 1 #roll back unknown tag


        for cEl in _el:
            yield from self.iterateTree(cEl, _dep+1)



    def __init__(self, _rootET):
        self.tree = []

        for cEl in self.iterateTree(_rootET):
            self.tree.append(cEl)



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
        for cDep, cShape in self.tree:
            if cDep <= prevDep: #out of branch
                matrixAcc = matrixAcc[:(cDep-prevDep-1)]
            prevDep = cDep

            matrixAcc.append(cShape.transformation_matrix())


            cXform = self.xform
            for m in matrixAcc:
                if m:
                    cXform = simpletransform.composeTransform(cXform, m)

            shapesA = self.shapeGen(cShape, cXform)

            el = self.shapeDecorate(cShape.xml(), shapesA)
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



    def shapeDecorate(self, _cEl, _shapes, _outCode=None):
        if not _outCode: _outCode = []


        injectPre = self.buildInline(self.shapePre, _cEl)

        if injectPre == False:
            return _outCode


        cI = 0
        for cShape in _shapes:
            if len(cShape):
                injectIn = self.buildInline(self.shapeIn, _cEl, cShape[0])
                injectOut = self.buildInline(self.shapeOut, _cEl, [_shapes, cI])

                _outCode += [injectPre or '']
                _outCode += self.buildMove(cShape[0])
                _outCode += [injectIn or '']
                _outCode += self.buildMove(cShape[1:])
                _outCode += [injectOut or '']

            cI += 1


        return _outCode



    def buildInline(self, _tmpl, _el, _arg=None):
        if callable(_tmpl):
            if _arg:
                _tmpl = _tmpl(_el, _arg)
            else:
                _tmpl = _tmpl(_el)

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



