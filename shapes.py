#!/usr/bin/env python

import logging
import traceback
import xml.etree.ElementTree as ET
from . import simplepath
from . import simpletransform 
from . import cubicsuperpath
from . import cspsubdiv


class SvgTag(object):
    mat = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]

    
    def __init__(self, xml_node, _parent=None):
        t = xml_node.get('transform')
        if t:
            self.mat = simpletransform.parseTransform(t)

        if _parent:
            self.mat = simpletransform.composeTransform(_parent, self.mat)

        self.xml_node = xml_node 

    def d_path(self):
        raise NotImplementedError

    def transformation_matrix(self, _parent=None):
        if not _parent:
            return self.mat

        return simpletransform.composeTransform(_parent, self.mat)


    def svg_path(self):
        dPath = self.d_path()
        if not dPath:
            return

        return "<path d=\"" + dPath + "\"/>"

    def xml(self):
        return self.xml_node

    def isgeo(self):
        return True

    def type(self):
        return self.__class__.__name__

    def cubicPath(self, xform=True):
        dPath = self.d_path()
        if not dPath:
            return []

        cubicP = cubicsuperpath.parsePath(dPath)

        if xform == True:
            xform = self.transformation_matrix()

        if xform:
            simpletransform.applyTransformToPath(xform, cubicP)

        return cubicP


    def divide(self, flatness, xform=True):
        for sp in self.cubicPath(xform):
            start = True
            prevsp = sp[0]
            for csp in sp[1:]:
                ssp = [prevsp, csp]
                cspsubdiv.subdiv( ssp, flatness)

                if start:
                    cp = ssp[0]
                    yield cp[1][0], cp[1][1], True
                    start = False

                for cp in ssp[1:]:
                    yield cp[1][0], cp[1][1], False

                prevsp = csp


class g(SvgTag):
     def __init__(self, xml_node, _parentMat=None):
        super(g, self).__init__(xml_node, _parentMat)

     def d_path(self):
        return False

     def isgeo(self):
        return False


class path(SvgTag):
     def __init__(self, xml_node, _parentMat=None):
        super(path, self).__init__(xml_node, _parentMat)

        if not self.xml_node == None:
            path_el = self.xml_node
            self.d = path_el.get('d')
        else:
            self.d = None 
            logging.error("path: Unable to get the attributes for %s", self.xml_node)

     def d_path(self):
        return self.d     

class rect(SvgTag):
  
    def __init__(self, xml_node, _parentMat=None):
        super(rect, self).__init__(xml_node, _parentMat)

        if not self.xml_node == None:
            rect_el = self.xml_node
            self.x  = float(rect_el.get('x')) if rect_el.get('x') else 0
            self.y  = float(rect_el.get('y')) if rect_el.get('y') else 0
            self.rx = float(rect_el.get('rx')) if rect_el.get('rx') else 0
            self.ry = float(rect_el.get('ry')) if rect_el.get('ry') else 0
            self.width = float(rect_el.get('width')) if rect_el.get('width') else 0
            self.height = float(rect_el.get('height')) if rect_el.get('height') else 0
        else:
            self.x = self.y = self.rx = self.ry = self.width = self.height = 0
            logging.error("rect: Unable to get the attributes for %s", self.xml_node)

    def d_path(self):
        a = list()
        a.append( ['M ', [self.x, self.y]] )
        a.append( [' l ', [self.width, 0]] )
        a.append( [' l ', [0, self.height]] )
        a.append( [' l ', [-self.width, 0]] )
        a.append( [' Z', []] )
        return simplepath.formatPath(a)     

class ellipse(SvgTag):

    def __init__(self, xml_node, _parentMat=None):
        super(ellipse, self).__init__(xml_node, _parentMat)

        if not self.xml_node == None:
            ellipse_el = self.xml_node
            self.cx  = float(ellipse_el.get('cx')) if ellipse_el.get('cx') else 0
            self.cy  = float(ellipse_el.get('cy')) if ellipse_el.get('cy') else 0
            self.rx = float(ellipse_el.get('rx')) if ellipse_el.get('rx') else 0
            self.ry = float(ellipse_el.get('ry')) if ellipse_el.get('ry') else 0
        else:
            self.cx = self.cy = self.rx = self.ry = 0
            logging.error("ellipse: Unable to get the attributes for %s", self.xml_node)

    def d_path(self):
        x1 = self.cx - self.rx
        x2 = self.cx + self.rx
        p = 'M %f,%f ' % ( x1, self.cy ) + \
            'A %f,%f ' % ( self.rx, self.ry ) + \
            '0 1 0 %f,%f ' % ( x2, self.cy ) + \
            'A %f,%f ' % ( self.rx, self.ry ) + \
            '0 1 0 %f,%f' % ( x1, self.cy )
        return p

class circle(ellipse):
    def __init__(self, xml_node, _parentMat=None):
        super(ellipse, self).__init__(xml_node, _parentMat)

        if not self.xml_node == None:
            circle_el = self.xml_node
            self.cx  = float(circle_el.get('cx')) if circle_el.get('cx') else 0
            self.cy  = float(circle_el.get('cy')) if circle_el.get('cy') else 0
            self.rx = float(circle_el.get('r')) if circle_el.get('r') else 0
            self.ry = self.rx
        else:
            self.cx = self.cy = self.r = 0
            logging.error("Circle: Unable to get the attributes for %s", self.xml_node)

class line(SvgTag):

    def __init__(self, xml_node, _parentMat=None):
        super(line, self).__init__(xml_node, _parentMat)

        if not self.xml_node == None:
            line_el = self.xml_node
            self.x1  = float(line_el.get('x1')) if line_el.get('x1') else 0
            self.y1  = float(line_el.get('y1')) if line_el.get('y1') else 0
            self.x2 = float(line_el.get('x2')) if line_el.get('x2') else 0
            self.y2 = float(line_el.get('y2')) if line_el.get('y2') else 0
        else:
            self.x1 = self.y1 = self.x2 = self.y2 = 0
            logging.error("line: Unable to get the attributes for %s", self.xml_node)

    def d_path(self):
        a = []
        a.append( ['M ', [self.x1, self.y1]] )
        a.append( ['L ', [self.x2, self.y2]] )
        return simplepath.formatPath(a)

class polycommon(SvgTag):

    def __init__(self, xml_node, _parentMat=None):
        super(polycommon, self).__init__(xml_node, _parentMat)
        self.points = list()

        if not self.xml_node == None:
            polycommon_el = self.xml_node
            points = polycommon_el.get('points') if polycommon_el.get('points') else list() 
            for pa in points.split():
                self.points.append(pa)
        else:
            logging.error("polycommon: Unable to get the attributes for %s", self.xml_node)


class polygon(polycommon):

    def __init__(self, xml_node, _parentMat=None):
         super(polygon, self).__init__(xml_node, _parentMat)

    def d_path(self):
        d = "M " + self.points[0]
        for i in range( 1, len(self.points) ):
            d += " L " + self.points[i]
        d += " Z"
        return d

class polyline(polycommon):

    def __init__(self, xml_node, _parentMat=None):
         super(polyline, self).__init__(xml_node, _parentMat)

    def d_path(self):
        d = "M " + self.points[0]
        for i in range( 1, len(self.points) ):
            d += " L " + self.points[i]
        return d

