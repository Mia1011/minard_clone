from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from matplotlib.patches import ConnectionPatch
import os

connection = sqlite3.connect("data/minard.db")
city_df = pd.read_sql("SELECT * FROM cities", connection)
temp_df = pd.read_sql("SELECT * FROM temperatures", connection)
troop_df = pd.read_sql("SELECT * FROM troops", connection)
con_df = pd.read_sql("""
                     SELECT t.temp, t.lont AS lons, c.latc AS lats
                     FROM temperatures t
                     JOIN cities c
                     ON c.lonc = t.lont
                     """, connection)
connection.close()

# 匯入資料
city_lons = city_df["lonc"].values # numpy array
city_lats = city_df["latc"].values
city_names = city_df["city"].values
troop_lons = troop_df["lonp"].values
troop_lats = troop_df["latp"].values
survivals = troop_df["surviv"].values
directions = troop_df["direc"].values
temp_lons = temp_df["lont"].values # numpy array
temp_celsius = (temp_df["temp"] * 5/4).astype(int) # nparray -> int

# 生成底圖
fig, axes = plt.subplots(nrows=2, # 上下兩個子圖
                         figsize=(25, 12), # 寬, 高
                         gridspec_kw={"height_ratios": [7, 2]}) # keyword arguments 分配高度比例
                         
# 繪製第一個子圖
m = Basemap(projection="lcc", resolution="i", width=1100000, height=400000, 
            lon_0=31, lat_0=55, ax=axes[0])
# ：地圖
m.drawcountries()
m.drawrivers(color="lightskyblue")
m.drawparallels(range(54, 57), labels=[True, False, False, False], color="grey", fontsize=12) # 左, 右, 上, 下
m.drawmeridians(range(23, 39, 2), labels=[False, False, False, True], color="grey", fontsize=12)
# ：城市圖
x, y = m(city_lons, city_lats) # 轉換經緯度為地圖座標
for xi, yi, city_names in zip(x, y, city_names):
    axes[0].annotate(text=city_names, xy=(xi, yi), ha="center", fontsize=15, zorder=2) # zorder：數字越大圖層越上面
# ：軍隊圖
rows = troop_df.shape[0] # shape()會回傳(rows, columns) -> tuple
x, y = m(troop_lons, troop_lats)
for i in range(rows-1):
    line_of_lons = (x[i], x[i+1])
    line_of_lats = (y[i], y[i+1])
    line_width = survivals[i]/5000
    if directions[i] == "A": # attack
        line_color = "tan" 
    elif directions[i] == "R": # retreat
        line_color = "olivedrab"
    m.plot(line_of_lons, line_of_lats, linewidth=line_width, color=line_color, zorder=1, )

# 繪製第二個子圖：氣溫圖
annotations = temp_celsius.astype(str).str.cat(temp_df["date"], sep="°C\n") # int -> str
axes[1].plot(temp_lons, temp_celsius, color="black")
for lon, temp, annotation in zip(temp_lons, temp_celsius, annotations):
    axes[1].annotate(annotation, xy=(lon-0.2, temp-15), fontsize=14)
axes[1].set_ylim(-55, 10)
axes[1].set_xlim(temp_lons.min()-2.9, temp_lons.max()+2)  # Adjust the length of the subplot
axes[1].spines["top"].set_visible(False)
axes[1].spines["right"].set_visible(False)
axes[1].spines["bottom"].set_visible(False)
axes[1].spines["left"].set_visible(False)
axes[1].grid(axis='y', alpha=0.7)
axes[1].set_xticklabels([])
axes[1].set_yticklabels([])
    
# 在兩個子圖之間添加虛線連接
important_lons = con_df["lons"].values
important_lats = con_df["lats"].values
important_temps = (con_df["temp"] * 5/4).values

for lon, lat, temp in zip(important_lons, important_lats, important_temps):
    x_map, y_map = m(lon, lat)  # 將經度轉換為第一個子圖的地圖座標，假設緯度固定為55
    x_temp = lon # 在第二個子圖中找到對應的x座標
    con = ConnectionPatch(
        xyA=(x_map, y_map), coordsA=axes[0].transData,
        xyB=(x_temp, temp), coordsB=axes[1].transData,
        linestyle="--", color="black", alpha=0.5
    )
    fig.add_artist(con)

axes[0].set_title("Napoleon's disastrous Russian campaign of 1812", loc="left", fontsize=25, fontweight="bold")
# plt.show()
plt.tight_layout()
output_path = "minard_clone.png"
if os.path.exists(output_path):
    os.remove(output_path)
fig.savefig(output_path)

"""
# 繪製地圖
m = Basemap(projection="lcc", resolution="i", width=1000000, height=400000, 
            lon_0=31, lat_0=55) # (lon_0, lat_0)：地圖中心點
m.drawcountries()
m.drawrivers()
m.drawparallels(range(54, 57), labels=[True, False, False, False]) # 左, 右, 上, 下
m.drawmeridians(range(23, 39, 2), labels=[False, False, False, True])
lons = [24.0, 37.6] # 37.6 55.8 Moscou 
lats = [55.0, 55.8] # 24.0 55.0 Kowno  
xi, yi = m(lons, lats)
m.scatter(xi, yi)

# 繪製城市圖
city_lons = city_df["lonc"].values # numpy array
city_lats = city_df["latc"].values
city_names = city_df["city"].values
fig, ax = plt.subplots()
m = Basemap(projection="lcc", resolution="i", width=1000000, height=400000, 
            lon_0=31, lat_0=55, ax=ax)
m.drawcountries()
m.drawrivers()
x, y = m(city_lons, city_lats)
for xi, yi, city_names in zip(x, y, city_names):
    plt.text(xi, yi, city_names, fontsize=6) 
    # ax.annotate(text=city_names, xy=(xi, yi), fontsize=6) # 另一種寫法

# 繪製氣溫圖 
temp_lons = temp_df["lont"].values # numpy array
temp_celsius = (temp_df["temp"] * 5/4).values # 列氏Reaumur * 5/4 = 攝氏Celsius
fig, ax = plt.subplots()
ax.plot(temp_lons, temp_celsius)
plt.show()

# 繪製軍隊圖
troop_lons = troop_df["lonp"].values
troop_lats = troop_df["latp"].values
survivals = troop_df["surviv"].values
directions = troop_df["direc"].values
fig, ax = plt.subplots()
rows = troop_df.shape[0] # shape()會回傳(rows, columns) -> tuple
for i in range(rows-1):
    line_of_lons = (troop_lons[i], troop_lons[i+1]) # troop_lons[i:i+2] 也可以
    line_of_lats = (troop_lats[i], troop_lats[i+1])
    line_width = survivals[i]/10000
    if directions[i] == "A": # attack
        line_color = "tan" 
    elif directions[i] == "R": # retreat
        line_color = "black"
    ax.plot(line_of_lons, line_of_lats, linewidth=line_width, color=line_color)
plt.show()
"""