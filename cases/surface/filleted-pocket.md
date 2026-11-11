+++
title = "A pocket with a rounded floor edge"
tags = ["3d", "pocket", "fillet", "concave"]
material = "6061 aluminium"
leftover = 0.05

[stock]
min = [0, 0, 0]
max = [80, 60, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 10
flute = 20
length = 35
holder = 30
feed = 1800
plunge = 400
rpm = 14000

[[tools]]
number = 2
shape = "ball"
diameter = 6
flute = 15
length = 35
holder = 30
feed = 1500
plunge = 400
rpm = 18000

[removed]
value = 11264.910549124468
exact = "(40·30 − (4 − π)·6²)·10 − (16 − 4π)(92 + 2π(2 + 2/(3(1 − π/4)))) = 9088 + 1928π/3 + 16π²"
tex = '\left(40\cdot 30 - (4 - \pi)\cdot 6^2\right)\cdot 10 - \left(16 - 4\pi\right)\left(92 + 2\pi\left(2 + \tfrac{2}{3(1 - \pi/4)}\right)\right) = 9088 + \tfrac{1928\pi}{3} + 16\pi^2'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with one pocket, 10
deep, in its top: a 40 by 30 rectangle from (20, 15) to (60, 45) whose vertical corners are rounded
to radius 6, with its floor at z = 10, and with the edge where the floor meets the walls rounded
all the way round to radius 4.

The flat tool cannot reach into the rounded floor edge; the ball tool, of radius 3, can reach every
part of the pocket. Leave no more than 0.05 of material anywhere on the part.
