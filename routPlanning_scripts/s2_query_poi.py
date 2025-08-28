import osmnx as ox
import folium
import os

# 调试信息
print("当前工作目录:", os.getcwd())
print("检查 GraphML 文件:", os.path.exists('D:/RoutePlan/project/data/manchester_graph.graphml'))

# 步骤 1: 加载本地路网
try:
    G = ox.load_graphml('D:/RoutePlan/project/data/manchester_graph.graphml')
    print("GraphML 文件加载成功。")
except Exception as e:
    print(f"错误：加载 GraphML 文件失败，{e}")
    exit(1)

# 步骤 2: 定义起点 (曼彻斯特大学)
accident_point = (53.4667, -2.2333)  # (lat, lon)

# 步骤 3: 查询 POI (警察局和医院)
try:
    # 查询警察局
    police_gdf = ox.geometries.geometries_from_point(accident_point, tags={'amenity': 'police'}, dist=10000)
    if police_gdf.empty:
        print("警告：未找到警察局，可能需扩大范围或检查数据。")
    else:
        police_point = (police_gdf.iloc[0].geometry.y, police_gdf.iloc[0].geometry.x)
        print(f"找到最近的警察局：{police_point}")

    # 查询医院
    hospital_gdf = ox.geometries.geometries_from_point(accident_point, tags={'amenity': 'hospital'}, dist=10000)
    if hospital_gdf.empty:
        print("警告：未找到医院，可能需扩大范围或检查数据。")
    else:
        hospital_point = (hospital_gdf.iloc[0].geometry.y, hospital_gdf.iloc[0].geometry.x)
        print(f"找到最近的医院：{hospital_point}")
except Exception as e:
    print(f"错误：查询 POI 失败，{e}")
    exit(1)

# 步骤 4: 创建地图并标记
m = folium.Map(location=accident_point, zoom_start=12)

# 标记事故点
folium.Marker(accident_point, popup='曼彻斯特大学 (事故点)', icon=folium.Icon(color='red')).add_to(m)

# 标记警察局
if not police_gdf.empty:
    folium.Marker(police_point, popup='警察局', icon=folium.Icon(color='blue')).add_to(m)

# 标记医院
if not hospital_gdf.empty:
    folium.Marker(hospital_point, popup='医院', icon=folium.Icon(color='green')).add_to(m)

# 保存地图
map_html = m._repr_html_()
with open('D:/RoutePlan/project/data/manchester_poi_map.html', 'w', encoding='utf-8') as f:
    f.write(map_html)
print("POI 地图已保存为 D:/RoutePlan/project/data/manchester_poi_map.html")

# 可选：本地查看 HTML 文件
import webbrowser
webbrowser.open('D:/RoutePlan/project/data/manchester_poi_map.html')