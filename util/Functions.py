import os
import pandas as pd
from . import Lists
import warnings
import time
import numpy as np
import re
import logging



def clean_result(value):
    if isinstance(value, str):
        if re.match(r'^<\d+(\.\d+)?$', value) or re.match(r'^\d+(\.\d+)?$', value):
            return value
    return np.nan

def write_data(Writing_file, df, sheet):

    while True:
        try:
            with pd.ExcelWriter(Writing_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer: 
                df.to_excel(writer, sheet_name= sheet, index=False)
                print("Completed entry for " + sheet  )
                logging.info("Completed entry for " + sheet  )
                break
        except PermissionError:
            print("Unable to write to file. It may be open in another program.")
            input("Please close the file if it's open and press any key to try again.")
            # Optional: add a delay before next attempt to avoid rapid, successive attempts
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            logging.error(f"An error occurred: {e}")
            input('Press any key to enc')
            exit(1)

def transform_parameters(df, test_type, parameter):
    
    Sample_no = list(df['Sample #'].unique())
    Sample_no = df[['Sample #', 'Client Sample #']].drop_duplicates().values.tolist()

    project_no = df['Project #'].loc[0]
    job_no = df['Job #'].loc[0] 
    
    if test_type == 'Dissolved|Total|Mercury':
        df = df[
            ~(df['Test'].str.contains('Dissolved|Total|Mercury', case=False, na=False))
        ]
    else:
        df = df[
            df['Test'].str.contains(test_type, case=False, na=False)
        ]
        df['Parameter'] = df['Parameter'].str.replace(parameter, '')

    parameter_check = False

    if df.empty:
        parameter_check = True
        df_pivot = pd.DataFrame()

        return df_pivot, parameter_check
    else:

        # Converting the ug/L values to mg/L         
        df['Result'] = df.apply(lambda row: process_result(row['Result'], row['Units']), axis=1)

        final_df = df[['Sampling Date','Client Sample #', 'Test', 'Parameter', 'Result']]

        df_pivot = final_df.pivot_table(index=['Sampling Date', 'Client Sample #'], columns='Parameter', values='Result', aggfunc=lambda x: ' '.join(str(v) for v in x)).reset_index()
        
        df_sample_no = pd.DataFrame(Sample_no, columns=['Sample #', 'Client Sample #'])

        df_pivot = df_pivot.merge(df_sample_no, left_on='Client Sample #', right_on='Client Sample #', how='left')
        df_pivot['Project #'] = project_no
        df_pivot['Job #'] = job_no

        df_pivot.insert(1, 'Sample #', df_pivot.pop('Sample #'))
        df_pivot.insert(2, 'Project #', df_pivot.pop('Project #'))
        df_pivot.insert(3, 'Job #', df_pivot.pop('Job #'))

    return df_pivot, parameter_check

def handle_detection_data(df):
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Iterate over columns starting from the 6th one (index 5)
        for col in df.columns[5:]:
            value = row[col]
            # Check if the value is NaN, and if so, skip processing
            if pd.isna(value):
                continue
            if isinstance(value, str) and '<' in value:
                # Remove '<' sign and convert to float, then divide by 2
                try:
                    new_value = float(value.replace('<', '')) / 2
                except ValueError:
                    new_value = np.nan  # Handle the case where conversion fails
                df.at[index, col] = new_value
                
    return df


def convert_to_float(df):
    
    list_of_columns = df.columns.tolist()

    list_of_columns = list_of_columns[5:]

    for i in list_of_columns:
        df[i] = df[i].apply(lambda x: float(x) if not x.startswith('<') else x)

    return df
        
def join_with_master(df_master, df_pivot):

    for idx, row in df_master.iterrows():
        df_pivot = df_pivot[~((df_pivot['Sample #'] == row['Sample #']) & (df_pivot['Client Sample #'] == row['Client Sample #']))]

    df_appended = df_master._append(df_pivot, ignore_index=True)

    df_appended['Sampling Date'] = pd.to_datetime(df_appended['Sampling Date'], errors='coerce')

    df_appended.sort_values(by='Sampling Date', inplace =True)

    return df_appended

def process_result(value, unit):
    if unit == 'ug/L':  # Process only if the unit is 'ug/L'
        if isinstance(value, str) and '<' in value:
            # Remove the '<', convert to mg/L, and add '<' back
            numeric_part = float(float(value.replace('<', '').strip())) / 1000
            return f'<{numeric_part}'
        elif pd.to_numeric(value, errors='coerce') is not None:
            # Convert numeric strings or floats to mg/L
            return float(value) / 1000
    return value