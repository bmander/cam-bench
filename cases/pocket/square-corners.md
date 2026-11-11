+++
title = "A rectangular pocket with square corners"
tags = ["2.5d", "pocket", "unreachable"]
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
value = 11922.743338823082
exact = "(40·30 − (4 − π)·3²)·10 = 11640 + 90π"
tex = '\left(40\cdot 30 - (4 - \pi)\cdot 3^2\right)\cdot 10 = 11640 + 90\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with one pocket, 10
deep, in its top: a 40 by 30 rectangle from (20, 15) to (60, 45) with square corners, a flat floor
at z = 10 and vertical walls.

A round tool cannot reach into a square corner. The tool can reach all of the pocket but a fillet
of radius 3, its own radius, in each of the four vertical corners, which is left standing. Clear
the rest without cutting into the walls.
