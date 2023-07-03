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
        
        # Remove numbers and replace underscores with spaces in player name
        player_name = " ".join(file_name.split('_')[:-1]).replace('_', ' ')
        
        # Add a column for the player name
        data['player'] = player_name
        
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
        'threat': 'sum',
        'total_points': 'sum',
        'transfers_in': 'sum',
        'transfers_out': 'sum',
        'value': 'sum',
        'yellow_cards': 'sum',
        'Involved': 'sum'
    }).reset_index()

    # Round the 'selected' field to 0 decimal places
    grouped_data['selected'] = grouped_data['selected'].round(0)

    # Create the 'Net Transfers' column
    grouped_data['Net Transfers'] = grouped_data['transfers_in'] - grouped_data['transfers_out']

    # Create the '90s completed' column
    grouped_data['90s completed'] = grouped_data['minutes'] / 90

    # Create the per 90 metrics
    grouped_data['expected_assists_per90'] = grouped_data['expected_assists'] / grouped_data['90s completed']
    grouped_data['expected_goal_involvements_per90'] = grouped_data['expected_goal_involvements'] / grouped_data['90s completed']
    grouped_data['expected_goals_per90'] = grouped_data['expected_goals'] / grouped_data['90s completed']
    grouped_data['expected_goals_conceded_per90'] = grouped_data['expected_goals_conceded'] / grouped_data['90s completed']

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
                var table = $('#dataTable').DataTable();
                
                // Custom filtering function for minutes
                $.fn.dataTable.ext.search.push(
                    function(settings, data, dataIndex) {{
                        var minMinutes = parseInt($('#minMinutes').val(), 10);
                        var minutes = parseFloat(data[8]) || 0; // minutes is in the 9th column (index 8)
                        return isNaN(minMinutes) || minutes >= minMinutes;
                    }}
                );
                
                // Re-filter the table when the minimum minutes input changes
                $('#minMinutes').keyup(function() {{
                    table.draw();
                }});
            }} );
        </script>
    </head>
    <body>
        <label>Min Minutes: <input type="text" id="minMinutes"></label>
        {html_table}
    </body>
    </html>
    """

    # Save the HTML content to a file with UTF-8 encoding
    with open('grouped_player_data_with_filter.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Save the filtered data to a CSV file
    grouped_data.to_csv('filtered_player_data.csv', index=False)
else:
    print("Failed to retrieve data")
