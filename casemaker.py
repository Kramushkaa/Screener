from PIL import Image, ImageDraw, ImageFont
import os
import csv
from urllib.request import urlopen, urlretrieve
from urllib.parse import quote
import ssl
import wand.image
 
# from cairosvg import svg2png

dirname = os.path.dirname(__file__)
spreadsheet_location=dirname
tournament_name="S3O4Q4D2"
output_directory= os.path.join(dirname,"screenshots")

def main(spreadsheet_location,tournament_name,output_directory):
    players_list=[]
    with open(os.path.join(spreadsheet_location,"%s.csv" %tournament_name),encoding="utf-8") as File:
        reader = csv.DictReader(File)
        for row in reader:
            players_list.append(row)

    for i in range(len(players_list)):
        deck_list=[]
        player_name=players_list[i]["Challonge"]
        # if players_list[i]["Truename"]:
        #     printed_name=players_list[i]["Truename"]
        # else:
        printed_name=players_list[i]["Challonge"]
        print(player_name)
        background = Image.open(os.path.join(output_directory,"templateQbg.png"), 'r')
        ability_offset = [[845,45],[1315,45],[1785,45],[2250,45]]
        deck_offset = [[721,223],[1192,223],[1660,223],[2130,223]]
        for key in players_list[i]:
            if key[:1]=="F" and len(key)==2:
                deckname=players_list[i][key].replace(" ","_").replace("/","").replace("'","")
                print(int(key[1]))
                deck_list.append(player_name.replace(" ","_").replace("/","")+ "_" + deckname)
                with Image.open(os.path.join(output_directory,"check","%s.png" %deck_list[int(key[1])-1]), 'r')  as img:
                    width,hight = img.size
                    if hight > 1210:
                        img = img.resize((width*1210//hight, 1210))
                        deck_offset[int(key[1])-1][0]+=(width-width*1210//hight)//2
                    background.paste(img, deck_offset[int(key[1])-1])
                deckname=deckname[5:]
                try:
                    with Image.open(os.path.join(output_directory,"Logos", "%s.png" %deckname), 'r') as im:
                        background.paste(im, ability_offset[int(key[1])-1], im.convert('RGBA'))
                except Exception as ex:
                    print(ex)
            if key=="Team":
                try:
                    with Image.open(os.path.join(output_directory,"Logos", "Team-%s.png" %players_list[i][key] ), 'r') as im:
                        background.paste(im, (100,800), im.convert('RGBA'))
                except Exception as ex:
                    print(ex)

        try:
            fnt = ImageFont.truetype(os.path.join(spreadsheet_location,"NotoSansJP.otf"),48)
            image_editable = ImageDraw.Draw(background)
            i=2
            while fnt.getlength(printed_name)>475:
                fnt=ImageFont.truetype(os.path.join(spreadsheet_location,"NotoSansJP.otf"),48-i)
                i+=2
            image_editable.text((351-fnt.getlength(printed_name)/2,650), printed_name, "black", size=40, font=fnt)
        except Exception as ex:
            print(ex)

        flag=os.path.join(output_directory,"flagtmp.png")
        try:
            if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
                ssl._create_default_https_context = ssl._create_unverified_context
            fnt = ImageFont.truetype(os.path.join(spreadsheet_location,"NotoSansJP.otf"),48)
            url = "http://masters.playgwent.com/en/rankings/masters-3/season-of-the-draconid/1/1/" + quote(player_name)
            html = str(urlopen(url).read())
            print("good")
            html=html[html.find("flag-icon-",html.find("c-ranking-table__tr")):]
            country=html[10:html.find('"')]

            image_editable.text((348-fnt.getlength(country.upper()),745), country.upper(), "black", size=40, font=fnt)
            url= "http://masters.playgwent.com/build/css/rankings-42b6285abc0113bfd21f.css"
            print("better")
            html= str(urlopen(url).read())
            link= html[html.find("flag-icon-"+country)+34:]
            link= "http://masters.playgwent.com" + link[:link.find(".svg")+4]
            try:
                urlretrieve(link,os.path.join(output_directory,"flagtmp.svg"))
                img = wand.image.Image(filename =os.path.join(output_directory,"flagtmp.svg"))
                img_convert = img.convert('png')
                img_convert.save(filename=flag)
                # svg2png(bytestring=img,write_to=flag)
                with Image.open(flag) as im:
                    print("opened")
                    im=im.resize((64,48))
                    background.paste(im, (363,761))
            except:
                print("Error with flag")

        except Exception as ex:
            print(ex)
        
        # background.show()

        background.save(os.path.join(output_directory, '%s' % tournament_name, '%s.png' % player_name.replace(" ","_").replace("/","")))


if __name__ == "__main__":
    main(spreadsheet_location,tournament_name,output_directory)