+++
title = "Cut a rounded rectangle out of a plate"
tags = ["2.5d", "profile", "through"]
material = "6061 aluminium"
spoilboard = 0.5

[stock]
min = [0, 0, 0]
max = [80, 60, 10]

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
value = 24309.026644707676
exact = "80·60·10 − (60·40 − (4 − π)·6²)·10 = 25440 − 360π"
tex = '80\cdot 60\cdot 10 - \left(60\cdot 40 - (4 - \pi)\cdot 6^2\right)\cdot 10 = 25440 - 360\pi'
+++

The stock is a plate from (0, 0, 0) to (80, 60, 10), held from below on a spoilboard. The part is
a 60 by 40 rectangle from (10, 10) to (70, 50) with its four corners rounded to radius 6, the full
thickness of the plate. Remove all of the plate around it, down to z = 0. The tool may cut up to
0.5 into the spoilboard below z = 0, outside the part.
