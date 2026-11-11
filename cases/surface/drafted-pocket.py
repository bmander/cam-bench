import math


def part(s):
    d = 10 * math.tan(math.radians(10))
    pocket = s.loft(s.rounded_rectangle_wire(15 + d, 10 + d, 65 - d, 50 - d, 6 - d, 10),
                    s.rounded_rectangle_wire(15, 10, 65, 50, 6, 20))
    return s.cut(s.box(0, 0, 0, 80, 60, 20), pocket)
