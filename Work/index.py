from cv2 import cv2
from os import listdir
from src.logger import logger
from random import random
import pygetwindow
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

time.sleep(2)

if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']

pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

pyautogui.FAILSAFE = False
login_attempts = 0
last_log_is_progress = False

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n
    
    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets
images = load_images()
logger('targets loaded')

def show(rectangles, img = None):

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img,name=None, timeout=3, threshold = ct['default']):
    logger(None, progress_indicator=True)
    if not name is None:
        pass
        print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    while(True):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True
        print("THIS SHOULD NOT PRINT")

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['login-fox'], name='login-fox', timeout = 10):
        logger('🎉 Connect wallet button detected, logging in!')
        login_attempts = login_attempts + 1
        #TODO mto ele da erro e poco o botao n abre
        # time.sleep(10)

    #if clickBtn(images['select-wallet-2'], name='sign button', timeout=8):
        # sometimes the sign popup appears imediately
       # login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))

    if clickBtn(images['select-wallet-2'], name='signBtn', timeout = 20):
        login_attempts = login_attempts + 1
        #print('sign button clicked')
        #print('{} login attempt'.format(login_attempts))
        # time.sleep(25)
        login_attempts = 0

def goMarket():
    if clickBtn(images['market-button'], name='market-button', timeout=5):
        clickBtn(images['buy-chicken'], name='buy-chicken', timeout=5)

    goTavern()

def goTown():
    clickBtn(images['town-button'],name='market-button', timeout=5)

def giveFood():
    global food_attempts
    food_attempts = 0
    #if clickBtn(images['chicken-empty'], name='chicken-empty', timeout=5):
        #food_attempts = food_attempts + 1
        #goMarket()

    if clickBtn(images['give-food']):
        food_attempts = food_attempts + 1
    time.sleep(1)
    clickBtn(images['give-food'])
    time.sleep(3)
    if clickBtn(images['give-chicken'], name='give-chicken', timeout=5):
        logger('food gived')
        food_attempts = food_attempts + 1
    
    if food_attempts == 2:
        giveFood()
        food_attempts = 0

def goTavern():
    global tavern_attempts
    tavern_attempts = 0

    if clickBtn(images['tavern-button']):
        time.sleep(1)
        clickBtn(images['tavern-button'])
        time.sleep(1)


def main():
    time.sleep(5)
    t = c['time_intervals']
    

    windows = []

    for w in pygetwindow.getWindowsWithTitle('WorkerTown'):
        windows.append({
            "window": w,
            "login" : 0,
            "food" : 0,
            "tavern" : 0,
            "check_for_captcha" : 0,
            "refresh" : 0
            })

    while True:
        now = time.time()

        for last in windows:
            last["window"].activate()
            time.sleep(2)

            if now - last["login"] > addRandomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last["login"] = now
                login()

            if now - last["food"] > addRandomness(t['give_food'] * 60):
                last["food"] = now
                giveFood()

            if now - last["tavern"] > addRandomness(t['go_tavern'] * 60):
                last["tavern"] = now
                logger("Go Tavern")
                goTavern()
  
            logger(None, progress_indicator=True)

            sys.stdout.flush()

            time.sleep(1)
            
main()

    