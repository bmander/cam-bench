+++
title = "A boss with a fillet smaller than the ball"
tags = ["3d", "surface", "fillet", "unreachable"]
material = "6061 aluminium"
leftover = 0.05

[stock]
min = [0, 0, 0]
max = [60, 60, 25]

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
+++

The stock is a block from (0, 0, 0) to (60, 60, 25). The part is a round boss on a base: the base
is the block cut down to z = 10, and the boss a post of radius 12 centered on (30, 30) standing on
it from z = 10 to z = 22, the edge where the boss meets the base rounded to radius 2.

The rounded edge is tighter than the ball tool, radius 3, and no flat tool reaches into it: part of
it can be reached by no tool, and is left standing. Clear everything else, the boss's top
included, without cutting into it. Leave no more than 0.05 of material anywhere a tool reaches.
