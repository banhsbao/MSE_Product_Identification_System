import cv2
# import RPi.GPIO as GPIO
from time import sleep
from ultralytics import YOLO

# Khởi tạo camera
camera = cv2.VideoCapture(0)  # Nếu camera được kết nối qua giao tiếp khác, cần chỉnh sửa lại chỉ số này

# Cấu hình YOLOv8
model = YOLO('yolov8n.pt')  # Tải model YOLOv8 pre-trained từ Ultralytics

# Cấu hình GPIO cho servo
servo_pin = 17  # Chọn chân GPIO bạn sử dụng cho servo
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servo_pin, GPIO.OUT)

# servo = GPIO.PWM(servo_pin, 50)  # Tần số 50Hz
# servo.start(0)

# def move_servo(angle):
#     duty_cycle = (angle / 18.0) + 2
#     GPIO.output(servo_pin, True)
#     servo.ChangeDutyCycle(duty_cycle)
#     sleep(1)
#     GPIO.output(servo_pin, False)
#     servo.ChangeDutyCycle(0)

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Không thể lấy ảnh từ camera.")
            break
        cv2.imshow('Camera', frame)

except KeyboardInterrupt:
    pass

finally:
    # Dọn dẹp tài nguyên
    # servo.stop()
    # GPIO.cleanup()
    camera.release()
    cv2.destroyAllWindows()
