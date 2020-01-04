from PIL import ImageGrab
from collections import deque
import os
import sys
import win32api
import win32con
import time

DEBUG = False  # If you need to save snapshots to analise and print data

# Performance
CLICK_TIME = 0.02
THINK_TIME = 0.02

# Coordinates
X0 = 472
Y0 = 780
W = 488 - X0
H = 957 - Y0
START_CURSOR_POSITION = (33, 90)
BRANCHES_Y = list(range(30, 131, 25))
NEW_BRANCH_MAX_Y = 18
LEFT_X = 0
RIGHT_X = 15

BOX = (X0, Y0, X0 + W, Y0 + H)

LEFT = True
RIGHT = False

BRANCH_COLOR = (161, 116, 56)  # Tree's branch brown color

BUTTONS = {'space': 0x20,
           'left': 0x25,
           'right': 0x27}


def mouse_pos(cord):
    win32api.SetCursorPos((X0 + cord[0], Y0 + cord[1]))


def press_kb_button(*args):
    """
    One press, one release.
    Accepts as many arguments as you want. e.g. press('left', 'space', 'right').
    """
    for i in args:
        win32api.keybd_event(BUTTONS[i], 0, 0, 0)
        time.sleep(CLICK_TIME)
        win32api.keybd_event(BUTTONS[i], 0, win32con.KEYEVENTF_KEYUP, 0)


def mouse_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(CLICK_TIME)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def first_parse():
    """
    Первоначальное построение очереди
    """
    q = deque()
    q.append(LEFT)
    im = ImageGrab.grab(BOX)
    for y in reversed(BRANCHES_Y):
        if im.getpixel((LEFT_X, y)) == BRANCH_COLOR:
            q.append(RIGHT)
        else:
            q.append(LEFT)
    return q


def new_branch_is_not_left(i):
    im = ImageGrab.grab(BOX)
    if DEBUG:
        im.save(os.getcwd() + '\\screenshot__' + str(i) + '.png', 'PNG')

    for y in range(0, NEW_BRANCH_MAX_Y, 3):
        if im.getpixel((LEFT_X, y)) == BRANCH_COLOR:
            return False
    return True


def main(expected_score):
    """
    Бот играет за вас в игру LumberJack в телеграм
    :param expected_score: Сколько очков вы хотите набрать
    """
    mouse_pos(START_CURSOR_POSITION)
    mouse_click()
    time.sleep(THINK_TIME)
    press_kb_button('space')
    time.sleep(0.1)
    q = first_parse()

    if DEBUG:
        new_branch_is_not_left(-1)
        print('Start', q)

    for i in range(0, expected_score - 1, 2):
        if q.popleft():
            press_kb_button('left')
            time.sleep(THINK_TIME)
            press_kb_button('left')
        else:
            press_kb_button('right')
            time.sleep(THINK_TIME)
            press_kb_button('right')
        time.sleep(THINK_TIME)
        q.append(new_branch_is_not_left(i))
        if DEBUG:
            print(i, q)

    time.sleep(THINK_TIME)
    if expected_score % 2 == 1:
        if q.popleft():
            press_kb_button('left')
            time.sleep(THINK_TIME)
        else:
            press_kb_button('right')
            time.sleep(THINK_TIME)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(100)
    else:
        main(int(sys.argv[1]))
