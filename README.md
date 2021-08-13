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
ggRows = ggObject.generate(
    smoothness = 0.02,
    feedRate = 10000,
    maxX = 200,
    maxY = 300,

    preamble = 'G90',
    shapePreamble = None,
    shapePostamble = None,
    postamble = ''
)
print ( "\n".join(ggRows) )
```

In addition to being strings, **shapePreamble** and **shapePostamble** passed can be callback functions to generate inline pre/post-amble at runtime.
**shapePreamble** accepts currently iterated SVG **element**, and **shapePostamble** accepts **element** and generated **gcode**:

```python
def shapePre(_element):
	return( f"(preamble for {_element.tag})" )

def shapePost(_element, _gcode):
	return( f"(postamble for {_element.tag} with code {_gcode})" )

ggRows = ggObject.generate( shapePreamble=shapePre, shapePostamble=shapePost )
```



Original project terms:
-----------------------

The compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code. 
