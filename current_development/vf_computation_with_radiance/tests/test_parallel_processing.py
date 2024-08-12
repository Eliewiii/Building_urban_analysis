"""
Test file for the parallel processing functions.
"""
from time import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils.utils_parallel_computing_with_return import parallel_computation_in_batches_with_return
from current_development.vf_computation_with_radiance.vf_computation_with_radiance.utils.utils_parallel_computing import parallel_computation_in_batches


def test_parallel_computation_in_batches_with_return():
    def add(a, b):
        return a + b

    def generate_random_int_pairs(n):
        return [[i, i + 1] for i in range(n)]

    n_pair = 100
    input_data = generate_random_int_pairs(n_pair)
    duration = time()
    results = parallel_computation_in_batches_with_return(add, input_data, batch_size=2, num_workers=2)
    print("")
    print(f"Duration for {n_pair} : {time() - duration}")
    n_pair = 1000
    input_data = generate_random_int_pairs(n_pair)
    duration = time()
    results = parallel_computation_in_batches_with_return(add, input_data, batch_size=2, num_workers=2)
    print(f"Duration for {n_pair} : {time() - duration}")


def add(a, b):
    return a + b

def generate_random_int_pairs(n):
    return [[i, i + 1] for i in range(n)]

def test_parallel_computation_in_batches_with_return_compare_thread_and_processes():


    batch_size_list = [1000000]
    num_worker_list = [8]

    n_pair_list = [10000000]
    for n_pairs in n_pair_list:

        input_data = generate_random_int_pairs(n_pairs)
        for num_worker in num_worker_list:
            for batch_size in batch_size_list:
                # Threads
                duration = time()
                results = parallel_computation_in_batches_with_return(add, input_data, batch_size=batch_size,
                                                                      num_workers=num_worker, executor_type=ThreadPoolExecutor)
                print("")
                print(f"Threading Duration for n_pair={n_pairs},batch_size={batch_size} and num_worker={num_worker} : {time() - duration}")
                # Processes
                duration = time()
                results = parallel_computation_in_batches_with_return(add, input_data, batch_size=batch_size,
                                                                      num_workers=num_worker, executor_type=ProcessPoolExecutor)
                print(f"Processing Duration for n_pair={n_pairs},batch_size={batch_size} and num_worker={num_worker} : {time() - duration}")


def test_parallel_computation_in_batches():
    def add(a, b):
        return a + b

    input_data = [[1, 2], [3, 4], [5, 6], [7, 8]]
    parallel_computation_in_batches(add, input_data, batch_size=2, num_workers=2)
