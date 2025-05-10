import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Khởi tạo trình duyệt
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL trang web
url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats'

try:
    # Truy cập trang web
    driver.get(url)
    time.sleep(5)  # Đợi trang tải xong

    # Phân tích HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Tìm bảng thống kê cầu thủ
    table = soup.find('table', {'id': 'stats_standard'})

    if table is None:
        print("Không tìm thấy bảng dữ liệu. Kiểm tra lại URL hoặc cách truy cập.")
    else:
        players = []
        for row in table.find('tbody').find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if cells:
                player_data = {}
                for cell in cells:
                    if cell.name == 'th':
                        player_data['player'] = cell.text.strip()
                    elif cell.name == 'td':
                        stat = cell.get('data-stat')
                        if stat:
                            player_data[stat] = cell.text.strip()
                minutes = player_data.get('minutes', '0').replace(',', '').strip()
                try:
                    minutes = int(minutes)
                    if minutes > 90:  # Lọc cầu thủ chơi trên 90 phút
                        players.append(player_data)
                except ValueError:
                    continue

        # Tạo DataFrame
        df = pd.DataFrame(players)

        # Đổi tên cột, đảm bảo ánh xạ đúng
        rename_dict = {
            'player': 'Player',
            'nationality': 'Nation',
            'position': 'Pos',
            'team': 'Squad',
            'age': 'Age',
            'birth_year': 'Born',
            'games': 'MP',
            'games_starts': 'Starts',
            'minutes': 'Min',
            'minutes_90s': '90s',
            'goals': 'Gls',
            'assists': 'Ast',
            'goals_assists': 'G+A',
            'goals_pens': 'G-PK',
            'pens_made': 'PK',
            'pens_att': 'PKatt',
            'cards_yellow': 'CrdY',
            'cards_red': 'CrdR',
            'xg': 'xG',
            'npxg': 'npxG',
            'xg_assist': 'xAG',
            'npxg_xg_assist': 'npxG+xAG',
            'progressive_carries': 'PrgC',
            'progressive_passes': 'PrgP',
            'progressive_passes_received': 'PrgR',
            'goals_per90': 'Gls/90',
            'assists_per90': 'Ast/90',
            'goals_assists_per90': 'G+A/90',
            'goals_pens_per90': 'G-PK/90',
            'goals_assists_pens_per90': 'G+A-PK/90',
            'xg_per90': 'xG/90',
            'xg_assist_per90': 'xAG/90',
            'xg_xg_assist_per90': 'xG+xAG/90',
            'npxg_per90': 'npxG/90',
            'npxg_xg_assist_per90': 'npxG+xAG/90',
            'matches': 'Matches'
        }
        df = df.rename(columns=rename_dict)

        # Chuyển đổi cột số
        numerical_cols = [
            'Age', 'MP', 'Starts', 'Min', '90s', 'Gls', 'Ast', 'G+A', 'G-PK', 'PK', 'PKatt',
            'CrdY', 'CrdR', 'xG', 'npxG', 'xAG', 'npxG+xAG', 'PrgC', 'PrgP', 'PrgR',
            'Gls/90', 'Ast/90', 'G+A/90', 'G-PK/90', 'G+A-PK/90', 'xG/90', 'xAG/90',
            'xG+xAG/90', 'npxG/90', 'npxG+xAG/90'
        ]
        for col in numerical_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Danh sách thống kê để phân tích
        stats_to_analyze = ['Gls', 'Ast', 'G+A', 'xG', 'npxG', 'xAG', 'PrgC', 'PrgP']

        # Tạo bảng kết quả
        results = []
        row_all = {'Team': 'all'}
        for stat in stats_to_analyze:
            if stat in df.columns:
                row_all[f'{stat}_median'] = df[stat].median()
                row_all[f'{stat}_mean'] = df[stat].mean()
                row_all[f'{stat}_std'] = df[stat].std()
        results.append(row_all)

        # Mỗi đội
        teams = df['Squad'].unique()
        for team in teams:
            team_df = df[df['Squad'] == team]
            row = {'Team': team}
            for stat in stats_to_analyze:
                if stat in team_df.columns:
                    row[f'{stat}_median'] = team_df[stat].median()
                    row[f'{stat}_mean'] = team_df[stat].mean()
                    row[f'{stat}_std'] = team_df[stat].std()
            results.append(row)

        # Lưu vào file results2.csv theo định dạng bảng
        results_df = pd.DataFrame(results)

        # Đảm bảo các cột được sắp xếp theo thứ tự mong muốn
        columns_order = ['Team']
        for stat in stats_to_analyze:
            columns_order.extend([f'{stat}_median', f'{stat}_mean', f'{stat}_std'])

        # Sắp xếp lại thứ tự cột
        results_df = results_df[columns_order]

        # Lưu vào file CSV
        results_df.to_csv('results2.csv', index=False, encoding='utf-8-sig')
        print("File results2.csv đã được lưu theo định dạng bảng.")

finally:
    driver.quit()