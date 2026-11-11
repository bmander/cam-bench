+++
title = "A pocket with drafted walls"
tags = ["3d", "pocket", "draft", "steep"]
material = "6061 aluminium"
leftover = 0.05

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
value = 18227.405387106683
exact = "10·(A(s) + 4A(s/2) + A(0))/6, A(t) = (50 − 2t)(40 − 2t) − (4 − π)(6 − t)², s = 10 tan 10°"
tex = '10\cdot\tfrac{A(s) + 4A(s/2) + A(0)}{6},\quad A(t) = (50 - 2t)(40 - 2t) - (4 - \pi)(6 - t)^2,\ s = 10\tan 10^\circ'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with one pocket, 10
deep, in its top, whose walls lean out at 10° from the vertical. At the block's top the pocket
is a rectangle from (15, 10) to (65, 50) with its corners rounded to radius 6; at its flat floor,
z = 10, every wall has come in by s = 10·tan 10° ≈ 1.763, so the floor is the rectangle from
(15 + s, 10 + s) to (65 − s, 50 − s) with its corners rounded to radius 6 − s. Each wall is flat,
and each corner part of a cone.

Both tools reach all of the pocket: the flat tool's corner can follow the drafted walls down to
the floor, and the ball reaches the floor's edge. A flat tool leaves a stair on a drafted wall as
tall as its step down, though, and the case leaves no more than 0.05 of material anywhere.
