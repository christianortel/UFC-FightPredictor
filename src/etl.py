import pandas as pd
import sqlite3
import os
from src.db_manager import init_db, get_connection, DB_NAME
from src.processor import clean_fighters

def run_etl():
    """
    Extracts data from CSV, Transforms it, and Loads it into SQLite.
    """
    # 1. Init DB
    init_db()
    
    # 2. Extract
    csv_path = 'data/fighters_master.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print("Extracting data from CSV...")
    df = pd.read_csv(csv_path)
    
    # 3. Transform
    print("Cleaning and Transforming data...")
    # Use the processor's cleaning logic (imputation, normalization)
    df = clean_fighters(df)
    
    # 4. Load
    print("Loading data into SQLite...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear existing data to avoid duplicates on re-run
    cursor.execute("DELETE FROM fighter_stats")
    cursor.execute("DELETE FROM fighters")
    
    # Prepare the query
    insert_fighter_sql = """
        INSERT INTO fighters (name, nickname, height_cm, reach_cm, stance, dob, weight_lbs, weight_class, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    insert_stats_sql = """
        INSERT INTO fighter_stats (
            fighter_id, wins, losses, draws, 
            sapm, slpm, str_acc, str_def, 
            td_avg, td_acc, td_def, sub_avg
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    count = 0
    for _, row in df.iterrows():
        try:
            # Insert into fighters table
            cursor.execute(insert_fighter_sql, (
                row['Name'], 
                row.get('Nickname', None), 
                row['Height_cm'], 
                row['Reach_cm'], 
                row['Stance'], 
                row.get('DOB', None),
                row.get('Weight_lbs', None),
                row.get('WeightClass', None),
                row['URL']
            ))
            
            fighter_id = cursor.lastrowid
            
            # Insert into stats table
            cursor.execute(insert_stats_sql, (
                fighter_id,
                row['Wins'], row['Losses'], row['Draws'],
                row['SApM'], row['SLpM'], row['Str_Acc'], row['Str_Def'],
                row['TD_Avg'], row['TD_Acc'], row['TD_Def'], row['Sub_Avg']
            ))
            count += 1
            
        except sqlite3.IntegrityError:
            print(f"Skipping duplicate: {row['Name']}")
        except KeyError as e:
            print(f"Missing column {e} for {row['Name']}")
        except Exception as e:
            print(f"Error inserting {row['Name']}: {e}")

    conn.commit()
    conn.close()
    print(f"ETL Complete! Loaded {count} fighters into {DB_NAME}")

if __name__ == "__main__":
    run_etl()
