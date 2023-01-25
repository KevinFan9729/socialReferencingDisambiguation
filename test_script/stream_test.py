import cv2
# vcap = cv2.VideoCapture("https://192.168.0.54:8080/video")
vcap = cv2.VideoCapture("http://192.168.1.7:8080/video")
# vcap = cv2.VideoCapture(0)

while(1):
    ret, frame = vcap.read()
    # print(frame)
    cv2.imshow('VIDEO', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
