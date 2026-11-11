+++
title = "Clear around a round boss"
tags = ["2.5d", "profile", "boss"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [60, 60, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 10
flute = 20
length = 30
holder = 30
feed = 1800
plunge = 400
rpm = 14000

[removed]
value = 25180.88526306456
exact = "(60·60 − π·12²)·8 = 28800 − 1152π"
tex = '\left(60\cdot 60 - \pi\cdot 12^2\right)\cdot 8 = 28800 - 1152\pi'
+++

The stock is a block from (0, 0, 0) to (60, 60, 20). The part is a round boss on a base: the base
is the block cut down to z = 12, and the boss a post of radius 12 centered on (30, 30) standing on
it from z = 12 to z = 20. Remove everything around the boss down to z = 12, out to the edges of
the block.
