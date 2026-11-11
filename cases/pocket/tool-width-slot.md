+++
title = "A slot exactly as wide as the tool"
tags = ["2.5d", "pocket", "slot", "degenerate"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [80, 40, 20]

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
value = 1341.3716694115408
exact = "(40·6 + π·3²)·5 = 1200 + 45π"
tex = '\left(40\cdot 6 + \pi\cdot 3^2\right)\cdot 5 = 1200 + 45\pi'
+++

The stock is a block from (0, 0, 0) to (80, 40, 20). The part is the block with a slot in its top,
5 deep: every point within 3 of the segment from (20, 20) to (60, 20), so a slot 6 wide with round
ends, with a flat floor at z = 15 and vertical walls.

The slot is exactly as wide as the tool, so the tool clears it in one pass down its middle, and
any pass off the middle cuts into a wall. A pocket's inward offset by the tool's radius is a single
line here, not an area.
