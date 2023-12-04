"""
This script shows how to add the directory of EnergyPlus to the PATH variable temporarily and then remove
it from the path.
"""

import os

# Assuming the path to EnergyPlus executable
energyplus_path = r'C:\energyplus23'

# Get the current PATH variable
original_path = os.environ.get('PATH', '')

# Remove existing energyplus directories from PATH if present
existing_energyplus_dirs = [dir_path for dir_path in original_path.split(os.pathsep) if 'energyplus' in dir_path.lower()]
for existing_dir in existing_energyplus_dirs:
    original_path = original_path.replace(existing_dir + os.pathsep, '')  # Remove directory and separator

try:
    # Append the EnergyPlus directory to the PATH using os.pathsep
    os.environ['PATH'] = f'{original_path}{os.pathsep}{energyplus_path}'
    print(os.environ['PATH'])

    # Your other code here...

except Exception as e:
    # Handle exceptions if needed
    print(f"An error occurred: {e}")

finally:
    # Revert the PATH to its original state, even if an error occurred
    os.environ['PATH'] = original_path
    print(os.environ['PATH'])