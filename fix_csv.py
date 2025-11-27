import pandas as pd
import os
import shutil

CSV_FILE = 'training_log.csv'
BACKUP_FILE = 'training_log.csv.bak'

def fix_csv():
    if not os.path.exists(CSV_FILE):
        print(f"File {CSV_FILE} not found.")
        return

    # Create backup
    shutil.copy(CSV_FILE, BACKUP_FILE)
    print(f"Backup created at {BACKUP_FILE}")

    try:
        # Read the raw lines to handle mixed schemas manually if needed, 
        # but pandas might be able to handle it if we are careful.
        # Let's try reading it as a standard CSV first, but treating everything as object to avoid type errors
        df = pd.read_csv(CSV_FILE, header=0)
        
        cleaned_rows = []
        
        for index, row in df.iterrows():
            # Create a standardized dictionary for the new row
            new_row = {
                'Timestamp': row.get('Timestamp'),
                'Username': row.get('Username'),
                'Email': 'N/A',
                'Score': 0,
                'Completed': False,
                'DurationSeconds': 999999
            }
            
            # Heuristic to detect Old Schema vs New Schema
            # Old Schema: Timestamp, Username, Score, Completed, DurationSeconds, Email (often N/A or missing)
            # New Schema: Timestamp, Username, Email, Score, Completed, DurationSeconds
            
            # Check if the 3rd column (index 2) looks like an email or a score
            # In the dataframe, we access by column name, but the column names might be shifted if the header was old.
            
            # Let's look at the raw values.
            # If 'Email' column exists and has an '@', it's likely the new schema or a correctly migrated row.
            # If 'Score' column has an '@', then the columns are shifted.
            
            # Actually, let's look at the file content provided in the context:
            # Line 1: Timestamp,Username,Score,Completed,DurationSeconds,Email
            # Line 18: 2025-11-26 10:23:35,Tech Savy,Lomo@myfiducia.com,1000,True,46.927396
            
            # In Line 18:
            # Timestamp = 2025-11-26 10:23:35
            # Username = Tech Savy
            # Score (header) -> Value is "Lomo@myfiducia.com" (This is the shift!)
            # Completed (header) -> Value is "1000"
            # DurationSeconds (header) -> Value is "True"
            # Email (header) -> Value is "46.927396"
            
            val_under_score = row.get('Score')
            val_under_completed = row.get('Completed')
            val_under_duration = row.get('DurationSeconds')
            val_under_email = row.get('Email')
            
            if isinstance(val_under_score, str) and '@' in val_under_score:
                # This is a NEW schema row but read with OLD header
                new_row['Email'] = val_under_score
                new_row['Score'] = val_under_completed
                new_row['Completed'] = val_under_duration
                new_row['DurationSeconds'] = val_under_email
            else:
                # This is an OLD schema row (or already correct?)
                # If it was correct, val_under_score would be a number.
                new_row['Score'] = val_under_score
                new_row['Completed'] = val_under_completed
                new_row['DurationSeconds'] = val_under_duration
                new_row['Email'] = val_under_email if pd.notna(val_under_email) else 'N/A'

            cleaned_rows.append(new_row)
            
        # Create new DataFrame
        new_df = pd.DataFrame(cleaned_rows)
        
        # Ensure columns are in correct order
        cols = ['Timestamp', 'Username', 'Email', 'Score', 'Completed', 'DurationSeconds']
        new_df = new_df[cols]
        
        # Save
        new_df.to_csv(CSV_FILE, index=False)
        print("CSV fixed successfully.")
        print(new_df.tail())
        
    except Exception as e:
        print(f"Error fixing CSV: {e}")
        # Restore backup
        shutil.copy(BACKUP_FILE, CSV_FILE)
        print("Restored backup due to error.")

if __name__ == "__main__":
    fix_csv()
