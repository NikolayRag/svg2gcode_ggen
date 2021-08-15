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
ggObject.set(
    smoothness = 0.02,
    feedRate = 0,
    park = False,
    maxX = 200,
    maxY = 300,

    precision = 4,
    preamble = '',
    shapePre = '',
    shapeIn = '',
    shapeOut = '',
    shapeFinal = '',
    postamble = ''
)
ggRows = ggObject.generate(
	join = False
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
    preamble = 'G90 M4 S0',
    shapePre = 'G0',
    shapeIn = 'S100 G1',
    shapeOut = 'S0',
    postamble = 'M5 G0 X0Y0'
)
```



Original project:
-----------------

Forked from [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode) without Inkscape branch.

Most notable changes:
* Python 3 compatable
* Is importable module
* GGen class as interface
* Fix: curved shapes collected with wrong points
* Fix: multishapes pre/in/post -decorated separately


Original project terms:

The compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code. 
