"""Number comparison utilities.

This module defines helper functions for finding the largest and smallest
values in a numeric sequence, followed by a simple example execution block.
"""


def find_largest(numbers):
    """Return the largest value from a sequence of numbers.

    Args:
        numbers: A sequence of comparable numeric values.

    Returns:
        The largest value, or None if the sequence is empty.
    """
    if not numbers:
        return None

    largest = numbers[0]
    for num in numbers:
        if num > largest:
            largest = num
    return largest


def find_smallest(numbers):
    """Return the smallest value from a sequence of numbers.

    Args:
        numbers: A sequence of comparable numeric values.

    Returns:
        The smallest value, or None if the sequence is empty.
    """
    if not numbers:
        return None

    smallest = numbers[0]
    for num in numbers:
        if num < smallest:
            smallest = num
    return smallest


nums = [10, 45, 23, 67, 12]

print("Largest number is:", find_largest(nums))
print("Smallest number is:", find_smallest(nums))