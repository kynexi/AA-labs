def merge_sort(arr, left, right):
    yield from _merge_sort_helper(arr, left, right)

def _merge_sort_helper(arr, left, right):
    if left < right:
        mid = (left + right) // 2
        yield from _merge_sort_helper(arr, left, mid)
        yield from _merge_sort_helper(arr, mid + 1, right)
        yield from _merge_helper(arr, left, mid, right)

def _merge_helper(arr, left, mid, right):
    left_size = mid - left + 1
    right_size = right - mid

    left_half = [0] * left_size
    right_half = [0] * right_size

    for i in range(left_size):
        left_half[i] = arr[left + i]
    for j in range(right_size):
        right_half[j] = arr[mid + 1 + j]

    i = 0
    j = 0
    k = left

    while i < left_size and j < right_size:
        if left_half[i] <= right_half[j]:
            arr[k] = left_half[i]
            i += 1
        else:
            arr[k] = right_half[j]
            j += 1
        yield (arr[:], k-1, k, -1, -1)
        k += 1

    while i < left_size:
        arr[k] = left_half[i]
        yield (arr[:], k-1, k, -1, -1)
        i += 1
        k += 1

    while j < right_size:
        arr[k] = right_half[j]
        yield (arr[:], k-1, k, -1, -1)
        j += 1
        k += 1


if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    merge_sort(arr, 0, len(arr) - 1)

    for num in arr:
        print(num, end=" ")
    print()