from pathlib import Path

import gdstk


CELL_NAME = "branding"
TEXT_LINES = ("Toxic x Crash <3", "Phoenix-V2")
ART_LAYER, ART_DATATYPE = 71, 20
BOUNDARY_LAYER, BOUNDARY_DATATYPE = 235, 4
CELL_WIDTH, CELL_HEIGHT = 46, 16
TEXT_MARGIN = 2
PIXEL_SIZE = 0.75
PIXEL_GAP = 0
CHAR_GAP = 0.4
TEXT_LINE_GAP = 4
FONT = {
    "T": ("111", "010", "010", "010", "010"),
    "C": ("011", "100", "100", "100", "011"),
    "P": ("110", "101", "110", "100", "100"),
    "V": ("101", "101", "101", "101", "010"),
    "a": ("010", "101", "111", "101", "101"),
    "c": ("000", "011", "100", "100", "011"),
    "e": ("000", "010", "101", "110", "011"),
    "h": ("100", "100", "110", "101", "101"),
    "i": ("010", "000", "010", "010", "010"),
    "n": ("000", "110", "101", "101", "101"),
    "o": ("000", "010", "101", "101", "010"),
    "r": ("000", "101", "110", "100", "100"),
    "s": ("011", "100", "010", "001", "110"),
    "t": ("010", "111", "010", "010", "001"),
    "x": ("000", "101", "010", "010", "101"),
    "<": ("001", "010", "100", "010", "001"),
    "2": ("110", "001", "010", "100", "111"),
    "3": ("110", "001", "010", "001", "110"),
    "-": ("000", "000", "111", "000", "000"),
}

OUTPUT_DIR = Path(__file__).resolve().parent


def write_lef(filename, cell_name, width, height):
    with open(filename, "w", encoding="ascii") as lef:
        lef.write(f"# LEF file generated for {cell_name}\n")
        lef.write("VERSION 5.8 ;\n")
        lef.write("NAMESCASESENSITIVE ON ;\n")
        lef.write('DIVIDERCHAR "/" ;\n')
        lef.write('BUSBITCHARS "[]" ;\n')
        lef.write("UNITS\n")
        lef.write("   DATABASE MICRONS 1000 ;\n")
        lef.write("END UNITS\n\n")
        lef.write(f"MACRO {cell_name}\n")
        lef.write("   CLASS BLOCK ;\n")
        lef.write(f"   FOREIGN {cell_name} 0 0 ;\n")
        lef.write(f"   SIZE {width:.3f} BY {height:.3f} ;\n")
        lef.write("   SYMMETRY X Y ;\n")
        lef.write("   OBS\n")
        lef.write("      LAYER met4 ;\n")
        lef.write(f"         RECT 0 0 {width:.3f} {height:.3f} ;\n")
        lef.write("   END\n")
        lef.write(f"END {cell_name}\n")


def add_pixel_text(cell, line, x, y):
    unknown_chars = set(line) - set(FONT) - {" "}
    if unknown_chars:
        raise ValueError(f"Unsupported logo characters: {sorted(unknown_chars)}")

    char_advance = 3 * (PIXEL_SIZE + PIXEL_GAP) + CHAR_GAP
    for char_index, char in enumerate(line):
        if char == " ":
            continue
        char_x = x + char_index * char_advance
        for row_index, row in enumerate(FONT[char]):
            for column_index, pixel in enumerate(row):
                if pixel == "1":
                    pixel_x = char_x + column_index * (PIXEL_SIZE + PIXEL_GAP)
                    pixel_y = y + (4 - row_index) * (PIXEL_SIZE + PIXEL_GAP)
                    cell.add(
                        gdstk.rectangle(
                            (pixel_x, pixel_y),
                            (pixel_x + PIXEL_SIZE, pixel_y + PIXEL_SIZE),
                            layer=ART_LAYER,
                            datatype=ART_DATATYPE,
                        )
                    )


def main():
    library = gdstk.Library()
    cell = library.new_cell(CELL_NAME)
    cell.add(
        gdstk.rectangle(
            (0, 0),
            (CELL_WIDTH, CELL_HEIGHT),
            layer=BOUNDARY_LAYER,
            datatype=BOUNDARY_DATATYPE,
        )
    )

    char_advance = 3 * (PIXEL_SIZE + PIXEL_GAP) + CHAR_GAP
    text_width = max(len(line) * char_advance - CHAR_GAP for line in TEXT_LINES)
    line_height = 5 * PIXEL_SIZE + 4 * PIXEL_GAP
    text_height = len(TEXT_LINES) * line_height + TEXT_LINE_GAP * (len(TEXT_LINES) - 1)
    if text_width > CELL_WIDTH - 2 * TEXT_MARGIN:
        raise ValueError(f"Logo text width {text_width:.3f} um exceeds cell width")
    if text_height > CELL_HEIGHT - 2 * TEXT_MARGIN:
        raise ValueError(f"Logo text height {text_height:.3f} um exceeds cell height")

    line_y = (CELL_HEIGHT + text_height) / 2 - line_height
    for line in TEXT_LINES:
        line_width = len(line) * char_advance - CHAR_GAP
        line_x = (CELL_WIDTH - line_width) / 2
        add_pixel_text(cell, line, line_x, line_y)
        line_y -= line_height + TEXT_LINE_GAP

    gds_path = OUTPUT_DIR / f"{CELL_NAME}.gds"
    cell.write_svg(str(OUTPUT_DIR / f"{CELL_NAME}.svg"))
    library.write_gds(str(gds_path))
    write_lef(OUTPUT_DIR / f"{CELL_NAME}.lef", CELL_NAME, CELL_WIDTH, CELL_HEIGHT)


if __name__ == "__main__":
    main()
