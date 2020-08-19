from bs4 import BeautifulSoup
import urllib.request
import json
import numpy as np
import pandas as pd
import folium
import folium.plugins
import math
import gpxpy.geo
import geojson

#강의실
a = pd.read_csv('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/crime.csv', thousands=',',encoding='euc-kr')
b = pd.read_csv('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/cctv1.csv', thousands=',',encoding='euc-kr')
police = pd.read_csv('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/police.csv', thousands=',',encoding='euc-kr')
#노트북
# a = pd.read_csv('C:/Users/His hacker/Desktop/gitlab/SK-Infosec/tens/crime.csv', thousands=',',encoding='euc-kr')
# b = pd.read_csv('C:/Users/His hacker/Desktop/gitlab/SK-Infosec/tens/cctv1.csv', thousands=',',encoding='euc-kr')
a.head()
b.head()
police.head()
# 원점의 폴리곤화
def calc_offsets(radi, lat):
    return (
        abs(360*math.asin(math.sin(radi/6271/2/2000)/math.cos(lat*math.pi/180))/math.pi),
        180*radi/6371/1000/math.pi
    )

def radian(degree):
    return math.pi/180*degree

def coordinate_after_rotation(c, degree, offsets):
    return (
        c[0]+math.cos(radian(degree))*offsets[0],
        c[1]+math.sin(radian(degree))*offsets[1]
    )

# 원점과 거리를 이용한 교차면적
def theta(R, r, d):
    return 2 * math.acos((pow(d, 2) + pow(R, 2) - pow(r, 2)) / (2 * d * R))

def intersection_area(R, r, d):
    t1 = theta(R, r, d)
    t2 = theta(r, R, d)
    return (pow(R, 2) * (t1 - math.sin(t1)) + pow(r, 2) * (t2 - math.sin(t2))) / 2

def distance(R1, R2):
    #R1 = 136.9122221, 35.1299227
    #R2 = 136.9116187, 35.1295955
    lat1 = R1[0] 
    lon1 = R1[1]
    lat2 = R2[0]
    lon2 = R2[1]
    #return 110.25 * math.sqrt(pow(lat1 - lat2, 2) + pow((lon1 - lon2) * math.cos(math.radians(lat2)), 2))
    return gpxpy.geo.haversine_distance(lat1, lon1, lat2, lon2)
#naver maps api return module
def search_map(search_text):
    client_id = '2o352tcqq0'
    client_secret = 'ZlXWXWm2BsZRkYOcv1ZiXm6vUEqCiQ042yABG7JR'
    encText = urllib.parse.quote(search_text)
    url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query='+encText
    request = urllib.request.Request(url)
    request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
    request.add_header('X-NCP-APIGW-API-KEY', client_secret)
    response = urllib.request.urlopen(request)
    #server info get
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        #print(response_body.decode('utf-8'))
        return response_body.decode('utf-8')
    else:
        print("Error Code:" + rescode)

# html button click
def crrosover(parameter):
    
    temp_user = search_map(parameter)
    temp_user = json.load(temp_user)
    temp_user = temp_user['addresses'][0]

    R2_p = (float(temp_user['x']),float(temp_user['y']))
    offsets = calc_offsets(radi_user, R2_p[1])
    coordinates = [coordinate_after_rotation(R2_p, e, offsets) for e in range(0, 360+1, rotating_degree)]
    asz = []
    for i in coordinates:
        asz.append(i)
    icon = folium.features.CustomIcon('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/user.png', icon_size=(15, 15))
    folium.Marker(
        R2_p,
        icon = icon,
        popup = R2_p
    ).add_to(fg_2)
    #각 cctv의 폴리곤 원형화
    folium.Polygon(
        locations = asz,
        fill = True,
        color = 'blue',
        tooltip = 'Polygon'
    ).add_to(fg_2)
    
    c = cc[i],tv[i]
    d = distance(c, R2_p)
    tmp_array = [cc[i], tv[i], d]
    lst.append(tmp_array)
    crros_over = min(lst, key=lambda item: item[2])
    R1_p = (crros_over[0], crros_over[1])
    pulse = (crros_over[2])

    # 첫번째 = cctv안에 유저 전체가 들어감 print(36%) <= 고정값
    # 세번째 = cctv안에 유저가 일부 들어감 print(1~35%) <= 거리기반값
    if pulse + R <= r : # 장소의 원안에 유저의 원이 존재할 경우
        ar = (math.pi * pow(R, 2)) / (math.pi * pow(r, 2)) 
        print("첫번째") 
    elif pulse + r <= R : #유저의 원안에 장소의 원이 존재할 경우
        ar = 1.0
        print("두번째")
    elif pulse < R + r : #두 원이 겹쳐지지 않은 경우 + 부분적으로 겹쳐진경우 MAX =36 ,Min = 1 
        ar = intersection_area(R, r, d) / (math.pi * pow(r, 2))
        print("세번째")
    else :
        print("에러")
    print(ar)
    
    d = round(d)
    #현재 위치 기준으로 반경내 이탈한지 체크
    if d < 5 :
        return # a = "cctv 반경 내에 위치합니다."
    else :
        return # a = "cctv 반경에서 벗어났습니다."
    return # a
    
#crrorover() 사용자 GPS 입력값
#######################################
#if parameter가 있을경우 아래 실행      #
#crrosover(parameter)                 #
#######################################


#csv에서 지역을 받아 리스트로 넣어줌
region = []
for value in a:
    region.append(value)
#
del region[0:1]
#print(region)

x = [] #네이버 api에서 받은 위도
y = [] #네이버 api에서 받은 경도
z = [] #네이버 api에서 받은 지역이름
cc = [] #cctv 위도
tv = [] #cctv 경도
lst = []
#web-site user input 
#사용자가 입력할때
#홈페이지에서 버튼 클릭시 수행

#    request = urllib.request.Request('http://localhost:8000') # web-site input gps
#    response = urllib.request.urlopen(request)
#    rescode = response.getcode()

#    response_body = response.read().decode('utf-8')
#    result = response_body
#    if result == not null :
#       getData(result)

#naver map api info
for value in region:
    temp_map = search_map(value)
    temp_map = json.loads(temp_map)
    temp_map = temp_map['addresses'][0]
    x.append(float(temp_map['x']))
    y.append(float(temp_map['y']))
    z.append(temp_map['roadAddress'])

print(x)
m = folium.Map(
    location=(37.4729081, 127.039306),
    tiles='cartodbpositron',
    zoom_start=8
)

#정보 부분 출력
fg_1 = folium.FeatureGroup(name='markers_1').add_to(m)
fg_2 = folium.FeatureGroup(name='markers_2').add_to(m) 
fg_3 = folium.FeatureGroup(name='markers_3').add_to(m) 
fg_4 = folium.FeatureGroup(name='markers_4').add_to(m) 

#지역별 범죄현황
#               16개
for i in range(len(x)):
    #map_osm = folium.Map(location=[y[i],x[i]])
    # popuptest = (a.iloc[[2], [0,i+1]]),(a.iloc[[3], [0,i+1]]),(a.iloc[[4], [0,i+1]]),(a.iloc[[5], [0,i+1]]),(a.iloc[[6], [0,i+1]]),(a.iloc[[7], [0,i+1]])
    classes = ('table table-striped table-hover'
               'taalbe-condensed table-responsive')

    popup = a.iloc[[0,1,2,3,4,5,6,7], [0,i+1]].to_html(classes=classes)

    folium.Marker(
        [y[i],x[i]],
        popup=popup,
        icon=folium.Icon(color='blue')
    ).add_to(fg_1)

#cctv append
for i in range(373):
    cc.append(b.iloc[i, 2]) #위도
    tv.append(b.iloc[i, 3]) #경도

radi = 30 #반경
radi_user = 15 #유저반경
rotating_degree = 45 #회전각도
ar = 0 #비율, 교차하지 않은 경우의 값
r = 50 #장소의 원의 반지름
R = 30 #유저의 원의 반지름

#cctv input
for i in range(373):
    # c = 각 cctv의 좌표
    c = cc[i],tv[i] #36.94273371 / 126.780918
    #사용자 입력 주소 (위,경도 변환된값)
    # tmp_dict = {"lat": cc[i], "lot": tv[i], "distance": d}
    offsets = calc_offsets(radi, c[1])
    coordinates = [coordinate_after_rotation(c, e, offsets) for e in range(0, 360+1, rotating_degree)]
    # b = 각 cctv의 폴리곤화
    b = []
    for i in coordinates:
        b.append(i)
    _geojson = {
        'feautres': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                }
            }
        ]
    }
    icon1 = folium.features.CustomIcon('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/cctv.png', icon_size=(17, 17))
    folium.Marker(
        c,
        icon = icon1,
        popup = c
    ).add_to(fg_2)
    #각 cctv의 폴리곤 원형화
    # folium.Polygon(
    #     locations = b,
    #     fill = True,
    #     color = 'red',
    #     tooltip = 'Polygon'
    # ).add_to(fg_2)
    folium.Circle(
        location = c,
        radius = 25,
        fill = True,
        color = 'red',
        tooltip = 'Polygon'
    ).add_to(fg_2)
police_we = []
police_gang = []
for i in range(2264):
    police_we.append(police.iloc[i, 4]) #위도
    police_gang.append(police.iloc[i, 3]) #경도



for i in range(2264):
    police_loc = (police_we[i],police_gang[i])
    #print(police_loc)
    icon2 = folium.features.CustomIcon('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/police.png', icon_size=(20, 20))
    folium.Marker(
        police_loc,
        icon=icon2,
        popup = police_loc
    ).add_to(fg_3)

folium.LayerControl(collapsed=False).add_to(m)
m.save('complete.html')
#경찰서 좌표 찍기 + dintance해서 
#
#마커 이미지
