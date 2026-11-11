def part(s):
    pocket = s.cut(s.rounded_box(10, 10, 70, 50, 12, 21, 5), s.cylinder(56, 30, 11, 22, 10))
    return s.cut(s.box(0, 0, 0, 80, 60, 20), pocket)
