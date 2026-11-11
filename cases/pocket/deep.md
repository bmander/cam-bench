+++
title = "A pocket deeper than the tool's flutes"
tags = ["2.5d", "pocket", "deep", "reach"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [60, 50, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 6
flute = 10
length = 30
holder = 30
feed = 1200
plunge = 300
rpm = 18000

[removed]
value = 10552.778684233861
exact = "(30·20 − (4 − π)·4²)·18 = 9648 + 288π"
tex = '\left(30\cdot 20 - (4 - \pi)\cdot 4^2\right)\cdot 18 = 9648 + 288\pi'
+++

The stock is a block from (0, 0, 0) to (60, 50, 20). The part is the block with one pocket, 18
deep, in its top: a 30 by 20 rectangle from (15, 15) to (45, 35) whose corners are rounded to
radius 4, with a flat floor at z = 2 and vertical walls.

The pocket is deeper than the tool's flutes, 10, though the tool stands far enough out of its
holder to reach the floor. The flutes must never have more than their length of material above
their tip within the tool's radius: a wall finished in one pass the full depth of the pocket,
after roughing has left some material on it, rubs the shank against what is left above the
flutes.
