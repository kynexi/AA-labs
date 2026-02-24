def count_sort(arr, left, right):
    yield from _count_sort_helper(arr)

def _count_sort_helper(arr):
    if len(arr) == 0:
        return

    n = len(arr)
    max_value = max(arr)

    count = [0] * (max_value + 1)

    for num in arr:
        count[num] += 1

    for i in range(1, max_value + 1):
        count[i] += count[i - 1]

    result = [0] * n

    for i in range(n - 1, -1, -1):
        num = arr[i]
        pos = count[num] - 1
        result[pos] = num
        count[num] -= 1
        yield (result[:], pos, -1, -1, -1)

    for i in range(n):
        arr[i] = result[i]
        yield (arr[:], i, -1, -1, -1)


if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    sorted_arr = count_sort(arr)

    print(sorted_arr)