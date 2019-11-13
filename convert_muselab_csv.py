#!/usr/bin/env python3

import numpy as np
import pandas as pd
import sys
import csv
import argparse
import math
import logging
from progress.bar import Bar, IncrementalBar
import json



def main(fname):


    max_number_of_columns = 10

    base = pd.read_csv(fname, header=None, names=list(range(max_number_of_columns)))
    base.columns =  ['time','datatype'] + list(base.columns[2:])

    print("\n")
    print("Base \n")
    print(base)
    print(base.describe())
    print(base.dtypes)
    print("\n")


    results = [base.iloc[:,:2]]


    print("\n")
    print("Results \n")
    print(results)
    print("\n")


    for datatype in base['datatype'].unique():
        group = base[base['datatype']==datatype].iloc[:,2:].dropna(how='all', axis=1) 
        group.columns = [f"{datatype}_{x}" for x in range(len(group.columns))]
        results.append(group)

    final = pd.concat(results, axis=1)

    print("\n")
    print("Final \n")
    print(final)
    print(final.columns)
    print("\n")


             
# Muse Lab Fields
# 
#  /muse/acc
#  /muse/algorithm/concentration
#  /muse/algorithm/mellow
#  /muse/batt
#  /muse/eeg
#  /muse/elements/alpha_absolute
#  /muse/elements/beta_absolute
#  /muse/elements/blink
#  /muse/elements/delta_absolute
#  /muse/elements/alpha_absolute
#  /muse/elements/horseshoe
#  /muse/elements/jaw_clench
#  /muse/elements/theta_absolute
#  /muse/elements/touching_forehead
#  /muse/gyro




 
 
    conversion_csv_fname = fname + "_c.csv"
    conversion_json_fname = fname + "_c.json"
    data_csv_file = open(conversion_csv_fname, "w+")
    data_json_file = open(conversion_json_fname, "w+")
  
    print("Converting to JSON file\n")
    conversion_json = final.to_json()
    print("Converting to CSV file\n")
    conversion_csv = final.to_csv()
    print("\n")

    print("Writing new JSON file\n")
    
    data_json_file.write(conversion_json)
    data_json_file.write("\n\n")

    print("\n")
    print("Writing new CSV file\n")

    data_csv_file.write(conversion_csv)
    data_csv_file.write("\n\n")
    
    data_json_file.close()
    data_csv_file.close()
   

#     print(conversion_json)
#     print(conversion_csv)
    

    print("\n")
    print(final)
#     print(df_new_data.describe())
    print(final.dtypes)
    print("\n")


    print("Finished \n")







if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="CSV file to read)")
    
    args = parser.parse_args()

    if args.file:
        print("Processing CSV File:")
        print(args.file)
        csv_file = args.file

        main(csv_file)

