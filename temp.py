


# Import packages
import pandas as pd
import gender_detector as gd
import numpy as np
pd.set_option('max_rows',500)
pd.set_option('max_columns',500)



# Directories
#my_dir='C:/Users/annaairoldi/Dropbox/'
my_dir = '/Users/ubc/Dropbox/'
mos_1921_data=my_dir+'MoS18/mos_data/raw/1921/postmerge/'
mos_1921_old=mos_1921_data + 'old/'
mos_1921_correction= my_dir+ 'MoS18/census_matching_project/Hong -/clean_MoS1921/correction/'
cleaning_dir=my_dir+'/MoS cleaning/cleaning_birthplaces/data/'



# Open the files
mos_new=pd.read_csv(mos_1921_old+'mos_1921_merged.csv', encoding='ISO-8859-1',low_memory=False)
mos_old=pd.read_csv(mos_1921_old+'AMoS1921_all.csv', encoding='ISO-8859-1',low_memory=False)
mos_corrected = pd.read_csv(mos_1921_correction+'MoS_entries_corrected.csv', encoding='ISO-8859-1',low_memory=False)



## check the columns in each file 

mos_new_col = list(mos_new.columns)
mos_old_col = list(mos_old.columns)
mos_corrected_col = list(mos_corrected.columns)

a =[x for x in mos_corrected_col if x not in mos_new_col]   
b =[x for x in mos_new_col if x not in mos_corrected_col]   

print(f'Columns in corrected file that are not in the new file: {a}')



### 1 NEW GENDER VARIABLE

#Drop older  female variable
mos_new=mos_new.drop(['Female'],axis='columns')

#Define new variable
from gender_detector import gender_detector
detector=gender_detector.GenderDetector('us')
mos_new['Gender']=0
for index,row in mos_new.iterrows():
    mos_new.loc[index,'Gender']=detector.guess(row['First Name'])
    if index % 1000 ==0:
        print(index)



## 2-3 GET FIELD AND STAR VARIABLE FROM OLDER FILE ##
## to do this, first I need to make the IDs comparable
## In the new file, the first ids are missing an 'A'. For instance A10 has id '10'
## I add the A back in.
mos_new['ID']=mos_new['ID'].astype('str')
mos_new['ID_new']=mos_new['ID'].copy()

for index, row in mos_new.iterrows():
    if row['ID'][0] in [0,1,2,3,4,5,6,7,8,9,'1','2','3','4','5','6','7','8','9']:
        mos_new.loc[index,'ID_new']='A'+str(row['ID'])
## I manually need to fix one of the IDs: same ID for two different people
mos_new.loc[9024,'ID_new']='B189b'


### Now I can map the Field1 variable and the star variable using the ID
mos_new['star'] = mos_new['ID_new'].map(mos_old.set_index('ID')['star'])
mos_new['Field1_correct'] = mos_new['ID_new'].map(mos_old.set_index('ID')['Field1'])



## Check the difference
mos_new[mos_new['ID_new'].str[0]=='A'][['Field1','Field1_correct','star']].head(10)


## Now I drop the wrong 'Field' column and rename the correct one
mos_new=mos_new.drop(['Field1'],axis='columns')
mos_new.columns = ['Field1' if x=='Field1_correct' else x for x in mos_new.columns]



### 4 FIX BIRTHSTATE AND BIRTH VARIABLE
## Cleaned versions of the variables are available in the cleaning directory
## We can match them to the file using ID_new as a key
cleaned_birthplaces=pd.read_csv(cleaning_dir+'mos1921_cleaned_birthplaces.csv',encoding='latin1')
mos_new['Birth State New']=mos_new['ID_new'].map(cleaned_birthplaces.set_index('ID_new')['Birth State New'])
mos_new['Birth Country New']=mos_new['ID_new'].map(cleaned_birthplaces.set_index('ID_new')['Birth Country New'])



mos_new[['ID_new','Birth State', 'Birth State New','Birth Country','Birth Country New']].head(5)



## Delete and rename
mos_new=mos_new.drop(['Birth State'],axis='columns')
mos_new.columns = ['Birth State' if x=='Birth State New' else x for x in mos_new.columns]
mos_new=mos_new.drop(['Birth Country'],axis='columns')
mos_new.columns = ['Birth Country' if x=='Birth Country New' else x for x in mos_new.columns]



## 5 FIX SOME OF THE SPECIAL CHARACTERS ENCODING
#It is impossible to find out what was the original encoding, but at least we can try to fix the characters using 
#the older file
#SO FAR I FIX ONLY FIRST AND LAST NAMES
# Other variables, like awards and institutions could be fixed.


### Find the characters which give me issues
first_names=[]
for index,row in mos_new.iterrows():
    x=row['First Name']
    try:
        x.encode('ascii')
    except:
        first_names.append([x,index,row['ID_new']])
first_names_old=[]
for x in first_names:
    name_old=mos_old[mos_old['ID']==x[2]]['FirstName'].values.tolist()
    first_names_old.append(name_old)
    
    
last_names=[]
for index,row in mos_new.iterrows():
    x=row['Last Name']
    try:
        x.encode('ascii')
    except:
        last_names.append([x,index,row['ID_new']])
last_names_old=[]
for x in last_names:
    name_old=mos_old[mos_old['ID']==x[2]]['LastName'].values.tolist()
    last_names_old.append(name_old)
for x in range(len(last_names)):
    print(last_names[x],last_names_old[x])
    
    
dict_garbled={'\x87':'á','Ø':'ÿ','\x97':'ó','\x8e':'é','\x8d':'ç','\x91':'ë','\x8f':'è','\x9a':'ö','\x8a':'ä','\x9f':'ü'}

    