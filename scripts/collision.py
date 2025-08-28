from ultralytics import YOLO
import cv2
import numpy as np

def calculate_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2
    x_left = max(x1, x3)
    y_top = max(y1, y3)
    x_right = min(x2, x4)
    y_bottom = min(y2, y4)
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    intersection = (x_right - x_left) * (y_bottom - y_top)
    area1 = (x2 - x1) * (y2 - y1)
    area2 = (x4 - x3) * (y4 - y3)
    return intersection / (area1 + area2 - intersection)

model = YOLO("runs/detect/train6/weights/best.pt")
cap = cv2.VideoCapture("../data/test2/test_video.mp4")
out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (int(cap.get(3)), int(cap.get(4))))
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    results = model.predict(frame, stream=True, conf=0.5, imgsz=640)
    collision_detected = False
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy()
        confidences = r.boxes.conf.cpu().numpy()
        for i in range(len(boxes)):
            if classes[i] == 1 and confidences[i] > 0.8:  # collision
                collision_detected = True
                cv2.rectangle(frame, (int(boxes[i][0]), int(boxes[i][1])),
                              (int(boxes[i][2]), int(boxes[i][3])), (0, 0, 255), 2)
                cv2.putText(frame, f"Collision {confidences[i]:.2f}", (int(boxes[i][0]), int(boxes[i][1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            elif classes[i] == 0:  # car
                cv2.rectangle(frame, (int(boxes[i][0]), int(boxes[i][1])),
                              (int(boxes[i][2]), int(boxes[i][3])), (0, 255, 0), 2)
                cv2.putText(frame, f"Car {confidences[i]:.2f}", (int(boxes[i][0]), int(boxes[i][1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            for j in range(i + 1, len(boxes)):
                if classes[i] == 0 and classes[j] == 0:  # car 之间的 IoU
                    iou = calculate_iou(boxes[i], boxes[j])
                    if iou > 0.5:
                        collision_detected = True
                        print(f"Collision detected: IoU={iou:.2f}")
                        cv2.rectangle(frame, (int(boxes[i][0]), int(boxes[i][1])),
                                      (int(boxes[i][2]), int(boxes[i][3])), (0, 0, 255), 2)
                        cv2.rectangle(frame, (int(boxes[j][0]), int(boxes[j][1])),
                                      (int(boxes[j][2]), int(boxes[j][3])), (0, 0, 255), 2)
        if collision_detected:
            cv2.putText(frame, "COLLISION DETECTED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        out.write(frame)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
cap.release()
out.release()
cv2.destroyAllWindows()