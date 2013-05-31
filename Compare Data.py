import csv, sys, re, time
from datetime import datetime, timedelta

FromAccess = 'importFiles/Access.csv'
FromSIR = 'importFiles/SIR.csv'
dups = 'exportFiles/dups.txt'

##FromAccess = 'importFiles/A1.csv'
##FromSIR = 'importFiles/S1.csv'

accessDictionary = []
sirDictionary = []



def makeDict (inFile, OutDict):
##    print ('-----------------------')
##    print ('Read file: ' + inFile)
    ifile  = open(inFile, 'r')
    reader = csv.reader(ifile)
    lineNum = 0
    for eachLine in reader:
        lineNum += 1
##      check for blank lines
        if not eachLine:
            print ('Blank Line')
            time.sleep(1)
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
##                print ('{0:30} ==> {1:30}'. format(colheader[colnum], col))
                bigDict [colHeader[colNum]] = eachCol.upper()
                colNum += 1
            OutDict.append(bigDict) 
    ifile.close()
    print ('Cycled trough ', inFile, ':', str(lineNum - 1))



minrow = 0
maxrow = 10000
makeDict (FromAccess, accessDictionary)
## clean data from access
for rowInAccess in accessDictionary:
    if rowInAccess['sex'] == '0':   # zero = male
       rowInAccess['sex'] = 'M' 
    elif rowInAccess['sex'] == '1':
       rowInAccess['sex'] = 'F' 

minrow = 0
maxrow = 7000
makeDict (FromSIR, sirDictionary)

for rowInSIR in sirDictionary:
    if rowInSIR['db_sex'] == '0':   # zero = male
       rowInSIR['db_sex'] = 'M' 
    elif rowInSIR['db_sex'] == '1':
       rowInSIR['db_sex'] = 'F' 


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
    d1 = datetime.strptime(d1, "%m/%d/%Y")
    d2 = datetime.strptime(d2, "%m/%d/%Y")
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


def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring


def cleanAddress(address):
    # define characters to be removed
    removeChars = ['.', '-', ',', '!!!']
    singleChars = [ 'APT', 'AVE', 'AVENUE', 'BVLD', 'CT', 'COURT', 'DR', 'DRIVE',
                'FT', 'FORT', 'PL', 'PLACE', 'RD', 'ROAD', 'SAINT', 'ST', 'STREET',
                'TER', 'TERR', 'TERRACE',
                'N', 'S', 'E', 'W', 'NORTH', 'SOUTH', 'EAST', 'WEST']

    # wherever they are remove them
    for i in removeChars:
        address = address.replace(i, ' ')

    # remove if spaces on both sides
    for i in singleChars:
        address = address.replace(' ' + i + ' ', ' ')

    # remove from end of address
    for i in singleChars:
        address = rchop(address, i)

    # replace specific phrases
    address = address.replace('BWAY ', 'BROADWAY')
    address = address.replace("B'WAY ", 'BROADWAY')
    address = address.replace('WASH ', 'WASHINGTON')
    address = address.replace('AAVE ', 'AVE')
    address = address.replace('FIRST ', '1ST')
    address = address.replace('SECOND ', '2ND')
    address = address.replace('THIRD ', '3RD')
    address = address.replace('FOURTH ', '4TH')
    address = address.replace('FIFTH ', '5TH')
    address = address.replace('SIXTH ', '6TH')
    address = address.replace('SEVENTH ', '7TH')
    address = address.replace('EIGHTH ', '8TH')
    address = address.replace('NINETH ', '9TH')
    address = address.replace('TENTH ', '10TH')
    address = ' '.join(address.split())  # one way to pack multiple spaces
    return (address)


def compareAddress (a1, a2):
    points = 0
    if cleanAddress(a2) in cleanAddress(a1):
        points += 8
    elif cleanAddress(a1) in cleanAddress(a2):
        points += 8
    for aword in cleanAddress(a2).split():
        if aword in cleanAddress(a1):
##            print(aword, ':',  cleanAddress(a1))
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

def sexFromAccess (sex1):
    if sex1 == '0':
        sex1 == 'M'
    elif sex1 == '1':
        sex1 == 'F'
    return (sex1)

##sys.exit('Debugging address')


print ('----Cycle Through Both Dictionaries----------')
accessLine = 0
accessPhoneBook = ['subject_phone_home', 'subject_phone_mobile', 'subject_phone_work', 'subject_phone_nursing']
SIRPhoneBook = ['swphone', 'shphone', 'cwphone', 'chphone']

with open(dups, 'w') as dupObject:

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
                
        if highPoint > 31:
            print ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format('', rowInAccess['lname'], rowInAccess['fname'], rowInAccess['dob'], highPhone, rowInAccess['address1']))
            print ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( highPoint, highLast, highFirst, highDOB, '', highAddress ))
            print ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( '', matchInfo ['pln'], matchInfo ['pfn'], matchInfo ['pdob'], matchInfo['pphone'], matchInfo['paddress']))
            print('----------------------\n')

            str1 = rowInAccess['lname'] +',' + rowInAccess['fname'] + ',' +  rowInAccess['dob'] + ',' + highPhone +',' + rowInAccess['address1']
            dupObject.write ('\n')
            dupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format('', rowInAccess['lname'], rowInAccess['fname'], rowInAccess['dob'], highPhone, rowInAccess['address1']))
            dupObject.write ('\n')
            dupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( highPoint, highLast, highFirst, highDOB, '', highAddress ))
            dupObject.write ('\n')
            dupObject.write ('{0:5} {1:10} {2:15} {3:10} {4:35} {5:20}'. format( '', matchInfo ['pln'], matchInfo ['pfn'], matchInfo ['pdob'], matchInfo['pphone'], matchInfo['paddress']))
            dupObject.write ('\n')
        else:
            print ('-')
    ##        print ('{0:5} {1:10} {2:15} {3:10} {4:35}'. format(highPoint, rowInAccess['lname'], rowInAccess['fname'], rowInAccess['dob'], highPhone, rowInAccess['address1']))
            
dupObject.close()


from itertools import groupby
##print ('---------- itertools -----------------')
##print ([len(list(group))  for key, group in groupby(birthdaylist)])

##print ([list(group)  for key, group in groupby(birthdaylist)])

print ('---------- MyEnd -----------------')
