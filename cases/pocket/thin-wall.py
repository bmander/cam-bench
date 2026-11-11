def part(s):
    return s.cut(s.box(0, 0, 0, 80, 50, 20), s.rounded_box(10, 10, 39.6, 40, 8, 21, 4),
                 s.rounded_box(40.4, 10, 70, 40, 8, 21, 4))
