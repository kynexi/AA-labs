def quick_sort(arr, left, right):
    yield from _quick_sort_helper(arr, left, right)

def _quick_sort_helper(arr, left, right):
    if left < right:
        pivot_index = yield from _partition(arr, left, right)
        yield from _quick_sort_helper(arr, left, pivot_index - 1)
        yield from _quick_sort_helper(arr, pivot_index + 1, right)

def _partition(arr, left, right):
    pivot = arr[right]
    smaller_index = left - 1

    for current in range(left, right):
        if arr[current] <= pivot:
            smaller_index += 1
            arr[smaller_index], arr[current] = arr[current], arr[smaller_index]
            yield (arr[:], smaller_index, current, -1, -1)

    arr[smaller_index + 1], arr[right] = arr[right], arr[smaller_index + 1]
    yield (arr[:], smaller_index + 1, right, -1, -1)
    return smaller_index + 1

if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    quick_sort(arr, 0, len(arr) - 1)

    for x in arr:
        print(x, end=" ")