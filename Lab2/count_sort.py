def count_sort(arr):
    if len(arr) == 0:
        return []

    n = len(arr)
    max_value = max(arr)

    # count array
    count = [0] * (max_value + 1)

    # count frequencies
    for num in arr:
        count[num] += 1

    # prefix sums
    for i in range(1, max_value + 1):
        count[i] += count[i - 1]

    # output array
    result = [0] * n

    # go backwards to keep stability
    for i in range(n - 1, -1, -1):
        num = arr[i]
        pos = count[num] - 1
        result[pos] = num
        count[num] -= 1

    return result


if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    sorted_arr = count_sort(arr)

    print(sorted_arr)