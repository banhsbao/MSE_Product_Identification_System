from flask import Flask, jsonify, Response, stream_with_context
from flask_cors import CORS, cross_origin
import uuid
import cv2
import base64
import threading
import traceback
import time

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

STATUS_IN_PROGRESS = "IN_PROGRESS"
STATUS_STOPPED = 'STOPPED'
STATUS_DONE = "DONE"
STATUS_ERROR = "ERROR"
STATUS_PASS = "PASS"

requests_store = {}
current_request = None

def capture_frame():
    cap = cv2.VideoCapture(0)
    try:
        ret, frame = cap.read()
        if not ret:
            raise ValueError("Failed to capture image")
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            raise ValueError("Failed to encode image")
        return buffer.tobytes()
    finally:
        cap.release()

def generate_request_object():
    return {
        "request_id": str(uuid.uuid4()),
        "status": STATUS_IN_PROGRESS,
        "step": 0,
        "body": {}
    }


def process_texts_handler(contents):
    import cv2
    import numpy as np
    import pytesseract
    import re
    # np_img = np.frombuffer(contents, np.uint8)
    # image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    image_path = "test.png"
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    _, thresholded_image = cv2.threshold(blurred_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pytesseract.pytesseract.tesseract_cmd = 'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Tesseract-OCR'
    text = pytesseract.image_to_string(thresholded_image, lang='eng')
    pnr_regex = re.compile(r'PNR (\w+)')
    ser_regex = re.compile(r'SER (\w+)')
    dmf_regex = re.compile(r'(\d{2}/\d{4})')
    pnr_value = pnr_regex.search(text).group(1) if pnr_regex.search(text) else None
    ser_value = ser_regex.search(text).group(1) if ser_regex.search(text) else None
    dmf_value = dmf_regex.search(text).group(1) if dmf_regex.search(text) else None
    ocr_result = {
        "pnr":pnr_value,
        "ser":ser_value,
        "dmf":dmf_value
    }
    return ocr_result

def step1_verification_stamp(req_obj):
    image = encode_image(capture_frame())
    # image_bytes = image.tobytes()
    ocr_result =  process_texts_handler({})
    if ocr_result is not None:
        req_obj['step'] = 1
        req_obj['body']['step1'] = {
            "status": STATUS_PASS,
            "note": "Product is verifying!",
            "image": image,
            "data": ocr_result,
        }
    else:
        req_obj['status'] = STATUS_ERROR
        req_obj['body']['step1'] = {
            "status": STATUS_ERROR,
            "note": "Product checking failed!",
            "image": image
        }
    time.sleep(5)

import ultralytics
MODEL_PATH = './dsp-model-latest.pt'
model = ultralytics.YOLO(MODEL_PATH)
def caculate_stuff(image):
    return {
        "screws": 1,
        "label_present": 2,
        "yellow_caps": 3,
    }
    yellow_caps = 0
    screws = 0
    label_present = False
    resized_image = cv2.resize(image, (640, 640))
    results = model.predict(source=resized_image, conf=0.25)
    for result in results:
        for box in result.boxes:
            label = int(box.cls[0])
            if label == 2:
                yellow_caps += 1
            elif label == 0: 
                screws += 1
            if label == 1:
                label_present = True
    return {
    yellow_caps,
    label_present,
    screws
}

def step2_verification_first_side(req_obj):
    #Required stuff
    required_screws = 0
    required_label_present = False
    required_yellow_caps= 0
    #Running
    image = encode_image(capture_frame())
    result = caculate_stuff(image)
    screws = result['screws']
    label_present = result['label_present']
    yellow_caps = result['yellow_caps']
    if required_screws != screws or required_label_present != label_present or yellow_caps!= required_yellow_caps:
        req_obj['step'] = 2
        req_obj['body']['step2'] = {
            "status": STATUS_PASS,
            "image": encode_image(capture_frame()),
            "screws": screws,
            "label_present": label_present,
            "yellow_caps": yellow_caps,
        }
    else:
        req_obj['status'] = STATUS_ERROR
        req_obj['body']['step2'] = {
            "status": STATUS_ERROR,
            "image": encode_image(capture_frame()),
            "screws": screws,
            "label_present": label_present,
            "yellow_caps": yellow_caps,
        }

def step3_verification_second_side(req_obj):
    #Required stuff
    required_screws = 0
    required_label_present = False
    required_yellow_caps= 0
    #Running
    image = encode_image(capture_frame())
    result = caculate_stuff(image)
    screws = result['screws']
    label_present = result['label_present']
    yellow_caps = result['yellow_caps']
    if required_screws != screws or required_label_present != label_present or yellow_caps!= required_yellow_caps:
        req_obj['step'] = 3
        req_obj['body']['step3'] = {
            "status": STATUS_PASS,
            "image": encode_image(capture_frame()),
            "screws": screws,
            "label_present": label_present,
            "yellow_caps": yellow_caps,
        }
    else:
        req_obj['status'] = STATUS_ERROR
    time.sleep(5)

def step4_verification_third_side(req_obj):
    #Required stuff
    required_screws = 0
    required_label_present = False
    required_yellow_caps= 0
    #Running
    image = encode_image(capture_frame())
    result = caculate_stuff(image)
    screws = result['screws']
    label_present = result['label_present']
    yellow_caps = result['yellow_caps']
    if required_screws != screws or required_label_present != label_present or yellow_caps != required_yellow_caps:
        req_obj['step'] = 4
        req_obj['body']['step4'] = {
            "status": STATUS_PASS,
            "image": encode_image(capture_frame()),
            "screws": screws,
            "label_present": label_present,
            "yellow_caps": yellow_caps,
        }
    else:
        req_obj['status'] = STATUS_ERROR
        req_obj['body']['step4'] = {
            "status": STATUS_ERROR,
            "image": capture_frame(),
            "screws": screws,
            "label_present": label_present,
            "yellow_caps": yellow_caps,
        }

def step5_verification_four_side(req_obj):
    screws = 0
    label = 0
    caps = 0
    req_obj['status'] = STATUS_DONE
    req_obj['step'] = 5
    req_obj['body']['step5'] = {
        "status": STATUS_PASS,
        "image": encode_image(capture_frame()),
        "screws": screws,
        "label": label,
        "caps": caps,
    }

step_functions = {
    0: step1_verification_stamp,
    1: step2_verification_first_side,
    2: step3_verification_second_side,
    3: step4_verification_third_side,
    4: step5_verification_four_side
}

def process_detection():
    global current_request
    
    while True:
        if current_request is None or current_request['status'] != STATUS_IN_PROGRESS:
            current_request = generate_request_object()
            request_id = current_request['request_id']
            requests_store[request_id] = current_request
        
        for step in range(5):
            if current_request['status'] != STATUS_IN_PROGRESS:
                break
            step_functions[step](current_request)
        
        if current_request['status'] != STATUS_IN_PROGRESS:
            print("Restart new cycle!")
            time.sleep(30)
            continue

        else:
            break

def encode_image(image_bytes):
    if isinstance(image_bytes, bytes):
        return base64.b64encode(image_bytes).decode('utf-8')
    return None

@app.route('/status', methods=['GET'])
@cross_origin()
def check_status():
    try:
        req_obj = current_request
        if not req_obj:
            return jsonify({"error": "No current request found"}), 404
                
        return jsonify(req_obj)
    except Exception as e:
        app.logger.error("Error in /status endpoint: %s", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/start_detection', methods=['GET'])
@cross_origin()
def start_detection():
    if current_request is None or current_request['status'] != STATUS_IN_PROGRESS:
        threading.Thread(target=process_detection).start()
        return jsonify({"message": "Detection started"}), 202
    else:
        return jsonify({"message": "Detection already in progress"}), 409

@app.route('/stop_detection', methods=['GET'])
@cross_origin()
def stop_detection():
    global current_request
    if current_request and current_request['status'] == STATUS_IN_PROGRESS:
        current_request['status'] = STATUS_STOPPED
        return jsonify({"message": "Detection stopped"}), 200
    else:
        return jsonify({"message": "No detection in progress"}), 409

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
@cross_origin()
def video_feed():
    return Response(stream_with_context(generate_frames()), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, threaded=True)
