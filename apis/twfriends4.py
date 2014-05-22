#this program collects the friends (followings) from a list of users
#this version removes the functions for collecting and evaluating new users to follow (spidering)
#this version uses the get friends.ids to output an edge list of user ids
#twitter call returns 5000 users every minute

import time

def printer(idlst,fhand,sn):
	bads,goods = 0,0
	j = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #first entry in output string
	try:
		for id in idlst:
			fhand.write(j + '\t' + sn + '\t' + str(id) + '\n')
			goods += 1
	except:
		print "couldn't print an id list for: " + sn
		bads += 1
	return goods,bads

def usrcoll(sn,next,ctr1,ctr2,fhand,t,type):
	totgoodstemp,totbadstemp,sntravstat = 0,0,1
	ctr3 = 0
	try:
		if type=='sn': userset = t.friends.ids(cursor=next,screen_name=sn)
		elif type=='id': userset = t.friends.ids(cursor=next,user_id=sn)
	except: #user is not accessible
		print 'cannot access friends list for ' + sn
		sntravstat = 0
		next = 0
		ids = []
		return ids,totgoodstemp,totbadstemp,sntravstat,next
	next = userset['next_cursor']
	ids = userset['ids']
	ctr3 += len(ids)
	(goodstemp,badstemp) = printer(ids,fhand,sn) #pass id list to printer function
	totgoodstemp += goodstemp
	totbadstemp += badstemp
	print str(ctr1) + ': friends batch ' + str(ctr2) + ' from ' + sn + ', ' + str(ctr3) + ' total users processed'
	return ids,totgoodstemp,totbadstemp,sntravstat,next
