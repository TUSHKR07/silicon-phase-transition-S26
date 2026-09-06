\# DFT based Study of Pressure-Driven Phase Transitions in Silicon. (this is still under construction)



This repository contains Density Functional Theory (DFT) calculation workflows and data processing scripts used to model the structural phase transition in Silicon from the ambient Diamond-Cubic phase to the high-pressure B-Tin Phase.



Project Overview:



Methods: First-principles calculations via Quantum ESPRESSO (PBE functional, pseudopotentials).

Calculations: Benchmarking Pseudopotentials, Enthalpy (H = E + PV) calculation across a range of hydrostatic pressure on both phases, equation of state (EOS) fitting, and electronic Band Structure with DOS calculations.

Analysis: Custom Python scripting using NumPy, SciPy, and Matplotlib for output file parsing, Birch-Murnaghan EOS fitting, and data visualization.



Repository Structure:

├── pseudopotential/  # Directory for storing pseudopotential .UPF files

├── input-templates/  # Input templates used for input generation

├── scripts/          # Python scripts for input generating, recursive running, output parsing, EOS fitting, and plotting

├── input-files/      # Generated input files are stored here

├── figures/          # plots generated using the parsed data

├── data/             # Processed energy-volume data and spectral/band logs

├── requirements.txt

├── .gitignore

└── README.md



