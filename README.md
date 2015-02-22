# lapsevid
Time lapse video from a moving platform

This software lets you take time-lapse video from a robot controlled by a raspberry pi. The sofware assumes that GPIO pins are connected to a motor driver like L293D. A pair of GPIO pins control one motor. There are two such pairs - one for left and one for right. In addition there's one GPIO pin to enable the driver.

Edit the values in the configfile to match your setup, then run:

sudo lapsevid.py configfile

Coming: sample videos.
