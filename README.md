# mediocre_script_collection
Dubious collection of scripts for plotting ICON data. Most function are hand tailored (not in a good way) to specific data and problems.


### Documenting code
If you write new code, it would be nice if it has Docstrings. 

Maybe [Doxygen type Docstrings](https://www.woolseyworkshop.com/2020/06/25/documenting-python-programs-with-doxygen/) or maybe, rather (Sphynx)[https://pythonhosted.org/an_example_pypi_project/sphinx.html)?


### Project management

[Dr.Watson](https://juliadynamics.github.io/DrWatson.jl/dev/), a project manager for Julia (exclusively). The [file and code structure part](https://juliadynamics.github.io/DrWatson.jl/dev/project/#Default-Project-Setup-1) is transferable to Python.

[Dr. Watson introduction by George Datseris (8min)](https://www.youtube.com/watch?v=jKATlEAu8eE)


### Criteria for good code

[George Datseris in his Lecture (2h)](https://www.youtube.com/watch?v=iIIBFujl254) proposed a separation of the functional part of your code (`source`) and the data display part of the code (`scripts`). He also suggests following a strict Functional Programming paradigm with pure functions, that are very short (a few lines of code) and build upon each other.



