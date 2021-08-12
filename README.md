A fast svg to gcode compiler module.

Forked from [vishpat/svg2gcode](https://github.com/vishpat/svg2gcode)


Original compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code. 
