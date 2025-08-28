import osmnx as ox
import os
from shapely.geometry import Point
import geopandas as gpd

# 调试信息
print("当前工作目录:", os.getcwd())
print("检查 GraphML 文件:", os.path.exists('D:/RoutePlan/project/data/manchester_graph.graphml'))

# 步骤 1: 加载 GraphML 文件
try:
    G = ox.load_graphml('D:/RoutePlan/project/data/manchester_graph.graphml')
    print("GraphML 文件加载成功。")
except Exception as e:
    print(f"错误：加载 GraphML 文件失败，{e}")
    exit(1)

# 步骤 2: 转换为 GeoDataFrame 检查节点属性
try:
    # 捕获返回值，避免解包错误
    result = ox.graph_to_gdfs(G, nodes=True, edges=False)
    if isinstance(result, tuple):
        nodes = result[0]  # 如果返回元组，取第一个元素（nodes）
    else:
        nodes = result  # 如果返回单一 GDF，直接使用
    print("节点数据提取成功，共有节点数:", len(nodes))

    # 过滤包含 amenity 标签的节点
    poi_nodes = nodes[nodes['amenity'].notna()]
    print("包含 amenity 标签的节点数:", len(poi_nodes))

    # 步骤 3: 根据输入点位置优化筛选
    input_point = Point(-2.2333, 53.4667)  # 输入点（lon, lat），曼彻斯特大学
    poi_nodes['distance'] = poi_nodes.distance(input_point)  # 计算距离（单位：米）
    nearby_poi = poi_nodes[poi_nodes['distance'] < 10000]  # 筛选 10km 内 POI
    nearby_poi = nearby_poi.sort_values('distance')  # 按距离排序

    print("10km 内 POI 数量:", len(nearby_poi))

    # 展示部分信息（前 5 个 POI）
    if not nearby_poi.empty:
        print("前 5 个 POI 信息:")
        for idx, row in nearby_poi.head(5).iterrows():
            amenity = row['amenity']
            coords = (row['y'], row['x'])
            distance = row['distance']
            print(f"  - {amenity} at {coords}, distance: {distance:.2f} m")
    else:
        print("警告：未找到 10km 内 POI。")
except Exception as e:
    print(f"错误：解析节点数据失败，{e}")
    exit(1)

