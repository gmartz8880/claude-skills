"""Desktop logic tests for a calculator app. Copy to <app>/tests/test_logic.py.
Mirror the app's math in plain Python functions and check the spec's test cases.
Run: python tests/test_logic.py   (exit 0 = all pass)"""
import math, sys

def circle_area(r):                 # mirror of the calculator code
    if r <= 0:
        raise ValueError("radius must be > 0")
    return round(math.pi * r * r, 6)

CASES = [  # (input, expected) - copy from the spec
    (1, 3.141593),
    (2.5, 19.634954),
]

def main():
    bad = 0
    for x, want in CASES:
        got = circle_area(x)
        ok = abs(got - want) < 1e-6
        bad += not ok
        print(("PASS" if ok else "FAIL"), x, "->", got, "expected", want)
    try:
        circle_area(0); print("FAIL 0 should be rejected"); bad += 1
    except ValueError:
        print("PASS 0 rejected")
    print("ALL PASS" if not bad else f"{bad} FAILED")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
