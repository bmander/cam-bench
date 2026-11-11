+++
title = "A pocket with a deeper pocket in its floor"
tags = ["2.5d", "pocket", "levels"]
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
value = 11744.026493985908
exact = "(50·40 − (4 − π)·5²)·5 + (24·16 − (4 − π)·4²)·5 = 11100 + 205π"
tex = '\left(50\cdot 40 - (4 - \pi)\cdot 5^2\right)\cdot 5 + \left(24\cdot 16 - (4 - \pi)\cdot 4^2\right)\cdot 5 = 11100 + 205\pi'
+++

The stock is a block from (0, 0, 0) to (80, 60, 20). The part is the block with a pocket in its
top and a second, smaller pocket in that pocket's floor:

- the outer pocket, a 50 by 40 rectangle from (15, 10) to (65, 50) with corners rounded to radius
  5, 5 deep, with its floor at z = 15;
- the inner pocket, a 24 by 16 rectangle from (28, 22) to (52, 38) with corners rounded to radius
  4, a further 5 deep, with its floor at z = 10.

Both have flat floors and vertical walls.
