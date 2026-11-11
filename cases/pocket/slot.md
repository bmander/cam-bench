+++
title = "A slot wider than the tool"
tags = ["2.5d", "pocket", "slot"]
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
value = 2871.238898038469
exact = "(40·10 + π·5²)·6 = 2400 + 150π"
tex = '\left(40\cdot 10 + \pi\cdot 5^2\right)\cdot 6 = 2400 + 150\pi'
+++

The stock is a block from (0, 0, 0) to (80, 40, 20). The part is the block with a slot in its top,
6 deep: every point within 5 of the segment from (20, 20) to (60, 20), so a slot 10 wide with round
ends, with a flat floor at z = 14 and vertical walls. The tool is 6 across, so the slot is wider
than one pass.
