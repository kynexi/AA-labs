def heap_sort(arr, left, right):
    yield from _heap_sort_helper(arr, left, right)

def _heap_sort_helper(arr, left, right):
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        yield from _heapify(arr, n, i)

    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        yield (arr[:], 0, end, -1, -1)
        yield from _heapify(arr, end, 0)

def _heapify(arr, size, index):
    largest = index
    left = 2 * index + 1
    right = 2 * index + 2

    if left < size and arr[left] > arr[largest]:
        largest = left

    if right < size and arr[right] > arr[largest]:
        largest = right

    if largest != index:
        arr[index], arr[largest] = arr[largest], arr[index]
        yield (arr[:], index, largest, -1, -1)
        yield from _heapify(arr, size, largest)


if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    heap_sort(arr)

    for value in arr:
        print(value, end=" ")