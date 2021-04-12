import time
import math
import keyboard
import ctypes
import tkinter
from tkinter.filedialog import askopenfilename
import osu_parser

def get_new_resolution():
    while True:
        try:
            x = int(input("\nX: "))
            y = int(input("Y: "))
        except ValueError:
            print("Insert an valid number.")
            continue

        if not (x >= 640 and y >= 480):
            print("Lowest possible resolution is 640x480. Please insert a valid one.")
            continue

        dif = (0.6 / 19) * y
        return (x, y, dif)

def busy_wait(duration):
    start = time.perf_counter()

    while (time.perf_counter() < start + duration):
        pass 

def move(path, duration, repeat, start, next_tracker):
    skip = duration / len(path) / 1000
    index = -1
    direction = -1

    for i in range(repeat):
        direction *= -1
        index += direction

        for point in path:
            ctypes.windll.user32.SetCursorPos(path[index][0], path[index][1])
            index += direction
            busy_wait(skip)

            if keyboard.is_pressed("s") or (time.perf_counter() - start) * 1000 >= next_tracker:
                return

def spin(duration, screen_x, screen_y, screen_dif):
    angle = 0
    end = time.perf_counter() + duration / 1000

    while end > time.perf_counter() and not keyboard.is_pressed("s"):
        x = int(math.cos(angle) * (screen_x * 0.025) + (screen_x / 2))
        y = int(math.sin(angle) * (screen_x * 0.025) + (screen_y + screen_dif) / 2)
    
        ctypes.windll.user32.SetCursorPos(x, y)
        angle += 1

def main():
    tkinter.Tk().withdraw()
    DT, HT = False, False
    LOADED = False
    f = None

    screen_x = ctypes.windll.user32.GetSystemMetrics(0)
    screen_y = ctypes.windll.user32.GetSystemMetrics(1)
    screen_dif = (0.6 / 19) * screen_y

    print(
        "Press L to load a map \n" \
        "Press P to start the map. " \
        "You can press S mid-map to stop. \n" \
        "Press D to toggle DT, H to toggle HT.\n" \
        "Press Q to change resolution manually.\n" \
        f"\nDT: {DT}   HT: {HT}\n{screen_x}x{screen_y}." 
    )

    while True:
        if keyboard.is_pressed("l"):
            beatmap = askopenfilename(filetypes=[("Osu files", "*.osu")])

            try:
                f = open(file=beatmap, mode="r", encoding="utf8")
            except FileNotFoundError:
                continue

            HOs = osu_parser.parse_HOs(f, DT, HT)
            osu_parser.convert_coordinates(HOs, screen_x, screen_y)
            print("Loaded successfully")

            LOADED = True

        elif keyboard.is_pressed("p") and LOADED:
            tracker = 0
            start = time.perf_counter()

            while len(HOs) > tracker and not keyboard.is_pressed("s"):
                if (time.perf_counter() - start) * 1000 >= HOs[tracker].offset - HOs[0].offset:
                    if HOs[tracker].obj == 1:
                        ctypes.windll.user32.SetCursorPos(HOs[tracker].x, HOs[tracker].y)
                    elif HOs[tracker].obj == 2:
                        try:
                            next_tracker = HOs[tracker + 1].offset - HOs[0].offset
                        except IndexError:
                            next_tracker = math.inf
                        move(HOs[tracker].path, HOs[tracker].duration, HOs[tracker].repeat, start, next_tracker)
                    else:
                        spin(HOs[tracker].end_offset - HOs[tracker].offset, screen_x, screen_y, screen_dif)

                    tracker += 1

        elif keyboard.is_pressed("d") or keyboard.is_pressed("h"):
            if keyboard.is_pressed("d"):
                DT = not DT
                if HT: HT = False
            elif keyboard.is_pressed("h"):
                HT = not HT
                if DT: DT = False

            if f is not None:
                HOs = osu_parser.parse_HOs(f, DT, HT)
                osu_parser.convert_coordinates(HOs, screen_x, screen_y)
 
            print(f"DT: {DT}   HT: {HT}")
            time.sleep(0.1)

        elif keyboard.is_pressed("q"):
            screen_x, screen_y, screen_dif = get_new_resolution()
            print(f"New resolution set to {screen_x}x{screen_y}")

if __name__ == "__main__":
    main()
