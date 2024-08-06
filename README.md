# Building Urban Analysis

A powerful urban building energy modeling (UBEM) tool for energy simulation, lca and Building Integrated Photovoltaic (BIPV) for python and Grasshopper. Available for now on Windows only.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)

  - [Updating the package](#updating-the-package)
- [Usage](#usage)
  - [Using Python](#using-python)
  - [Using Grasshopper](#using-grasshopper)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

## Introduction

Building Urban Analysis is a powerful urban building energy modeling (UBEM) tool for energy simulation, Life Cycle Assessment (LCA) and Building Integrated Photovoltaic (BIPV) for python and Grasshopper. 
It is designed to help architects, engineers, and urban planners to analyze the energy performance of buildings and urban areas, and to optimize the design of buildings and urban areas for energy efficiency and sustainability.

The tool used the LadybugTools (Ladybug, Honeybee and Dragonfly) objects and functions, and should be used alongside these tools and Grasshopper components.

## Features

- Energy simulation of buildings and urban areas
- Building Integrated Photovoltaic (BIPV) analysis
- Life Cycle Assessment (LCA) of BIPV at urban scale
- User-friendly interface for easy input and output in Grasshopper
- Compatibility with LadybugTools (Ladybug, Honeybee, Dragonfly)
- Python use only for advanced users (automation, parametric optimization, etc.)

## Getting Started

To get started with Building Urban Analysis, follow these steps:

### Prerequisites
- Windows 10/11
- Rhino 7 or 8 (if you plan to use the Grasshopper interface)
- Polination for Grasshopper (that can be downloaded from [here](https://www.pollination.cloud/grasshopper-plugin))


### Installation

1. Open the page of the last release of Building_Urban_Analysis in GitHub
2. Download the BUA_installer.bat
3. run the BUA_installer.bat

You will need to accept the first popups from Python for its installation.

You might encounter some additional popups from python, just close the windows. If the installation failed you can run 
the BUA_installer.bat again. 

## Usage

Please refer to the documentation in the documentation folder or in the additional documents of the last release to understand the logic and how to use the tool.

### Using Python 
Using the tool through Python enable further customization and automation of the tool, running many simulations at once, or performing parametric optimization. 

You can create you own scripts using the Building Urban Analysis package. No documentation is available yet, 
but you can check the examples in unit_test folder and run your scripts using the virtual environment created during the installation of the tool.

Even for python user, it will be recommended to use the Grasshopper interface for building modeling and plotting purposes.

### Using Grasshopper
The Grasshopper interface is a user-friendly way to use the tool. You can find the Grasshopper components in the Building Urban Analysis tab in Grasshopper. They should be installed and updated automatically with the installer/updater of the tool.
If you cannot see the components, you can try to restart Rhino and Grasshopper.

You can find example files .


## Updating the package
To update the package you can run the BUA_updater.bat. This will download the last version of the package and install it. This file is available in the last release of the tool in GitHub.

## Contributing

We welcome contributions from the community!

We are not yet ready to accept contributions in standard ways, but we will be soon.

If you have any questions or suggestions, please feel free to open an issue or contact us at elie-medioni@campus.technion.ac.il 

## Credits
This tool was created by Elie Medioni as part of his PhD research at the Technion - Israel Institute of Technology, under the supervision of Prof. Sabrina Spatari and Ass. Prof. Abraham Yezioro.

The project was funded by the Israeli Ministry of Energy in order to develop methods and guidance for BIPV deployments 
in new or existing residential neighborhood in urban areas.

Thank you to Hilany Yelloz and Julius Jandl for their contribution to the project.

## License
