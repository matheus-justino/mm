import cv2

cam = cv2.VideoCapture(0, cv2.CAP_ANY)

while True:
    ret, frame = cam.read()
    if ret == True:
        cv2.imshow('frame', frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    else:
        break

cv2.imshow('frame captured', frame)
cv2.waitKey()