# My Config Tool

This repository represents my attempt at reproducing the results of the GBT config tool.

As of this writing it has only demonstrated configuration of most receivers for Continuum observations with the DCR (those standard configurations used with Auto procedures).


## Installation

The supported parts of this repo only require Python 3, so no installation required.

## Unit Tests

First, you have to prepare your data, which must be extracted from the Python 2 pickle file using Python 2 into a text file that Python 3
can read.

python pkl2txtPy2.py

Then you can run the python 3 tests:

python3 configureDCRTests.py

## Design

Currently, this code only configures the DCR for Continuum observations, so the function 'configureDCR' is our entry point.  This takes in a configuration dictionary (same that is used by the current config tool).  It returns the IF paths to be used, along with the manager parameters to be set.

<img src="data/myConfigClasses.png"></img>

### IF Paths

Paths to be used through the GBT IF system are represented by lists of IFPathNode lists ([[IFPathNode]]).  Each of these IFPathNode objects can identify what device they represent, and what is happening with the frequency bandpass.

All valid paths leading from a single receiver are derived first from the pickle file generated by the current config tool (a product of standard.cabling and some extra value added stuff).  Since this pickle file is generated from Python 2, we include code to convert these to text files for Python 3.

The text files are read from the path module (getIFPaths) and create [[IFPathNode]] representation.  Each of these IFPathNode objects only has information it could have obtained from the text file, which is a standard.cabling style name of a port, i.e. VEGAS:J1.  Simple string parsing is done to define this node's device and port, etc.

As the IF paths for the configuration are choosen and decisions about the frequencies along the path are made, this information is added to the IFPathNode objects, via the IFInfo, Bandpasses and Bandpass classes.

### Choosing IF Paths for the DCR

This happens in configureDCR:getDCRPaths()

The algorithm for choosing paths from a given receiver to the DCR for Continuum observations is fairly straightforward.  First, a path from the given receiver to the choosen backend is arbitraryly picked.

Note: the config tool does not seem to order the contents of the pickle file, so the arbitrary nature of this first IF path that is picked means that this code may not always pick the same path as the current config tool.  Note that here we *do* order our paths so that the first path choosen is at least deterministic.

Once this first path is choosen, the second path is choosen using the following criteria:

   * different polarization, or feed
   * different backend node
   * if IFXS node is used, make sure port (setting) is the same

That's it!

### Making frequency decisions along the paths

This happens in configureDCR:calcFreqs()

Here's where things get more complicated.  We need to understand better were some of the equations comes from for these decisions, but here's the rough outline:

   * if1 frequency are calculated. (if1 = (multiplier1 * (freqLocal - skyFreq) + ifNom))
   * NOTE: current code does NOT handle Doppler Shifts
   * receiver filter choices made.
   * LO1 mixing frequency calculated (if1 + restfreq)
   * Bandpasses set for receiver IFPathNode (filter and lo info from above)
   * IF rack filter choice made, with bandpasses for that IFPathNode updated
   * Parameters are set along the way   

## Manifest

A note on additional modules:

   * StaticDefs.py: stolen directly from config tool, a collection of python dictionaries with attributes of various receivers and other devices.
   * ifpaths.py: An original attempt at finding paths through the IF system.  Tests cover both DCR *and* VEGAS.  Uses graphviz and matplotlib.
   * iffreqs.py: An original attempt at reproducing frequency decisions made by the config tool.  Tests cover both DCR *and* VEGAS.  Uses ifpaths module, and relies on results from config tool's IF window collapse algorithm.