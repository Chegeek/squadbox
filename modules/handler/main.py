import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay
from models import *
from email.utils import *

'''
Slow_Email Main Handler

@author: Anant Bhardwaj
@date: Oct 20, 2012
'''

HOST = 'slow.csail.mit.edu'
NO_REPLY = 'no-reply' + '@' + HOST

@route("(group_name)-add@(host)", group_name=".+", host=HOST)
@stateless
def add(message, group_name=None, host=None):
	try:
		group = Group.objects.get(name=group_name)
		relay.reply(message, NO_REPLY, "Error", "Mailing group %s@slow.csail.mit.edu already exists" %(group_name))
	except Group.DoesNotExist:
		name, addr = parseaddr(message['from'])
		group = Group(name=group_name, status=True)
		group.save()
		user = User(email = addr, group = group, admin = True, status = True)
        	user.save()
		relay.reply(message, NO_REPLY, "Success", "Mailing group %s@slow.csail.mit.edu created" %(group_name))
        return

@route("(group_name)-subscribe@(host)", group_name=".+", host=HOST)
@stateless
def subscribe(message, group_name=None, host=None):
	group = None
	name, addr = parseaddr(message['from'])
	try:                    
                group = Group.objects.get(name=group_name)
		user = User.objects.get(email = addr, group = group)
		relay.reply(message, NO_REPLY, "Error", "You are already subscribed to: %s@slow.csail.mit.edu" %(group_name))
	except User.DoesNotExist:
                user = User(email = addr, group = group, admin = False, status = True)
		user.save()
		relay.reply(message, NO_REPLY, "Success", "You are now subscribed to: %s@slow.csail.mit.edu" %(group_name))
        except Group.DoesNotExist:
       	 	relay.reply(message, NO_REPLY, "Error", "Could not locate %s@slow.csail.mit.edu group" %(group_name))
        return


@route("(group_name)-unsubscribe@(host)", group_name=".+", host=HOST)
@stateless
def unsubscribe(message, group_name=None, host=None):
	group = None
	name, addr = parseaddr(message['from'])
	try:                    
                group = Group.objects.get(name=group_name)
		user = User.objects.get(email = addr, group = group)
		user.delete()
		relay.reply(message, NO_REPLY, "Success", "You are now un-subscribed from: %s@slow.csail.mit.edu" %(group_name))
	except User.DoesNotExist:
		relay.reply(message, NO_REPLY, "Error", "You are not subscribed to: %s@slow.csail.mit.edu" %(group_name))
        except Group.DoesNotExist:
       	 	relay.reply(message, NO_REPLY, "Error", "Could not locate %s@slow.csail.mit.edu group" %(group_name))
        return


@route("(group_name)-info@(host)", group_name=".+", host=HOST)
@stateless
def info(message, group_name=None, host=None):
        try:
                group = Group.objects.get(name=group_name)
		members = User.objects.filter(group=group)
                relay.reply(message, NO_REPLY, "Success", "Grroup Name: %s@slow.csail.mit.edu, Members: %s" %(group_name, str(members)))
        except Group.DoesNotExist:
		relay.reply(message, NO_REPLY, "Error", "Could not locate %s@slow.csail.mit.edu group" %(group_name))
        return


@route("(address)@(host)", address="ask", host=HOST)
@stateless
def handle(message, address=None, host=None):
	name, addr = parseaddr(message['from'])
	p = Post(from_addr = addr, message=str(message))
	p.save()
	relay.reply(message, address + '@' + HOST, message['Subject'], message.body())
	return


