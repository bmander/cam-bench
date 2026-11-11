def part(s):
    pocket = s.rounded_box(20, 15, 60, 45, 10, 21, 6)
    # round the floor's edge: the edges of the pocket's tool body that lie on its floor
    pocket = s.fillet(pocket, 4, lambda x0, y0, z0, x1, y1, z1: abs(z0 - 10) < 1e-6 and abs(z1 - 10) < 1e-6)
    return s.cut(s.box(0, 0, 0, 80, 60, 20), pocket)
