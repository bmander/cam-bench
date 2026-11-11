+++
title = "A rectangular pocket with round corners"
tags = ["2.5d", "pocket"]
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
value = 11862.654824574367
exact = "(40·30 − (4 − π)·4²)·10 = 11360 + 160π"
tex = '\left(40\cdot 30 - (4 - \pi)\cdot 4^2\right)\cdot 10 = 11360 + 160\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with one pocket, 10
deep, in its top: a 40 by 30 rectangle from (20, 15) to (60, 45) whose four corners are rounded to
radius 4, with a flat floor at z = 10 and vertical walls.

The tool's radius, 3, is under the corners' radius, so it can reach every part of the pocket.
