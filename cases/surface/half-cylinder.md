+++
title = "A half cylinder lying on a plate"
tags = ["3d", "surface", "convex", "steep"]
material = "6061 aluminium"
leftover = 0.05

[stock]
min = [0, 0, 0]
max = [80, 60, 25]

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
value = 53904.426315322795
exact = "80·60·15 − 80·π·12²/2 = 72000 − 5760π"
tex = '80\cdot 60\cdot 15 - 80\cdot \tfrac{\pi\cdot 12^2}{2} = 72000 - 5760\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 25). The part is a plate with a ridge on it: the
plate is the block cut down to z = 10, and the ridge the upper half of a cylinder of radius 12
lying along x, its axis the line y = 30, z = 10, from x = 0 to x = 80. Its top is at z = 22, and
its sides stand vertical where they meet the plate.

The flat tool can reach the plate right up to the ridge, and the ball tool all of the ridge but
its foot, where the plate keeps the ball out of the corner: there only the flat tool's side
reaches the ridge, up to about z = 12.4. Leave no more than 0.05 of material anywhere on the part,
the steep sides included.
