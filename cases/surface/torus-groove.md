+++
title = "A round groove in a ring"
tags = ["3d", "surface", "concave", "groove"]
material = "6061 aluminium"
leftover = 0.05

[stock]
min = [0, 0, 0]
max = [80, 80, 20]

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
value = 2368.705056261446
exact = "π²r²R, r = 4, R = 15: 240π²"
tex = '\pi^2 r^2 R,\quad r = 4,\ R = 15'
+++

The stock is a block from (0, 0, 0) to (80, 80, 20). The part is the block with a groove in its
top: the lower half of a torus cut away, its tube of radius 4 about a circle of radius 15 centered
on (40, 40) in the block's top, z = 20. The groove is 8 wide at the top and 4 deep, round in
section, and runs round in a ring.

The ball tool, radius 3, reaches all of the groove; the flat tool reaches its bottom only in steps.
Leave no more than 0.05 of material anywhere on the part.
