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
from matplotlib import pyplot as plt

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
logger('prevent server erro !')
time.sleep(2)


def show(rectangles, img = None):

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
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
    global reSize

    logger('Checking if game has disconnected')

    if login_attempts > 2:
        logger('Too many login attempts, refreshing')
        login_attempts = 0
        time.sleep(2)
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['login-fox'], name='login-fox', timeout = 8):
        logger('Connect wallet button detected, logging in!')
        login_attempts = login_attempts + 1
        # time.sleep(10)
        if clickBtn(images['select-wallet-2'], name='signBtn', timeout = 20):
            login_attempts = login_attempts + 1

def goMarket():
    if clickBtn(images['market-button'], name='market-button', timeout=5):
        clickBtn(images['buy-chicken'], name='buy-chicken', timeout=5)

def goTownRest():
    if clickBtn(images['town-button'], name='town-button', timeout=5):
        time.sleep(3)
        clickBtn(images['house'], timeout=2)
        time.sleep(3)

        finishRest = positions(images['finish-rest-bed'],threshold=ct['default'])
        empty = positions(images['bed-empty'],threshold=ct['default'])
        if len(finishRest) != 0:
            clickBtn(images['finish-rest-bed'], name='finish-rest-bed', timeout=3)
            time.sleep(3)
        
        check_avaliable()

def check_avaliable():
    avaliable = positions(images['avaliable-bed'],threshold=ct['default'])
    
    if len(avaliable) == 1:
        clickBtn(images['avaliable-bed'], name='avaliable bed', timeout=3)
        time.sleep(2)
        eight = positions(images['8hrs'],threshold=ct['default'])
        seventwo = positions(images['72hrs'],threshold=ct['default'])

        if len(eight) == 1:
            clickBtn(images['8hrs'], name='Go Rest 8 hrs', timeout=3)
            time.sleep(2)
            bed_end = positions(images['error-bed-time'],threshold=ct['default'])
            if len(bed_end) != 0:
                clickBtn(images['close'], timeout=2)
                clickBtn(images['trash-bed'], timeout=2)
                time.sleep(2)
                clickBtn(images['bed-empty'], timeout=2)
                time.sleep(3)
                clickBtn(images['legendary-bed-price'], timeout=2)
                time.sleep(3)
                check_avaliable()
            clickBtn(images['close'], timeout=2)
            time.sleep(2)
            
        elif len(seventwo) == 1:
            clickBtn(images['72hrs'], name='Go Rest 72 hrs', timeout=3)
            time.sleep(2)
            bed_end = positions(images['error-bed-time'],threshold=ct['default'])
            if len(bed_end) != 0:
                clickBtn(images['close'], timeout=2)
                clickBtn(images['trash-bed'], timeout=2)
                time.sleep(2)
                clickBtn(images['bed-empty'], timeout=2)
                time.sleep(3)
                clickBtn(images['legendary-bed-price'], timeout=2)
                time.sleep(3)
                check_avaliable()
            clickBtn(images['close'], timeout=2)
            time.sleep(2)
    else: 
        clickBtn(images['close'], timeout=2)
        if clickBtn(images['second-house'], timeout=2):
            avaliable = positions(images['avaliable-bed'],threshold=ct['default'])

            if len(avaliable) == 1:
                clickBtn(images['avaliable-bed'], name='avaliable bed', timeout=3)
                time.sleep(2)
                eight = positions(images['8hrs'],threshold=ct['default'])
                seventwo = positions(images['72hrs'],threshold=ct['default'])

                if len(eight) == 1:
                    clickBtn(images['8hrs'], name='Go Rest 8 hrs', timeout=3)
                    time.sleep(2)
                    bed_end = positions(images['error-bed-time'],threshold=ct['default'])
                    if len(bed_end) != 0:
                        clickBtn(images['close'], timeout=2)
                        clickBtn(images['trash-bed'], timeout=2)
                        time.sleep(2)
                        clickBtn(images['bed-empty'], timeout=2)
                        time.sleep(3)
                        clickBtn(images['legendary-bed-price'], timeout=2)
                        time.sleep(3)
                        check_avaliable()
                    clickBtn(images['close'], timeout=2)
                elif len(seventwo) == 1:
                    clickBtn(images['72hrs'], name='Go Rest 72 hrs', timeout=3)
                    time.sleep(2)
                    if len(bed_end) != 0:
                        clickBtn(images['close'], timeout=2)
                        clickBtn(images['trash-bed'], timeout=2)
                        time.sleep(2)
                        clickBtn(images['bed-empty'], timeout=2)
                        time.sleep(3)
                        clickBtn(images['legendary-bed-price'], timeout=2)
                        time.sleep(3)
                        check_avaliable()
                    clickBtn(images['close'], timeout=2)
                    time.sleep(2)
            clickBtn(images['close'], timeout=2)
    
    goTavern()

def giveFood():
    food_attempts = 0
    #if clickBtn(images['chicken-empty'], name='chicken-empty', timeout=5):
        #food_attempts = food_attempts + 1
        #goMarket()

    if clickBtn(images['give-food'], name='give-food', timeout=5):
        food_attempts = food_attempts + 1
        logger('food !')
        time.sleep(3)
        if clickBtn(images['give-chicken'], name='give-chicken', timeout=5):
            food_attempts = food_attempts + 1
            logger('food gived')
            time.sleep(3)
    
    if food_attempts == 2:
        giveFood()
        food_attempts = 0

def goTavern():
    if clickBtn(images['tavern-button'],name='tavern-button', timeout=3):
        logger('tavern')
        time.sleep(3)
    exausted = positions(images['exausted'],threshold=ct['default'])
    claim_potion = positions(images['claim-button'],threshold=ct['default'])
    time.sleep(3) 
    if len(claim_potion) != 0:
        clickBtn(images['claim-button'])
    if len(exausted)!= 0:
        goTownRest()
    

def callBack():
    
    if clickBtn(images['finshed-working'], name='finshed-working', timeout=5):
        time.sleep(1)
        clickBtn(images['call-back'], name='call-back', timeout=3)
        time.sleep(1)
    


def goWork():
    if clickBtn(images['finished-resting'], name='finished-resting', timeout=5):
        time.sleep(2)
        clickBtn(images['call-back'])
        time.sleep(2)
        goTownRest()
    if clickBtn(images['go-work'], name='Go Work', timeout=5):
        time.sleep(2)
        clickBtn(images['send-work'])


def main():
    time.sleep(5)
    pyautogui.hotkey('ctrl','f5')
    t = c['time_intervals']
    windows = []
    Window = pygetwindow.getWindowsWithTitle('WorkerTown')

    for w in Window:
        windows.append({
            "window": w,
            "login" : 0,
            "food" : 0,
            "tavern" : 0,
            "finish-work" : 0,
            "goWork" : 0
            })

    while True:
        now = time.time()
        
        for last in windows:
            last["window"].activate()
            time.sleep(2)

            if now - last["login"] > addRandomness(t['check_for_login'] * 60):
                sys.stdout.flush()
                last["login"] = now
                #goTownRest() 
                
                """a = 0
                #b = 0
                a = positions(images['royal-bed-price'], threshold=ct['default'])
                #b = positions(images['royal-bed-crown'],threshold=ct['default'])
                print('buttons: {}'.format(len(a)))
                #print('buttons: {}'.format(len(b)))

                show(a) 
                #show(b)"""
                

                login()


            if now - last["tavern"] > addRandomness(t['go_tavern'] * 60):
                last["tavern"] = now
                goTavern()
            

            if now - last["food"] > addRandomness(t['give_food'] * 60):
                last["food"] = now
                time.sleep(3)
                giveFood()


            if now - last["finish-work"] > addRandomness(t['finish-work'] * 60):
                last["finish-work"] = now
                callBack()

            if now - last["goWork"] > addRandomness(t['goRest'] * 60):
                last["goWork"] = now
                goWork()

  
            logger(None, progress_indicator=True)

            sys.stdout.flush()

            time.sleep(1)
            
main()

    