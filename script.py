import random 
import pyautogui as pg 
import time

word = 'ae ri harsh bandariya' 
time.sleep(8)

for i in range(100):
    pg.write(word)
    pg.press('enter') 