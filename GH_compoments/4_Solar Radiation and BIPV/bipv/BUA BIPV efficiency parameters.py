"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "elie-medioni"
__version__ = "2023.09.06"


ghenv.Component.Name = "BUA BIPV Efficiency Computation Parameters"
ghenv.Component.NickName = 'BIPVEfficiencyComputationParameters'
ghenv.Component.Message = '0.0.0'
ghenv.Component.Category = 'BUA'
ghenv.Component.SubCategory = '4 :: Solar Radiation and BIPV'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

def clean_path(path):
    path = path.replace("\\", "/")
    return (path)

# Raise error if the compuattion method is not compatible with the BIPV type