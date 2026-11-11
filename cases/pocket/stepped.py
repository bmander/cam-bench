def part(s):
    return s.cut(s.box(0, 0, 0, 80, 60, 20), s.rounded_box(15, 10, 65, 50, 15, 21, 5),
                 s.rounded_box(28, 22, 52, 38, 10, 21, 4))
