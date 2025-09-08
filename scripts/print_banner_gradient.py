import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def gradient(text, start_color, end_color):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    lines = text.splitlines()
    n = len(lines)
    for i, line in enumerate(lines):
        ratio = i / max(n-1, 1)
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        print(f'\033[38;2;{r};{g};{b}m{line}\033[0m')


if __name__ == "__main__":
    with open("banner.txt") as f:
        banner = f.read()
    gradient(banner, "#b266ff", "#00e6e6")
    