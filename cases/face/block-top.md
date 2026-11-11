+++
title = "Face the top of a block"
tags = ["2.5d", "face"]
material = "6061 aluminium"

[stock]
min = [0, 0, 0]
max = [100, 60, 22]

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

[removed]
value = 12000.0
exact = "100·60·2"
tex = '100\cdot 60\cdot 2'
+++

The stock is a block from (0, 0, 0) to (100, 60, 22). The part is the same block faced down by 2:
from (0, 0, 0) to (100, 60, 20). Remove the top 2 over the whole block, leaving a flat top at
z = 20.
