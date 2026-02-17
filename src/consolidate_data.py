"""
Consolidates multiple scraper output CSVs into a single master file.
"""
import pandas as pd
import os
import glob

def consolidate():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    data_dir = os.path.normpath(data_dir)
    
    # Find all fighter CSVs
    csv_files = glob.glob(os.path.join(data_dir, 'fighters*.csv'))
    
    if not csv_files:
        print("No fighter CSVs found to consolidate.")
        return

    print(f"Found {len(csv_files)} files: {[os.path.basename(f) for f in csv_files]}")
    
    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not dfs:
        return

    # Combine
    master_df = pd.concat(dfs, ignore_index=True)
    
    # Drop duplicates (based on URL)
    before = len(master_df)
    master_df.drop_duplicates(subset=['URL'], keep='last', inplace=True)
    after = len(master_df)
    print(f"Combined {before} records into {after} unique fighters.")
    
    # Sort by name
    master_df.sort_values('Name', inplace=True)
    
    # Save master
    master_path = os.path.join(data_dir, 'fighters_master.csv')
    master_df.to_csv(master_path, index=False)
    print(f"Saved master file to {master_path}")
    
    # Cleanup (Optional - maybe keep them for backup? Let's keep for now)
    # for f in csv_files:
    #     if f != master_path:
    #         os.remove(f)

if __name__ == "__main__":
    consolidate()
