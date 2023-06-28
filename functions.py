#functions for data extraction and cleaning

#import modules
import regex as re
import pandas as pd
import numpy as np
import string
import googletrans as gt
from googletrans import Translator
translator = Translator()


#function to highlight rows with duplicate CAS values
def highlight_dup(dataframe, CAS_column):
    '''
    function to highlight rows with duplicate values in one column
    '''
    #create a copy of the dataframe
    df = dataframe.copy()
    #create a new column to highlight duplicates
    df['highlight'] = np.where(df[CAS_column].duplicated(), 'background-color: yellow', '')
    #return the highlighted dataframe
    return df.style.apply(lambda x: x.highlight, axis=1)

#Once highlighted, user can filter the dataframe to show only the highlighted rows
#df[df['highlight'] == 'background-color: yellow']
#If CAS numbers are same but values in limit columns are different, user must use own intuition to combine rows into 1 CAS number.



#function to remove rows of duplicate CAS numbers when limit values are also the same
def remove_dup(dataframe, CAS_column):
    '''
    function to only remove rows of duplicate CAS numbers when the rows for limit values are also duplicates
    '''
    #create a copy of the dataframe
    df = dataframe.copy()
    #create a new column to highlight duplicates
    df['highlight'] = np.where(df[CAS_column].duplicated(), 'background-color: yellow', '')
    #return the highlighted dataframe
    df = df[df['highlight'] == 'background-color: yellow']
    #drop the highlighted rows
    df = df.drop_duplicates(subset=['CAS Number', 'Limit Value'])
    #return the dataframe with highlighted rows removed
    return df


#function to translate csv file into a dataframe
def csv_to_df(csv_file):
    '''
    function to translate csv file into a dataframe
    '''
    #read csv file into a dataframe
    df = pd.read_csv(csv_file)
    #return the dataframe
    return df


#function to separate CAS number from chemical name in a dataframe
def extract_cas(df, column):
    '''
    function to extract CAS number into separate column when joined to a chemical name in a dataframe
    '''
    #create a copy of the dataframe
    df = df.copy()
    #create a new column for CAS number
    df['CAS Number'] = df[column].str.extract(r'(\d{2,7}-\d{2}-\d)', expand=False).str.strip()

    #return the dataframe
    return df

#function to separate chemical name from CAS number in a dataframe 
# NOT WORKING CORRECTLY YET
def extract_name(df, column):
    '''
    function to extract chemical name into separate column when joined to a CAS number in a dataframe
    '''
    #create a copy of the dataframe
    df = df.copy()
#create a new column for chemical name that removes the square brackets and CAS number
    df['Chemical Name'] = df[column].str.split(r'(\[\d{2,7}-\d{2}-\d)', expand=True)[0]
    #remove ascii characters from chemical name
    pattern = re.compile(f"[^{string.printable}]")
    filtered_data = df['Chemical Name'].apply(lambda x: pattern.sub('', x))
    df['Chemical Name'] = filtered_data.str.strip()

    #return the dataframe
    return df


#function to translate multiple specific columns in a dataframe from a detected language to english using googletrans
def translate(df, columns, df2):
    '''
    Function to translate multiple specific columns in a dataframe from a detected language to english using googletrans.
    The columns in the original language are then appended to the translated dataframe for future reference.

    Note: This function requires googletrans version 3.1.0a0 to be installed to avoid messages about the 'text' attribute not being found.
            Functions includes a print statement to show the version of googletrans being used.
    '''
    import googletrans as gt
    from googletrans import Translator
    print('Googletrans version =' + str(gt.__version__))
    if gt.__version__ != '3.1.0a0':
        print('Please install googletrans version 3.1.0a0 to avoid errors')
    translator = Translator()
    #copy the columns to another dataframe to append to the original dataframe later
    print('copying original columns of interest')
    df2 = df[columns].copy()
    #start translation
    print('starting translation')
    for column in columns:
        df[column] = df[column].apply(translator.translate, src='auto', dest='en').apply(getattr, args=('text',))
    #append the translated columns to the original dataframe
    df2.rename(columns={columns[0]: columns[0] + '_original', columns[1]: columns[1] + '_original'}, inplace=True)
    df = df.join(df2)
    #return the dataframe
    return df

