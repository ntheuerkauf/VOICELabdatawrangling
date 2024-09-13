# -*- coding: utf-8 -*-
"""

@author: ntheuerkauf

This script was created to clean up a large set of data that my research PI gave to me.
Part of this task was to throw out undded columns and poor responses, normalize responses, and transform some columns into a more readable format
I also was tasked with harvesting some data from this data set and creating new files from it for future use.

I currently cannot upload the files with the data as it is not published yet, but I will add to the repository when available

"""



### importing needed libraries

import re
import pandas as pd

### loading up dataframe and dropping an unneeded row
df = pd.read_csv('languagehistory.csv')
df.drop(df.index[:4], inplace=True)


### lisitng all of the regexs needed for removal
delCol = [
    "lextale_complete",
    "lhq_time",
    "language([6-9]|\d{2,})",
    "agespeak([6-9]|\d{2,})",
    "ageread([5-9]|\d{2,})",
    "agelisten([5-9]|\d{2,})",
    "agewrite([5-9]|\d{2,})",
    "yearsuse([5-9]|\d{2,})",
    "country[2-4]",
    "lengthofstay[2-4]",
    "countrylanguage[2-4]",
    "langtraveluse[2-4]",
    "nonnative[2-9]",
    "athome([6-9]|\d{2,})",
    "withfriends([6-9]|\d{2,})",
    "atschool([6-9]|\d{2,})",
    "atwork([6-9]|\d{2,})",
    "langsoft([6-9]|\d{2,})",
    "game([5-9]|\d{2,})",
    "doctorswitch",
    "both$",
    "listen([6-9]|\d{2,})",
    "speak([6-9]|\d{2,})",
    "read([6-9]|\d{2,})",
    "write([6-9]|\d{2,})",
    "accent[5-9]",
    "^test",
    "tv([3-9]|\d{2,})",
    "radio([3-9]|\d{2,})",
    "funread([3-9]|\d{2,})",
    "workread([3-9]|\d{2,})",
    "internet([3-9]|\d{2,})",
    "workwrite([3-9]|\d{2,})",
    "family([3-9]|\d{2,})",
    "friend([3-9]|\d{2,})",
    "classmate([3-9]|\d{2,})",
    "other([3-9]|\d{2,})",
    "think([4-9]|\d{2,})",
    "self([4-9]|\d{2,})",
    "emote([4-9]|\d{2,})",
    "dream([4-9]|\d{2,})",
    "math([4-9]|\d{2,})",
    "number([4-9]|\d{2,})",
    "percent([4-9]|\d{2,})",
    "culture([3-9]|\d{2,})"
    "wayoflife([4-9]|\d{2,})",
    "^food",
    "^music",
    "^art",
    "^city",
    "^sport",
    "lhq_complete",
    "ego_time"   
    ]


### combining the regular expressions
combined = "(" + ")|(".join(delCol) + ")"

### removing the columns with regular expressions
for col in df:
    if re.match(combined, col):
        df = df.drop(col, axis=1)


###This removes participants who didn't fill out the survey fully
for index, row in df.iterrows():
    if type(row['name1']) == float or type(row['caregiver1_status']) == float or pd.isna(row['tie1']): 
        df.drop(index, inplace=True)

### Makes the dataframe lowercase and removes NaN
df = df.fillna('').astype(str).apply(lambda x: x.str.lower())



### dictionary used to normalize all of the responses to the "caregiver" questions
caregiverDict = {"my mother" : "mother","mom": "mother", "dad" : "father", "my father": "father", 
                 "biological mother": "mother", "biological father": "father", "daughter/mother": "mother",
                 "daughter/father": "father", "my mother, she was my main support,": "mother", "my father, he helped me continue studying.": "father",
                 "she's my mother.": "mother", "he's my father." : "father", "my mother. ": "mother", "my father.": "father",
                 "mother, made all of the meals and spent much more time with me." : "mother", "father, still took care of me but not as much because of work.": "father",
                 "my mother was home more from work.": "mother", "my father was there but somewhat less.": "father", "mother/son": "mother", "father/son": "father", "none": "",
                 'somewhat close.': 'other', 'not very close. ': 'other'}

### cleaning up the caregiver columns
df= df.replace(caregiverDict)



### Cleaning up the country columns, same technique for the caregivers columns

us = 'united states' #I only used this because I'm lazy
countryDict = {'usa': us, "u.s": us, 'us': us, 'united states of america': us, 'u.s.a.': us, 'america': us}

df= df.replace(countryDict)




### Cleaning up the culture column
c = ', '
d = ''
cultureDict = {'/ ': c, '/':c,'\(language\)': d, '-':c, ' \(':c, "\?": '','\)':d, 'speaking, ':d}

for col in ['culture1', 'culture2', 'culture3']:
    df[col] = df[col].replace(cultureDict, regex = True)
    
    
    

#### creating the switch column an deleting others


### List of words in the switch columns that don't trigger a switch
noSwitchList = ['n.a','na','-1', 'n/a', 'nothing', 'did not switch', '', 'english', 'english', '(it did not switch from english, but the survey will not let me continue if i do not answer this)','not yet']

### initalizing lists
switchData = []
eduSwitch = []
eduLang = []

### getting lists of the columns we need for this task
for col in df.columns.tolist():
    if re.search('switch$', col):
        eduSwitch.append(col)
    if re.search('language$', col):
        eduLang.append(col)


###finding which participants switch langauges or not
for index, row in df.iterrows():
    tempRow = []
    for i in eduSwitch:
        tempRow.append(row[i])
        
    if tempRow[0] == 'english' and re.search('spanish',  row['elementarylanguage']):  ### This only works because so many participants are ESL and native speakers of spanish
        switchData.append('1')
    elif all(empty in noSwitchList for empty in tempRow): ###If every item in a row is a word that doesn't actually signify a switch, then so switch has happened
        switchData.append('0')
    else: ### If a particpants passed the previous test, then a switch must have happened
        switchData.append('1')


### dropping the switch columns

for col in df:
    if re.search('switch$', col):
        df = df.drop(col, axis=1)

### adding the new data back into the dataframe
df.insert(df.columns.get_loc('doctorlanguage')+1, "switch", switchData)


### exporting the new csv file
df.to_csv('languagehistory_cleaned.csv', index = False)


### creating attribute list csv file


### lists of data
record_id = []
names = []
nodeID = []
relationship = []
strength = []
exposure = []
age = []
accent = []
langStatus = []



### Conversion dictionaries, used to make data more readable
tieDict = {'1.0':'family member', '2.0': 'significant other/partner', '3.0': 'friend', '4.0':'classmate', '5.0':'neighbor', '6.0':'colleague', '7.0':'other'}
ego_tieDict = {'1.0': "not close", "2.0": "somewhat close", "3.0": 'very close'}
exposreDict = {"1.0": "less than three years", "2.0":"three to six years", "3.0": "more than six years", "99.0": "don't know"}
ageDict = {'1.0': "0-12 years", "2.0": "13-17 years", "3.0": "18-25 years", "4.0": "26-40 years", "5.0": "41-60 years", "6.0": "61+ years"}
accentDict = {'1.0': "speaks like me", "2.0": "has a different regional accent", "3.0": "has a foreign accent", "4.0": "other varieties of english"}
langStatusDict = {"1.0": "bilingual", "2.0": "monolingual", "3.0": "not sure"}

### iterating through original data 
for index, row in df.iterrows():
    for i in range(1,16):
        record_id.append(row['record_id'])
        names.append(row['name'+str(i)])
        nodeID.append(str(i))
        relationship.append(tieDict[row['tie'+str(i)]])
        strength.append(ego_tieDict[row['ego_tie'+str(i)]])
        exposure.append(exposreDict[row['name' + str(i) + 'length']])
        age.append(ageDict[row['name' + str(i) + "age"]])
        accent.append(accentDict[row['name' + str(i) + "accent"]])
        langStatus.append(langStatusDict[row['name' + str(i) + "billingual"]])
   
        
### creating data dictionary, creating data frame, creating csv
attlistDict = {"record_id": record_id, "names": names, "nodeID": nodeID, "strength": strength, "exposure": exposure, "age": age, "accent": accent, "langStatus": langStatus}
attlist = pd.DataFrame(attlistDict)
attlist.to_csv('attributeList.csv', index = False)


### creating edgeList csv

### lists
record_id_edge = []
names_edge = []
from_edge = []
to_edge = []
relationship_edge = []

relationship_edgeDict = {'0.0':"no relationship", '1.0': "not close", "2.0": "somewhat close", "3.0": 'very close'}

for index, row in df.iterrows():
    for i in range(1,15):
        for j in range(i+1, 16):
            if relationship_edgeDict[row['a'+str(i)+'_tie_'+str(j)]] != 'no relationship':
                record_id_edge.append(row['record_id'])
                names_edge.append(row["name"+str(i)]+'_'+row['name'+str(j)])
                relationship_edge.append(relationship_edgeDict[row['a'+str(i)+'_tie_'+str(j)]])
                from_edge.append(str(i))
                to_edge.append(str(j))


        
        


### data dictionary, dataframe, and csv
edgeListdict = {'record_id': record_id_edge, "names": names_edge, "from":from_edge, "to":to_edge,"relationship":relationship_edge}
edgeList = pd.DataFrame(edgeListdict)
edgeList.to_csv("edgeList.csv", index = False)




