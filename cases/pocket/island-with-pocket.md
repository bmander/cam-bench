+++
title = "An island below the top, with a pocket of its own"
tags = ["2.5d", "pocket", "island", "levels"]
material = "6061 aluminium"

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

[removed]
value = 20843.256600888213
exact = "(A₁ − A₂)·10 + A₂·4 + A₃·4, A₁ = 60·40 − (4 − π)·5², A₂ = 30·20 − (4 − π)·5², A₃ = 14·10 − (4 − π)·3² = 20416 + 136π"
tex = '(A_1 - A_2)\cdot 10 + A_2\cdot 4 + A_3\cdot 4,\quad A_1 = 60\cdot 40 - (4-\pi)\,5^2,\ A_2 = 30\cdot 20 - (4-\pi)\,5^2,\ A_3 = 14\cdot 10 - (4-\pi)\,3^2'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a pocket in its
top, and an island in the pocket with a pocket of its own:

- the pocket, a rectangle from (10, 10) to (70, 50) whose corners are rounded to radius 5, 10
  deep, its floor at z = 10;
- the island standing in it, a rectangle from (25, 20) to (55, 40) whose corners are rounded to
  radius 5, from the floor up to z = 16, 4 below the block's top;
- the island's pocket, a rectangle from (33, 25) to (47, 35) whose corners are rounded to radius
  3, down from the island's top to z = 12.

Every floor is flat and every wall vertical. The island's top is a floor too, below the stock's
top, so it is to be cut as well.
