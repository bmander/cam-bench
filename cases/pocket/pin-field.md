+++
title = "A pocket with a field of pins"
tags = ["2.5d", "pocket", "island", "many-islands"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [80, 60, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 4
flute = 12
length = 20
holder = 25
feed = 900
plunge = 200
rpm = 20000

[removed]
value = 13222.672648001524
exact = "(60·40 − (4 − π)·3² − 15·π·2²)·6 = 14184 − 306π"
tex = '\left(60\cdot 40 - (4 - \pi)\cdot 3^2 - 15\pi\cdot 2^2\right)\cdot 6 = 14184 - 306\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a pocket in its
top, 6 deep: a rectangle from (10, 10) to (70, 50) whose corners are rounded to radius 3, with a
flat floor at z = 14 and vertical walls. Fifteen pins stand in it to the full height of the
block, each a round post of radius 2, from the floor to z = 20, centered on the points (x, y)
with x = 20, 30, 40, 50 or 60 and y = 20, 30 or 40.

The pins stand 6 apart, and 8 from the walls, so the tool, 4 across, reaches all of the pocket.
