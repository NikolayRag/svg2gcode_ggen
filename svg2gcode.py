#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import shapes as shapes_pkg
from shapes import point_generator

def generate_gcode(
    root,
    smoothness = 0.02,
    bed_max_x = 200,
    bed_max_y = 300,

    svg_shapes = set(['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path']),
    preamble = 'G90',
    shape_preamble = '',
    shape_postamble = '',
    postamble = ''
):
    outG = []
    width = root.get('width')
    height = root.get('height')
    if width == None or height == None:
        viewbox = root.get('viewBox')
        if viewbox:
            _, _, width, height = viewbox.split()                

    if width == None or height == None:
        print("Unable to get width and height for the svg")
        sys.exit(1)

    width = float(width)
    height = float(height)

    scale_x = bed_max_x / max(width, height)
    scale_y = bed_max_y / max(width, height)

    outG.append(preamble)
    
    for elem in root.iter():
        
        try:
            _, tag_suffix = elem.tag.split('}')
        except ValueError:
            continue

        if tag_suffix in svg_shapes:
            shape_class = getattr(shapes_pkg, tag_suffix)
            shape_obj = shape_class(elem)
            d = shape_obj.d_path()
            m = shape_obj.transformation_matrix()

            if d:
                outG.append(shape_preamble)
                p = point_generator(d, m, smoothness)
                for x,y in p:
                    if x > 0 and x < bed_max_x and y > 0 and y < bed_max_y:  
                        outG.append( "G1 X%0.1f Y%0.1f" % (scale_x*x, scale_y*y) )
                outG.append(shape_postamble)

    outG.append(postamble)


    return outG
