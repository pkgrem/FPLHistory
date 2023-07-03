import pandas as pd

def main():
    # Load the data
    filtered_data_url = 'https://raw.githubusercontent.com/pkgrem/FPLHistory/main/filtered_player_data.csv'
    cleaned_data_url = 'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/cleaned_players.csv'

    filtered_data = pd.read_csv(filtered_data_url)
    cleaned_data = pd.read_csv(cleaned_data_url)

    # Concatenate first_name and second_name
    cleaned_data['full_name'] = cleaned_data['first_name'] + ' ' + cleaned_data['second_name']

    # Select only the desired columns from cleaned_data
    cleaned_data = cleaned_data[['full_name', 'first_name', 'second_name', 'now_cost', 'element_type']]

    # Merge the two dataframes based on player names
    merged_data = pd.merge(filtered_data, cleaned_data, left_on='player', right_on='full_name', how='left')

    # Save the merged DataFrame to a new CSV file
    merged_data.to_csv('merged_filtered_player_data.csv', index=False)

    print("Data has been merged and saved to 'merged_filtered_player_data.csv'")

if __name__ == "__main__":
    main()
