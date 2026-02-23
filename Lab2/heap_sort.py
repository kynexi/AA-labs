# fix heap at a given index
def heapify(arr, size, index):
    largest = index

    left = 2 * index + 1
    right = 2 * index + 2

    # check left child
    if left < size and arr[left] > arr[largest]:
        largest = left

    # check right child
    if right < size and arr[right] > arr[largest]:
        largest = right

    # if root is not the largest, swap
    if largest != index:
        arr[index], arr[largest] = arr[largest], arr[index]

        # fix the affected subtree
        heapify(arr, size, largest)


# heap sort function
def heap_sort(arr):
    n = len(arr)

    # build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # extract elements one by one
    for end in range(n - 1, 0, -1):
        # move max element to the end
        arr[0], arr[end] = arr[end], arr[0]

        # rebuild heap with reduced size
        heapify(arr, end, 0)


if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    heap_sort(arr)

    for value in arr:
        print(value, end=" ")