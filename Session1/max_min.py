def find_largest(numbers):
    if not numbers:
        return None
    
    largest = numbers[0]
    for num in numbers:
        if num > largest:
            largest = num
    return largest


def find_smallest(numbers):
    if not numbers:
        return None
    
    smallest = numbers[0]
    for num in numbers:
        if num < smallest:
            smallest = num
    return smallest


# Example usage
nums = [10, 45, 23, 67, 12]

print("Largest number is:", find_largest(nums))
print("Smallest number is:", find_smallest(nums))