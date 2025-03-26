#!/usr/bin/env python3

import numpy as np
from glob import glob
import numpy as np
import csv

fnames = glob('C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/level_2_morphology.ome_seg.npy')

for f in fnames:
    dat = np.load(f, allow_pickle=True).item()

    for key in dat.keys():
        dtype = type(dat[key])
        print("Key:", key)
        print("Dtype:", dtype)

        if isinstance(dat[key], np.ndarray):
            print("Dimension:", dat[key].shape)
        elif isinstance(dat[key], list):
            print("Length:", len(dat[key]))

        # empty line between keys
        print()
        
        
        
# Open a CSV file for writing
with open('output.csv', mode='w', newline='') as csvfile:
    # Create a CSV writer object
    csv_writer = csv.writer(csvfile)
    
    # Write the header row
    csv_writer.writerow(['Key', 'Dtype', 'Additional_Info'])

    for f in fnames:
        dat = np.load(f, allow_pickle=True).item()

        for key in dat.keys():
            dtype = type(dat[key])
            additional_info = ""

            if isinstance(dat[key], np.ndarray):
                additional_info = f"Dimension: {dat[key].shape}"
            elif isinstance(dat[key], list):
                additional_info = f"Length: {len(dat[key])}"

            # Write a row in the CSV file for each key
            csv_writer.writerow([key, dtype, additional_info])