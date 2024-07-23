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


def parallel_batch_processing(tasks, batch_size, num_workers):
    batches = split_into_batches(tasks, batch_size=batch_size)
    print (batches)
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit one future per batch
        futures = [executor.submit(run_in_batch, process, batch) for batch in batches]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    return results


if __name__ == "__main__":
    tasks = [[i] for i in range(1000)]  # Example tasks
    batch_size = 10  # User-defined batch size
    num_workers = 100  # Number of workers
    duration = time.time()
    results = parallel_batch_processing(tasks, batch_size, num_workers)
    print(f"Duration: {time.time() - duration:.2f} seconds")
    # print(results)
