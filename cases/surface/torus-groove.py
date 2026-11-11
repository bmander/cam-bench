def part(s):
    return s.cut(s.box(0, 0, 0, 80, 80, 20), s.torus((40, 40, 20), 15, 4))
