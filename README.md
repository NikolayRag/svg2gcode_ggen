SVG to GCode converter
----------------------


Source provided is an SVG within xml.etree.ElementTree root Element, as used widely.

Quick useage, also showing defaults:
------------------------------------

```python
import xml.etree.ElementTree as XML
svgRoot = XML.parse('file.svg').getroot()


import GGen

ggObject = GGen.GGen( svgRoot )

ggObject.setDevice(
    feedRate = 0,
    park = False
)

ggObject.set(
    scale = 1,
    smoothness = 0.02,
    precision = 4,

    preamble = '',
    shapePre = '',
    shapeIn = '',
    shapeOut = '',
    shapeFinal = '',
    postamble = ''
)
ggRows = ggObject.generate(
    scale = None,
    smoothness = None,
    precision = None
)
```

In addition to being strings, **shapePre**, **shapeIn**, **shapeOut** and **shapeFinal** passed can be hook functions to generate inline:

* **shapePre(currentSvgElement)**  
    called once, inlined before starting point of each sub-shape
* **shapeIn(currentSvgElement, pointZero)**  
    called for each sub-shape, inlined after starting point
* **shapeOut(currentSvgElement, pointsList)**  
    called for each sub-shape and inlined after last point
* **shapeFinal(currentSvgEelement, shapesList)**  
    called once, inlined once at end of all sub-shapes


```python
def shapePreHook(_element):
    return( f"(pre for {_element.tag})" )

def shapeInHook(_element, _point):
    return( f"(in for {_element.tag}, starting at {_point})" )

def shapeOutHook(_element, _shape):
    return( f"(post for {_element.tag}, {len(_shape)} points)" )

def shapeFinalHook(_element, _shapes):
	return( f"(final for {_element.tag}, {len(_shapes)} sub-shapes)" )


ggObject.set(
    shapePre = shapePreHook,
    shapeIn = shapeInHook,
    shapeOut = shapeOutHook,
    shapeFinal = shapeFinalHook
)
```

Typical static config for laser engraver can be:
```python
ggObject.set(
    preamble = 'G90 M4 S0', #Set laser on with 0% bightness
    shapePre = 'G0', #Fast position
    shapeIn = 'S100 G1',  #Set 100% laser bightness and start feed move
    shapeOut = 'S0', #Set 0% laser bightness
    postamble = 'M5 G0 X0Y0' #Set laser off and park
)
```



Reference:
----------

Forked from [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode) without Inkscape branch.

Most notable changes:
* Python 3 compatable
* Is importable module
* GGen class as interface
* 
* Fix: curved shapes collected with wrong points [https://github.com/NikolayRag/svg2gcode_ggen/commit/2733998fb56177be35ea0a91014296366bd2bd3a](#2733998)
* Fix: multishapes proccessed separately per-shape [https://github.com/NikolayRag/svg2gcode_ggen/commit/43d4dba31fd7cfb5d92c99fd018b30991fcd4d90](43d4dba)
* Fix: complex curves out or recursion limits [https://github.com/NikolayRag/svg2gcode_ggen/commit/33737f2b23cd614b60b2f5b16a2896b5cdddc1d3](#33737f2)


Original project terms:

The compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code. 
