# Lizard Body V9
# changelog
# update 8-3-25
# obfuscation
# Moved to GitHub
# Changed person configuration to use cvs instead of hard programming
# Update 2-11-25
# changed leadership naming for easier change of power
# Update 1-1-25
# 9: Made switchboards into csv file for easier reading and editing
#   changed status flag arrays to object properties
# Update 12-30-24
# 8:Added users and wifi functionality, changed file names
# Update 3-9-24
# 7: Functions now divided between 2 programs, one to administer the server
#   and this one to send regular notifications
#   ------------------------------------------
#   Will reset when it doesn't have valid IP
#   Added log file for pushes per month
# 6: Now with report requesting
# 5: Now with pushbullet
# 4: Now with classes
# 3: Now with selective notifications
from urllib.request import urlopen
import time, re, socket, os, pickle, csv
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64encode
# for dealing with attachment MIME types
from email.mime.text import MIMEText
from pushbullet import Pushbullet

time.sleep(120)

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("/home/pi/Documents/3D/Lizard/token.pickle"):
        with open("/home/pi/Documents/3D/Lizard/token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('/home/pi/Documents/3D/Lizard/info.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("/home/pi/Documents/3D/Lizard/token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


# get the Gmail API service
service = gmail_authenticate()
f = open("/home/pi/Documents/3D/Lizard/email.txt", "r")
emailAddress = f.read()
f.close()


def build_message(destination, obj, body):
    message = MIMEText(body)
    message['to'] = destination
    message['from'] = emailAddress
    message['subject'] = obj
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}


def send_message(service, destination, obj, body):  # send text/email
    return service.users().messages().send(
        userId='me',
        body=build_message(destination, obj, body)
    ).execute()


def push_send(subject, message, email):  # send pushbullet notification
    try:
        push = pb.push_note(subject, message, email=email)
        global pushes, remaining, reset
        current_file = "/home/pi/Documents/3D/Lizard/push_" + str(time.localtime()[1]) + ".txt"
        if os.path.isfile(current_file):
            f = open(current_file, "r")
            pushes = int(f.read())
            f.close()
        else:
            pushes = 0
        pushes += 1
        f = open(current_file, "w")
        f.write(str(pushes))
        f.close()
        remaining = push['rate_limit']['remaining']
        reset = int(push['rate_limit']['reset'])
    except:
        pass


class person:  # Person class
    def __init__(self, listedname, name):
        self.l = listedname
        self.n = name
        self.arr = 0
        self.here = 0
        self.left = 0


class personA(person):  # alerted person class
    def __init__(self, listedname, name, salutation, email, switchboard):
        person.__init__(self, listedname, name)
        self.s = salutation
        self.e = email
        self.sw = switchboard


class personP(personA):  # Pushbutton person class
    def send(self, subject, message):
        try:
            if afterFirst:
                push_send(subject, message, self.e)
        except:
            pass


class personT(personA):  # text person class
    def send(self, subject, message):
        try:
            if afterFirst:
                send_message(service, self.e, subject, message)
        except:
            pass

alerted = []
people = []

# pull switchboards from file and apply to alerted
f = open('/home/pi/Documents/3D/Lizard/data.csv', 'r')
csvFile = csv.reader(f)
data = []
for lines in csvFile:
    data.append(lines)
f.close()
del data[0]

for i in range(len(data)):
    if data[i][1] == 'P':
        alerted.append(personP(data[i][2], data[i][3], data[i][4], data[i][5], []))
        people.append(alerted[-1])
    elif data[i][1] == 'T':
        alerted.append(personT(data[i][2], data[i][3], data[i][4],data[i][5], []))
        people.append(alerted[-1])
    elif data[i][1] == 'R':
        people.append(person(data[i][2], data[i][3]))

switchboards = []
for i in range(len(alerted)):  # convert to int
    switchboards.append([])
    for k in range(6, 6+len(people)):
        switchboards[i].append(int(data[i][k]))

for i in range(len(alerted)):  # apply to alerted
    alerted[i].sw = switchboards[i]

# load current pushes
current_file = "/home/pi/Documents/3D/Lizard/push_" + str(time.localtime()[1]) + ".txt"
if os.path.isfile(current_file):
    f = open(current_file, "r")
    pushes = int(f.read())
    f.close()
else:
    pushes = 0

# setup pushbullet
key_file = "/home/pi/Documents/3D/Lizard/LizardGills.txt"
f = open(key_file, "r")
key = f.read()
f.close()
pb = Pushbullet(key)

afterFirst = 0
remaining = '0'
reset = 0
f=open("/home/pi/Documents/3D/Lizard/url.txt","r")
url=f.read()
f.close()
emailSubject = ''
roster = []
while len(roster) < 20:  # wait to get valid list of people
    try:
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode('utf-8')
        roster = re.findall('[A-Z][a-z]+, [A-Z][a-z]+', html)
    except:
        time.sleep(10)
        continue
# generate initial log of people
for i in range(len(people)):
    if people[i].l in html:
        people[i].here = 1
while True:
    if time.localtime()[2] == 1 and time.localtime()[3] == 1 and time.localtime()[4] < 3:
        pushes = 0
    try:
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode('utf-8')
        roster = re.findall('[A-Z][a-z]+, [A-Z][a-z]+', html)
    except:
        time.sleep(60)
        continue
    # Log people
    if len(roster) > 20:
        for i in range(len(people)):
            if people[i].l in html and people[i].arr == 0 and people[i].here == 0:  # just arrived
                people[i].arr = 1
                people[i].left = 0
            elif people[i].l in html and people[i].arr == 1:  # here
                people[i].arr = 0
                people[i].here = 1
            elif people[i].l not in html and (people[i].here == 1 or people[i].arr == 1):  # just left
                people[i].left = 1
                people[i].here = 0
                people[i].arr = 0
            elif people[i].l not in html:  # gone
                people[i].left = 0
                people[i].here = 0
                people[i].arr = 0
    try:
        last = pb.get_pushes(limit=1)[0]  # check for commands_____________________
    except:
        continue
    if last['body'].lower() == 'report':  # Report request
        emailContent = ''
        for i in range(len(people)):
            if people[i].arr == 1 or people[i].here == 1:  # check if person arrived
                if hasattr(people[i], 'e'):  # exclude requester
                    if last['sender_email'] != people[i].e:
                        emailContent += people[i].n + ' '
                else:
                    emailContent += people[i].n + ' '
        emailContent += 'here.'
        if len(emailContent) == 5:
            emailContent = 'No one is here.'
        push_send('', emailContent, last['sender_email'])

    elif last['body'].lower() == 'stats':  # Stats request_________________________
        emailContent = str(pushes + 1) + ' total pushes. ' + str(remaining) + ' rate left.' + str(
            int(reset - time.time())) + ' time till reset.'
        push_send('', emailContent, last['sender_email'])

    elif last['body'].lower() == 'roster':  # list of all people request___________________
        push_send('', '\n'.join(roster), last['sender_email'])

    # send messages out
    for i in range(len(alerted)):
        if alerted[i].arr == 1:  # message on arrival
            if time.localtime()[3] < 12:
                emailContent = 'Good Morning ' + alerted[i].s + '.'
            elif time.localtime()[3] >= 12:
                emailContent = 'Good Evening ' + alerted[i].s + '.'
            if i == 0:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
                emailContent += ' My IP address is ' + local_ip + '. ' + str(
                    pushes + 1) + ' total pushes. ' + remaining + ' rate left.' + str(
                    int(reset - time.time())) + ' time till reset.'
                s.close()
            nList = []
            for j in range(len(people)):  # Build notification list
                if (people[j].here == 1 or people[j].arr == 1) and alerted[i].sw[j] > 0:
                    nList.append(people[j].n)
            if len(nList) == 1:
                emailContent = emailContent + ' ' + nList[0] + ' is also here.'
            elif len(nList) > 1:
                emailContent = emailContent + ' Some people are here: ' + ', '.join(nList) + '.'
            alerted[i].send(emailSubject, emailContent)
        elif alerted[i].here == 1:  # standard messages
            for j in range(len(people)):
                if people[j].arr == 1 and alerted[i].sw[j] > 0:  # check if person arrived
                    emailContent = people[j].n + ' is here.'
                    alerted[i].send(emailSubject, emailContent)
                if people[j].left == 1 and alerted[i].sw[j] > 1:  # check if person just left
                    emailContent = people[j].n + ' has left.'
                    alerted[i].send(emailSubject, emailContent)

    time.sleep(60)
    afterFirst = 1