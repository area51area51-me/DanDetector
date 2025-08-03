#Admin V2
#changelog
# 8-3-25
# obfuscation
# added to GitHub

#1: All administration function has been moved to this program to prevent locks
import time, socket, os, requests
from pushbullet import Pushbullet
time.sleep(90)
# wait on boot to get internet connection established and config changes
#check to see if ip address is valid
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 80))
local_ip=s.getsockname()[0]
if int(local_ip.split('.')[0])!=10:
    os.system("sudo reboot")

def push_send(subject,message,email):  # send pushbullet notification
    try:
        push=pb.push_note(subject,message,email=email)
        current_file="/home/pi/Documents/3D/Lizard/push_"+str(time.localtime()[1])+".txt"
        if os.path.isfile(current_file):
            f=open(current_file,"r")
            pushes=int(f.read())
            f.close()
        else:
            pushes=0
        pushes+=1
        f=open(current_file,"w")
        f.write(str(pushes))
        f.close()
    except:
        pass

f=open("/home/pi/Documents/3D/Lizard/LizardGills.txt","r")
key=f.read()
f.close()
pb=Pushbullet(key)

f=open("/home/pi/Documents/3D/Lizard/links.txt","r")
links=f.read()
f.close()
links=links.split('\n')
links.insert(0,'')

while True:
    #check to see if device got banned and reboot
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip=s.getsockname()[0]
    except:
        time.sleep(10)
        continue
    if int(local_ip.split('.')[0])!=10:
        os.system("sudo reboot")
    try:
        last = pb.get_pushes(limit=1)[0]  # check for commands_____________________
    except:
        time.sleep(10)
        continue
    if last['body'].lower()=='ip': #IP address request_________________________
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip=s.getsockname()[0]
        emailContent=' My IP address is ' + local_ip + '. '
        s.close()
        push_send('', emailContent,last['sender_email'])
    elif last['body'].lower()=='reboot':  # reboot request_______________________
        push_send('', 'Server reboot',last['sender_email'])
        os.system("sudo reboot")
    elif 'download' in last['body'].lower():  # Download new version of lizard
        try:
            downloadUrl=links[int(last['body'].split(' ')[1])]
            response=requests.get(downloadUrl)
            if int(last['body'].split(' ')[1]) == 1:
                open('/home/pi/Documents/3D/Lizard/LizardBodyV9.py','wb').write(response.content)
                push_send('', 'New Detector version ready',last['sender_email'])
            elif int(last['body'].split(' ')[1]) == 2:
                open('/home/pi/Documents/3D/Lizard/LizardHeadV2.py','wb').write(response.content)
                push_send('', 'New Admin version ready',last['sender_email'])
            else:
                push_send('', 'No download',last['sender_email'])
        except:
            push_send('', 'Error', last['sender_email'])
    time.sleep(60)