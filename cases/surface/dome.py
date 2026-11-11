def part(s):
    return s.union(s.box(0, 0, 0, 80, 80, 10),
                   s.common(s.sphere((40, 40, -10), 30), s.box(0, 0, 10, 80, 80, 25)))
