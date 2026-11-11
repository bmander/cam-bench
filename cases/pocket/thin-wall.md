+++
title = "Two pockets either side of a thin wall"
tags = ["2.5d", "pocket", "thin-wall"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [80, 50, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 6
flute = 15
length = 25
holder = 30
feed = 1200
plunge = 300
rpm = 18000

[removed]
value = 20982.371578978484
exact = "2·(29.6·30 − (4 − π)·4²)·12 = 19776 + 384π"
tex = '2\left(29.6\cdot 30 - (4 - \pi)\cdot 4^2\right)\cdot 12 = 19776 + 384\pi'
+++

The stock is a block from (0, 0, 0) to (80, 50, 20). The part is the block with two pockets in its
top, each 12 deep with its floor at z = 8 and vertical walls, and each a rectangle whose corners
are rounded to radius 4: one from (10, 10) to (39.6, 40), the other from (40.4, 10) to (70, 40).
Between them stands a wall 0.8 thick, from x = 39.6 to x = 40.4, the full height of the block.

The wall is thinner than any slack a program might allow itself: a pass that strays toward it by
more than the case's tolerance cuts into it.
