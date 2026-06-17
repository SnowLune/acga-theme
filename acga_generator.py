# quick and dirty script to modify a palette to meet a contrast requirement
# Let's remember how to write python, it's been a whileee

# take a palette, assign a background color, calculate contrast for all
#  colors against background color, if too low increase color brightness
#  brightness, if color brightness max and contrast still not high enough
#  increase others colors by 1, repeat, return new palette

import wcag_contrast_ratio as contrast 

def hex_to_percent(hexrgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r = hexrgb[0] / 255.0
    g = hexrgb[1] / 255.0
    b = hexrgb[2] / 255.0
    return (r, g, b)

WCAG_AA =   4.5
WCAG_AAA =  7
UINT8 = 0xFF
RGB_CHANNELS = [0, 1, 2]

class Color:
    def __init__(self,
                 rgb: tuple[int, int, int],
                 ansi_value: int,
                 rgbi_value: int,
                 primary_channels: list[int],
    ):
        self.rgb = rgb
        self.ansi_value = ansi_value
        self.rgbi_value = rgbi_value
        self.primary_channels = primary_channels
        self.secondary_channels = list(
            set(RGB_CHANNELS) - set(self.primary_channels))
        self.contrast_ratio = 0.0

NORMAL_COLORS = {
    "black":    Color((0x00, 0x00, 0x00), 0, 0, [0, 1, 2]), 
    "blue":     Color((0x00, 0x00, 0xAA), 4, 1, [2]),
    "green":    Color((0x00, 0xAA, 0x00), 2, 2, [1]),
    "cyan":     Color((0x00, 0xAA, 0xAA), 6, 3, [1, 2]),
    "red":      Color((0xAA, 0x00, 0x00), 1, 4, [0]),
    "magenta":  Color((0xAA, 0x00, 0xAA), 5, 5, [0, 2]),
    "yellow":   Color((0xAA, 0x55, 0x00), 3, 6, [0, 1]),
    "white":    Color((0xAA, 0xAA, 0xAA), 7, 7, [0, 1, 2])
}

INTENSE_COLORS = {
    "intense_black":    Color((0x55, 0x55, 0x55), 8, 8, [0, 1, 2]),
    "intense_blue":     Color((0x55, 0x55, 0xFF), 12, 9, [2]),
    "intense_green":    Color((0x55, 0xFF, 0x55), 10, 10, [1]),
    "intense_cyan":     Color((0x55, 0xFF, 0xFF), 14, 11, [1, 2]),
    "intense_red":      Color((0xFF, 0x55, 0x55), 9, 12, [0]),
    "intense_magenta":  Color((0xFF, 0x55, 0xFF), 13, 13, [0, 2]),
    "intense_yellow":   Color((0xFF, 0xFF, 0x55), 11, 14, [0, 1]),
    "intense_white":    Color((0xFF, 0xFF, 0xFF), 15, 15, [0, 1, 2]) 
}

RGBI_PALETTE = {**NORMAL_COLORS, **INTENSE_COLORS}

def check_contrast(
        fg_rgb24: tuple[int, int, int],
        bg_rgb24: tuple[int, int, int]
):
    fg1 = hex_to_percent(fg_rgb24)
    bg1 = hex_to_percent(bg_rgb24)
    contrast_ratio = contrast.rgb(fg1, bg1)
    return contrast_ratio

# modify an RGB tuple
def modify_rgb(
        rgb: tuple[int, int, int],
        channels: list[int],
        direction: int
):
    rgb_list = list(rgb)

    for channel in channels:
        rgb_list[channel] += direction

    for i in range(len(rgb_list)):
        # clamp
        rgb_list[i] = max(0, rgb_list[i])
        rgb_list[i] = min(UINT8, rgb_list[i])

    return tuple(rgb_list)

def main():

    bg_rgb24 = RGBI_PALETTE["intense_white"].rgb
    print(f"background: {bg_rgb24}")


    for color_name, color in RGBI_PALETTE.items():
        # Calculate contrast
        color.contrast_ratio = check_contrast(color.rgb, bg_rgb24)

        # Increase or decrease color amplitude depending on background color
        if bg_rgb24 == RGBI_PALETTE["intense_white"].rgb:
            direction = -1
        else:
            direction = 1

        # Skip if same as background color
        if color.rgb == bg_rgb24:
            continue

        ratio_requirement = (
                WCAG_AAA if color_name in INTENSE_COLORS else WCAG_AA)

        # Messy handling of bright black
        if (color_name == "intense_black" 
                and bg_rgb24 == RGBI_PALETTE["black"].rgb
        ):
            color.contrast_ratio = 0
            color.rgb = bg_rgb24
            ratio_requirement = WCAG_AA


        while color.contrast_ratio < ratio_requirement:
            if direction == -1 and all(color.rgb[c] == 0 for c in color.secondary_channels):
                channels_to_modify = color.primary_channels
            elif direction == -1:
                channels_to_modify = color.secondary_channels
            elif direction == 1 and all(color.rgb[c] >= UINT8 for c in color.primary_channels):
                channels_to_modify = color.secondary_channels
            else:
                channels_to_modify = color.primary_channels
            color.rgb = modify_rgb(color.rgb, channels_to_modify, direction)
            color.contrast_ratio = check_contrast(color.rgb, bg_rgb24)

        RGBI_PALETTE[color_name].rgb = color.rgb        

    for color_name, color in RGBI_PALETTE.items():
        print(f"\033[48;2;{bg_rgb24[0]};{bg_rgb24[1]};{bg_rgb24[2]}m\033[38;2;{color.rgb[0]};{color.rgb[1]};{color.rgb[2]}m{color_name:>16} #{color.rgb[0]:02X}{color.rgb[1]:02X}{color.rgb[2]:02X}{color.contrast_ratio:>12.8f}\033[0m")

if __name__=="__main__":
    main()    
