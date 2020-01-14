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
GAME_WIDTH = 150  # Width of game box
HALF_SCREEN = 67
BRANCH_STEP = 25  # Расстояние между ближайшими ветками по вертикали

LEFT = True
RIGHT = False

BRANCH_COLOR = (161, 116, 56)  # Tree's branch brown color
SKY_COLOR = (211, 247, 255)  # Clear sky color
GRASS_COLOR = (174, 221, 127)

BUTTONS = {'space': 0x20,
           'right': 0x25,
           'left': 0x27}


def get_game_box_size():
    """
    :return: coordinates of game box left top and right bottom corners
    """
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
        box = (left_x + 67, top_y, left_x + 82, bottom_y)
        return box
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
    box = get_game_box_size()  # Получаем координаты игры, по которым будем делать скриншоты для анализа веток.
    if not box:
        print("Game box didn't exist")
        return -1

    win32api.SetCursorPos((box[0], box[1]))  # Устанавливаем курсор в окно с игрой
    mouse_click()
    time.sleep(0.2)
    press_kb_button('space')  # Пробел для начала игры
    time.sleep(0.2)

    im = ImageGrab.grab(box)  # Первый скриншот для анализа первоначального рсположения веток
    if DEBUG:
        im.save(os.getcwd() + '\\00.png', 'PNG')

    branches_x = {}  # Относительные значения x для полос пикселей, по которым будем определять наличие веток
    for x in range(0, im.width):
        if im.getpixel((x, 0)) == BRANCH_COLOR:
            branches_x['left'] = x - 2
            branches_x['right'] = x + 12
            break

    start_y = None
    start_branch = None
    if not branches_x:
        print('Branches not found')
        return -1

    for y in range(im.height):
        for side in branches_x:
            if im.getpixel((branches_x[side], y)) == BRANCH_COLOR:
                start_y = y  # y координата верхней ветки
                start_branch = side  # Сторона верхней ветки left или right
                break
        else:
            continue
        break

    q = deque()  # Очередь веток снизу вверх. При игре мы будем из очереди брать самое левое значение
    q.append('left')  # Первые два удара не важны. Можно добавить как right, так и left

    if not start_y or not start_branch:
        print('Start branch position not found')
        return -1

    # Первоначальное построение очереди веток
    for y in reversed(range(start_y, im.height - 40, BRANCH_STEP)):
        for side in branches_x:
            if im.getpixel((branches_x[side], y)) == BRANCH_COLOR:
                q.append(side)
                break

    last_start_y = start_y
    last_start_branch = start_branch

    # После каждого удара будем делать скриншот и добавлять новые ветки в очередь справа
    for i in range(0, score - 1, 2):
        branch_side = q.popleft()
        for j in range(2):
            press_kb_button(branch_side)
            im = ImageGrab.grab(box)
            if im.getpixel((branches_x['left'] + 2, 0)) != BRANCH_COLOR:
                print(f'Game over! Score {i + j - 1}')
                return 0

            if DEBUG:
                im.save(os.getcwd() + '\\{:02}_{}.png'.format(i + j + 1, branch_side), 'PNG')

            # Определяем наскколько сдвинулоь дерево
            if im.getpixel((branches_x[last_start_branch], last_start_y)) == BRANCH_COLOR:
                if im.getpixel((branches_x[last_start_branch], last_start_y - 1)) == BRANCH_COLOR:
                    for y in range(last_start_y + 6, last_start_y + 2 * BRANCH_STEP):
                        if im.getpixel((branches_x[last_start_branch], y)) == BRANCH_COLOR:
                            last_start_y = y
                            break
            else:
                for y in range(last_start_y, last_start_y + 2 * BRANCH_STEP):
                    if im.getpixel((branches_x[last_start_branch], y)) == BRANCH_COLOR:
                        last_start_y = y
                        break

            if DEBUG:
                print(i + j + 1, last_start_y)

            # Идем вверх и добавляем новые ветки
            for y in range(last_start_y - BRANCH_STEP, 0, -BRANCH_STEP):
                for side in branches_x:
                    if im.getpixel((branches_x[side], y)) == BRANCH_COLOR:
                        q.append(side)
                        last_start_y = y
                        last_start_branch = side
                        break

            if DEBUG:
                print(q)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        play(score=1000)
    else:
        play(score=int(sys.argv[1]))
