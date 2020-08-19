from bs4 import BeautifulSoup
import urllib.request
import json
import numpy as np
import pandas as pd
import folium
import folium.plugins
import math
import gpxpy.geo
from decimal import *
#강의실
a = pd.read_csv('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/crime.csv', thousands=',',encoding='euc-kr')
b = pd.read_csv('C:/Users/USER/Desktop/SK infosec/SK-Infosec/tens/cctv1.csv', thousands=',',encoding='euc-kr')
#노트북
# a = pd.read_csv('C:/Users/His hacker/Desktop/gitlab/SK-Infosec/tens/crime.csv', thousands=',',encoding='euc-kr')
# b = pd.read_csv('C:/Users/His hacker/Desktop/gitlab/SK-Infosec/tens/cctv1.csv', thousands=',',encoding='euc-kr')
a.head()
b.head()
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
# 사용자 입력값을 api로 위/경도 변환 함수 + 폴리곤화(색상 블루, 크기 cctv보다 작게)
def getData(parameter):
    request = urllib.request.Request(parameter)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    response_body = response.read().decode('utf-8')
    result = response_bdy
    temp_user = search_map(result)
    temp_user = json.load(temp_user)
    temp_user = temp_user['addresses'][0]

    user_info = (float(temp_user['x']),float(temp_user['y']))
    #사용자 위/경도 (수정예정)
    return user_info

#수정예정 R2_p -> 함수에서 나온 사용자 위도/경도

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

#web-site user input 


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
rotating_degree = 10 #회전각도 5개
ar = 0 #비율, 교차하지 않은 경우의 값
r = 50 #장소의 원의 반지름
R = 10 #유저의 원의 반지름
R2_p = (37.459590, 126.904861) ##수정예정 R2_p -> 함수에서 나온 사용자 위도/경도
lst = []
#cctv input
for i in range(373):
    # c = 각 cctv의 좌표
    c = cc[i],tv[i] #36.94273371 / 126.780918
    #사용자 입력 주소 (위,경도 변환된값)
    d = distance(c, R2_p)
    # tmp_dict = {"lat": cc[i], "lot": tv[i], "distance": d}
    tmp_array = [cc[i], tv[i], d]
    #d = math.floor(d)
    # lst.append(d)
    lst.append(tmp_array)
    offsets = calc_offsets(radi, c[1])
    coordinates = [coordinate_after_rotation(c, e, offsets) for e in range(0, 360+1, rotating_degree)]
    # b = 각 cctv의 폴리곤화
    b = []
    for i in coordinates:
        b.append(i)

    folium.Marker(
        c,
        icon = folium.Icon(color='red'), #icon='C:/Users/His hacker/Desktop/gitlab/SK-Infosec/tens/images.png'
        popup = c
    ).add_to(fg_2)
    # 각 cctv의 폴리곤 원형화
    folium.Polygon(
    locations = b,
    fill = True,
    color = 'red',
    tooltip = 'Polygon'
    ).add_to(fg_2)

search = min(lst, key=lambda item: item[2])
print(search)

# 교차 면적 함수 구하기
# cctv = 37.4596667, 126.90474640000002
# R2_p = 37.459485, 126.905046
# distance = 0.03299627717084893 
R1_p = (search[0], search[1])
pulse = (search[2])
   #0.013  10   50
if pulse + R <= r : # 장소의 원안에 유저의 원이 존재할 경우
    ##error ar 값이 r과 R로만 이루어짐
    ar = (math.pi * pow(R, 2)) / (math.pi * pow(r, 2))
    print("첫번째")
elif pulse + r <= R : #유저의 원안에 장소의 원이 존재할 경우
    ar = 1.0
    print("두번째")
elif pulse < R + r : #두 원이 겹쳐지지 않은 경우 + 부분적으로 겹쳐진경우
    ar = intersection_area(R, r, d) / (math.pi * pow(r, 2))
    print("세번째")
else :
    print("에러")
print(ar)

folium.LayerControl(collapsed=False).add_to(m)

# coordinates = [coordinate_after_rotation(c, e, offsets) for e in range(0, 360+1, rotating_degree)]
# # b = 각 cctv의 폴리곤화
# b = []
# for i in coordinates:
#     b.append(i)
offsets = calc_offsets(radi_user, R2_p[1])
coordinates = [coordinate_after_rotation(R2_p, e, offsets) for e in range(0, 360+1, rotating_degree)]
asz = []
for i in coordinates:
    asz.append(i)
#수정예정 R2_p -> 함수에서 나온 사용자 위도/경도
folium.Marker(
    R2_p,
    icon = folium.Icon(color='blue'), #icon='C:/Users/His hacker/Desktop/gitlab/SK-Infosec/tens/images.png'
    popup = R2_p
).add_to(fg_2)

#수정예정 R2_p -> 함수에서 나온 사용자 위도/경도
#각 cctv의 폴리곤 원형화
folium.Polygon(
    locations = asz,
    fill = True,
    color = 'blue',
    tooltip = 'Polygon'
).add_to(fg_2)

m.save('complete.html')

