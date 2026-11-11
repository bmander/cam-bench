+++
title = "A channel open to the edge of the stock"
tags = ["2.5d", "pocket", "open"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [80, 60, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 8
flute = 20
length = 30
holder = 30
feed = 1500
plunge = 400
rpm = 16000

[removed]
value = 9514.15926535898
exact = "(40·30 − 2(1 − π/4)·5²)·8 = 9200 + 100π"
tex = '\left(40\cdot 30 - 2\left(1 - \tfrac{\pi}{4}\right)\cdot 5^2\right)\cdot 8 = 9200 + 100\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a channel in its
top, 8 deep, open to the block's left face: the rectangle from (0, 15) to (40, 45), its two
corners at x = 40 rounded to radius 5, with a flat floor at z = 12 and vertical walls. At x = 0
it has no wall: the channel runs out of the block.

The tool can come in from outside the block, at depth, rather than ramping or plunging into it.
