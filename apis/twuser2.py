#this program receives sets of user ids (plus twitter connection and output file), lumps users into sets of 100, 
# gets their user objects, identifies their desired components, cleans them, and prints them
#twitter call returns 100 users every six seconds

import time
import re

def usrcoll(ids,t,fhand): #main program, batches into 100s #fprob excluded
	totgoodstemp,totbadstemp = 0,0
	ctr3,idset,batct,ctr4 = 0,"",0,0
	gotusers = {}
	chtype = 0
	for i in ids:
		if re.search('[a-z]|[A-Z]',i): chtype += 1
	if chtype > 0: type = 'sn'
	else: type = 'id'
	#print 'type: ' + str(type) + '\tchtype: ' + str(chtype)
	for i in ids:
		ctr4 += 1
		idset += str(i) + ","
		ctr3+=1
		if ctr3 % 100 == 0:
			batct += 1
			idset = idset[:-1]
			userset = collfn(idset,t,batct,type)
			
			for user in userset: sn = user['screen_name']; gotusers[sn] = 1
			#idsetch = re.sub("'",'',idset); 
			idsetch = idset.split(',')
			#for ich in idsetch: 
			#	if not ich in gotusers: fprob.write(ich + '\tuserinfo\n')

			(goodstemp,badstemp) = usrproc(userset,fhand,batct)
			totgoodstemp += goodstemp
			totbadstemp += badstemp
			ctr3,idset = 0,''
	if len(idset) > 0:
		batct += 1
		idset = idset[:-1]
		userset = collfn(idset,t,batct,type)
		for user in userset: sn = user['screen_name']; gotusers[sn] = 1
		#idsetch = re.sub("'",'',idset); 
		idsetch = idset.split(',')
		#for ich in idsetch: 
		#	if not ich in gotusers: fprob.write(ich + '\tuserinfo\n')
		(goodstemp,badstemp) = usrproc(userset,fhand,batct)
		totgoodstemp += goodstemp
		totbadstemp += badstemp
	return totgoodstemp,totbadstemp,batct,ctr4

def collfn(idset,t,batct,type): #twitter call routine
	#print 'idset: ' + str(idset) + '\ttype: ' + str(type)
	userset = []
	try:
		if type=='sn': userset = t.users.lookup(screen_name=idset,include_entities='false')
		elif type=='id': userset = t.users.lookup(user_id=idset,include_entities='false')
		time.sleep(6)
	except:
		print "entered into problem sequence for batch: " + str(batct)
		idbats=[]
		idlst = idset.split(','); z = len(idlst); q,q2 = 0,11
		while q2<z:
			idsettmp = idlst[q:q2]; idbats.append(idsettmp)
			q += 10
			if q == 10: q+=1 #to avoid overlaps
			if q2 + 10 < z + 1: q2 += 10
			else: q2 = z; idsettmp = idlst[q:q2]; idbats.append(idsettmp)
		x = 0
		for i in idbats:
			x+=1
			idset = ""
			for i2 in i:
				idset += str(i2) + ","
			idset = idset[:-1]
			print 'iter ' + str(x) + ', idset: ' + idset
			try: 
				if type=='sn': usersettmp = t.users.lookup(screen_name=idset,include_entities='false')
				elif type=='id': usersettmp = t.users.lookup(user_id=idset,include_entities='false')
				time.sleep(6) 
				for i4 in usersettmp: userset.append(i4)	
			except: 
				idsetparts = idset.split(',')
				print 'iter ' + str(x) + ": couldn't access idset of length " + str(len(idsetparts)) + ' going to individual collection efforts'
				x2 = 0
				for i3 in idsetparts:
					try:
						x2+=1
						if type=='sn': usersettmp = t.users.lookup(screen_name=i3,include_entities='false')
						elif type=='id': usersettmp = t.users.lookup(user_id=i3,include_entities='false')
						time.sleep(6) 
						for i4 in usersettmp: userset.append(i4)
					except: continue
				print str(x2) + ' of the 10 individual ids found'
		print 'able to retrieve ' + str(len(userset)) + ' users for batch: ' + str(batct)
	return userset
	
def usrproc(userset,fhand,batct):	#extract user data and send to cleaner and printer
	ctrtmp,goodstemp,badstemp = 0,0,0
	for user in userset:
		ctrtmp += 1
		sn,id,verstat,follct = user['screen_name'],user['id'],user['verified'],user['followers_count']
		statct,descr,frct,loc = user['statuses_count'],user['description'],user['friends_count'],user['location']
		follstat,geo,lang,favct = user['following'],user['geo_enabled'],user['lang'],user['favourites_count']
		name,url,crdate,tz = user['name'],user['url'],user['created_at'],user['time_zone']
		imgurl,bkgdimgurl=user['profile_image_url'],user['profile_background_image_url']
		try: stattxt = user['status']['text']
		except: stattxt = ''
		dirtylst = [sn,name,id,verstat,follct,statct,frct,favct,descr,loc,geo,lang,url,crdate,tz,follstat,imgurl,bkgdimgurl,stattxt]
		cleanlst = cleaner(dirtylst)
		try:
			printer(cleanlst,fhand)
			goodstemp += 1
			#print sn,id
		except: badstemp += 1
	print 'batch ' + str(batct) + ': ' + str(ctrtmp) + ' users processed; print status = ' + str(goodstemp)
	return goodstemp,badstemp
			
def cleaner(lst):
	z,bad,tmpbad = 0,0,0
	for i in lst:
		try:
			i = i.encode('ascii','replace')
		except:
			i = str(i)
			i = i.encode('ascii','replace')
		try:
			i = re.sub('(\n)|(\r)|(\f)|(\t)',' ',i)
		except:
			tmpbad = 1
		lst[z] = i
		z += 1
		if tmpbad==1: bad += 1
	if bad>0: print str(bad) + " items couldn't be cleaned"
	return lst

def printer(lst,fhand):
	bads,goods = 0,0#
	j = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  #first entry in output string
	try:
		for i in lst:
			j += '\t' + str(i) #then add entries
		goods += 1#
		j += '\n'
		fhand.write(j)
	except:
		print "couldn't print this one :( : "
		print lst
		bads += len(lst)#
	return