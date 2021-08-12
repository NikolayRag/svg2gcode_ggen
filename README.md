A svg to gcode compiler Py3 module.
Forked from [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode)

Quick useage:

```python
import xml.etree.ElementTree as XML
svg = XML.parse(_fileName)


import GGen

ggObject = GGen( svg.getroot() )
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

**shapePreamble** and **shapePostamble** passed can be callback functions,
accepting currently iterated SVG ET **element**:

```python
def shapePre(_shape):
	return( f"(preamble for {_shape.tag})" )

ggRows = ggObject.generate( shapePreamble=shapePre )

```



original project terms:
-----------------------

Compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code. 
