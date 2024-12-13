import xarray as xr
import os
from collections import defaultdict

# Define the directory to search
search_directory = "Base Climate Data"

# Find all NetCDF files in the directory
all_files = [
    f for f in os.listdir(search_directory)
    if f.endswith(".nc")
]

# Extract unique prefixes based on the first part of the file name
prefixes = set(f.split("_")[0] for f in all_files)

# Group files by their prefix
files_by_prefix = defaultdict(list)
for f in all_files:
    prefix = f.split("_")[0]
    files_by_prefix[prefix].append(os.path.join(search_directory, f))

# Process each group of files
for prefix, file_paths in files_by_prefix.items():
    datasets = []
    data_names = []
    
    for fp in file_paths:
        dataset = xr.open_dataset(fp)
        datasets.append(dataset)
        
        # Extract the variable names and attributes
        for var_name in dataset.data_vars:
            var_attrs = dataset[var_name].attrs
            data_names.append({
                "file_name": os.path.basename(fp),
                "variable_name": var_name,
                "attributes": var_attrs
            })
    
    # Concatenate datasets along the time dimension
    combined_data = xr.concat(datasets, dim="time")
    
    # Determine the name for the output file based on the prefix and variable name
    if data_names:
        output_variable_name = data_names[0]['variable_name']
        output_path = f"src/data/Processed Climate Data/combined_{prefix}_{output_variable_name}_data.nc"
    else:
        output_path = f"/src/data/Processed Climate Data/combined_{prefix}_climate_data.nc"
    
    # Save the combined dataset to a new NetCDF file
    combined_data.to_netcdf(output_path)
    
    # Output metadata information for review
    print(f"Combined dataset for prefix '{prefix}' saved to:", output_path)
    print("Extracted Metadata:")
    for entry in data_names:
        print(entry)
