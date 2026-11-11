def part(s):
    body = s.union(s.box(0, 0, 0, 60, 60, 10), s.cylinder(30, 30, 10, 22, 12))
    # round the circle where the boss meets the base, and no edge of the base
    return s.fillet(body, 2, lambda x0, y0, z0, x1, y1, z1: abs(z0 - 10) < 1e-6 and abs(z1 - 10) < 1e-6
                    and x0 > 10 and x1 < 50 and y0 > 10 and y1 < 50)
