#!/usr/bin/env python
import curses
import time
import RPi.GPIO as GPIO
import control2 as ctl


screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

ctl.reset__()

try:
    while True:
        char =screen.getch()
        if char == ord('q'):
            ctl.detach();
        elif char == curses.KEY_UP:
            print("forward")
            ctl.forward()
        elif char == curses.KEY_DOWN:
            print("backward")
            ctl.backward();
        elif char == curses.KEY_RIGHT:
            print("right")
            ctl.turn_right();
        elif char == curses.KEY_LEFT:
            print("left")
            ctl.turn_left();
        elif char == 0:
            ctl.detach()
            
finally:
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
    ctl.break_stop()
    ctl.restore()        
