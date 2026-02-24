import random
import time
import matplotlib.pyplot as plt

from algorithms.merge_sort import merge_sort
from algorithms.quick_sort import quick_sort
from algorithms.heap_sort import heap_sort
from algorithms.count_sort import count_sort

input_sizes = [100, 1000, 5000, 10000, 25000, 50000, 100000]

results = {
    "Merge Sort": [],
    "Quick Sort": [],
    "Heap Sort": [],
    "Counting Sort": []
}


def test_algorithm(sort_func, arr):
    start_time = time.time()
    sort_func(arr)
    end_time = time.time()
    return end_time - start_time


for size in input_sizes:
    base_array = [random.randint(0, 1_000_000) for _ in range(size)]

    results["Merge Sort"].append(
        test_algorithm(lambda a: merge_sort(a, 0, len(a)-1), base_array.copy())
    )

    results["Quick Sort"].append(
        test_algorithm(lambda a: quick_sort(a, 0, len(a)-1), base_array.copy())
    )

    results["Heap Sort"].append(
        test_algorithm(heap_sort, base_array.copy())
    )

    results["Counting Sort"].append(
        test_algorithm(count_sort, base_array.copy())
    )


for algo, times in results.items():
    print(f"\n{algo}:")
    for size, t in zip(input_sizes, times):
        print(f"size of {size}: {t:.6f} sec")


for algo, times in results.items():
    plt.plot(input_sizes, times, marker='o', label=algo)

plt.title("Runtime Comparison")
plt.xlabel("Array Size")
plt.ylabel("Time (seconds)")
plt.legend()
plt.grid()
plt.show()


for algo, times in results.items():
    plt.figure()
    plt.plot(input_sizes, times, marker='o')
    plt.title(f"{algo} Runtime")
    plt.xlabel("Array Size")
    plt.ylabel("Time (seconds)")
    plt.ylim(0, 0.5) 
    plt.grid()
    plt.show()