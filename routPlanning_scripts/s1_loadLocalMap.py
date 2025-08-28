import osmnx as ox
import matplotlib.pyplot as plt
import os
import osmium

# 调试信息
print("当前工作目录:", os.getcwd())
print("检查文件:", os.path.exists('D:/RoutePlan/project/data/greater-manchester-latest.osm.pbf'))

# # 步骤 0: 使用 pyosmium 转换 PBF 到 OSM (无需命令行)
# class PbfToOsmConverter(osmium.SimpleHandler):
#     def __init__(self, output_file):
#         super().__init__()
#         self.output = open(output_file, 'w', encoding='utf-8')
#         self.output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
#         self.output.write('<osm version="0.6" generator="pyosmium">\n')
#
#     def __del__(self):
#         self.output.write('</osm>\n')
#         self.output.close()
#
#     def node(self, n):
#         self.output.write(f'  <node id="{n.id}" lat="{n.location.lat}" lon="{n.location.lon}" />\n')
#
#     def way(self, w):
#         self.output.write(f'  <way id="{w.id}">')
#         for nd in w.nodes:
#             self.output.write(f'<nd ref="{nd.ref}" />')
#         self.output.write('</way>\n')
#
#     def relation(self, r):
#         self.output.write(f'  <relation id="{r.id}">')
#         for m in r.members:
#             self.output.write(f'<member type="{m.type}" ref="{m.ref}" role="{m.role}" />')
#         self.output.write('</relation>\n')
#
# try:
#     converter = PbfToOsmConverter('D:/RoutePlan/project/data/greater-manchester-latest.osm')
#     converter.apply_file('D:/RoutePlan/project/data/greater-manchester-latest.osm.pbf')
#     print("PBF 成功转换为 OSM 文件。")
# except Exception as e:
#     print(f"错误：转换 PBF 到 OSM 失败，{e}")
#     exit(1)

# # 步骤 1: 从 OSM 文件加载路网
# osm_file = 'D:/RoutePlan/project/data/greater-manchester-latest.osm'  # 转换后的 OSM 文件
# try:
#     if not os.path.exists(osm_file):
#         raise FileNotFoundError(f"文件 {osm_file} 不存在，请检查转换过程。")
#     G = ox.graph_from_xml(osm_file, simplify=True)  # 加载 OSM 文件
#     ox.save_graphml(G, 'D:/RoutePlan/project/data/manchester_graph.graphml')  # 保存为 GraphML
#     print("OSM 文件成功转换为 GraphML。")
# except Exception as e:
#     print(f"错误：加载 OSM 文件失败，{e}")
#     exit(1)

# 步骤 2: 从 GraphML 加载路网
try:
    G_loaded = ox.load_graphml('D:/RoutePlan/project/data/manchester_graph.graphml')
    print("GraphML 文件加载成功。")
except Exception as e:
    print(f"错误：加载 GraphML 文件失败，{e}")
    exit(1)


# 步骤 3: 可视化地图以验证加载
try:
    fig, ax = ox.plot_graph(G_loaded, show=False, save=True, filepath='D:/RoutePlan/project/data/manchester_map.png')
    plt.show()  # 显示图像
    print("地图加载成功，已保存为 D:/RoutePlan/project/data/manchester_map.png")
except Exception as e:
    print(f"错误：绘制地图失败，{e}")
    exit(1)