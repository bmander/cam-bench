+++
title = "A pocket with tight corners and a narrow side slot, for two tools"
tags = ["2.5d", "pocket", "rest", "two-tools"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [90, 60, 20]

[[tools]]
number = 1
shape = "flat"
diameter = 12
flute = 25
length = 40
holder = 35
feed = 2000
plunge = 500
rpm = 12000

[[tools]]
number = 2
shape = "flat"
diameter = 4
flute = 12
length = 20
holder = 25
feed = 900
plunge = 200
rpm = 20000

[removed]
value = 24538.83847656827
exact = "(60·40 − (4 − π)·2² + 9.5·5 + π·2.5²/2)·10 = 24315 + 71.25π"
tex = '\left(60\cdot 40 - (4 - \pi)\cdot 2^2 + 9.5\cdot 5 + \tfrac{\pi\cdot 2.5^2}{2}\right)\cdot 10 = 24315 + 71.25\pi'
+++

The stock is a block from (0, 0, 0) to (90, 60, 20). The part is the block with a pocket in its
top, 10 deep, with a flat floor at z = 10 and vertical walls:

- a rectangle from (10, 10) to (70, 50) whose corners are rounded to radius 2;
- and a narrow slot 5 wide running out of its right wall: the rectangle from (70, 27.5) to
  (79.5, 32.5), ending in a half disk of radius 2.5 centered on (79.5, 30).

The 12 mm tool clears most of the pocket quickly but reaches neither its corners nor the slot;
the 4 mm tool reaches all of it. A program may use either or both.
