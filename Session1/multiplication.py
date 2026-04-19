"""Multiplication table generator.

This script reads an integer from the user and prints its multiplication table
from 1 through 10.
"""


num = int(input("Enter a number: "))

for i in range(1, 11):
    print(f"{num} x {i} = {num * i}")