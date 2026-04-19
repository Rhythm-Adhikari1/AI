"""Grade classification script.

This module accepts a student's marks as input and assigns a letter grade
based on a fixed percentage scale.
"""


marks = float(input("Enter student's marks: "))

if marks >= 90:
    grade = "A"
elif marks >= 80:
    grade = "B"
elif marks >= 70:
    grade = "C"
elif marks >= 60:
    grade = "D"
else:
    grade = "Fail"

print("Grade:", grade)