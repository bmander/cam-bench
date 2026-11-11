+++
title = "A round bowl"
tags = ["3d", "surface", "concave", "steep"]
material = "6061 aluminium"
leftover = 0.05

[stock]
min = [0, 0, 0]
max = [70, 70, 20]

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
value = 10602.875205865552
exact = "πh²(3R − h)/3, R = 20, h = 15: 3375π"
tex = '\tfrac{\pi h^2 (3R - h)}{3},\quad R = 20,\ h = 15'
+++

The stock is a block from (0, 0, 0) to (70, 70, 20). The part is the block with a bowl in its top:
the part of a ball of radius 20 centered on (35, 35, 25) that lies in the block, cut away. The
bowl is 15 deep, its bottom at (35, 35, 5) and its rim a circle of radius √375 ≈ 19.36 on the
block's top. Near the rim its wall stands at 75° from the horizontal.

The ball tool, radius 3, reaches all of the bowl. Leave no more than 0.05 of material anywhere on
the part.
