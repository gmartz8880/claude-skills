# TI-84 Plus CE Python Edition app skeleton (Python app 5.x)
# Battery : uses the blocking ti_system.wait_key() so the CPU is not spinning while you think.
# Stability: input is validated, all errors are caught and explained, [clear] always exits.
# Snappy  : plain text screens, no heavy imports, results computed once.
# Note    : the CE Python heap is small (tens of KB) - keep lists short, avoid big strings.
try:
    from ti_system import disp_clr, wait_key
    ON_CALC = True
except ImportError:
    ON_CALC = False
    def disp_clr():
        print("\n" * 2)
    def wait_key():
        return 0

import math

TITLE = "MY CE PY APP V1.0"


def ask_float(prompt, minimum=None):
    while True:
        try:
            v = float(input(prompt))
            if minimum is not None and v <= minimum:
                print("Must be >", minimum)
                continue
            return v
        except ValueError:
            print("Numbers only.")


def run():
    while True:
        disp_clr()
        print(TITLE)
        print("1:Circle area")
        print("2:Help")
        print("3:Quit")
        c = input("Pick 1-3: ").strip()
        if c == "1":
            r = ask_float("Radius: ", 0)
            print("Area =", round(math.pi * r * r, 6))
            print("[any key] menu")
            wait_key()
        elif c == "2":
            print("Type a number, press enter.")
            print("[any key] menu")
            wait_key()
        elif c == "3":
            return


try:
    run()
except KeyboardInterrupt:                 # [on] key break
    pass
except Exception as e:
    print("Error:", e)
