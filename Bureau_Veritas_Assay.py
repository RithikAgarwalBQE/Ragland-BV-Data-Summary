import pandas as pd
import warnings
import numpy as np
import logging
from util import Extract
from util import Functions
from util import Post_Processing
warnings.filterwarnings("ignore")


logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='Logs.log'  # Output log messages to a file
)

#Production = 0 when application is under build and production = 1 when the application is deployed
production = 0

#setting up path to all the required files
if production == 1:
    folder_path = 'Input_files'
    file_path = folder_path + '\\'
    Writing_file = 'Database\\' + 'MasterData.xlsx'
    destination = 'Archive_Files'
else:
    folder_path = "../Input_files"
    file_path = folder_path + '/'
    Writing_file = '../Database/' + 'MasterData.xlsx'
    destination = "../Archive_Files"


file_list = Extract.get_file_list(folder_path)


print("Starting...............")
logging.info("Starting...............")

error_files = []

for file in file_list:

    print("Working on file", file)
    logging.info("Working on file" + file)
    file_location = file_path + file
    

    df = Extract.read_file(file_location, file)

    if df.empty:
        continue

    try:
        df['Result'] = df['Result'].apply( lambda x: Functions.clean_result(x))

        df_pivot_metal, no_metal  = Functions.transform_parameters(df, test_type='Total', parameter ='Total Extractable ' )
        
        if df_pivot_metal.empty:
            print("No total metal")
            logging.info("No total metal")
            no_metal = True
        
        else:
            df_pivot_metal = Functions.convert_to_float(df_pivot_metal)

    except KeyError as e:
        print(f"A KeyError occurred: {str(e)}. Please make sure the necessary columns exist in the input data.")
        logging.error(f"A KeyError occurred: {str(e)}. Please make sure the necessary columns exist in the input data.")
        continue
    except Exception as e:
        print(f"An error occurred while processing the data: {str(e)}")
        logging.error(f"An error occurred while processing the data: {str(e)}")
        continue
    
    if no_metal == False: 

        metal_master_df = Extract.read_database(Writing_file, sheet = 'Metals')

        df_appended_metal = Functions.join_with_master(metal_master_df, df_pivot_metal)
            
        Functions.write_data(Writing_file, df_appended_metal, sheet='Metals')

        df_metal_refined = Functions.handle_detection_data(df_pivot_metal)

        metal_refined_master_df = Extract.read_database(Writing_file, sheet = 'Metal Refined')

        df_appended_metal_refined = Functions.join_with_master(metal_refined_master_df, df_metal_refined)
            
        Functions.write_data(Writing_file, df_appended_metal_refined, sheet='Metal Refined')



    try:
        df_pivot_metal_dissolved,no_dissolved_metal  = Functions.transform_parameters(df, test_type='Dissolved', parameter= 'Dissolved ')


        if df_pivot_metal_dissolved.empty:
            print("No dissolved metal")
            logging.info("No dissolved metal")
            no_dissolved_metal = True
        else:
            df_pivot_metal_dissolved = Functions.convert_to_float(df_pivot_metal_dissolved)
            
    except KeyError as e:
        print(f"A KeyError occurred: {str(e)}. Please make sure the necessary columns exist in the input data.")
        logging.error(f"A KeyError occurred: {str(e)}. Please make sure the necessary columns exist in the input data.")
        continue
    except Exception as e:
        print(f"An error occurred while processing the data: {str(e)}")
        logging.error(f"An error occurred while processing the data: {str(e)}")
        continue
    
    if no_dissolved_metal == False:
        dissolved_metal_master_df = Extract.read_database(Writing_file, sheet= 'Dissolved')

        df_appended_metal_dissolved = Functions.join_with_master(dissolved_metal_master_df, df_pivot_metal_dissolved)

        Functions.write_data(Writing_file, df_appended_metal_dissolved, sheet='Dissolved')

        df_dissolved_refined = Functions.handle_detection_data(df_pivot_metal_dissolved)   

        dissolved_refined_master_df = Extract.read_database(Writing_file, sheet = 'Dissolved Refined')

        df_appended_dissolved_refined = Functions.join_with_master(dissolved_refined_master_df, df_dissolved_refined)
            
        Functions.write_data(Writing_file, df_appended_dissolved_refined, sheet='Dissolved Refined')

        

    try:
        df_pivot_conventional,no_conventional  = Functions.transform_parameters(df, test_type='Dissolved|Total|Mercury', parameter= '')

        if df_pivot_conventional.empty:
            print("No dissolved metal")
            logging.info("No dissolved metal")
            no_conventional = True
        else:
            df_pivot_conventional = Functions.convert_to_float(df_pivot_conventional)

    except KeyError as e:
        print(f"A KeyError occurred: {str(e)}. Please make sure the necessary columns exist in the input data.")
        logging.error(f"A KeyError occurred: {str(e)}. Please make sure the necessary columns exist in the input data.")
        input("Press Enter to end ")
        continue
    except Exception as e:
        print(f"An error occurred while processing the data: {str(e)}")
        logging.error(f"An error occurred while processing the data: {str(e)}")
        input("Press Enter to end ")
        continue

    if no_conventional == False:

        conventional_master_df = Extract.read_database(Writing_file, sheet='Conventional')

        df_appended_conventional = Functions.join_with_master(conventional_master_df, df_pivot_conventional)

        Functions.write_data(Writing_file, df_appended_conventional, sheet='Conventional' )

        df_conventional_refined = Functions.handle_detection_data(df_pivot_conventional)

        conventional_refined_master_df = Extract.read_database(Writing_file, sheet = 'Conventional Refined')

        df_appended_conventional_refined = Functions.join_with_master(conventional_refined_master_df, df_conventional_refined)
            
        Functions.write_data(Writing_file, df_appended_conventional_refined, sheet='Conventional Refined')

    print(f"completed entry for file {file}")
    logging.info(f"completed entry for file {file}")
    print("...................................")

Post_Processing.remove_files(file_list, file_path)

input("Master Data Updated, please press Enter to end")
logging.info("Master Data Updated, please press Enter to end")