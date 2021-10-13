from PIL import Image
import csv
import os
# from multiprocessing import Queue,Process
from queue import Queue
# getting url list
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

logger=1

tournament_name = "correct"
dirname = os.path.dirname(__file__)
LOGLIST = os.path.join(dirname,"loglist.txt")
crop_ability = False
output_directory= os.path.join(dirname,"screenshots")
spreadsheet_location=dirname

def players_list_maker(spreadsheet_location,tournament_name):
    players_list=[]
    with open(os.path.join(spreadsheet_location,"%s.%s" %(tournament_name,'csv')),encoding="utf-8") as File:
        reader = csv.DictReader(File)
        for row in reader:
            players_list.append(row)
    return players_list

def url_fixer(a,players_list,screenshot_number):
    global LOGLIST
    for i in range(len(players_list)):
        url=[]
        deck=[]
        
        for key in players_list[i]:
            if key[:4]=="Deck":
                if players_list[i][key].find("playgwent.com/")!=-1:
                    players_list[i][key] = "https://www.playgwent.com/" + language + players_list[i][key][players_list[i][key].find("/decks"):].replace(" ","")
                    if len(players_list[i][key])!=67:         #if some error with link occured, mark the deck number and record to log 
                        with open(LOGLIST, 'a') as loglist:
                            loglist.write("wrong link %s \n" %players_list[i][key])
                            continue
                    else:
                        url.append(players_list[i][key])
                        screenshot_number+=1
            if key[:1]=="F" and len(key)==2:
                deckname=players_list[i][key].replace(" ","_").replace("/","").replace("'","")
                deck.append(players_list[i]["Challonge"].replace(" ","").replace("/","").replace("'","")+ "_" + deckname)
        for j in range(len(url)):
            print(url[j],deck[j])
            a.put((url[j],deck[j]))
    return screenshot_number

    
#POSTPROCESSING
def postproc(a,q,screenshots_to_do,tournament_name,output_directory,crop_ability):
    while (True):
        if screenshots_to_do == 0:
            print("Всё!")  
            break
        global LOGLIST
        Path=os.path.join(output_directory, '%s' % tournament_name)
        Pathtmp=os.path.join(output_directory, 'tmp')
        os.makedirs(Path, exist_ok=True)
        if q.empty():
            break
        url,deck = q.get()
        if logger:
            print("postprocing",deck)
        try: 
            address= os.path.join(Pathtmp, ('%s.%s' % (deck, "png")))
            img = Image.open(address).convert("RGB")
            img = img.resize((1200,1790))

            #Compare color of the img zone with the faction color in case there's a cookie
            pix = img.load()
            if logger:
                print(deck,"pix loaded")
            try:
                faction=deck[deck.find("_[")+2:deck.find("_[")+4]

                if pix[300, 400] == (41,12,8): 
                    if not(faction == "MO"):
                        with open (LOGLIST, 'a') as loglist:
                            loglist.write("deck %s is MO, not %s\n" % deck,faction)
                elif pix[300, 400] == (31,28,39):
                    if not(faction == "SK"):
                        with open (LOGLIST, 'a') as loglist:
                            loglist.write("deck %s is SK, not %s\n" % deck,faction)
                elif pix[300, 400] == (21,21,11):
                    if not(faction == "ST"):
                        with open (LOGLIST, 'a') as loglist:
                            loglist.write("deck %s is ST, not %s\n" % deck,faction)
                elif pix[300, 400] == (12,22,31):
                    if not(faction == "NR"):
                        with open (LOGLIST, 'a') as loglist:
                            loglist.write("deck %s is NR, not %s\n" % deck,faction)
                elif pix[300, 400] == (18,16,19): 
                    if not(faction == "NG"):
                        with open (LOGLIST, 'a') as loglist:
                            loglist.write("deck %s is NG, not %s\n" % deck,faction)
                elif pix[300, 400] == (51,24,5):
                    if not(faction == "SY"):
                        with open (LOGLIST, 'a') as loglist:
                            loglist.write("deck %s is SY, not %s\n" % deck,faction)
            except:
                pass
            #if no cookie notification -- img must be OK
            rl=[]
            x=131
            for y in range(1190,img.size[1]):
                rl.append(sum(pix[x, y])) #узнаём значение красного цвета пикселя
                if y>1210:  
                    if rl[y-1190]<49 and rl[y-1210]<49:
                        break
            if crop_ability == True:          
                left, top, right, bottom = 128, 510, 530, y-17 #no ability
            else:
                left, top, right, bottom = 128, 428, 530, y-17 #with ability
            img_res = img.crop((left, top, right, bottom))
            player_name=deck[:deck.find("_[")]
            New_Path=os.path.join(Path, player_name)
            os.makedirs(New_Path, exist_ok=True)
            img_res.save(os.path.join(New_Path, '%s.png' % deck))
            img_res.save(os.path.join(output_directory,"check", '%s.png' % deck))
            print("Good " + deck)
            screenshots_to_do-=1
            # if logger:
            print (screenshots_to_do)
            # Cleanup screen folder
            os.remove(os.path.join(Pathtmp, '%s.png' % deck))

        except Exception as Ex:
            print("exception raised while postprocing",deck)
            print(Ex)
            with open(LOGLIST, 'a') as loglist:
                loglist.write("Some error occured with link %s in deck %s \n" %(url,deck))

def screenshoot(a,q,output_directory):
    Pathtmp=os.path.join(output_directory, 'tmp')
    os.makedirs(Pathtmp, exist_ok=True)
    while True:
        if a.empty():
            break
        url,deck=a.get()

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        driver = webdriver.Chrome(executable_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),"chromedriver"), options=chrome_options)

        driver.get(url)
        time.sleep(1)
        try:
            clearbutton = driver.find_element_by_css_selector("#CybotCookiebotDialogBodyButtonAccept")
            clearbutton.click()
            if logger:
                print("clicked")
        except:
            if logger:
                print("not found")
        time.sleep(0.5)
        driver.set_window_size(1200, 1790)
        driver.save_screenshot(os.path.join(Pathtmp, deck) + '.png')
        driver.quit()

        if logger:
            print(deck,"shot")
        q.put((url,deck))


def main(language,spreadsheet_location,tournament_name,output_directory,crop_ability):
    global LOGLIST
    #Cleaning the log
    open(LOGLIST, 'w').close()

    #Getting content out of CSV file
    players_list = players_list_maker(spreadsheet_location,tournament_name)

    #Making lists of names and links
    a = Queue()
    q = Queue()
    screenshot_number=url_fixer(a,players_list,0)

    # while True:
    screenshoot(a,q,output_directory)

    postproc(a,q,screenshot_number,tournament_name,output_directory,crop_ability)


    # screenshot_number=a.qsize()
    # q=Queue()

    # process_one = Process(target=screenshoot, args=(a,q,output_directory))
    # process_two = Process(target=postproc, args=(a,q,screenshot_number,tournament_name,output_directory,crop_ability))
    
    # process_one.start()
    # process_two.start()
    
    # while True:
    #     if not process_two.is_alive():
    #         process_one.kill()
    #         break

    # q.close()
    # q.join_thread()
    
    # process_one.join()
    # process_two.join()

    with open(LOGLIST,"r") as f:
        a=f.read()
        print(a)

if __name__ == "__main__" :
    language = "en"
    main(language,spreadsheet_location,tournament_name,output_directory,crop_ability)