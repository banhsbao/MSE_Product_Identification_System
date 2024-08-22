import cv2
from flask import Flask, request, jsonify, Response, stream_with_context
import RPi.GPIO as GPIO
import time

IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)

def step_motor(steps, delay):
    step_sequence = [
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1],
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
    ]
    for _ in range(steps):
        for step in step_sequence:
            set_step(step[0], step[1], step[2], step[3])
            time.sleep(delay)

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(stream_with_context(generate_frames()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/step', methods=['POST'])
def step():
    data = request.json
    steps = int(data.get('steps', 512))
    delay = float(data.get('delay', 0.001))
    step_motor(steps, delay)
    return jsonify({'status': 'Motor moved', 'steps': steps, 'delay': delay})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
