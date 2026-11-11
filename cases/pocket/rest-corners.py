def part(s):
    pocket = s.union(s.rounded_box(10, 10, 70, 50, 10, 21, 2), s.box(65, 27.5, 10, 79.5, 32.5, 21),
                     s.cylinder(79.5, 30, 10, 21, 2.5))
    return s.cut(s.box(0, 0, 0, 90, 60, 20), pocket)
