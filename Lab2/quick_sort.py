# partition function
def partition(arr, left, right):
    pivot = arr[right]  # last element as pivot
    
    smaller_index = left - 1

    # go through the array
    for current in range(left, right):
        if arr[current] <= pivot:
            smaller_index += 1
            swap(arr, smaller_index, current)

    # place pivot in correct position
    swap(arr, smaller_index + 1, right)
    return smaller_index + 1

# swap helper
def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]

# quicksort function
def quick_sort(arr, left, right):
    if left < right:
        pivot_index = partition(arr, left, right)

        # sort left part
        quick_sort(arr, left, pivot_index - 1)

        # sort right part
        quick_sort(arr, pivot_index + 1, right)

if __name__ == "__main__":
    arr = [38, 27, 43, 10]

    quick_sort(arr, 0, len(arr) - 1)

    for x in arr:
        print(x, end=" ")