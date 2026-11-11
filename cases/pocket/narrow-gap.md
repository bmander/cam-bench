+++
title = "An island too near a wall for the tool to pass"
tags = ["2.5d", "pocket", "island", "unreachable"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [80, 60, 20]

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
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a pocket in its
top, 8 deep: a rectangle from (10, 10) to (70, 50) whose corners are rounded to radius 5, with a
flat floor at z = 12 and vertical walls. An island stands in it to the full height of the block: a
round post of radius 10 centered on (56, 30), from the floor to z = 20.

The island stands 4 from the pocket's right wall, closer than the tool's diameter, 6: the tool
cannot pass between them, so the pocket is two regions joined only above the gap, and the
material in the gap that the tool cannot reach from either side is left standing. Clear the
rest without cutting into the island or the wall.
