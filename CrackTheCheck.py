#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=E1101

import pytesseract, sys, cv2, numpy as np
from selenium import webdriver
from PIL import Image, ImageEnhance
from subprocess import check_output
from time import sleep
from pynput.mouse import Button, Controller

# Benutzereinstellungen
name = 'paula88'        # GoC Name
pwd = '123456'          # GoC Passwort
delay = 2.5             # Verzögerungen in Sekunden
trainieren = False      # Training an und abschalten (False / True)
max_fails = 3           # Nach wievielen Versuchen abgebrechen?

# System Variablen
training = []
failed = 0

# Auto Security Check
def auto_check(driver):
    global name
    global pwd
    global delay
    global trainieren
    global training
    global max_fails
    global failed
    if 'Gangs of Crime' in driver.title:
        ''' 
        Status: Eingeloggt
        '''
        pass
    elif 'Security' in driver.title:
        ''' 
        Status: Security Check
            -> Screenshot
            -> Captcha auschneiden
            -> Ocr - Captcha lesen
            -> Ocr Text mit Training vergleichen
            -> Bild Position bestimmen
            -> Maus auf Bild bewegen
            -> Mausklick auf Bild
            -> Ergebniss prüfen
            -> Training
         '''
        ocr_text = None
        resultat = None
        koordinaten = None
        while ocr_text is None:
            driver.save_screenshot('screenshot.png')
            ipt = 'screenshot.png'
            img = Image.open(ipt)
            cropbox = (410, 196, 850, 255)
            captcha = img.crop(cropbox)
            captcha.save('captcha.png')
            captcha = pytesseract.image_to_string(Image.open('captcha.png'), lang='deu', 
                config='-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
            ocr_text = captcha.replace(' ', '').lower()
            if len(ocr_text) < 3 or '\n' in ocr_text:
                ocr_text = None
                driver.refresh()
                sleep(delay)
            else:
                ''' Training vergleichen '''
                namen_liste = ['schmetterling', 'kleeblatt', 'flugzeug', 'telefon', 'sonne', 'hund', 'katze', 'feuer', 'herz']
                ordner_training = sys.path[0] + '/Training/'
                datei_endung = '.txt'
                for n in namen_liste:
                    pfad = ordner_training + n + datei_endung
                    with open(pfad, 'r') as liste:
                        for wort in liste:
                            if wort.strip('\n') in ocr_text:
                                resultat = n
                if resultat is None:
                    training.append(ocr_text)
                    ocr_text = None
                    driver.refresh()
                    sleep(delay)
        ''' Bild Position bestimmen '''
        vgl_obj = sys.path[0] + '/Vergleichsobjekte/sw_' + resultat + '.bmp'
        while koordinaten is None:
            img_rgb = cv2.imread('screenshot.png')
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(vgl_obj,0)
            res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            loc = np.where(res >= threshold)
            try:
                ''' Bild anklicken '''
                koordinaten = str(loc[0][0] + 100) + '-' + str(loc[1][0] + 100)
                xy = koordinaten.split('-')
                mouse = Controller()
                mouse.position = (int(xy[1]), int(xy[0]))
                mouse.move(55, 200)
                mouse.press(Button.left)
                mouse.release(Button.left)
                sleep(delay)
                ''' Ergebniss prüfen '''
                if 'Gangs of Crime' in driver.title:
                    if trainieren:
                        ''' Training '''
                        with open(pfad, 'a') as liste:
                            for eintrag in training:
                                liste.write(eintrag.encode('ascii', 'ignore').decode('ascii') + '\n')
                    del training[:]
                else:
                    ''' Wenn kein Erfolg - neu starten '''
                    failed = failed + 1
                    if failed < max_fails:
                        auto_check(driver)
                    else:
                        print '[!] Max Fails wurden erreicht'
            except:
                koordinaten = None
                driver.refresh()
                sleep(delay)
                driver.save_screenshot('screenshot.png')
    elif 'Strategiespiele' in driver.title:
        ''' 
        Status: Ausgeloggt 
            -> Einloggen
        '''
        driver.find_element_by_xpath('//input[@id="psgaslogin_username_input"]').send_keys(name)
        driver.find_element_by_xpath('//input[@id="psgaslogin_password_input"]').send_keys(pwd)
        driver.find_element_by_xpath('//input[@id="psgaslogin_submit_input"]').click()
        sleep(delay)
        auto_check(driver)
    else:
        ''' 
        Status: falsche Url
            -> GoC aufrufen
        '''
        driver.get('http://gangsofcrime.de/')
        sleep(delay * 3)
        auto_check(driver)


if __name__ == '__main__':
    if trainieren:
        print '[*] Crack the Check - Training'
    else:
        print '[*] Crack the Check - Demo'
    print '[+] Webdriver erstellen'
    driver = webdriver.Firefox()
    print '[+] Gangs of Crime aufrufen'
    driver.get('http://gangsofcrime.de/')
    runden = int(raw_input('[?] Runden: '))
    for i in range(runden):
        print '[+] Einloggen\n[+] Autocheck'
        auto_check(driver)
        print '[*] Winner Winner Chicken Dinner'
        sleep(delay * 2)
        print '[+] Ausloggen'
        driver.find_element_by_xpath('//img[@id="logout"]').click()
        sleep(delay)
    driver.quit()
    print '[+] Beendet'
