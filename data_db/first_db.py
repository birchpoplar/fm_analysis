import os
import re
import json
import sqlite3
import pandas as pd
from datetime import datetime

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('fm_data.db')
cur = conn.cursor()
print('Connected to SQLite database')

# Create tables
cur.execute('''
    CREATE TABLE IF NOT EXISTS models
    (id INTEGER PRIMARY KEY, modelname TEXT, date TEXT, tag TEXT, data TEXT)
''')
print('Created table models')

# Check if the table has been created
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='models'")
if cur.fetchone():
    print('Table "models" exists.')
else:
    print('Table "models" does not exist.')

# Regular expression to extract model name, date, and tag from filename
regex = r'(.+)-(\d{6})_(.+)\.csv'

# Walk through all CSV files in directory
for root, dirs, files in os.walk('/home/johnnie/Projects/fm_analysis/data_db/data'):
    for file in files:
        if file.endswith('.csv'):
            # Parse filename
            print('Parsing file: ' + file)
            match = re.fullmatch(regex, file)
            if match:
                modelname, date, tag = match.groups()
                # Read CSV file into pandas DataFrame
                df = pd.read_csv(os.path.join(root, file))
                if df.empty:
                    print('DataFrame is empty.')
                else:
                    print(df)
                # Convert DataFrame to JSON
                df_json = df.to_json()
                # Store in database
                cur.execute('''
                    INSERT INTO models (modelname, date, tag, data) 
                    VALUES (?, ?, ?, ?)
                ''', (modelname, date, tag, df_json))
                print('Inserted data into database')

# Verify insertion
cur.execute("SELECT * FROM models")
rows = cur.fetchall()
if rows:
    print('Data has been successfully inserted.')
else:
    print('Data has not been inserted.')
                
# Commit changes and close connection
conn.commit()
conn.close()
print('Committed changes and closed connection')
