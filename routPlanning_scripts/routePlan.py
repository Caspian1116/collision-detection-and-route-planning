from flask import Flask, request, render_template_string
import osmnx as ox
import networkx as nx
import folium
import random
from datetime import datetime, time
from shapely.geometry import Point  # 使用 shapely 的 Point

app = Flask(__name__)

def is_school_avoidance_time():
    """检查当前是否为学校高峰期（7-9 AM, 3-5 PM）"""
    current_time = datetime.now().time()
    morning_start = time(7, 0)
    morning_end = time(9, 0)
    afternoon_start = time(15, 0)
    afternoon_end = time(17, 0)
    return (morning_start <= current_time <= morning_end) or (afternoon_start <= current_time <= afternoon_end)

def get_nearest_poi(G, accident_point, tag):
    """查询最近的POI（警察局或医院）从离线数据"""
    point = Point(accident_point[1], accident_point[0])  # (lon, lat)
    try:
        gdf = ox.geometries.geometries_from_point(point, tags=tag, dist=20000)
        if gdf.empty:
            print(f"警告：{tag} 数据为空，可能需检查离线数据。")
            return None
        distances = gdf.distance(point)
        nearest_idx = distances.idxmin()
        nearest_poi = (gdf.loc[nearest_idx].geometry.y, gdf.loc[nearest_idx].geometry.x)
        print(f"找到最近的 {tag['amenity']}：{nearest_poi}")
        return nearest_poi
    except AttributeError as e:
        print(f"错误：geometries_from_point 不可用，错误信息：{e}")
        return None
    except Exception as e:
        print(f"意外错误：{e}")
        return None

def calculate_path(G, start_node, end_node, avoidance_factor=1.0):
    """使用A*计算路径，应用避开权重"""
    for u, v, key, d in G.edges(keys=True, data=True):
        d['time'] = d['length'] * (1 + random.uniform(0, 0.5))  # 模拟交通
        d['time'] *= avoidance_factor  # 应用学校避开
    return nx.astar_path(G, start_node, end_node, weight='time')

@app.route('/')
def index():
    """主页面：自动规划去程路径"""
    lat = float(request.args.get('lat', 53.4667))  # 默认曼彻斯特大学
    lon = float(request.args.get('lon', -2.2333))
    accident_point = (lat, lon)

    # 加载离线路网
    try:
        G = ox.load_graphml('D:/RoutePlan/project/manchester_graph.graphml')
        if not G:
            return "错误：无法加载离线路网文件，请确保 manchester_graph.graphml 存在。"
    except Exception as e:
        return f"错误：加载离线路网失败，{e}"

    # 查询最近警察局和医院
    police_point = get_nearest_poi(G, accident_point, {'amenity': 'police'})
    hospital_point = get_nearest_poi(G, accident_point, {'amenity': 'hospital'})
    if not police_point or not hospital_point:
        return "无法找到最近的警察局或医院。"

    # 查询学校用于避开和高亮
    try:
        schools = ox.geometries.geometries_from_point(
            Point(accident_point[1], accident_point[0]),
            tags={'amenity': 'school'},
            dist=20000
        )
    except AttributeError as e:
        return f"错误：geometries_from_point 不可用，{e}"

    # 最近节点
    accident_node = ox.nearest_nodes(G, lon, lat)
    police_node = ox.nearest_nodes(G, police_point[1], police_point[0])
    hospital_node = ox.nearest_nodes(G, hospital_point[1], hospital_point[0])

    # 学校避开因子
    avoidance_factor = 10 if is_school_avoidance_time() else 1.0

    # 计算去程路径（起点：警察局/医院，终点：事故点）
    police_route = calculate_path(G, police_node, accident_node, avoidance_factor)
    hospital_route = calculate_path(G, hospital_node, accident_node, avoidance_factor)

    # 创建地图
    m = folium.Map(location=accident_point, zoom_start=12)

    # 添加标记
    folium.Marker(accident_point, popup='事故点', icon=folium.Icon(color='red')).add_to(m)
    folium.Marker(police_point, popup='警察局', icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker(hospital_point, popup='医院', icon=folium.Icon(color='green')).add_to(m)

    # 添加路径（颜色编码交通：基于平均时间权重）
    avg_time_police = sum(G.edges[police_route[i], police_route[i+1], 0]['time'] for i in range(len(police_route)-1)) / len(police_route)
    color_police = 'red' if avg_time_police > 100 else 'green'  # >100m视为拥堵
    folium.PolyLine([[G.nodes[n]['y'], G.nodes[n]['x']] for n in police_route], color=color_police, weight=5, popup='警察局路线').add_to(m)

    avg_time_hospital = sum(G.edges[hospital_route[i], hospital_route[i+1], 0]['time'] for i in range(len(hospital_route)-1)) / len(hospital_route)
    color_hospital = 'red' if avg_time_hospital > 100 else 'green'
    folium.PolyLine([[G.nodes[n]['y'], G.nodes[n]['x']] for n in hospital_route], color=color_hospital, weight=5, popup='医院路线').add_to(m)

    # 高亮学校避开区域
    for _, school in schools.iterrows():
        if hasattr(school.geometry, 'x') and hasattr(school.geometry, 'y'):
            school_loc = (school.geometry.y, school.geometry.x)
            folium.Circle(school_loc, radius=500, color='orange', fill=True, fill_opacity=0.2, popup='学校缓冲区').add_to(m)

    # 添加返回按钮
    map_html = m._repr_html_()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>自动报警路径规划</title></head>
    <body>
        <h1>事故点路径规划（去程）</h1>
        <div id="map" style="width:100%; height:500px;">{{ map_html|safe }}</div>
        <button onclick="location.href='/return_path?lat={{ lat }}&lon={{ lon }}'">救援结束，规划返回路线</button>
    </body>
    </html>
    """, map_html=map_html, lat=lat, lon=lon)

@app.route('/return_path')
def return_path():
    """手动规划返回路径"""
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    accident_point = (lat, lon)

    # 加载离线路网
    try:
        G = ox.load_graphml('D:/RoutePlan/project/manchester_graph.graphml')
        if not G:
            return "错误：无法加载离线路网文件，请确保 manchester_graph.graphml 存在。"
    except Exception as e:
        return f"错误：加载离线路网失败，{e}"

    police_point = get_nearest_poi(G, accident_point, {'amenity': 'police'})
    hospital_point = get_nearest_poi(G, accident_point, {'amenity': 'hospital'})
    schools = ox.geometries.geometries_from_point(
        Point(accident_point[1], accident_point[0]),
        tags={'amenity': 'school'},
        dist=20000
    )

    accident_node = ox.nearest_nodes(G, lon, lat)
    police_node = ox.nearest_nodes(G, police_point[1], police_point[0])
    hospital_node = ox.nearest_nodes(G, hospital_point[1], hospital_point[0])

    avoidance_factor = 10 if is_school_avoidance_time() else 1.0

    police_return = calculate_path(G, accident_node, police_node, avoidance_factor)
    hospital_return = calculate_path(G, accident_node, hospital_node, avoidance_factor)

    m = folium.Map(location=accident_point, zoom_start=12)
    folium.Marker(accident_point, popup='事故点', icon=folium.Icon(color='red')).add_to(m)
    folium.Marker(police_point, popup='警察局', icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker(hospital_point, popup='医院', icon=folium.Icon(color='green')).add_to(m)

    avg_time_police = sum(G.edges[police_return[i], police_return[i+1], 0]['time'] for i in range(len(police_return)-1)) / len(police_return)
    color_police = 'red' if avg_time_police > 100 else 'green'
    folium.PolyLine([[G.nodes[n]['y'], G.nodes[n]['x']] for n in police_return], color=color_police, weight=5, popup='返回警察局路线').add_to(m)

    avg_time_hospital = sum(G.edges[hospital_return[i], hospital_return[i+1], 0]['time'] for i in range(len(hospital_return)-1)) / len(hospital_return)
    color_hospital = 'red' if avg_time_hospital > 100 else 'green'
    folium.PolyLine([[G.nodes[n]['y'], G.nodes[n]['x']] for n in hospital_return], color=color_hospital, weight=5, popup='返回医院路线').add_to(m)

    for _, school in schools.iterrows():
        if hasattr(school.geometry, 'x') and hasattr(school.geometry, 'y'):
            school_loc = (school.geometry.y, school.geometry.x)
            folium.Circle(school_loc, radius=500, color='orange', fill=True, fill_opacity=0.2, popup='学校缓冲区').add_to(m)

    map_html = m._repr_html_()
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>返回路径规划</title></head>
    <body>
        <h1>返回路径规划</h1>
        <div id="map" style="width:100%; height:500px;">{{ map_html|safe }}</div>
    </body>
    </html>
    """, map_html=map_html)

if __name__ == '__main__':
    app.run(debug=True)