from PIL import ImageGrab
from collections import deque
import os
import sys
import win32api
import win32con
import time

DEBUG = False  # If you need to save snapshots to analise and print data

# Performance
CLICK_TIME = 0.01  # 0.02
THINK_TIME = 0.02  # 0.02

# Coordinates
X0 = 472
Y0 = 700
W = 488 - X0
H = 957 - Y0
START_CURSOR_POSITION = (33, 90)
BRANCHES_Y = list(range(110, 211, 25))
NEW_BRANCH_MAX_Y = 95
LEFT_X = 0
RIGHT_X = 15
GAME_WIDTH = 150

BOX = (X0, Y0, X0 + W, Y0 + H)

LEFT = True
RIGHT = False

BRANCH_COLOR = (161, 116, 56)  # Tree's branch brown color
SKY_COLOR = (211, 247, 255)  # Clear sky color
GRASS_COLOR = (174, 221, 127)

BUTTONS = {'space': 0x20,
           'left': 0x25,
           'right': 0x27}


def mouse_pos(cord):
    win32api.SetCursorPos((X0 + cord[0], Y0 + cord[1]))


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
    time.sleep(THINK_TIME * 2)
    press_kb_button('space')
    time.sleep(0.1)
    q = first_parse()
    think_time = THINK_TIME * 2

    if DEBUG:
        new_branch_is_not_left(-1)
        print('Start', q)

    for i in range(0, expected_score - 1, 2):
        if i > 20:
            think_time = THINK_TIME
        if q.popleft():
            press_kb_button('left')
            time.sleep(think_time)
            press_kb_button('left')
        else:
            press_kb_button('right')
            time.sleep(think_time)
            press_kb_button('right')
        time.sleep(think_time)
        q.append(new_branch_is_not_left(i))
        if DEBUG:
            print(i, q)

    time.sleep(think_time)
    if expected_score % 2 == 1:
        if q.popleft():
            press_kb_button('left')
        else:
            press_kb_button('right')


def test_10_frames():
    """
    Функция сбора 10 скриншотов для анализа при очень быстрой игре
    """
    x0 = 432
    y0 = 650
    w = 518 - x0
    h = 1007 - y0
    box = (x0, y0, x0 + w, y0 + h)

    mouse_pos(START_CURSOR_POSITION)
    mouse_click()
    time.sleep(THINK_TIME * 2)
    press_kb_button('space')
    time.sleep(0.1)
    q = first_parse()
    think_time = 0.005

    im = ImageGrab.grab(box)
    im.save(os.getcwd() + '\\{:02}_start.png'.format(0), 'PNG')

    for i in range(5):
        if q.popleft():
            press_kb_button('left')
            im = ImageGrab.grab(box)
            im.save(os.getcwd() + '\\{:02}_left.png'.format(2 * i + 1), 'PNG')
            time.sleep(think_time)
            press_kb_button('left')
            im = ImageGrab.grab(box)
            im.save(os.getcwd() + '\\{:02}_left.png'.format(2 * i + 2), 'PNG')
            print(i)
        else:
            press_kb_button('right')
            im = ImageGrab.grab(box)
            im.save(os.getcwd() + '\\{:02}_right.png'.format(2 * i + 1), 'PNG')
            time.sleep(think_time)
            press_kb_button('right')
            im = ImageGrab.grab(box)
            im.save(os.getcwd() + '\\{:02}_right.png'.format(2 * i + 2), 'PNG')
            print(i)
        time.sleep(think_time)


def fast_game(score):
    box = get_game_box_size()
    think_time = 0.02

    if not box:
        print("Game box didn't exist")
        return -1

    win32api.SetCursorPos((box[0], box[1]))
    mouse_click()
    time.sleep(THINK_TIME * 2)
    press_kb_button('space')
    time.sleep(0.2)

    im = ImageGrab.grab(box)
    im.save(os.getcwd() + '\\00.png', 'PNG')
    left_branch_x, right_branch_x = None, None
    for x in range(0, im.width):
        if im.getpixel((x, 0)) == BRANCH_COLOR:
            left_branch_x = x - 1
            right_branch_x = left_branch_x + 13
            break

    start_y = None
    start_branch = None
    if left_branch_x:
        for y in range(im.height):
            if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                start_y = y + 3  # Сдвиг на 3, потому что ветка слева шире вдоль дерева
                start_branch = 'left'
                break
            elif im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                start_y = y
                start_branch = 'right'
                break

    q = deque()
    q.append('left')

    print(start_y)
    print(start_branch)

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

    print(q)

    for i in range(5):
        move_direction = q.popleft()
        press_kb_button(move_direction)
        time.sleep(think_time)
        im = ImageGrab.grab(box)
        im.save(os.getcwd() + '\\{:02}_{}.png'.format(2 * i, move_direction), 'PNG')
        if last_start_branch == 'left':
            if im.getpixel((left_branch_x, last_start_y - 3)) == BRANCH_COLOR:
                for y in range(last_start_y - 3, last_start_y - 50, -1):
                    if im.getpixel((left_branch_x, y)) != BRANCH_COLOR:
                        new_y = y - 1
                        break
            else:
                for y in range(last_start_y - 3, last_start_y + 50):
                    if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                        new_y = y
                        break
        else:
            if im.getpixel((right_branch_x, last_start_y)) == BRANCH_COLOR:
                for y in range(last_start_y, last_start_y - 50, -1):
                    if im.getpixel((right_branch_x, y)) != BRANCH_COLOR:
                        new_y = y - 1
                        break
            else:
                for y in range(last_start_y, last_start_y + 50):
                    if im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                        new_y = y
                        break
        print(last_start_y, new_y, (new_y - last_start_y) % 20)
        last_start_y = new_y
        press_kb_button(move_direction)
        time.sleep(think_time)
        im = ImageGrab.grab(box)
        im.save(os.getcwd() + '\\{:02}_right.png'.format(2 * i + 1), 'PNG')
        if last_start_branch == 'left':
            if im.getpixel((left_branch_x, last_start_y - 3)) == BRANCH_COLOR:
                for y in range(last_start_y - 3, last_start_y - 50, -1):
                    if im.getpixel((left_branch_x, y)) != BRANCH_COLOR:
                        new_y = y - 1
                        break
            else:
                for y in range(last_start_y - 3, last_start_y + 50):
                    if im.getpixel((left_branch_x, y)) == BRANCH_COLOR:
                        new_y = y
                        break
        else:
            if im.getpixel((right_branch_x, last_start_y)) == BRANCH_COLOR:
                for y in range(last_start_y, last_start_y - 50, -1):
                    if im.getpixel((right_branch_x, y)) != BRANCH_COLOR:
                        new_y = y - 1
                        break
            else:
                for y in range(last_start_y, last_start_y + 50):
                    if im.getpixel((right_branch_x, y)) == BRANCH_COLOR:
                        new_y = y
                        break
        print(last_start_y, new_y, (new_y - last_start_y) % 20)
        last_start_y = new_y


if __name__ == '__main__':
    # test_10_frames()
    # if len(sys.argv) == 1:
    #     main(730)
    # else:
    #     main(int(sys.argv[1]))
    fast_game(10)
