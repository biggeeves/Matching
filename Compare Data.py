import csv, sys, re
import datetime as DT
##from datetime import datetime, timedelta

import lib.MatchingFunctions as AC

startTime = DT.datetime.now()
print ("Program start : %s" % startTime )

FromAccess = 'G:/SURVEY/access/importFiles/Access.csv'
FromSIR = 'G:/SURVEY/access/importFiles/SIR.csv'
FromSPSS = 'G:/SURVEY/access/importFiles/RELEVATE _2 FOR GREG.csv'
dups = 'G:/SURVEY/access/exportFiles/dups.csv'

##FromAccess = 'importFiles/A1.csv'
##FromSIR = 'importFiles/S1.csv'

accessDict = []
sirDict = []
SPSSDict = []
highPointList = []
highSir = {}
highAccess = {}



def makeDict (inFile, OutDict):
##    print ('-----------------------')
##    print ('Read file: ' + inFile)
    ifile  = open(inFile, 'r')
    reader = csv.reader(ifile)
    lineNum = 0
    colHeader =[]
    for eachLine in reader:
        lineNum += 1
##      check for blank lines
        if not eachLine:
            print ('Blank Line')
            continue
##      Save header row.
        if lineNum == 1:
##          Create Lowercase column header list
            for colItem in eachLine:
                colHeader.append(colItem.lower())
        else:
            bigDict = {}
            colNum = 0
            if (minrow > lineNum or lineNum > maxrow):
                continue 
            for eachCol in eachLine:
                bigDict [colHeader[colNum]] = eachCol.upper()
                colNum += 1
            OutDict.append(bigDict) 
    ifile.close()
    print ('Cycled trough ', inFile, ':', str(lineNum - 1))


# ACCESS IMPORT
minrow = 0
maxrow = 90000
makeDict (FromAccess, accessDict)
## clean data from access
for rowInAccess in accessDict:
    if rowInAccess['sex'] == '0':   # zero = male
       rowInAccess['sex'] = 'M' 
    elif rowInAccess['sex'] == '1':
       rowInAccess['sex'] = 'F' 
    rowInAccess['address1'] = AC.cleanAddress(rowInAccess['address1'] )
linesInAccess = len(accessDict)

# SIR IMPORT
minrow = 0
maxrow = 90000
makeDict (FromSIR, sirDict)
for rowInSIR in sirDict:
    if rowInSIR['db_sex'] == '0':   # zero = male
       rowInSIR['db_sex'] = 'M' 
    elif rowInSIR['db_sex'] == '1':
       rowInSIR['db_sex'] = 'F'
    rowInSIR['address'] = AC.cleanAddress(rowInSIR['address'] )

# SPSS IMPORT.   A SINGLE SPACE MEANS NOTHING WAS IN THE COLUMN
minrow = 0
maxrow = 10000
makeDict (FromSPSS, SPSSDict)

for rowInSPSS in SPSSDict:
    if rowInSPSS['dobdd'] == ' ':
        rowInSPSS['dobdd'] = '15'
    if rowInSPSS['dobmm'] == ' ':
        rowInSPSS['dobmm'] = '6'
    rowInSPSS['dob'] = rowInSPSS['dobmm'] + '/' + rowInSPSS['dobdd'] + '/' + rowInSPSS['dobccyy']
    rowInSPSS['address1'] += ' ' + rowInSPSS['address2'] 
    rowInSPSS['address1'] = AC.cleanAddress(rowInSPSS['address1'] )
    rowInSPSS['highPoint'] = 0


## finding months and days and years
def formatDate(somedate):
    if somedate == '':
        return ()
    month, day, year = map(int, somedate.split('/'))
    month = "{0:0=2d}".format(month)
    day   = "{0:0=2d}".format(day)
    stringDate = str(month) + '/' + str(day) + '/' + str(year)
    return (month, day, year, stringDate)

def days_between(d1, d2):
    d1 = DT.datetime.strptime(d1, "%m/%d/%Y")
    d2 = DT.datetime.strptime(d2, "%m/%d/%Y")
    return abs((d2 - d1).days)

def compareDOB (d1, d2):
    if d1 == '' or d2 == '':
        pointDOB = 0
        return (pointDOB)
    month1, day1, year1, date1 = formatDate(d1)
    month2, day2, year2, date2 = formatDate(d2)
    
    if date1 == date2:
        pointDOB = 15
    elif days_between(d1, d2) <32 :
        pointDOB = 5
    elif days_between(d1, d2) <400 :
        pointDOB = 2
    elif days_between(d1, d2) <765 :
        pointDOB = 1
    elif days_between(d1, d2) > (365*10) + 31:
        pointDOB = -4
    else: # everything between 765 and 10 years gets 0 points
        pointDOB = 0
    # dole out points for having correct month, day or year
    if month1 == month2:
        pointDOB += 2
    if day1 == day2:
        pointDOB += 2
    if year1 == year2:
        pointDOB += 2
    ##print ('--------')
    ##print (days_between(date1, date2), pointDOB)
    return (pointDOB)



def compareAddress (a1, a2):
    points = 0
    if a2 in a1 or a1 in a2:
        points += 8
    for aword in a2.split():
        if aword in a1:
            points += 1
    return (points)

def compareLName (lname1, lname2):
    points = 0
    if lname1 == lname2:
        points = 10
    return (points)
    
def compareFName (fname1, fname2):
    points = 0
    if fname1 == fname2:
        points = 10
    return (points)


def comparePhone (phone1, phone2):
    points = 0
    if phone1 == '' or phone2 == '':
        points = 0
    elif phone1 == phone2:
        points = 10
    return (points)

#sys.exit('Debugging address')


print ('----Cycle Through Both Dictionaries----------')
SPSSLine = 0
accessPhoneBook = ['subject_phone_home', 'subject_phone_mobile', 'subject_phone_work', 'subject_phone_nursing']
SPSSPhoneBook = ['phonenumber']
SIRPhoneBook = ['swphone', 'shphone', 'cwphone', 'chphone']

with open(dups, 'w', newline='') as CSVDupObject:
    print ('File Object Type: ' , type(CSVDupObject))

    a = csv.DictWriter(CSVDupObject, delimiter=',', fieldnames=SPSSDict[0])
    a.writeheader()

    
    for rowInSPSS in SPSSDict:
        SPSSLine += 1
        sirLine = 0
        highID = highLast = highDOB =highPhone = ''
        highMatch = highAddress = 0

        for rowInSIR in sirDict:
            sirLine +=1
            skipRow = 0
            pointTotal = pointDOB= pointFirstName = pointLastName = pointAddress = pointPhone= 0
            matchingPhones = ''
            MUL_FACT = 2
    ##      speed things ups
            if len(rowInSPSS['lastname']) and  len(rowInSIR['lname']):
                if rowInSPSS['lastname'][0] !=  rowInSIR['lname'][0]:
                    if rowInSPSS['firstname'][0] !=  rowInSIR['lname'][0]:
                        skipRow = 1

            if skipRow == 1:  continue               
                
            pointAddress = compareAddress (rowInSPSS['address1'], rowInSIR['address'])

            pointDOB = compareDOB (rowInSPSS['dob'] , rowInSIR['db_dob'])

            pointLastName = compareLName(rowInSPSS['lastname'], rowInSIR['lname'])
            
    ##      Same phone number in multiple columns is a problem.
            SPSSPhoneList = sirPhoneList = []
            for eachSPSSPhone in SPSSPhoneBook:
                SPSSPhoneList.append(rowInSPSS[eachSPSSPhone])
            SPSSPhoneList = sorted(set(SPSSPhoneList))
            for eachSIRPhone in SIRPhoneBook:
                sirPhoneList.append(rowInSIR[eachSIRPhone])
            sirPhoneList = sorted(set(sirPhoneList))
            for eachSPSSPhone in SPSSPhoneList:
                for eachSIRPhone in sirPhoneList:
                    tempPhonePoints = comparePhone (eachSIRPhone, eachSPSSPhone) 
                    if tempPhonePoints > 0 :
                        matchingPhones += eachSIRPhone + ' = ' + eachSPSSPhone + ','
                        pointPhone += tempPhonePoints
                            

            if pointLastName == 10 :
                MUL_FACT *= 2
                if rowInSPSS['firstname'] == rowInSIR['fname']:
                    pointFirstName += 8
                    MUL_FACT *= 2
                elif rowInSIR['fname'] in rowInSPSS['firstname']:
                    pointFirstName += 10  # but no mult_factor
                    MUL_FACT *= 2

            elif rowInSPSS['firstname'] == rowInSIR['fname']:
                pointFirstName  += 3
            pointTotal = 0
            pointTotal = pointDOB + pointLastName + pointFirstName + pointAddress + pointPhone
            if pointTotal > rowInSPSS['highPoint'] :
                rowInSPSS['highPoint'] = pointTotal
                
                highSir['id'] = rowInSIR['id_num']
                highSir['lname'] = rowInSIR['lname']
                highSir['fname'] = rowInSIR['fname']
                highSir['dob'] = rowInSIR['db_dob']
                highSir['address'] = rowInSIR['address']
                highSir['phone'] = matchingPhones
                highSir['sex'] = rowInSIR['db_sex']

                
                highID = rowInSIR['id_num']
                highLast = rowInSIR['lname']
                highFirst = rowInSIR['fname']
                highDOB = rowInSIR['db_dob']
                highPhone = matchingPhones
                highAddress = rowInSIR['address']
                matchInfo = {'pln': pointLastName, 'pfn': pointFirstName, 'pdob' : pointDOB, 'pphone' : pointPhone, 'paddress' : pointAddress}
        highPointList.append(rowInSPSS['highPoint'])
        a.writerow(rowInSPSS)
        print (SPSSLine , rowInSPSS['highPoint'], rowInSPSS['firstname'], rowInSPSS['lastname'])

### reporting section            
    print ('Counts: ')
    highPointDict = {}
    for i in set(highPointList):
        highPointDict[i] = highPointList.count(i)
    print ('One Way:')
    for i in sorted(set(highPointList)):
        print (i, highPointList.count(i))
    print ('Or Another:')
    for dictItem in sorted(highPointDict):
        print (dictItem, ' points =', highPointDict[dictItem])


    print ('Average: ' , sum(highPointList)/len(highPointList), 'Min: ' , min(highPointList), 'Max: ', max(highPointList))

CSVDupObject.close()


from itertools import groupby
##print ('---------- itertools -----------------')
##print ([len(list(group))  for key, group in groupby(birthdaylist)])

##print ([list(group)  for key, group in groupby(birthdaylist)])

endTime = DT.datetime.now()
print ("Program end : %s" % endTime)

diffTime = endTime - startTime
print ("Run time ", diffTime.days, "Days:",diffTime.seconds , "Seconds", diffTime.microseconds, "MicroSeconds: ")
