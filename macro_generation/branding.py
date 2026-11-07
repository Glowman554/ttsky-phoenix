from pathlib import Path
import gdstk

FONT = {
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'o': ['00000', '00000', '01110', '10001', '10001', '10001', '01110'],
    'x': ['00000', '00000', '10001', '01010', '00100', '01010', '10001'],
    'i': ['1', '0', '1', '1', '1', '1', '1'],
    'c': ['00000', '00000', '01111', '10000', '10000', '10000', '01111'],
    'C': ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
    'r': ['000', '000', '101', '110', '100', '100', '100'],
    'a': ['00000', '00000', '01110', '00001', '01111', '10001', '01111'],
    's': ['00000', '00000', '01111', '10000', '01110', '00001', '11110'],
    'h': ['10000', '10000', '10110', '11001', '10001', '10001', '10001'],
    '<': ['0001', '0010', '0100', '1000', '0100', '0010', '0001'],
    '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'e': ['00000', '00000', '01110', '10001', '11111', '10000', '01110'],
    'n': ['00000', '00000', '10110', '11001', '10001', '10001', '10001'],
    '-': ['000', '000', '000', '111', '000', '000', '000'],
    'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
    '2': ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
    ' ': ['00', '00', '00', '00', '00', '00', '00'],
}
LINES = ('Toxic x Crash <3', 'Phoenix-V2')
PIXEL, GAP, MARGIN = 0.490, 0.300, 0.000
PITCH = PIXEL + GAP
OUT = Path(__file__).resolve().parents[1] / 'macros'


def generate():
    lib = gdstk.Library(unit=1e-6, precision=1e-9)
    cell = lib.new_cell('branding')
    widths = [
        (sum(len(FONT[char][0]) + 1 for char in line) - 2) * PITCH + PIXEL
        for line in LINES
    ]
    for line_index, line in enumerate(LINES):
        offset = round((max(widths) - widths[line_index]) / 2 / 0.005) * 0.005
        column = 0
        for char in line:
            glyph = FONT[char]
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == '1':
                        x = MARGIN + offset + (column + col) * PITCH
                        y = MARGIN + ((1 - line_index) * 7 + 6 - row) * PITCH
                        cell.add(gdstk.rectangle((x, y), (x + PIXEL, y + PIXEL),
                                                 layer=71, datatype=20))
            column += len(glyph[0]) + 1
    width = max(widths) + 2 * MARGIN
    height = 13 * PITCH + PIXEL + 2 * MARGIN
    OUT.mkdir(exist_ok=True)

    cell.write_svg(str(OUT / 'branding.svg'), scaling=20, pad=0,
                   background='white', shape_style={(71, 20): {'fill': '#161616'}})
    cell.add(gdstk.rectangle((0, 0), (width, height), layer=235, datatype=4))
    lib.write_gds(str(OUT / 'branding.gds'))
    (OUT / 'branding.lef').write_text(f'''VERSION 5.8 ;
BUSBITCHARS "[]" ;
DIVIDERCHAR "/" ;
UNITS
  DATABASE MICRONS 1000 ;
END UNITS
MACRO branding
  CLASS BLOCK ;
  ORIGIN 0 0 ;
  FOREIGN branding 0 0 ;
  SIZE {width:.3f} BY {height:.3f} ;
  SYMMETRY X Y ;
  OBS
    LAYER met4 ;
    RECT 0 0 {width:.3f} {height:.3f} ;
  END
END branding
END LIBRARY
''')
    print(f'branding: {width:.3f} x {height:.3f} um')


if __name__ == '__main__':
    generate()
