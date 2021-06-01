import psycopg2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import os
import time
import threading
from selenium import webdriver
import requests
from decouple import config

TOKEN = config("TOKEN")
PORT = int(config('PORT', 5000))
DATBASE_URL = confif("DATBASE_URL")


def fetch(ID):
    query = """SELECT * from quoradbs where id = %s"""%ID
    cur.execute(query)
    data = cur.fetchall()
    try:
        return data[0]
    except:
        return False
    
def insert(ID, url, num, uname):
    cur.execute("""INSERT into quoradbs (ID, URL, NUM, UNAME) VALUES (%s,'%s', %s, '%s')"""%(ID,url,num,uname))
    conn.commit()

def update(ID, num):
    cur.execute("UPDATE quoradbs SET num = %s WHERE id = %s;"%(num, ID))
    conn.commit()

def execute(qur):
    cur.execute(qur)
    try:
        conn.commit()
        return cur.fetchall()
        
    except:
        conn.commit()
        return False

def exists(url):
    data = execute("Select COUNT(*) from quoradbs where url = '%s'"%url)
    return bool(data[0][0])
    

# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--no-sandbox")
# driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
##driver = webdriver.Chrome("C:/Users/pc/Desktop/Work/New folder (3)/drivers/chromedriver/win32/88.0.4324.96/chromedriver.exe")

def executeit(bot, update):
    message = update.message.text
    message = message.replace("/execute","")
    message = message.strip()
    data = execute(message)
    if data:
        update.message.reply_text(str(data))
    else:
        update.message.reply_text("Command successfully executed")

def get_answers(url):
    global case
    count = 0
    print(url)
    try:
        if "www.quora.com/" in url:
            cont = requests.get(url+"/answers").text#driver.get(url+"/answers")
            #elemen = driver.find_element_by_xpath('//*[@id="root"]/div/div/div/div/div[4]/div/div[1]/div[3]/div/div[3]/div/div[1]/div')
            #data = (elemen.text).split()[0]
            data = cont.replace("\\","").split(""""numPublicAnswers":""")[1].split(",")[0]
            numofans = data
            case = True
            return numofans, f"Account registered, you have written {numofans} answer/s\nYou will be notified when any of your answers collapses."
                    
        else:
            case = False
            return "Ankit", "Account not found or invalid URL"
    except Exception as e:
        print(e)
        case = False
        return url, "URL not found, enter valid URL"



def sendtoowner(message):
    robot = telegram.Bot(TOKEN)
    robot.sendMessage(561489747,message)
    
def runforever():
    robot = telegram.Bot(TOKEN)
    while "do forever":
        datas = execute("SELECT * From quoradbs")
        for lines in datas:
            try:
                print(lines)
                data = lines
                olddata = lines
                oldnum = data[2]
                rand = data[3]
                content = get_answers(data[1])
                newnum = content[0]
                print(newnum)
                if int(oldnum) > int(newnum):
                    if int(oldnum) - int(newnum) > 1:
                        singplu = "answers are"
                    else:
                        singplu = "answer is"
                    robot.sendMessage(data[0],f"{int(oldnum) - int(newnum)} {singplu} not visible in your account.\nIn case you haven't deleted any answer in past sixty minutes, it might have collapsed.")
                    update(data[0], newnum)
                if int(oldnum) < int(newnum):
                    robot.sendMessage(data[0],"Congratulations for writing one or more new answer(s).\nIn case you have restored any previous answer, ignore this message.")
                    update(data[0], newnum)
            except Exception as e:
                print(e)
                pass
        time.sleep(300)
         



def start(bot, update):
    global case
    print(case)
    case = False
    message = update.message.text
    message = message.replace("/notify","")
    message = message.strip()
    print("Message is " +message)

    urlq = message.split("?")
    message = urlq[0]

    if not message:
        update.message.reply_text("Invalid command")

    elif exists(message):
        update.message.reply_text("This account has already been registered")

    else: 
        out = get_answers(message)
        chat_id = update.message.chat_id
        if case:
            print("here")
            insert(chat_id, message, out[0], "@"+update.effective_user.username)
            #file.close()
            case = False
            sendtoowner(f"{chat_id} {message} {out[0]} @{update.effective_user.username}")
        update.message.reply_text(out[1])
        

def data(bot, update):
    username = update.effective_user.username
    print(username)
    if username == "Tag_kiya_kya":
        bot.send_document(chat_id=update.message.chat.id, document=open("bot.py","rb"))

    else:
        update.message.reply_text("Command for admins only, you can not access the database.")
    
def help(bot, update):
    """Send a message when the command /help is issued."""
    chat_id = update.message.chat_id
    update.message.reply_text('None')#,reply_markup=reply_markup)

def main():
    updater = Updater(TOKEN)#, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('notify',start))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('database',data))
    #dp.add_handler(CommandHandler('execute', executeit))
##    updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
    updater.bot.setWebhook('https://collapsedquora.herokuapp.com/' + TOKEN)
    updater.idle()

if __name__ == '__main__':
    threading.Thread(target=runforever).start()
    main()





# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# import telegram
# #from urllib.request import urlopen
# #from telegram import Update, Bot
# #import json
# import os
# import time
# import threading
# from selenium import webdriver
# import requests as req

# chrome_options = webdriver.ChromeOptions()
# chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--no-sandbox")
# driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

# ##driver = webdriver.Chrome("C:/Users/pc/Desktop/Geet/chromedriver.exe")
# TOKEN = os.environ.get("TOKEN")
# ## PORT = int(os.environ.get('PORT', 5000))
# case = False
# url = "http://ankitrajmahapatra22200112.000webhostapp.com/quoradbs.php?action="


# ##def get_answers(url):
# ##    global case
# ##    count = 0
# ##    print(url)
# ##    #send()
# ##    try:
# ##        cont = requests.get(url)
# ##        if cont.status_code == 200:
# ##            data = cont.content
# ##            data = str(data)
# ##            lst = data.split("\\\\")
# ##            #print('"numPublicAnswers' in lst)
# ##            for i in lst:
# ##                count+=1
# ##                if i == '"numPublicAnswers':
# ##                    numofans = lst[count].replace('":',"").replace(",","")
# ##                    case = True
# ##                    return numofans, f"Account registered, you have written {numofans} answers\nYou will be notified when any of your answer collapses."
# ##        else:
# ##            return "Account not found or invalid URL"
# ##    except:
# ##        return "URL not found"

# def manage(action,data=None):
#     if action == "r":
#         res = req.get(url+"read")
#         data = res.content
#         return data.decode()
#     if action == "w":
#         res = req.get(f"{url}write&data={data}-")
#     if action == "a":
#         res = req.get(f"{url}append&data={data}-")

# def get_answers(url):
#     global case
#     count = 0
#     print(url)
#     #send()
#     try:
#         cont = driver.get(url)
#         if "www.quora.com/" in url:
#             elemen = driver.find_elements_by_xpath('//*[@class="q-text qu-medium qu-fontSize--small qu-color--red"]')[1]
#             data = (elemen.text).split()[0]
#             numofans = data
#             case = True
#             return numofans, f"Account registered, you have written {numofans} answer/s\nYou will be notified when any of your answers collapses."
#             #lst = data.split("\\\\")
#             #print('"numPublicAnswers' in lst)
# ##            for i in lst:
# ##                count+=1
# ##                if i == '"numPublicAnswers':
# ##                    numofans = lst[count].replace('":',"").replace(",","")
# ##                    case = True
                    
#         else:
#             case = False
#             return "Ankit", "Account not found or invalid URL"
#     except Exception as e:
#         print(e)
#         case = False
#         return url, "URL not found, enter valid URL"

# def updatetxt(oldnum, olddata, newnum, lines):
#     newdata = lines.replace(" "+oldnum," "+newnum)
#     cont = manage("r")
# ##    cont = file.read()
#     cont = cont.replace(olddata,newdata)
# ##   file.close()
#     manage("w",cont)
# ##    file = open("C:/Users/pc/Desktop/database.txt","w")
# ##    file.write(cont)
# ##    file.close()
# ####    newdata = lines.replace(" "+oldnum," "+newnum)
# ####    file = open("requirements.txt")
# ####    cont = file.read()
# ####    cont = cont.replace(olddata,newdata)
# ####    file.close()
# ####    file = open("requirements.txt","w")
# ####    file.write(cont)
# ####    file.close()

# def sendtoowner(message):
#     robot = telegram.Bot(TOKEN)
#     robot.sendMessage(561489747,message)
    
# def runforever():
#     robot = telegram.Bot(TOKEN)
#     while "do forever":
#         data = manage("r")
#         allline = data.split("\n")
#         for lines in allline:
                    
#             try:
#                 lines = lines.strip()
#                 print(lines)
#                 data = lines.split()
#                 olddata = lines
#                 oldnum = data[2]
#                 rand = data[3]
#                 content = get_answers(data[1])
#                 newnum = content[0]
#                 print(newnum)
#                 if int(oldnum) > int(newnum):
#                     if int(oldnum) - int(newnum) > 1:
#                         singplu = "answers are"
#                     else:
#                         singplu = "answer is"
#                     robot.sendMessage(data[0],f"{int(oldnum) - int(newnum)} {singplu} not visible in your account.\nIn case you haven't deleted any answer in past sixty minutes, it might have collapsed.")
#                     updatetxt(oldnum = oldnum, olddata = olddata, newnum = newnum, lines = lines)
#                  #   newdata = lines.replace(" "+oldnum," "+newnum)
#                 if int(oldnum) < int(newnum):
#                     robot.sendMessage(data[0],"Congratulations for writing one or more new answer(s).\nIn case you have restored any previous answer, ignore this message.")
#                     updatetxt(oldnum = oldnum, olddata = olddata, newnum = newnum, lines = lines)
#             except Exception as e:
#                 print(e)
#                 pass
#         time.sleep(300)
         



# def start(bot, update):
#     global case
#     print(case)
#     case = False
#     message = update.message.text
#     message = message.replace("/notify","")
#     message = message.strip()
# ##    file = open("requirements.txt")
#     data = manage("r")
# ##    file.close()
#     print("Message is " +message)

#     urlq = message.split("?")
#     message = urlq[0]

#     if not message:
#         update.message.reply_text("Invalid command")

#     elif message in data:
#         update.message.reply_text("This account has already been registered")

#     else: 
#         out = get_answers(message)
#         chat_id = update.message.chat_id
#         if case:
#             print("here")
#             #file = open("requirements.txt","a")
#             manage("a",f"\n{chat_id} {message} {out[0]} @{update.effective_user.username}")
#             #file.close()
#             case = False
#             sendtoowner(f"{chat_id} {message} {out[0]} @{update.effective_user.username}")
#         update.message.reply_text(out[1])
        
# ##def savedbs(bot,update):
# ##    username = update.effective_user.username
# ##    name = update.message.document.file_name
# ##    print(name)
# ##    if name == "requirements.txt":
# ##        if username == "Tag_kiya_kya":
# ##            file = bot.getFile(update.message.document.file_id)
# ##            file.download("requirements.txt")
# ##            update.message.reply_text("File accepted")
        

# ##    else:
# ##        update.message.reply_text("Only admins can update database by sending documents.")

# def data(bot, update):
#     username = update.effective_user.username
#     print(username)
#     if username == "Tag_kiya_kya":
#         bot.send_document(chat_id=update.message.chat.id, document=open("bot.py","rb"))

#     else:
#         update.message.reply_text("Command for admins only, you can not access the database.")
    
# def help(bot, update):
#     """Send a message when the command /help is issued."""
#     chat_id = update.message.chat_id
#     update.message.reply_text('None')#,reply_markup=reply_markup)

# def main():
#     updater = Updater(TOKEN)#, use_context=True)
#     dp = updater.dispatcher
#     dp.add_handler(CommandHandler('notify',start))
#     dp.add_handler(CommandHandler('help',help))
#     dp.add_handler(CommandHandler('database',data))
#     #dp.add_handler(MessageHandler(Filters.document,savedbs))
# ##    updater.start_polling()
#     updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
#     updater.bot.setWebhook('https://collapsedquora.herokuapp.com/' + TOKEN)
#     updater.idle()

# if __name__ == '__main__':
# ##    try:
# ##        open("database.txt")
# ##    except:
# ##        file = open("database.txt","w")
# ##        file.close()
#     threading.Thread(target=runforever).start()
#     main()
