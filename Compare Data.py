import csv, sys, re
import datetime as DT
##from datetime import datetime, timedelta

import lib.MatchingFuctions as AC

startTime = DT.datetime.now()
print ("Program start : %s" % startTime )

FromAccess = 'G:/SURVEY/access/importFiles/Access.csv'
FromSIR = 'G:/SURVEY/access/importFiles/SIR.csv'
FromSPSS = 'G:/SURVEY/access/importFiles/RELEVATE _2 FOR GREG.csv'
dups = 'G:/SURVEY/access/exportFiles/dups.csv'

##FromAccess = 'importFiles/A1.csv'
##FromSIR = 'importFiles/S1.csv'

accessDictionary = []
sirDictionary = []
SPSSDictionary = []
highPointList = []



def makeDict (inFile, OutDict):
##    print ('-----------------------')
##    print ('Read file: ' + inFile)
    ifile  = open(inFile, 'r')
    reader = csv.reader(ifile)
    lineNum = 0
    print (maxrow)
    for eachLine in reader:
        lineNum += 1
##      check for blank lines
        if not eachLine:
            print ('Blank Line')
            continue
##      Save header row.
        lowerList = []
        if lineNum == 1:
            colHeader = eachLine
##          Lowercase column headers
            for colItem in colHeader:
                lowerList.append(colItem.lower())
            colHeader = lowerList
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
maxrow = 10
makeDict (FromAccess, accessDictionary)
## clean data from access
for rowInAccess in accessDictionary:
    if rowInAccess['sex'] == '0':   # zero = male
       rowInAccess['sex'] = 'M' 
    elif rowInAccess['sex'] == '1':
       rowInAccess['sex'] = 'F' 
    rowInAccess['address1'] = AC.cleanAddress(rowInAccess['address1'] )
linesInAccess = len(accessDictionary)

# SIR IMPORT
minrow = 0
maxrow = 10
makeDict (FromSIR, sirDictionary)
for rowInSIR in sirDictionary:
    if rowInSIR['db_sex'] == '0':   # zero = male
       rowInSIR['db_sex'] = 'M' 
    elif rowInSIR['db_sex'] == '1':
       rowInSIR['db_sex'] = 'F'
    rowInSIR['address'] = AC.cleanAddress(rowInSIR['address'] )

# SPSS IMPORT.   A SINGLE SPACE MEANS NOTHING WAS IN THE COLUMN
minrow = 0
maxrow = 5
makeDict (FromSPSS, SPSSDictionary)
print (SPSSDictionary)
for rowInSPSS in SPSSDictionary:
    print (rowInSPSS['dobdd'] )
    if rowInSPSS['dobdd'] == ' ':
        rowInSPSS['dobdd'] = '15'
    if rowInSPSS['dobmm'] == ' ':
        rowInSPSS['dobmm'] = '6'
    rowInSPSS['dob'] = rowInSPSS['dobmm'] + '/' + rowInSPSS['dobdd'] + '/' + rowInSPSS['dobccyy']
    rowInSPSS['address1'] += ' ' + rowInSPSS['address2'] 
    rowInSPSS['address1'] = AC.cleanAddress(rowInSPSS['address1'] )
    print (rowInSPSS['address1'])

    



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
accessLine = 0
accessPhoneBook = ['subject_phone_home', 'subject_phone_mobile', 'subject_phone_work', 'subject_phone_nursing']
SIRPhoneBook = ['swphone', 'shphone', 'cwphone', 'chphone']

with open(dups, 'w', newline='') as CSVDupObject:
    print ('File Object Type: ' , type(CSVDupObject))

    a = csv.DictWriter(CSVDupObject, delimiter=',', fieldnames=accessDictionary[0])
    a.writeheader()

    
    for rowInAccess in accessDictionary:
        accessLine += 1
        sirLine = 0
        highPoint = 0
        highID = highLast = highDOB =highPhone = ''
        highMatch = highAddress = 0

        for rowInSIR in sirDictionary:
            sirLine +=1
            skipRow = 0
            pointTotal = pointDOB= pointFirstName = pointLastName = pointAddress = pointPhone= 0
            matchingPhones = ''
            MUL_FACT = 2
    ##      speed things ups
            if len(rowInAccess['lname']) and  len(rowInSIR['lname']):
                if rowInAccess['lname'][0] !=  rowInSIR['lname'][0]:
                    if rowInAccess['fname'][0] !=  rowInSIR['lname'][0]:
                        skipRow = 1

            if skipRow == 1:  continue               
                
            pointAddress = compareAddress (rowInSIR['address'] , rowInAccess['address1'])

            pointDOB = compareDOB (rowInSIR['db_dob'] , rowInAccess['dob'] )

            pointLastName = compareLName(rowInSIR['lname'],  rowInAccess['lname'])
            
    ##      Same phone number in multiple columns is a problem.
            accessPhoneList = sirPhoneList = []
            for eachAccessPhone in accessPhoneBook:
                accessPhoneList.append(rowInAccess[eachAccessPhone])
            accessPhoneList = sorted(set(accessPhoneList))
            for eachSIRPhone in SIRPhoneBook:
                sirPhoneList.append(rowInSIR[eachSIRPhone])
            sirPhoneList = sorted(set(sirPhoneList))
            for eachAccessPhone in accessPhoneList:
                for eachSIRPhone in sirPhoneList:
                    tempPhonePoints = comparePhone (eachSIRPhone, eachAccessPhone) 
                    if tempPhonePoints > 0 :
                        matchingPhones += eachSIRPhone + ' = ' + eachAccessPhone + ','
                        pointPhone += tempPhonePoints
                            

            if pointLastName == 10 :
                MUL_FACT *= 2
                if rowInSIR['fname'] == rowInAccess['fname']:
                    pointFirstName += 8
                    MUL_FACT *= 2
                elif rowInSIR['fname'] in rowInAccess['fname']:
                    pointFirstName += 10  # but no mult_factor
                    MUL_FACT *= 2

            elif rowInSIR['fname'] == rowInAccess['fname']:
                pointFirstName  += 3
                
            pointTotal = pointDOB + pointLastName + pointFirstName + pointAddress + pointPhone
            if pointTotal > highPoint:
                highPoint = pointTotal
                highID = rowInSIR['id_num']
                highLast = rowInSIR['lname']
                highFirst = rowInSIR['fname']
                highDOB = rowInSIR['db_dob']
                highPhone = matchingPhones
                highAddress = rowInSIR['address']
                matchInfo = {'pln': pointLastName, 'pfn': pointFirstName, 'pdob' : pointDOB, 'pphone' : pointPhone, 'paddress' : pointAddress}
        highPointList.append(highPoint)
        if highPoint > 59:
##            print ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format('', rowInAccess['lname'], rowInAccess['fname'], rowInAccess['dob'], highPhone, rowInAccess['address1']))
##            print ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( highPoint, highLast, highFirst, highDOB, '', highAddress ))
##            print ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( '', matchInfo ['pln'], matchInfo ['pfn'], matchInfo ['pdob'], matchInfo['pphone'], matchInfo['paddress']))
##            print('----------------------\n')

            str1 = rowInAccess['lname'] + ',' + rowInAccess['fname'] + ',' +  rowInAccess['dob'] + ',' + highPhone +',' + rowInAccess['address1']
            a.writerow(rowInAccess)
            
   
##            CSVDupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( highPoint, highLast, highFirst, highDOB, '', highAddress ))
##            CSVDupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( '', matchInfo ['pln'], matchInfo ['pfn'], matchInfo ['pdob'], matchInfo['pphone'], matchInfo['paddress']))

##            CSVDupObject.write ('\n')
##            CSVDUPObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format('', rowInAccess['lname'], rowInAccess['fname'], rowInAccess['dob'], highPhone, rowInAccess['address1']))
##            CSVDupObject.write ('\n')
##            CSVDupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( highPoint, highLast, highFirst, highDOB, '', highAddress ))
##            CSVDupObject.write ('\n')
##            CSVDupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( '', matchInfo ['pln'], matchInfo ['pfn'], matchInfo ['pdob'], matchInfo['pphone'], matchInfo['paddress']))
##            CSVDupObject.write ('\n')
        elif highPoint != 0:
##            print (accessLine,'/',linesInAccess, rowInAccess['lname'], highPoint)
            print ('{0:5} {1:10} {2:15} {3:10} {4:35}'. format(highPoint, rowInAccess['lname'], rowInAccess['fname'], rowInAccess['dob'], highPhone, rowInAccess['address1']))

### reporting section            
##    print ('Counts: ')
##    highPointDict = {}
##    for i in set(highPointList):
##        highPointDict[i] = highPointList.count(i)
##    print ('One Way:')
##    for i in sorted(set(highPointList)):
##        print (i, highPointList.count(i))
##    print ('Or Another:')
##    for dictItem in sorted(highPointDict):
##        print (dictItem, ' points =', highPointDict[dictItem])
##

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
