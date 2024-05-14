# Building Urban Analysis

A powerful urban building energy modeling (UBEM) tool for energy simulation, lca and Building Integrated Photovoltaic (BIPV) for python and Grasshopper.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Building Urban Analysis is a powerful urban building energy modeling (UBEM) tool for energy simulation, lca and Building Integrated Photovoltaic (BIPV) for python and Grasshopper. It is designed to help architects, engineers, and urban planners to analyze the energy performance of buildings and urban areas, and to optimize the design of buildings and urban areas for energy efficiency and sustainability.

## Features

- Energy simulation of buildings and urban areas
- Building Integrated Photovoltaic (BIPV) analysis
- Life Cycle Assessment (LCA) of BIPV at urban scale
- User-friendly interface for easy input and output in Grasshopper

## Getting Started

To get started with Building Urban Analysis, follow these steps:

### Prerequisites
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

Please refer to the documentation in the documentation folder to understand the logic and how to use the tool.

### Using Python 
Using the tool through Python enable further customization and automation of the tool, running many simulations at once, or performing parametric optimization. 

You can create you own scripts using the Building Urban Analysis package. No documentation is available yet, 
but you can check the examples in unit_test folder and run your scripts using the virtual environment created during the installation of the tool.

Even for python user, it will be recommended to use the Grasshopper interface for building modeling and plotting purposes.

### Using Grasshopper
The Grasshopper interface is a user-friendly way to use the tool. You can find the Grasshopper components in the Building Urban Analysis tab in Grasshopper. They should be installed and updated automatically with the installer/updater of the tool.


## Updating the package
To update the package you can run the BUA_updater.bat. This will download the last version of the package and install it. This file is available in the last release of the tool in GitHub.

## Contributing

We welcome contributions from the community! If you'd like to contribute to ChatBot-3000, please follow these guidelines:
- Fork the repository
- Create a new branch (`git checkout -b feature/foo`)
- Make your changes
- Commit your changes (`git commit -am 'Add new feature'`)
- Push to the branch (`git push origin feature/foo`)
- Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


