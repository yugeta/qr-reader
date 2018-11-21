
# 必要なモジュールのインストール

from flask import Flask, Response
from pyzbar import pyzbar
from picamera.array import PiRGBArray
from picamera import PiCamera
from datetime import datetime

import numpy as np
import cv2
import time


# picameraアクセス準備

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(0.5)

app = Flask(__name__)


# エンドポイントの作成

@app.route('/stream')
def stream():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen():
    while True:
        frame = get_frame()
        yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
# icameraからフレームを読み込み、QR認識とその位置を描画する関数の呼び出し

def get_frame():
    camera.capture(rawCapture, format="bgr", use_video_port=True)
    frame = rawCapture.array
    process_frame(frame)
    ret, jpeg = cv2.imencode('.jpg', frame)
    rawCapture.truncate(0)

    return jpeg.tobytes()


# 取得したフレームを使ってQR認識と認識したポジションの描画

def process_frame(frame):
    decoded_objs = decode(frame)
    draw_positions(frame, decoded_objs)
    
    
# Pyzbarライブラリを使って実際にQRを認識するコード

def decode(frame):
    decoded_objs = pyzbar.decode(frame, scan_locations=True)
    for obj in decoded_objs:
        print(datetime.now().strftime('%H:%M:%S.%f'))
        print('Type: ', obj.type)
        print('Data: ', obj.data)
        
    return decoded_objs
  
  
# 認識したQRコードの位置をフレームに描画する関数

def draw_positions(frame, decoded_objs):
    for decoded_obj in decoded_objs:
        left, top, width, height = decoded_obj.rect
        frame = cv2.rectangle(frame,
                  (left, top),
                  (left + width, height + top),
                  (0, 255, 0), 2)
        
# Flaskのサーバを立ち上げる処理

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, threaded=True)
    

