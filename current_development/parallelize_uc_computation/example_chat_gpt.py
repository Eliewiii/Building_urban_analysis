import threading
import os
from functools import wraps

folder_creation_lock = threading.Lock()

def synchronized_folder_creation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with folder_creation_lock:
            return func(*args, **kwargs)
    return wrapper

@synchronized_folder_creation
def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

class Building:
    def __init__(self, identifier, folder_path):
        self.identifier = identifier
        self.attribute = 0
        self.folder_path = folder_path

    def perform_computation(self, uc_value):
        # Ensure the folder exists before performing computations
        ensure_folder_exists(self.folder_path)

        # Perform the computation
        result = self.attribute + uc_value
        self.attribute = result
        print(f"Building {self.identifier} computed attribute: {self.attribute} using uc_value: {uc_value}")


class UC:
    def __init__(self, folder_path):
        self.buildings = {}
        self.lock = threading.Lock()
        self.shared_value = 10
        self.folder_path = folder_path

    def add_building(self, identifier, building):
        with self.lock:
            self.buildings[identifier] = building

    def process_buildings(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            with self.lock:
                for building in self.buildings.values():
                    futures.append(executor.submit(building.perform_computation, self.shared_value))
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Task generated an exception: {e}")


# Example usage
if __name__ == "__main__":
    folder_path = "shared_folder"
    uc = UC(folder_path)

    for i in range(5):
        uc.add_building(f"building_{i}", Building(f"building_{i}", folder_path))

    uc.process_buildings()
