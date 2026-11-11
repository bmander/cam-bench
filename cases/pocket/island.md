+++
title = "A pocket around a round island"
tags = ["2.5d", "pocket", "island"]
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

[removed]
value = 17419.823092079983
exact = "(60·40 − (4 − π)·5² − π·8²)·8 = 18400 − 312π"
tex = '\left(60\cdot 40 - (4 - \pi)\cdot 5^2 - \pi\cdot 8^2\right)\cdot 8 = 18400 - 312\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a pocket in its
top, 8 deep, around an island. The pocket is a 60 by 40 rectangle from (10, 10) to (70, 50) whose
corners are rounded to radius 5, with a flat floor at z = 12 and vertical walls. In its middle an
island stands to the full height of the block: a round post of radius 8 centered on (40, 30),
from the floor to z = 20.
