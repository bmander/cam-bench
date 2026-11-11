def part(s):
    pocket = s.cut(s.rounded_box(10, 10, 70, 50, 12, 21, 5), s.cylinder(40, 30, 11, 22, 8))
    return s.cut(s.box(0, 0, 0, 80, 60, 20), pocket)
