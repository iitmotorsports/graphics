import os
import re
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
LOGOS = ("Rectangle", "Square")
ORIGINAL_PATH = "Original"
OUTPUT = "Generated"

FILL_FORMAT = "fill:#{};"
FILL_TOKEN = "fill:#FFFFFF;"

ET.register_namespace("", "http://www.w3.org/2000/svg")  # Does this change?


class Color:
    def __init__(self, name: str, hex_code: str) -> None:
        super().__init__()
        self.name = name
        self.hex = hex_code

    def __str__(self) -> str:
        return f"{self.name} : #{self.hex}"


STD_COLORS = (
    Color("red", "CE1126"),
    Color("orange", "D97300"),
    Color("gold", "E89E00"),
    Color("gray", "6F7377"),
    Color("black", "231F20"),
    Color("white", "FFFFFF"),
    Color("transparent", "00000000"),
)

STD_SCHEME = (
    {
        "BG": STD_COLORS[5],
        "Logo": STD_COLORS[0],
        "Text": STD_COLORS[3],
    },
    {
        "BG": STD_COLORS[5],
        "Logo": STD_COLORS[0],
        "Text": STD_COLORS[4],
    },
    {
        "BG": STD_COLORS[0],
        "Logo": STD_COLORS[5],
        "Text": STD_COLORS[5],
    },
    {
        "BG": STD_COLORS[4],
        "Logo": STD_COLORS[0],
        "Text": STD_COLORS[0],
    },
    {
        "BG": STD_COLORS[4],
        "Logo": STD_COLORS[0],
        "Text": STD_COLORS[5],
    },
    {
        "BG": STD_COLORS[4],
        "Logo": STD_COLORS[5],
        "Text": STD_COLORS[5],
    },
    {
        "BG": STD_COLORS[5],
        "Logo": STD_COLORS[4],
        "Text": STD_COLORS[4],
    },
    {
        "BG": STD_COLORS[5],
        "Logo": STD_COLORS[3],
        "Text": STD_COLORS[3],
    },
    {
        "BG": STD_COLORS[5],
        "Logo": STD_COLORS[0],
        "Text": STD_COLORS[0],
    },
    {
        "BG": STD_COLORS[1],
        "Logo": STD_COLORS[4],
        "Text": STD_COLORS[4],
    },
    {
        "BG": STD_COLORS[4],
        "Logo": STD_COLORS[2],
        "Text": STD_COLORS[2],
    },
    {
        "BG": STD_COLORS[4],
        "Logo": STD_COLORS[1],
        "Text": STD_COLORS[1],
    },
)


def input_loop(text: str, options: tuple[str], show: bool = True, error_msg=None) -> str:
    options = [x for x in options]  # huh?
    while True:
        if show:
            text = f"{text} ({'/'.join(options)}) : "
        txt = input(text).lower()
        sel = None
        for i in options:
            if i.lower().startswith(txt):
                if sel or not txt:
                    if error_msg:
                        print(error_msg)
                    continue
                sel = i
        if sel:
            return sel
        if error_msg:
            print(error_msg)


def logo_select() -> str:
    print("Logo options:", str(LOGOS).strip("() ").replace("'", ""))
    while True:
        selected = input_loop("Type selection: ", LOGOS, False).title()

        if selected in LOGOS:
            print(f"Using {selected} Logo\n")
            break
        else:
            print("Invalid selection")

    return selected


def color_select() -> dict[str, Color]:
    color_map = STD_SCHEME[0]
    print("--[Color options]--\n", "\n".join(f"[{STD_COLORS.index(x)}] {str(x)}" for x in STD_COLORS), sep="")
    print("\nSelect color code: ")
    options = (str(x) for x in range(0, len(STD_COLORS)))
    for k in color_map:
        col = STD_COLORS[int(input_loop(f"{k}: ", options, False, "Select a number from the above colors where x in [x] is the number"))]
        color_map[k] = col
    return color_map


def gen_logo(parser: ET.ElementTree, selected: str, color_map: dict[str, Color], extra_text: str):
    root = parser.getroot()

    if extra_text:
        color_map["Subtext"] = color_map["Text"]

    for i in root:
        try:
            curr = re.findall(r"fill:#(.+?);", i.attrib["style"])[0]
            col = color_map[i.attrib["id"]].hex
            i.attrib["style"] = i.attrib["style"].replace(curr, col)
            if extra_text and i.attrib["id"] == "Subtext":
                i.text = extra_text
        except KeyError:
            pass

    bg_c = color_map["BG"].name
    fg_c = color_map["Logo"].name
    sd_c = color_map["Text"].name
    fgsd_c = f"{fg_c}_{sd_c}" if fg_c != sd_c else fg_c
    et_n = f"_{extra_text}" if extra_text else ""

    out = os.path.join(OUTPUT, f"IIT_Motorsports_Logo_{bg_c.title()}_{fgsd_c.title()}_{selected.title()}{et_n}.svg")
    parser.write(out)


def main():
    selected: str = logo_select()

    extra_text: str = input("Extra Text? (Blank for none): ")

    if extra_text:
        selected += "_Stacked"

    parser = ET.parse(os.path.join(ORIGINAL_PATH, f"{selected}.svg"))

    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)

    if input_loop("Generate default schemes?", ('yes', 'no')) == 'yes':
        if input_loop("Transparent BGs?", ('yes', 'no')) == 'yes':
            for scheme in STD_SCHEME:
                scheme["BG"] = STD_COLORS[6]
        for scheme in STD_SCHEME:
            gen_logo(parser, selected, scheme, extra_text)
    else:
        color_map: dict[str, Color] = color_select()
        gen_logo(parser, selected, color_map, extra_text)


main()
