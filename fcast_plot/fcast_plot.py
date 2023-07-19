import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, EngFormatter
import numpy as np
import ast
import datetime

# Define a function to format the date as quarter
def format_quarter(x, pos=None):
    month = mdates.num2date(x).month
    year = mdates.num2date(x).year
    quarter = (month - 1) // 3 + 1
    return f'Q{quarter}-{year}'

# Connect to the sqlite database
conn = sqlite3.connect('complete_data.db')

# Get the names of all tables in the database
table_names = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
table_names = [name[0] for name in table_names if name[0].startswith('snapshot')]

# Read each table into a DataFrame and store them in a list
tot_rev_data = [pd.read_sql_query(f"SELECT * from {name}", conn) for name in table_names]

# Read the 'models' table from the data base
models = pd.read_sql_query("SELECT * from models", conn)

# Convert 'data' column back to dictionaries
models['data'] = models['data'].apply(ast.literal_eval)

# Create a single plot for all model snapshots
fig, ax = plt.subplots(figsize=(15, 10))

# Create a colormap to map the line color to the snapshot date
cmap = plt.get_cmap('cool')
colors = [cmap(i) for i in np.linspace(0, 1, len(tot_rev_data))]

for i, (data, color) in enumerate(zip(tot_rev_data, colors[::-1])):  # Reverse the colors list so that the most recent snapshot has the strongest color
    # Remove the row with 'Month' in the 'month' column and convert 'month' column to datetime
    data = data.loc[data['month'] != 'Month'].copy()
    data['month'] = pd.to_datetime(data['month'])
    
    # Filter data for years 2022 and 2023
    data = data.loc[(data['month'].dt.year == 2022) | (data['month'].dt.year == 2023)]
    
    # Plot forecast data
    forecast_data = data[data['act_fcast'] == 'Fcast']
    snapshot_date = models.iloc[i]['date']
    snapshot_parsed_date = datetime.datetime.strptime(snapshot_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    ax.plot(forecast_data['month'], forecast_data['tot_rev'].astype(np.float), label=f'Snapshot {snapshot_parsed_date} - Forecast', color=color, linestyle='--')

# Format the date on the x-axis to show quarter only
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(FuncFormatter(format_quarter))

# Apply EngFormatter to the y-axis
ax.yaxis.set_major_formatter(EngFormatter())

plt.title('Total Revenue Over Time (2022-2023)')
plt.xlabel('Date')
plt.ylabel('Total Revenue')
plt.legend()
plt.grid(True)
# plt.show()
plt.savefig('tot_rev_fcast.png')

# Close the database connection
conn.close()
