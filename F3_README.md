# graphs
School project for a Graphs Theory class 

# Group F3

### external modules needed : `rich`, `tabulate` & `graphviz`

To use the possibility of graphical rendering, you must download the graphviz executable **and add it to your `PATH`**


The given test graphs are in `graphs/`

All execution traces can be found in the `traces/` folder and was generated with the `src/traces.py` script.

This includes the textual traces which are named: `F3_<number_of_graph>.txt`, 

the graphical render of the graph `F3_<number_of_graph>.png`, 

and if it is possible the graphical render with the longest path highlighted: `F3_<number_of_graph>_highlighted_path.png` 

---
To execute the files on Windows you must add the `-X utf8` argument to python, because the windows console does not natively have utf8 encoding.

example: `python -X utf8 F3_main.py`