from PIL import ImageGrab
from collections import deque
import os
import sys
import win32api
import win32con
import time

DEBUG = False  # If you need to save snapshots to analise and print data

# Performance
CLICK_TIME = 0.001

# Coordinates
GAME_WIDTH = 150

LEFT = True
RIGHT = False

BRANCH_COLOR = (161, 116, 56)  # Tree's branch brown color
SKY_COLOR = (211, 247, 255)  # Clear sky color
GRASS_COLOR = (174, 221, 127)

BUTTONS = {'space': 0x20,
           'left': 0x25,
           'right': 0x27}


def get_game_box_size():
    left_x, top_y, bottom_y = None, None, None
    im = ImageGrab.grab()
    for y in range(im.height):
        for x in range(im.width):
            if im.getpixel((x, y)) == SKY_COLOR:
                top_y = y
                left_x = x
                break
        else:
            continue
        break

    if top_y:
        for y in range(top_y, im.height):
            if im.getpixel((left_x, y)) == GRASS_COLOR:
                bottom_y = y
    if top_y and bottom_y:
        box = (left_x, top_y, left_x + GAME_WIDTH, bottom_y)
        return box
    else:
        return None


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


def play(score):
    box = get_game_box_size()
    if not box:
        print("Game box didn't exist")
        return -1

    win32api.SetCursorPos((box[0], box[1]))
    mouse_click()
    time.sleep(0.2)
    press_kb_button('space')
    time.sleep(0.2)

    im = ImageGrab.grab(box)
    if DEBUG:
        im.save(os.getcwd() + '\\00.png', 'PNG')

    left_branch_x, right_branch_x = None, None
    for x in range(0, im.width):
        if im.getpixel((x, 0)) == BRANCH_COLOR:
            left_branch_x = x - 2
            right_branch_x = left_branch_x + 14
            break

    start_y = None
    start_branch = None
    if left_branch_x:
        for y in range(im.height):
            if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                start_y = y
                start_branch = 'left'
                break
            elif im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                start_y = y
                start_branch = 'right'
                break

    q = deque()
    q.append('left')

    if not start_y or not start_branch:
        return -1

    for y in reversed(range(start_y, im.height - 40, 25)):
        if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
            q.append('right')
        elif im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
            q.append('left')
        else:
            break
    last_start_y = start_y
    last_start_branch = start_branch

    for i in range(0, score - 1, 2):
        move_direction = q.popleft()
        for j in range(2):
            press_kb_button(move_direction)
            im = ImageGrab.grab(box)
            if im.getpixel((left_branch_x + 2, 0)) != BRANCH_COLOR:
                print(f'Game over! Score {i + j - 1}')
                return 0

            if DEBUG:
                im.save(os.getcwd() + '\\{:02}_{}.png'.format(i + j + 1, move_direction), 'PNG')
            if last_start_branch == 'left':
                if im.getpixel((left_branch_x, last_start_y)) == BRANCH_COLOR:
                    if im.getpixel((left_branch_x, last_start_y - 1)) == BRANCH_COLOR:
                        for y in range(last_start_y + 6, last_start_y + 50):
                            if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                                last_start_y = y
                                break
                else:
                    for y in range(last_start_y, last_start_y + 50):
                        if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                            last_start_y = y
                            break
            else:
                if im.getpixel((right_branch_x, last_start_y)) == BRANCH_COLOR:
                    if im.getpixel((right_branch_x, last_start_y - 1)) == BRANCH_COLOR:
                        for y in range(last_start_y + 6, last_start_y + 50):
                            if im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                                last_start_y = y + 1
                                break
                else:
                    for y in range(last_start_y, last_start_y + 50):
                        if im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                            last_start_y = y
                            break
            if DEBUG:
                print(i + j + 1, last_start_y)

            # Идем вверх и добавляем новые ветки
            for y in range(last_start_y - 25, 0, -25):
                if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                    q.append('right')
                    last_start_y = y
                    last_start_branch = 'left'
                elif im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                    q.append('left')
                    last_start_y = y
                    last_start_branch = 'right'
                else:
                    break
            if DEBUG:
                print(q)


if __name__ == '__main__':
    play(score=800)
