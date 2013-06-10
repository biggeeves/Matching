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
    address = address.replace('BWAY ', 'BROADWAY ')
    address = address.replace("B'WAY ", 'BROADWAY ')
    address = address.replace('WASH ', 'WASHINGTON ')
    address = address.replace('AAVE ', 'AVE ')
    address = address.replace('FIRST ', '1ST ')
    address = address.replace('SECOND ', '2ND ')
    address = address.replace('THIRD ', '3RD ')
    address = address.replace('FOURTH ', '4TH ')
    address = address.replace('FIFTH ', '5TH ')
    address = address.replace('SIXTH ', '6TH ')
    address = address.replace('SEVENTH ', '7TH ')
    address = address.replace('EIGHTH ', '8TH ')
    address = address.replace('NINETH ', '9TH ')
    address = address.replace('TENTH ', '10TH ')
    address = ' '.join(address.split())  # one way to pack multiple spaces
    return (address)

def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring