import concurrent.futures
import time


def split_into_batches(input_table: [list], batch_size):
    """
    Split multiple lists of data into batches of a specified size
    """
    num_items = len(input_table)
    if num_items < batch_size:
        return [input_table]
    # Create batches for each list
    batches = []
    for start in range(0, num_items, batch_size):
        end = min(start + batch_size, num_items)
        batch = input_table[start: end]
        batches.append(batch)
    return batches


def process(task):
    # Process a single task
    time.sleep(0.1)
    # print(f"Processed task {task}")


def run_in_batch(func, batch_input):
    """

    """
    for input in batch_input:
        func(input)
    print("batch done")


def radiant_vf_parallel_computation(input_tables:[list],nb_rays: int = 10000, command_batch_size:int=1, batch_size:int = 10, num_workers:int=4):
    """
    Computes view factors in parallel with Radiance.
    :param input_tables: [list], tables of input data. Respectivelly [path_emitter_rad_file, path_receiver_rad_file, path_output_file, path_octree_context]
    :param nb_rays: int, the number of rays to use.
    :param command_batch_size: int, number of Radiant command to run within the same terminal call.
    :param batch_size: int, the size of the batch for each worker.
    :param num_workers: int, the number of workers.
    """
    input_batches = split_into_batches(input_tables, batch_size=batch_size)
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
    # with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit one future per batch
        futures = [executor.submit(run_in_batch, process, batch) for batch in input_batches]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return results

#
# if __name__ == "__main__":
#     tasks = [[i] for i in range(1000)]  # Example tasks
#     batch_size = 10  # User-defined batch size
#     num_workers = 100  # Number of workers
#     duration = time.time()
#     results = parallel_batch_processing(tasks, batch_size, num_workers)
#     print(f"Duration: {time.time() - duration:.2f} seconds")
#     # print(results)
