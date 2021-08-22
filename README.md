SVG to GCode converter
----------------------


Source provided is an SVG within xml.etree.ElementTree root Element, as used widely.

Quick useage, also showing defaults:
------------------------------------

```python
import xml.etree.ElementTree as XML
svgXml = XML.parse('file.svg')


import GGen

ggObject = GGen.GGen( svgXml.getroot() )

ggObject.setDevice(
    feedRate = 0,
    park = False
)

#notice default xform is only Y-inverted, NOT offset to place in positive area
ggObject.set(
    xform = [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0]],

    smoothness = 0.02,
    precision = 4,

    preamble = '',
    shapePre = '',
    shapeIn = '',
    shapeOut = '',
    shapeFinal = '',
    postamble = ''
)

for gEntity in ggObject.generate(
    xform = None,

    smoothness = None,
    precision = None
):
    do_something_with( gEntity )
```
where **gEntity** will be complete list of G-commands one for head, each shape, and tail.

Converting to string explicitely with ```str(ggObject)``` or implicitely like in ```print(ggObject)``` is allowed, obvoiusly resulting in complete g-code within one string.


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
* Used as generator
* Gather transform all over hierarchy for node
* Fix: curved shapes collected with wrong points [#2733998](https://github.com/NikolayRag/svg2gcode_ggen/commit/2733998fb56177be35ea0a91014296366bd2bd3a)
* Fix: proccess multishapes per-shape [#43d4dba](https://github.com/NikolayRag/svg2gcode_ggen/commit/43d4dba31fd7cfb5d92c99fd018b30991fcd4d90)
* Fix: complex curves out or recursion limits [#33737f2](https://github.com/NikolayRag/svg2gcode_ggen/commit/33737f2b23cd614b60b2f5b16a2896b5cdddc1d3)
