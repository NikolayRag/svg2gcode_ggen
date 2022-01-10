SVG to GCode converter
----------------------


Source provided is an SVG within xml.etree.ElementTree root, as used widely.

Quick useage, also showing defaults:
------------------------------------

```python
import xml.etree.ElementTree as XML
svgXml = XML.parse('file.svg')


import GGen

ggObject = GGen.GGen( svgXml.getroot() )

#notice default xform is only Y-inverted matrix
ggObject.set(
    xform = [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0]],

    smoothness = 0.02,
    precision = 4,

    shapePre = '',
    shapeIn = '',
    shapeOut = ''
)

for gShape, gList in ggObject.generate(
    xform = None,

    smoothness = None,
    precision = None
):
    do_something_with( gList )

#or

gString = ggObject.str(
    xform = None,

    smoothness = None,
    precision = None
)

```
where **gList** will be per-shape G-commands lists, and **gShape** is bound to SVG shape.
**gShape** can be accessed iterating **.tree()**. **.setData()** and **.data()** can be used to store arbitrary data within shape.


In addition to being strings, **shapePre**, **shapeIn** and **shapeOut** passed can be hook functions to generate inline:

* **shapePre(currentSvgTag)**  
    Called once, inlined before starting point of each sub-shape.
    May return False to skip shape entirely.

* **shapeIn(currentSvgTag, pointZero)**  
    Called for each sub-shape, inlined after starting point
    
* **shapeOut(currentSvgTag, shapePointsList)**  
    Called for each sub-shape and inlined after last point.

All hook functions should return either value or list of values.


```python
def shapePreHook(_tag):
    print( f"(pre for {_tag})" )

def shapeInHook(_tag, _point):
    print( f"(in for {_tag}, starting at {_point})" )

def shapeOutHook(_tag, _shape):
    print( f"(out for {_tag}, {len(_shape)}")


ggObject.set(
    shapePre = shapePreHook,
    shapeIn = shapeInHook,
    shapeOut = shapeOutHook
)
```

Typical static config for laser engraver can be:
```python
ggObject.set(
    shapePre = 'G0', #Fast position
    shapeIn = 'S1000 G1',  #Set 100% laser bightness and start feed move
    shapeOut = 'S0', #Set 0% laser bightness
)
```



Reference:
----------

Forked from [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode) without Inkscape branch.

Most notable changes:
* Python 3 compatable
* Is importable module
* GGen class as interface
* Used as generator
* Gather transform all over hierarchy for node
* Fix: curved shapes collected with wrong points [#2733998](https://github.com/NikolayRag/svg2gcode_ggen/commit/2733998fb56177be35ea0a91014296366bd2bd3a)
* Fix: proccess multishapes per-shape [#43d4dba](https://github.com/NikolayRag/svg2gcode_ggen/commit/43d4dba31fd7cfb5d92c99fd018b30991fcd4d90)
* Fix: complex curves out or recursion limits [#33737f2](https://github.com/NikolayRag/svg2gcode_ggen/commit/33737f2b23cd614b60b2f5b16a2896b5cdddc1d3)
