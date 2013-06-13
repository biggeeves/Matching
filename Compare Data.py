import csv, sys, re, msvcrt, time
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

aborted = False

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
    rowInSPSS['dataSource'] = 'na'
    rowInSPSS['highPoint'] = 0
    rowInSPSS['highPhone']   = -1
    rowInSPSS['highFirstName']   = -1
    rowInSPSS['highLastName']   = -1
    rowInSPSS['highMixedName']   = -1
    rowInSPSS['highAddress'] = -1
    rowInSPSS['highSex']     = -1
    rowInSPSS['multFactor']  = -1
    
    rowInSPSS['matchID'] = 'na'
    rowInSPSS['matchLname'] = 'na'
    rowInSPSS['matchFname'] = 'na'
    rowInSPSS['matchDOB'] = 'na'
    rowInSPSS['matchAddress'] = 'na'
    rowInSPSS['matchPhone'] = 'na'
    rowInSPSS['matchSex'] = 'na'


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
    pointDOB = 0
    if d1 == '' or d2 == '':
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
    if a1 == '' or a2 == '':
        return (points)
    if a1 == a2
        points += 10
    if a2 in a1 or a1 in a2:
        points += 8
    for aword in a2.split():
        if aword in a1:
            points += 1
    return (points)

def compareName (name1, name2):
    points = 0
    if name1 == name2:
        points = 10
    elif name1 in name2 or name2 in name1:
        points = 7        
    return (points)
    
def comparePhone (phone1, phone2):
    points = 0
    if phone1 == '' or phone2 == '':
        points = 0
    elif phone1 == phone2:
        points = 10
    return (points)

def compareSex (sex1, sex2):
    points = 0
    if sex1 == '' or sex2 == '':
        points = 0
    elif sex1 == sex2:
        points = 18
    return (points)

def checkRow (lnameA, fnameA, lnameB, fnameB):
    includeRow = 0
    if (len(lnameA) == 0 or len(lnameB) == 0 ): return (includeRow)
    if lnameA[0] ==  lnameB[0]: includeRow = 1
    if lnameA[0] ==  fnameB[0]: includeRow = 1
    if fnameA[0] ==  lnameB[0]: includeRow = 1
    if fnameA[0] ==  fnameB[0]: includeRow = 1
    return(includeRow)

def afterJuly1943 (somedate):
    # return True to skip the checks and automatically 
    if somedate == '': return (False)
    cutOff = time.strptime('07/01/1943', '%m/%d/%Y')
    checkDate = time.strptime(somedate, '%m/%d/%Y')
    if checkDate > cutOff: return (True)
    return (False)

def writeCSVrow ():
    a.writerow(rowInSPSS)
    highPointList.append(rowInSPSS['highPoint'])
    print (SPSSLine , rowInSPSS['dataSource'], rowInSPSS['highPoint'], rowInSPSS['firstname'], rowInSPSS['lastname'], sep=',')




##sys.exit('Debugging address')

print ('----Cycle Through Both Dictionaries----------')
SPSSLine = 0
accessPhoneBook = ['subject_phone_home', 'subject_phone_mobile', 'subject_phone_work', 'subject_phone_nursing']
SPSSPhoneBook = ['phonenumber']
SIRPhoneBook = ['swphone', 'shphone', 'cwphone', 'chphone']
outputFieldNames = ['id', 'highPoint', 'dataSource', 'multFactor', 'highFirstName', 'highLastName', 'highFirstLast', 'highLastFirst',
                    'highDOB', 'highSex', 'highAddress', 'highPhone', 
                    'lastname', 'firstname', 'address1', 'dob' , 'gendercode', 'zip5',
                    'matchID', 'matchLname', 'matchFname' ,'matchDOB' , 'matchSex', 'matchAddress', 'matchPhone']

with open(dups, 'w', newline='') as CSVDupObject:

##    a = csv.DictWriter(CSVDupObject, delimiter=',', fieldnames=SPSSDict[0])
    a = csv.DictWriter(CSVDupObject, delimiter=',', fieldnames= outputFieldNames, extrasaction='ignore')
    a.writeheader()

    for rowInSPSS in SPSSDict:
        SPSSLine += 1
        if rowInSPSS['zip5'] == '10025':  # any person with a ZIP of 10025 will not be previously known to us
            writeCSVrow ()
            continue
        if afterJuly1943(rowInSPSS['dob']):
            writeCSVrow ()
            continue

        SPSSPhoneList = []
        for eachSPSSPhone in SPSSPhoneBook:
            SPSSPhoneList.append(rowInSPSS[eachSPSSPhone])
        SPSSPhoneList = sorted(set(SPSSPhoneList))
##      if Escape is press, stop for loop and display summary report.  Only works when py file is double clicked
        if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode():
            aborted = True
            if aborted:
                print ('aborted')
                time.sleep(2)
                break

##      Compare to SIR data
        for rowInSIR in sirDict:
##          reset values
            pointTotal = pointLastName = pointFirstName = pointFirstLast = pointLastFirst = 0
            pointDOB = pointSex = pointAddress = pointPhone = 0
            matchingPhones = ''
            multFactor = 1

    ##      speed things ups, match only if first letter of either name match
            includeRow = checkRow(rowInSPSS['lastname'], rowInSPSS['firstname'], rowInSIR['lname'],rowInSIR['fname'])
            if includeRow == 0:  continue               
                
            pointAddress = compareAddress (rowInSPSS['address1'], rowInSIR['address'])

            pointDOB = compareDOB (rowInSPSS['dob'] , rowInSIR['db_dob'])

            pointLastName = compareName(rowInSPSS['lastname'], rowInSIR['lname'])

            pointFirstName = compareName(rowInSPSS['firstname'], rowInSIR['fname'])

            pointFirstLast = compareName(rowInSPSS['lastname'], rowInSIR['fname'])

            pointLastFirst = compareName(rowInSPSS['firstname'], rowInSIR['lname'])

            pointSex = compareSex(rowInSPSS['gendercode'], rowInSIR['db_sex'])
            
    ##      Same phone number in multiple columns is a problem.
            sirPhoneList = []    
            for eachSIRPhone in SIRPhoneBook:
                sirPhoneList.append(rowInSIR[eachSIRPhone])
            sirPhoneList = sorted(set(sirPhoneList))
            
            for eachSPSSPhone in SPSSPhoneList:
                for eachSIRPhone in sirPhoneList:
                    tempPhonePoints = comparePhone (eachSIRPhone, eachSPSSPhone) 
                    if tempPhonePoints > 0 :
                        matchingPhones += eachSIRPhone + ' = ' + eachSPSSPhone + ','
                        pointPhone += tempPhonePoints
 
            if pointLastName >= 6 :
                if pointLastName >= 10:     multFactor *= 3
                if pointFirstName >= 10:    multFactor *= 2
                elif pointFirstName >= 6:   multFactor *= 1.5
                if pointDOB > 9:            multFactor *= 2
                elif pointDOB == 9:         multFactor *= 1.5
                elif pointDOB < 0 :         multFactor /= 2
                if pointSex >= 18:          multFactor *= 2
                if pointAddress >= 8:       multFactor *= 2
                if pointPhone >= 10:        multFactor *= 2
            
                    
            elif pointFirstName >= 10:
                multFactor *=1.1
                if pointDOB == 9:           multFactor *= 1.2
                elif pointDOB > 9:          multFactor *= 1.5
                elif pointDOB < 0 :         multFactor /= 2
                if pointSex >= 18:          multFactor *= 1.5
                if pointAddress >= 8:       multFactor *= 2
                if pointPhone >= 10:        multFactor *= 2
                

            elif pointFirstLast >=6 and pointLastFirst >=6:
                if pointFirstLast >=10 and pointLastFirst >=10: multFactor *= 2
                if pointDOB == 9:       multFactor *= 1.2
                elif pointDOB > 9:      multFactor *= 1.5
                elif pointDOB < 0 :     multFactor /= 2
                if pointSex >= 18:      multFactor *= 1.2
                if pointAddress >= 8:   multFactor *= 2
                if pointPhone >= 10:    multFactor *= 2

            pointTotal = (pointLastName + pointFirstName + pointFirstLast + pointLastFirst +
                          pointDOB + pointSex + pointAddress + pointPhone)
            pointTotal *= multFactor
            pointTotal = round(pointTotal)
            if pointTotal > rowInSPSS['highPoint'] :
                rowInSPSS['highPoint']      = pointTotal
                rowInSPSS['dataSource']     = 'SIR'
                rowInSPSS['multFactor']     = multFactor
                rowInSPSS['highPhone']      = pointPhone
                rowInSPSS['highFirstName']  = pointFirstName
                rowInSPSS['highLastName']   = pointLastName
                rowInSPSS['highFirstLast']  = pointFirstLast
                rowInSPSS['highLastFirst']   = pointLastFirst
                rowInSPSS['highAddress']    = pointAddress
                rowInSPSS['highSex']        = pointSex
                rowInSPSS['highDOB']        = pointDOB
                
                rowInSPSS['matchID']      = rowInSIR['id_num']
                rowInSPSS['matchLname']   = rowInSIR['lname']
                rowInSPSS['matchFname']   = rowInSIR['fname']
                rowInSPSS['matchDOB']     = rowInSIR['db_dob']
                rowInSPSS['matchAddress'] = rowInSIR['address']
                rowInSPSS['matchPhone']   = matchingPhones
                rowInSPSS['matchSex']     = rowInSIR['db_sex']


##      Compare to Access data
        for rowInAccess in accessDict:
##          reset values
            pointTotal = pointLastName = pointFirstName = pointFirstLast = pointLastFirst = 0
            pointDOB = pointSex = pointAddress = pointPhone = 0
            matchingPhones = ''
            multFactor = 1

    ##      speed things ups, match only if first letter of either name match
            includeRow = checkRow(rowInSPSS['lastname'], rowInSPSS['firstname'], rowInAccess['lname'],rowInAccess['fname'])
            if includeRow == 0:  continue
              
            pointAddress = compareAddress (rowInSPSS['address1'], rowInAccess['address1'])

            pointDOB = compareDOB (rowInSPSS['dob'] , rowInAccess['dob'])

            pointLastName = compareName(rowInSPSS['lastname'], rowInAccess['lname'])

            pointFirstName = compareName(rowInSPSS['firstname'], rowInAccess['fname'])

            pointFirstLast = compareName(rowInSPSS['lastname'], rowInAccess['fname'])

            pointLastFirst = compareName(rowInSPSS['firstname'], rowInAccess['lname'])

            pointSex = compareSex(rowInSPSS['gendercode'], rowInAccess['sex'])
            
    ##      Same phone number in multiple columns is a problem.
            accessPhoneList = []    
            for eachAccessPhone in accessPhoneBook:
                accessPhoneList.append(rowInAccess[eachAccessPhone])
            accessPhoneList = sorted(set(accessPhoneList))
            
            for eachSPSSPhone in SPSSPhoneList:
                for eachAccessPhone in accessPhoneList:
                    tempPhonePoints = comparePhone (eachAccessPhone, eachSPSSPhone) 
                    if tempPhonePoints > 0 :
                        matchingPhones += eachAccessPhone + ' = ' + eachSPSSPhone + ','
                        pointPhone += tempPhonePoints
 
            if pointLastName >= 6 :
                if pointLastName >= 10:     multFactor *= 3
                if pointFirstName >= 10:    multFactor *= 2
                elif pointFirstName >= 6:   multFactor *= 1.5
                if pointDOB > 9:            multFactor *= 2
                elif pointDOB == 9:         multFactor *= 1.5
                elif pointDOB < 0 :         multFactor /= 2
                if pointSex >= 18:          multFactor *= 2
                if pointAddress >= 8:       multFactor *= 2
                if pointPhone >= 10:        multFactor *= 2
            
                    
            elif pointFirstName >= 10:
                multFactor *=1.1
                if pointDOB == 9:           multFactor *= 1.2
                elif pointDOB > 9:          multFactor *= 1.5
                elif pointDOB < 0 :         multFactor /= 2
                if pointSex >= 18:          multFactor *= 1.5
                if pointAddress >= 8:       multFactor *= 2
                if pointPhone >= 10:        multFactor *= 2
                

            elif pointFirstLast >=6 and pointLastFirst >=6:
                if pointFirstLast >=10 and pointLastFirst >=10: multFactor *= 2
                if pointDOB == 9:       multFactor *= 1.2
                elif pointDOB > 9:      multFactor *= 1.5
                elif pointDOB < 0 :     multFactor /= 2
                if pointSex >= 18:      multFactor *= 1.2
                if pointAddress >= 8:   multFactor *= 2
                if pointPhone >= 10:    multFactor *= 2

            pointTotal = (pointLastName + pointFirstName + pointFirstLast + pointLastFirst +
                          pointDOB + pointSex + pointAddress + pointPhone)
            pointTotal *= multFactor
            pointTotal = round(pointTotal)
            if pointTotal > rowInSPSS['highPoint'] :
                rowInSPSS['highPoint']      = pointTotal
                rowInSPSS['dataSource']     = 'Access'
                rowInSPSS['multFactor']     = multFactor
                rowInSPSS['highPhone']      = pointPhone
                rowInSPSS['highFirstName']  = pointFirstName
                rowInSPSS['highLastName']   = pointLastName
                rowInSPSS['highFirstLast']  = pointFirstLast
                rowInSPSS['highLastFirst']   = pointLastFirst
                rowInSPSS['highAddress']    = pointAddress
                rowInSPSS['highSex']        = pointSex
                rowInSPSS['highDOB']        = pointDOB
                
                rowInSPSS['matchID']      = rowInAccess['idnum']
                rowInSPSS['matchLname']   = rowInAccess['lname']
                rowInSPSS['matchFname']   = rowInAccess['fname']
                rowInSPSS['matchDOB']     = rowInAccess['dob']
                rowInSPSS['matchAddress'] = rowInAccess['address1']
                rowInSPSS['matchPhone']   = matchingPhones
                rowInSPSS['matchSex']     = rowInAccess['sex']


##      end of specific row in SPSS comparisons, add to output and report

        writeCSVrow ()

CSVDupObject.close()

### reporting section

    
print ('Counts: ')
highPointDict = {}
for i in set(highPointList):
    highPointDict[i] = highPointList.count(i)
##print ('One Way:')
##for i in sorted(set(highPointList)):
##    print (i, highPointList.count(i))

print ('Or Another:')
for dictItem in sorted(highPointDict):
    print (dictItem, ' points =', highPointDict[dictItem])


print ('Average: ' , round(sum(highPointList)/len(highPointList)), 'Min: ' , min(highPointList), 'Max: ', max(highPointList))


from itertools import groupby
##print ('---------- itertools -----------------')
##print ([len(list(group))  for key, group in groupby(birthdaylist)])

##print ([list(group)  for key, group in groupby(birthdaylist)])

endTime = DT.datetime.now()
print ("Program end : %s" % endTime)

diffTime = endTime - startTime
print ("Run time ", diffTime.days, "Days:",diffTime.seconds , "Seconds", diffTime.microseconds, "MicroSeconds: ")


if aborted: input("press any key to exit")
