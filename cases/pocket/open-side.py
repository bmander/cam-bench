def part(s):
    channel = s.union(s.rounded_box(-10, 15, 40, 45, 12, 21, 5), s.box(-10, 15, 12, 20, 45, 21))
    return s.cut(s.box(0, 0, 0, 80, 60, 20), channel)
