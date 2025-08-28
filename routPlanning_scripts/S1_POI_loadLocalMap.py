import osmnx as ox
import matplotlib.pyplot as plt
import os
import xml.etree.ElementTree as ET
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point

# 调试信息
print("当前工作目录:", os.getcwd())
print("检查文件:", os.path.exists('D:/RoutePlan/project/data/greater-manchester-latest.osm.pbf'))

# 步骤 1: 从 OSM 文件加载路网
osm_file = 'D:/RoutePlan/project/data/greater-manchester-latest.osm'
try:
    if not os.path.exists(osm_file):
        raise FileNotFoundError(f"文件 {osm_file} 不存在，请先使用 osmium cat 转换 PBF 到 OSM。")
    # 加载基础路网
    G = ox.graph_from_xml(osm_file, simplify=True)
    print("OSM 文件加载成功。")
except Exception as e:
    print(f"错误：加载 OSM 文件失败，{e}")
    exit(1)

# 步骤 2: 手动解析 OSM 文件提取 POI
poi_nodes = []
try:
    tree = ET.parse(osm_file)
    root = tree.getroot()
    for elem in root.findall('.//node'):
        tags = {tag.get('k'): tag.get('v') for tag in elem.findall('tag')}
        if 'amenity' in tags:
            poi_nodes.append({
                'osmid': int(elem.get('id')),
                'lat': float(elem.get('lat')),
                'lon': float(elem.get('lon')),
                'amenity': tags['amenity']
            })
    print(f"找到 {len(poi_nodes)} 个带 amenity 标签的 POI。")
except Exception as e:
    print(f"警告：解析 POI 数据失败，{e}")

# 步骤 3: 将 POI 合并到图中
if poi_nodes:
    try:
        # 转换为 GeoDataFrame
        poi_gdf = gpd.GeoDataFrame(poi_nodes, geometry=[Point(lon, lat) for lon, lat in zip([n['lon'] for n in poi_nodes], [n['lat'] for n in poi_nodes])])
        poi_gdf = poi_gdf.set_index('osmid')

        # 将 POI 数据添加到图的节点属性
        for idx, row in poi_gdf.iterrows():
            if idx in G.nodes:
                nx.set_node_attributes(G, {idx: {'amenity': row['amenity']}})
        print("POI 数据成功合并到图的节点属性。")
    except Exception as e:
        print(f"错误：合并 POI 数据失败，{e}")
else:
    print("警告：未找到任何 POI 数据，使用原始路网。")

# 步骤 4: 保存 GraphML
try:
    ox.save_graphml(G, 'D:/RoutePlan/project/data/manchester_graph_with_poi.graphml')
    print("OSM 文件成功转换为 GraphML，包含 POI 数据。")
except Exception as e:
    print(f"错误：保存 GraphML 文件失败，{e}")
    exit(1)

# 步骤 5: 从 GraphML 加载路网
try:
    G_loaded = ox.load_graphml('D:/RoutePlan/project/data/manchester_graph_with_poi.graphml')
    print("GraphML 文件加载成功。")
except Exception as e:
    print(f"错误：加载 GraphML 文件失败，{e}")
    exit(1)

# 步骤 6: 可视化地图以验证加载
try:
    fig, ax = ox.plot_graph(G_loaded, show=False, save=True, filepath='D:/RoutePlan/project/data/manchester_map.png')
    plt.show()
    print("地图加载成功，已保存为 D:/RoutePlan/project/data/manchester_map.png")
except Exception as e:
    print(f"错误：绘制地图失败，{e}")
    exit(1)