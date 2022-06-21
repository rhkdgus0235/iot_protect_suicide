from importlib.resources import is_resource
import io
import queue
import sounddevice as sd
import soundfile as sf
import sys
from datetime import datetime
import boto3
from io import BytesIO
import numpy as np
import time
import threading
import pymysql
from voice_recognize2 import recognize
from voice_synthesize2 import URL,HEADERS,make_text
import requests
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
ACCESS_KEY_ID = 'AKIA5VZTIAOJSVDQABX5' #s3 관련 권한을 가진 IAM계정 정보
ACCESS_SECRET_KEY = '+b3Lq5ZqjSEa5121nckFwkzOzV1BgUeqpPrr9ewk'
BUCKET_NAME = 'msa-test03'



samplerate = 44100
channels = 1
sd.default.samplerate = samplerate 
sd.default.channels = channels

volume_norm=0
a=0
b=0
turnstatus=True

client_boto = boto3.client("sns",aws_access_key_id="AKIA5VZTIAOJ6CIZCN4O", aws_secret_access_key="Xb1RcFMxM/iLAHtkxWxN3FHqNfgKpFvgLM5ZshMV",    region_name="us-west-1")






# STEP 2: MySQL Connection 연결
con = pymysql.connect(host='54.215.185.52', user='cloud3', password='cloud3',
                       db='cloud3', charset='utf8') # 한글처리 (charset = 'utf8')
 
# STEP 3: Connection 으로부터 Cursor 생성
cur = con.cursor()
 
# STEP 4: SQL문 실행 및 Fetch
# sql = "SELECT * FROM input_sentence"
# cur.execute(sql)
 
# # 데이타 Fetch
# rows = cur.fetchall()
# print(rows)     # 전체 rows

# STEP 5: DB 연결 종료
# con.close()



# def callback(indata, frames, time, status): 
#     global volume_norm
#     volume_norm = np.linalg.norm(indata)*10
#     if status:
#         print(status, file=sys.stderr)
#     q.put(indata.copy())  # 녹음    데이터    큐에    추가





import paho.mqtt.client as mqtt
import time,json

cheerup_state=False
# 브로커    접속    시도    결과    처리    콜백    함수
def on_connect(client, userdata, flags, rc): 
    print("Connected with result code "+ str(rc)) 
    if rc == 0:
        client.subscribe("iot/#")  # 연결    성공시    토픽    구독    신청 
    else:
        print('연결    실패    :  ', rc)
# 관련    토픽    메시지    수싞    콜백    함수
def on_message(client, userdata, msg): 
    global cheerup_state
    # value = msg.payload.decode()
    value = msg.payload
    # print(f" {msg.topic} {value}")
    # print(type(value))
    encoded_img = np.frombuffer(value, dtype = np.uint8)
    # print(type(encoded_img))
    img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
    # cv2.imshow('hi',img)
    # cv2.waitKey(0)
    # print(type(img))
    # print('hi')
    if msg.topic=="iot/detect":
        print(msg.payload.decode())
        client_boto.publish(PhoneNumber="+8201033831857",    Message=msg.payload.decode())
    elif msg.topic=="iot/detect_sms":
        print(msg.payload.decode())
        client_boto.publish(PhoneNumber="+8201033831857",    Message=msg.payload.decode())
    elif msg.topic=="iot/django":
        print("안녕")
        print(msg.payload.decode())
        data=make_text(msg.payload.decode())
        res_sound=requests.post(URL,headers=HEADERS,data=data.encode('utf-8'))

        sound=BytesIO(res_sound.content)
        song=AudioSegment.from_mp3(sound)
        cheerup_state=True
        play(song)
        sleep(2)
        cheerup_state=False
        
        print("또 안녕")
    elif msg.topic=="iot/bigdata":
        print(msg.payload.decode())
        client_boto.publish(PhoneNumber="+8201033831857",    Message=msg.payload.decode())
        client_boto.publish(PhoneNumber="+8201042214602",    Message=msg.payload.decode())
        cheerup_state=True
        playsound('./aws/sounds/cheerup.mp3')
        sleep(2)
        cheerup_state=False
        

client = mqtt.Client()
# 2. 관련    이벤트에    대한    콜백    함수    등록 
client.on_connect = on_connect
client.on_message = on_message 
try :
# 3. 브로커    연결
    # client.connect("54.161.238.9")
    client.connect("18.144.44.57")
# 4. 메시지    루프    - 이벤트    발생시    해당    콜백    함수    호출됨 
    client.loop_start()
except Exception as err: 
    print('에러    : %s'%err)




from gpiozero import MotionSensor,DistanceSensor
from time import sleep
import cv2
from signal import pause
pir=MotionSensor(26)
distancesensor=DistanceSensor(19,13,max_distance=4,threshold_distance=0.1)

# cap = cv2.VideoCapture(0) # 노트북 웹캠을 카메라로 사용
# cap.set(3,640) # 너비
# cap.set(4,480) # 높이



def distnace_with_camera():
    
    print("distance")
    
    print(distancesensor.distance)
    
    cap = cv2.VideoCapture(0) # 노트북 웹캠을 카메라로 사용
    cap.set(3,640) # 너비
    cap.set(4,480) # 높이
    sleep(1)
    for i in range(5):
        if distancesensor.distance<=2:
            if i==0:
                start=datetime.now()
                fname=start.strftime('./pics/%Y%m%d_%H%M%S.jpg')
                fname2=start.strftime('%Y%m%d_%H%M%S')
                ret, frame = cap.read() # 사진 촬영
                print(frame[:20])
                print(type(frame))
                
                # frame_str=cv2.imdecode('.jpg',frame).tobytes()
                
                frame = cv2.flip(frame, 1) # 좌우 대칭
                
                # gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                print("image: "+fname2)
                
                img_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

                # cv2.imwrite(fname, gray) # 사진 저장
                # handle_upload_img(fname2)

                client.publish('iot/image',img_bytes,qos=1)
            print("count")
            sleep(1)
        

def stop():
    
    print("stop")
    



def detect_thread():
    pir.when_motion=distnace_with_camera
    pir.when_no_motion=stop
    pause()



# t=threading.Thread(target=detect_thread,args=())
# t.start()






while True:
    sleep(1)
    
    
    if cheerup_state==False:
        try:
            print("감지중")

            is_success,result=recognize()
            print("인식중")

            if is_success:
                start2=datetime.now()
                fname3=start2.strftime('%Y-%m-%d %H:%M:%S')
                
                print(result['value'])
                # client.publish("iot/recognize",result['value'],qos=1)
                
                sql = f'INSERT INTO `input_sentence`(user_num,sentence,date,done) VALUES (%s,%s,%s,%s);'

                cur.execute(sql,(1,result['value'],fname3,1))
                con.commit()
                print("db 업로드")
                a=0
        except ValueError:
            print("다시 확인")
            continue