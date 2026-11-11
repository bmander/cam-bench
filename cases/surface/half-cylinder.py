def part(s):
    ridge = s.common(s.cylinder_along((0, 30, 10), (1, 0, 0), 12, 80), s.box(0, 0, 10, 80, 60, 25))
    return s.union(s.box(0, 0, 0, 80, 60, 10), ridge)
