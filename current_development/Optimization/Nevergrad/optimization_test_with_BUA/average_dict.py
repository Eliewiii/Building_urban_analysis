"""
Function to compute the average of a list of dictionaries with identical structures.
"""

from typing import List

def average_dicts(dict_list: List[dict]) -> dict:
    """
    Compute the average of a list of dictionaries with identical structures.

    """
    def recursive_average(dicts: List[dict]) -> dict:
        """
        Recursively compute the average of a list of dictionaries.
        """
        if not dicts:
            return {}

        # Initialize the result dictionary
        result = {}

        # Get keys from the first dictionary (assuming all dicts have identical structures)
        keys = dicts[0].keys()

        for key in keys:
            # Extract all values for the current key
            values = [d[key] for d in dicts]

            # Check if values are dictionaries themselves
            if all(isinstance(v, dict) for v in values):
                # Recurse for nested dictionaries
                result[key] = recursive_average(values)
            elif all(isinstance(v, (int, float)) for v in values):
                # Compute the average for the current key
                result[key] = sum(values) / len(values)
            else:
                # If the values are not all numerical, return the first value
                result[key] = None

        return result

    return recursive_average(dict_list)


if __name__ == "__main__":

    # Example usage
    dict1 = {
        'a': {'x': 1, 'y': 2},
        'b': {'z': 3}
    }
    dict2 = {
        'a': {'x': 3, 'y': 4},
        'b': {'z': 6}
    }
    dict3 = {
        'a': {'x': 5, 'y': 6},
        'b': {'z': 9}
    }

    average = average_dicts([dict1, dict2, dict3])
    print(average)
