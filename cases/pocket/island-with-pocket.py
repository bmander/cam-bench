def part(s):
    island = s.cut(s.rounded_box(25, 20, 55, 40, 10, 16, 5), s.rounded_box(33, 25, 47, 35, 12, 17, 3))
    return s.union(s.cut(s.box(0, 0, 0, 80, 60, 20), s.rounded_box(10, 10, 70, 50, 10, 21, 5)), island)
