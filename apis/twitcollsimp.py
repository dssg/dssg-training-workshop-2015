#this program integrates subprograms to collect users and friends
#note that this program is set up for one-time data collection in that it skips previously traversed screen names
#this version generates 3 data files (users, friends, and problems) plus a dictionary, to-be-checked-for-traversal user list, traversed user list, and temporary to-be-checked-for-traversal list
#this version blocks duplicate data collection in two stages: at the stage of putting friends into the to-be-checked-for-traversal file, and at the stage of putting users into the to-be-traversed list
#it also outputs all info as it goes in case of program interruptions; it should be capable of resuming at any point as long as temporary-to-be-traversal file is stored for later adding into the final version of the to-be-traversal file

import twitter
import oauthDance
import json
import time
import re
from sys import exit

import twuser2
import twfriends4

print "Enter a project name:",
fname = raw_input()

t = oauthDance.login()
print 'init twitter data collection under project ' + fname + '\n'
t1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

#load dictionary
lctr0,dict = 0,{}
fnmdict = fname + '-dictionary.txt'
try:
	fdict = open(fnmdict)
	for line in fdict:
		lctr0 += 1;	line = line.rstrip(); dict[line.lower()] = 1; line2 = line + 's'; dict[line2.lower()] = 1;
	fdict.close();	print str(len(dict.keys())) + ' primary dictionary terms input from ' + str(lctr0) + ' lines\n'
except:
	fdict = open(fnmdict,'a')
	print 'no primary dictionary file available - first time storing data under ' + fname; print "Enter a comma-delimited set of dictionary terms (e.g. food,tacos,...,beer):",
	dictlst = raw_input().split(',')
	for i in dictlst: i = i.rstrip(); dict[i] = 1; fdict.write(str(i) + '\n')
	fdict.close(); print str(len(dict.keys())) + ' dictionary terms input from user\n'
	
#load to be collected users; note that process to build userlst excludes already traversed users
lctr00,usrdict1,snlst = 0,{},[]
fnmusr1 = fname + '-userlist.txt'
try:
	fusr1 = open(fnmusr1,'rb')
	for line in fusr1:
		lctr00 += 1
		if not re.search('\w',line): continue
		line = line.rstrip(); usrdict1[line] = 1;
	fusr1.close()
	for i in usrdict1: snlst.append(i)
	print str(len(usrdict1.keys())) + ' untraversed users loaded from ' + str(lctr00) + ' lines\n'
except:
	print 'no users file available - first time storing this data under ' + fname
	print "Enter a comma-delimited set of screen names:",
	snlst = raw_input().split(',')
	print str(len(snlst)) + ' screen names input from user\n'

#screen out the to-be-collected users that we already have user data for (so no need to collect their user data again but will still go into check phase); this can occur from duplicate friends or from restarts
print 'screening out the untraversed users that we already have user data for...'
lctr01,usrdict2,usrdict3 = -1,{},{}
fnmusr2 = fname + '-users.txt'
try:
	fusr2 = open(fnmusr2,'rb')
	for line in fusr2:
		lctr01 += 1
		if lctr01 == 0: continue
		line = line.rstrip(); dat = line.split('\t'); sn = dat[1]; id = dat[3]
		usrdict2[sn] = 1; usrdict3[id] = 1
	fusr2.close()
	print str(len(usrdict2.keys())) + ' user records loaded from ' + str(lctr01) + ' lines'
except:
	print 'skipping this step because no previous user data was available'
ctrch,ctrch2,snlstmiss,acoll = 0,0,[],0
for sn in snlst:
	ctrch += 1
	chstat = 0
	if sn in usrdict2: chstat=1
	elif sn in usrdict3: chstat=1
	if chstat==1: acoll += 1; continue
	ctrch2 += 1
	snlstmiss.append(sn)
print str(ctrch) + ' traversal targets checked, ' + str(ctrch2) + ' not found in user table and sent on to user collection phase'

#Start record output
fnmrec = fname + '-record.txt'
try: frec = open(fnmrec); frec.close(); frec = open(fnmrec,'a')
except: frec = open(fnmrec,'a'); frec.write('start\tpossibusr\tusrsel\talreadycoll\tend\tgoodfrct\tbadfrct\tusrtravct\tusrtravlst\tusrNtravct\tusrNtravlst\n'); print '\nrecord file created'
recout = ''; recout = t1 + '\t' + str(ctrch) + '\t' + str(ctrch2) + '\t' + str(acoll) + '\t'
frec.write(recout)

#Collect user info
print '\ngetting user info...'
#fnmusr2 = fname + '-users.txt'
try: fusr2 = open(fnmusr2); fusr2.close(); fusr2 = open(fnmusr2,'a')
except: fusr2 = open(fnmusr2,'a'); fusr2.write('accessed\tsn\tname\tid\tverstat\tfollct\tstatct\tfrct\tfavct\tdescr\tloc\tgeo\tlang\turl\tcrdate\ttz\tfollstat\timgurl\tbkgdimgurl\tstattxt\n')
(totgoods,totbads,batct,usrct) = twuser2.usrcoll(snlstmiss,t,fusr2) #pass info to user collection program
fusr2.close();
print '\nsummary of user collection results:'
print str(batct) + ' batches processed, ' + str(usrct) + ' users processed;'
print str(totgoods) + ' printed users and ' + str(totbads) + ' failed to print'

#check users to select traversal targets (get user info, get donzo list, define check routine, run snlst through the routine)
print '\naccessing user records to check for keyword matches...'
lctr01,usrdict2,usrdict3 = -1,{},{}
try:
	fusr2 = open(fnmusr2,'rb')
	for line in fusr2:
		lctr01 += 1
		if lctr01 == 0: continue
		line = line.rstrip(); dat = line.split('\t'); sn = dat[1]; nm = dat[2]; descr = dat[9]; id = dat[3]
		usrdict2[sn] = [nm,descr]; usrdict3[id] = sn
	fusr2.close()
	print str(len(usrdict2.keys())) + ' user records loaded from ' + str(lctr01) + ' lines'
except:
	print 'Sorry - no data on users was available for the next step (check against dictionary)'
	exit()

lctr02,donedict = 0,{}
fnmdone = fname + '-traversed.txt'
try:
	fdone = open(fnmdone)
	for line in fdone:
		lctr02 += 1
		line = line.rstrip(); donedict[line] = 1
	fdone.close()
	print str(len(donedict.keys())) + ' already traversed users loaded from ' + str(lctr02) + ' lines'
except:
	print 'no file of already traversed users found'
	
ctrch,ctrch2,snlst2,badct = 0,0,[],0 
for sn in snlst:
	ctrch += 1
	#if ctrch > 30: break #use this to restrict computations
	#if ctrch%100==0: print str(ctrch) + ' records processed and ' + str(ctrch2) + ' accepted'
	try: #sn in usrdict3 or sn in usrdict2:
		if not re.search('[a-z]|[A-Z]',sn): rsn = usrdict3[sn]; nm,descr = usrdict2[rsn][0],usrdict2[rsn][1]
		else: nm,descr = usrdict2[sn][0],usrdict2[sn][1]; rsn = sn
	except: #else:
		badct += 1
		continue
	if rsn in donedict: continue
	
	chstat = 0
	
	nm = re.sub('[,.]',' ',nm); descr = re.sub('[,.]',' ',descr);
	wrds = {}; wrds[rsn.lower()] = 1
	for i in nm.split(): 
		wrds[i.lower().rstrip('\'\"-,.:;!?')] = 1
	for i in descr.split(): 
		wrds[i.lower().rstrip('\'\"-,.:;!?')] = 1
	for chwrd in wrds:
		if chwrd in dict: chstat = 1
		if chstat==1:
			ctrch2 += 1 
			snlst2.append(rsn)
			#print '\n',rsn,nm,descr
			break
print '\n' + str(ctrch2) + ' out of ' + str(ctrch) + ' users selected for further traversal based on keywords'
print snlst2
if badct>0: print 'warning: ' + str(badct) + ' records without user info'

#collect friends
def frcoll(sn,frnext,type):
	idlst,goodstmp,badstmp,sntravstat,frnextbak = twfriends4.usrcoll(sn,frnext,ctr1,ctr2fr,ffr,t,type)
	if sntravstat==1: sntravfr[sn] = 1
	else: notravfr[sn] = 1; fprob.write(sn + '\tfriends\n')
	return idlst,frnextbak,goodstmp,badstmp

#***Main Program for Traversal***
fnmffr = fname + '-friends.txt'; fnmprob = fname + '-problems.txt'
try: ffr = open(fnmffr); ffr.close(); ffr = open(fnmffr,'a')
except: ffr = open(fnmffr,'a'); ffr.write('accessed\tfromSN\ttoID\n'); print 'friends file created'
try: fprob = open(fnmprob); fprob.close(); fprob = open(fnmprob,'a')
except: fprob = open(fnmprob,'a'); fprob.write('sn\tproblem\n'); print 'problems file created'
fdone = open(fnmdone,'a')
fnmusr1tmp = fname + '-userlsttmp.txt'; fusr1tmp = open(fnmusr1tmp,'w')

ctr1,sntravfr,notravfr,totgoodfr,totbadfr = 0,{},{},0,0
idset = {}
for sn in snlst2:
	if re.search('[a-z]|[A-Z]',sn): type = 'sn'
	else: type = 'id'
	ctr1 += 1
	print '\nworking on ' + str(sn) + ' (' + str(ctr1) + ' out of ' + str(ctrch2) + ')'
	ctr2fr = 0
	x1 = 1
	frnext = -1
	while (x1) > 0: #loop until friend calls for sn have been exhausted
		ctr2fr += 1; idlst,x1,goodstmp,badstmp = frcoll(sn,frnext,type); frnext = x1; totgoodfr += goodstmp; totbadfr += badstmp #if user was not traversed in prior data collection or traversal is complete, do so now
		for i in idlst: 
			if i in usrdict3: continue #new friends don't get written out to usrlist if their user info has already been collected
			idset[i] = 1; fusr1tmp.write(str(i) + '\n')
		time.sleep(60)
	fdone.write(str(sn)+'\n')
ffr.close(); fprob.close(); fdone.close(); fusr1tmp.close()

print '\nsummary of friends results:'
print 'captured ',totgoodfr,'printable users,',totbadfr,'not printable from'
print str(len(sntravfr.keys())) + ' screen names traversed: ' + str(sntravfr.keys())
print str(len(notravfr.keys())) + ' screen names could not be traversed: ' + str(notravfr.keys())

#get friends and put into [fname]-userlst.txt (fnmusr1)
fusr1 = open(fnmusr1,'w')
ctout = 0
for i in idset:
	#if i in usrdict3: continue #redundant because idset is already censored this way
	ctout += 1
	fusr1.write(str(i) + '\n')
fusr1.close()
print '\n' + str(ctout) + ' friends output into user list for the next round of processing out of ' + str(len(idset.keys())) + ' total friends'

t2 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print '\ntime started: ' + t1
print 'time completed: ' + t2

#finish record output
recout = t2 + '\t' + str(totgoodfr) + '\t' + str(totbadfr) + '\t' + str(len(sntravfr.keys())) + '\t' + str(sntravfr.keys()) + '\t' + str(len(notravfr.keys())) + '\t' + str(notravfr.keys()) + '\n'
frec.write(recout)
frec.close()