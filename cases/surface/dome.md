+++
title = "A dome on a plate"
tags = ["3d", "surface", "convex"]
material = "6061 aluminium"
leftover = 0.05

[stock]
min = [0, 0, 0]
max = [80, 80, 25]

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
value = 87622.41959042722
exact = "80·80·15 − πh²(3R − h)/3, R = 30, h = 10: 96000 − 8000π/3"
tex = '80\cdot 80\cdot 15 - \tfrac{\pi h^2 (3R - h)}{3},\quad R = 30,\ h = 10'
+++

The stock is a block from (0, 0, 0) to (80, 80, 25). The part is a plate with a dome on it: the
plate is the block cut down to z = 10, and the dome the part of a ball of radius 30 centered on
(40, 40, −10) that lies above the plate, a cap 10 high whose top is at z = 20.

Where the dome meets the plate the two make an edge, not a fillet. The flat tool can reach the
plate right up to the dome, and the ball tool all of the dome but the foot of it, where the plate
keeps the ball out of the corner: there only the flat tool's edge reaches the dome, up to about
z = 11. Leave no more than 0.05 of material anywhere on the part.
