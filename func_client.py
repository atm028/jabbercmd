#!/usr/bin/python

# $Id: test_client.py,v 1.11 2003/11/08 06:37:36 snakeru Exp $

# You may need to change the above line to point at
# python rather than python2 depending on your os/distro
from subprocess import Popen, PIPE
import socket
from select import select
from string import split,strip,join
import sys,os

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import jabber

True = 1
False = 0

# Change this to 0 if you dont want a color xterm
USE_COLOR = 1

Who = ''
MyStatus = ''
MyShow   = ''

#jabber.xmlstream.ENCODING='koi8-r'      # Default is "utf-8"

def messageCB(con, msg):
    """Called when a message is recieved"""
    if msg.getBody(): ## Dont show blank messages ##
	if msg.getBody() == "IP":
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("gmail.com", 80))
		txt = s.getsockname()[0]
		s.close()
		msg = jabber.Message("timmoor@jabber.ru", strip(txt))
            	msg.setType('chat')
            	con.send(msg)
	if msg.getBody() == "PROC":
		process = Popen(['ps', '-eo' ,'pid,args'], stdout=PIPE, stderr=PIPE)
		stdout, notused = process.communicate()
		process_list = "\r\n"
		for line in stdout.splitlines():
		        pid, cmdline = line.split(' ', 1)
		        if cmdline.count("confserv_64") != 0:
		            process_list += "confserv \r\n"
		        if cmdline.count("multiserver_64") != 0:
		            process_list += "dbserver \r\n"
		        if cmdline.count("MessageServer_64") != 0:
		            process_list += "Message server \r\n"
		        if cmdline.count("sip_server") != 0:
		            process_list += "sip_server \r\n"
		        if cmdline.count("urs_server") != 0:
		            process_list += "urs_server \r\n"
		        if cmdline.count("SIPProxy") != 0:
		            process_list += "sipproxy \r\n"

		msg = jabber.Message("timmoor@jabber.ru", process_list)
            	msg.setType('chat')
            	con.send(msg)


#        print colorize(
#            u'<' + str(msg.getFrom()) + '>', 'green'
#            ) + ' ' + msg.getBody()

def presenceCB(con, prs):
    """Called when a presence is recieved"""
    who = str(prs.getFrom())
    type = prs.getType()
    if type == None: type = 'available'

    # subscription request: 
    # - accept their subscription
    # - send request for subscription to their presence
    if type == 'subscribe':
        print colorize(u"subscribe request from %s" % (who), 'blue')
        con.send(jabber.Presence(to=who, type='subscribed'))
        con.send(jabber.Presence(to=who, type='subscribe'))

    # unsubscription request: 
    # - accept their unsubscription
    # - send request for unsubscription to their presence
    elif type == 'unsubscribe':
        print colorize(u"unsubscribe request from %s" % (who), 'blue')
        con.send(jabber.Presence(to=who, type='unsubscribed'))
        con.send(jabber.Presence(to=who, type='unsubscribe'))

    elif type == 'subscribed':
        print colorize(u"we are now subscribed to %s" % (who), 'blue')

    elif type == 'unsubscribed':
        print colorize(u"we are now unsubscribed to %s"  % (who), 'blue')

    elif type == 'available':
        print colorize(u"%s is available (%s / %s)" % \
                       (who, prs.getShow(), prs.getStatus()),'blue')
    elif type == 'unavailable':
        print colorize(u"%s is unavailable (%s / %s)" % \
                       (who, prs.getShow(), prs.getStatus()),'blue')


def iqCB(con,iq):
    """Called when an iq is recieved, we just let the library handle it at the moment"""
    pass

def disconnectedCB(con):
    print colorize("Ouch, network error", 'red')
    sys.exit(1)

def colorize(txt, col):
    """Return colorized text"""
    if not USE_COLOR: return txt ## DJ - just incase it breaks your terms ;) ##
    if type(txt)==type(u''): txt=txt.encode(jabber.xmlstream.ENCODING,'replace')
    cols = { 'red':1, 'green':2, 'yellow':3, 'blue':4}
    initcode = '\033[;3'
    endcode  = '\033[0m'
    if type(col) == type(1): 
        return initcode + str(col) + 'm' + txt + endcode
    try: return initcode + str(cols[col]) + 'm' + txt + endcode
    except: return txt




Server = sys.argv[1]
Username = ''
Password = ''
Resource = 'default'


con = jabber.Client(host=Server,debug=jabber.DBG_ALWAYS ,log="/home/tmorozov/jfunc.log")

# Experimental SSL support
#
# con = jabber.Client(host=Server,debug=True ,log=sys.stderr,
#                    port=5223, connection=xmlstream.TCP_SSL)

try:
    con.connect()
except IOError, e:
    print "Couldn't connect: %s" % e
    sys.exit(0)
else:
    print colorize("Connected",'red')

con.registerHandler('message',messageCB)
con.registerHandler('presence',presenceCB)
con.registerHandler('iq',iqCB)
con.setDisconnectHandler(disconnectedCB)

if len(sys.argv) == 2:
    # Set up a jabber account
    con.requestRegInfo()
    req = con.getRegInfo()
    print req[u'instructions']
    for info in req.keys():
        if info != u'instructions' and \
           info != u'key':
            print "enter %s;" % info
            con.setRegInfo( info,strip(sys.stdin.readline()) )
    con.sendRegInfo()
    req = con.getRegInfo()
    Username = req['username']
    Password = req['password']
else:
    Username = sys.argv[2]
    Password = sys.argv[3]
    Resource = sys.argv[4]

print colorize("Attempting to log in...", 'red')


if con.auth(Username,Password,Resource):
    print colorize(u"Logged in as %s to server %s" % ( Username, Server), 'red')
else:
    print "eek -> ", con.lastErr, con.lastErrCode
    sys.exit(1)

print colorize("Requesting Roster Info" , 'red')
con.requestRoster()
con.sendInitPresence()
print colorize("Ok, ready" , 'red')
print colorize("Type /help for help", 'red')

JID = Username + '@' + Server + '/' + Resource

while(1):
    inputs, outputs, errors = select([sys.stdin], [], [],1)
    con.process(1)
    
        









