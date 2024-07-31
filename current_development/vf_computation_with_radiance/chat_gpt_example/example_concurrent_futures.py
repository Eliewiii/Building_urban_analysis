import concurrent.futures
import subprocess
import os
from threading import Lock


# Assume generate_radiance_command is defined as follows:
def generate_radiance_command(rad_file1, rad_file2, output_file):
    return f"rad -o {output_file} {rad_file1} {rad_file2}"


def run_radiance_command(rad_pair, output_dir, lock):
    rad_file1, rad_file2 = rad_pair
    output_file = os.path.join(output_dir, f"{os.path.basename(rad_file1)}_{os.path.basename(rad_file2)}.txt")
    command = generate_radiance_command(rad_file1, rad_file2, output_file)

    with lock:  # Ensure thread-safe access if needed
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Completed: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {command}: {e}")


def process_view_factors(rad_file_pairs, output_dir, num_workers):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a lock for thread safety
    lock = Lock()

    # with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit tasks and collect futures
        futures = [executor.submit(run_radiance_command, pair, output_dir, lock) for pair in rad_file_pairs]

        # Collect results and handle exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # This will raise an exception if the task failed
            except Exception as e:
                print(f"Task generated an exception: {e}")


# Example usage
if __name__ == "__main__":
    rad_file_pairs = [
        ("path/to/rad1a.rad", "path/to/rad1b.rad"),
        ("path/to/rad2a.rad", "path/to/rad2b.rad"),
        # Add more pairs as needed
    ]
    output_dir = "path/to/output"
    num_workers = 4  # Adjust this based on your system's capabilities

    process_view_factors(rad_file_pairs, output_dir, num_workers)
