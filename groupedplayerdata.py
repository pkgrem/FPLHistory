import requests
import pandas as pd
from io import StringIO
from urllib.parse import quote

# GitHub API URL for the repository folder
api_url = "https://api.github.com/repos/vaastav/Fantasy-Premier-League/contents/data/2022-23/players"

# Make a request to the GitHub API
response = requests.get(api_url)

# List to store individual DataFrames
dataframes = []

# Columns to keep
columns_to_keep = [
    'assists', 'bonus', 'bps', 'clean_sheets', 'creativity', 'element',
    'expected_assists', 'expected_goal_involvements', 'expected_goals',
    'expected_goals_conceded', 'goals_conceded', 'goals_scored', 'ict_index',
    'influence', 'minutes', 'own_goals', 'penalties_missed', 'penalties_saved',
    'red_cards', 'saves', 'selected', 'starts', 'team_a_score', 'team_h_score',
    'threat', 'total_points', 'transfers_in', 'transfers_out', 'value', 'yellow_cards',
    'player'  # This is the additional column we added for player names
]

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    files = response.json()
    
    # Base URL for raw files
    base_raw_url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/players"
    
    # Loop through each file in the folder
    for file in files:
        # Get the file name
        file_name = file['name']
        
        # Encode the file name
        encoded_file_name = quote(file_name)
        
        # Construct the raw file URL
        raw_file_url = f"{base_raw_url}/{encoded_file_name}/gw.csv"
        
        # Print a message indicating which file is being processed
        print(f"Processing {file_name}...")
        
        # Read the CSV data directly into a DataFrame
        data = pd.read_csv(raw_file_url)
        
        # Add a column for the player name
        data['player'] = file_name
        
        # Add the 'Involved' column based on the 'minutes' column
        data['Involved'] = data['minutes'].apply(lambda x: 1 if x > 0 else 0)
        
        # Append the DataFrame to the list
        dataframes.append(data)

    # Concatenate all the DataFrames into a single DataFrame
    combined_data = pd.concat(dataframes, ignore_index=True)

    # Group by 'player' and 'element' and aggregate
    grouped_data = combined_data.groupby(['player', 'element']).agg({
        'assists': 'sum',
        'bonus': 'sum',
        'bps': 'sum',
        'clean_sheets': 'sum',
        'creativity': 'sum',
        'expected_assists': 'sum',
        'expected_goal_involvements': 'sum',
        'expected_goals': 'sum',
        'expected_goals_conceded': 'sum',
        'goals_conceded': 'sum',
        'goals_scored': 'sum',
        'ict_index': 'sum',
        'influence': 'sum',
        'minutes': 'sum',
        'own_goals': 'sum',
        'penalties_missed': 'sum',
        'penalties_saved': 'sum',
        'red_cards': 'sum',
        'saves': 'sum',
        'selected': 'mean',
        'starts': 'sum',
        'team_a_score': 'sum',
        'team_h_score': 'sum',
        'threat': 'sum',
        'total_points': 'sum',
        'transfers_in': 'sum',
        'transfers_out': 'sum',
        'value': 'sum',
        'yellow_cards': 'sum',
        'Involved': 'sum'
    }).reset_index()

    # Save the grouped data to a CSV file
    grouped_data.to_csv('grouped_player_data.csv', index=False)

    # Convert the DataFrame to an HTML table
    html_table = grouped_data.to_html(index=False, classes="display", table_id="dataTable")

    # HTML content with DataTables
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css">
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js"></script>
        <script>
            $(document).ready( function () {{
                $('#dataTable').DataTable();
            }} );
        </script>
    </head>
    <body>
        {html_table}
    </body>
    </html>
    """

    # Save the HTML content to a file with UTF-8 encoding
    with open('grouped_player_data.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
else:
    print("Failed to retrieve data")
