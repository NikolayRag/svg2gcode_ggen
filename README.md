SVG to GCode converter
----------------------
Forked from [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode) without Inkscape branch.


Most notable changes:
* Python 3 compatable
* Is importable module
* GGen class as interface

Source provided is an SVG within xml.etree.ElementTree root Element, as used widely.

Quick useage:
------------

```python
import xml.etree.ElementTree as XML
svg = XML.parse(_fileName)


import GGen

ggObject = GGen.GGen( svg.getroot() )
ggObject.set(
    smoothness = 0.02,
    feedRate = 0,
    park = False,
    maxX = 200,
    maxY = 300,

    preamble = '',
    shapePreamble = None,
    shapePostamble = None,
    postamble = ''
)
ggRows = ggObject.build(
	join=False
)
```

In addition to being strings, **shapePreamble** and **shapePostamble** passed can be callback functions to generate inline pre/post-amble at runtime.
**shapePreamble** accepts currently iterated SVG **element**, and **shapePostamble** accepts **element** and generated **gcode**:

```python
def shapePre(_element):
	return( f"(preamble for {_element.tag})" )

def shapePost(_element, _gcode):
	return( f"(postamble for {_element.tag}, {len(_gcode)} segments)" )


ggObject.set( shapePreamble=shapePre, shapePostamble=shapePost )
ggStrings = ggObject.build(True)
```



Original project terms:
-----------------------

The compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code. 
