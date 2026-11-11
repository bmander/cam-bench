def part(s):
    return s.union(s.box(0, 0, 0, 60, 60, 12), s.cylinder(30, 30, 12, 20, 12))
