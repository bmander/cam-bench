def part(s):
    pins = [s.cylinder(x, y, 13, 22, 2) for x in (20, 30, 40, 50, 60) for y in (20, 30, 40)]
    pocket = s.cut(s.rounded_box(10, 10, 70, 50, 14, 21, 3), *pins)
    return s.cut(s.box(0, 0, 0, 80, 60, 20), pocket)
