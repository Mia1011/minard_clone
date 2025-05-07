import pandas as pd
import sqlite3


class CreateMinardDB: 
    def __init__(self): 
        with open("data/minard.txt") as f: 
            lines = f.readlines()
        self.lines = lines
        
        # 資料清理(欄位名稱)
        columns = (lines[2].split()) # a list
        # ['(lonc', 'latc', 'city$', 'lont', 'temp', 'days', 'date$', 'lonp', 'latp', 'surviv', 'direc$', 'division),']
        patterns_to_be_replaced = {'(', '$', ')', ','}

        adjusted_columns = []
        for column in columns:
            for pattern in patterns_to_be_replaced:
                if pattern in column:
                    column = column.replace(pattern, '') # (a, b) replace a with b
            adjusted_columns.append(column) # add the cleaned column name to the list
        self.city_columns = adjusted_columns[:3]
        self.temp_columns = adjusted_columns[3:7]
        self.troop_columns = adjusted_columns[7:]
    
    def create_city_df(self): 
        lonc, latc, city = [], [], [] # lists
        for i in range(6, 26): 
            line = self.lines[i].split()[:3]
            lonc.append(float(line[0]))
            latc.append(float(line[1]))
            city.append(line[2])
        city_data = (lonc, latc, city) # tuple
        city_df = pd.DataFrame()
        for column, data in zip(self.city_columns, city_data):
            city_df[column] = data
        return city_df

    def create_temp_df(self):
        lont, temp, days, date = [], [], [], [] # lists
        for i in range(6, 15): 
            line = self.lines[i].split()
            lont.append(float(line[3]))
            temp.append(float(line[4]))
            days.append(int(line[5]))
            if i == 10: date.append("Nov 24")
            else: date.append(line[6]+" "+line[7])
        temp_data = (lont, temp, days, date) # tuple
        temp_df = pd.DataFrame()
        for column, data in zip(self.temp_columns, temp_data):
            temp_df[column] = data
        return temp_df

    def create_troop_df(self):
        lonp, latp, surviv, direc, division = [], [], [], [], [] # lists
        for i in range(6, 54): 
            line = self.lines[i].split()[-5:]
            lonp.append(float(line[0]))
            latp.append(float(line[1]))
            surviv.append(int(line[2]))
            direc.append(str(line[3]))
            division.append(int(line[4]))
        troop_data = (lonp, latp, surviv, direc, division) # tuple
        troop_df = pd.DataFrame()
        for column, data in zip(self.troop_columns, troop_data):
            troop_df[column] = data
        return troop_df
    
    def create_db(self):
        connection = sqlite3.connect("data/minard.db")

        city_df = self.create_city_df()
        temp_df = self.create_temp_df()
        troop_df = self.create_troop_df()
        df_dict = {
            "cities": city_df,
            "temperatures": temp_df,
            "troops": troop_df
        }
        for k, v in df_dict.items():
            v.to_sql(name=k, con=connection, if_exists='replace', index=False)
        connection.close()

db = CreateMinardDB()
db.create_db()