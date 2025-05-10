import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import os

# URL và XPath
URL = "https://www.footballtransfers.com"
TRANSFER_SECTION_XPATH = "//h2[contains(text(), 'Biggest Transfers')]"
TRANSFER_LIST_XPATH = "following-sibling::ul"
TRANSFER_ITEM_TAG = "li"

# Function to initialize WebDriver
def initialize_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to scrape transfer values for players
def scrape_transfer_values():
    driver = initialize_driver()
    players_data = []

    try:
        print("Loading transfer page...")
        driver.get(URL)
        
        driver.implicitly_wait(10)
        try:
            transfers_section = driver.find_element(By.XPATH, TRANSFER_SECTION_XPATH)
            transfers_list = transfers_section.find_element(By.XPATH, TRANSFER_LIST_XPATH)

            # Extract player data
            transfers = transfers_list.find_elements(By.TAG_NAME, TRANSFER_ITEM_TAG)
            if not transfers:
                print("No players found in the transfer list.")
                return

            for transfer in transfers:
                try:
                    player_info = transfer.text.strip().split(" - ")
                    if len(player_info) == 2:
                        name, value = player_info
                        players_data.append({'Name': name.strip(), 'Value': value.strip()})
                        print(f"Scraped player: {name.strip()}, Value: {value.strip()}")
                    else:
                        print(f"Skipping invalid transfer data: {transfer.text}")
                except Exception as e:
                    print(f"Error parsing transfer data: {e}")
                    continue

            # Save data to CSV
            if players_data:
                df = pd.DataFrame(players_data)
                df.to_csv('transfer_values.csv', index=False, encoding='utf-8-sig')
                print("Transfer values saved to transfer_values.csv")
            else:
                print("No data scraped. Transfer values file will not be created.")

        except Exception as e:
            print("Không tìm thấy phần 'Biggest Transfers'. Kiểm tra lại cấu trúc HTML.")
            return

    except Exception as e:
        print(f"Error occurred during scraping: {e}")
    finally:
        driver.quit()

# Function to estimate player values using machine learning
def estimate_player_values():
    # Check if transfer_values.csv exists and is not empty
    if not os.path.exists('transfer_values.csv'):
        raise FileNotFoundError("transfer_values.csv not found. Run scrape_transfer_values first.")
    
    transfer_df = pd.read_csv('transfer_values.csv')
    if transfer_df.empty:
        raise ValueError("transfer_values.csv is empty. Scraping may have failed.")

    # Load stats data
    stats_df = pd.read_csv('results2.csv')

    # Merge datasets on player name
    merged_df = pd.merge(stats_df, transfer_df, on='Name', how='inner')

    # Select features and target
    features = ['Gls_mean', 'Ast_mean', 'xG_mean', 'xAG_mean', 'PrgC_mean', 'PrgP_mean']
    target = 'Value'

    # Handle missing values
    merged_df = merged_df.dropna(subset=features + [target])

    # Convert target (Value) to numeric
    merged_df[target] = merged_df[target].str.replace('€', '').str.replace('M', '').astype(float)

    # Split data into training and testing sets
    X = merged_df[features]
    y = merged_df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train the model
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")

    # Save the model
    joblib.dump(model, 'player_value_model.pkl')
    print("Model saved as player_value_model.pkl")

# Main function to run both parts
def main():
    # Step 1: Scrape transfer values
    scrape_transfer_values()

    # Step 2: Estimate player values
    try:
        estimate_player_values()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")

# Run the main function
if __name__ == "__main__":
    main()