import cv2
import mediapipe as mp
import websocket
import json

# Connect to WebSocket
ws = websocket.WebSocket()
ws.connect("ws://localhost:8080/draw")

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Setup video writer to record the session
out = cv2.VideoWriter('hand_tracking.avi',
                      cv2.VideoWriter_fourcc(*'XVID'),
                      20.0,
                      (frame_width, frame_height))

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    # Flip for mirror effect
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Index finger tip
            x = int(hand_landmarks.landmark[8].x * img.shape[1])
            y = int(hand_landmarks.landmark[8].y * img.shape[0])
            ws.send(json.dumps({"x": x, "y": y}))

    # Write frame to video file
    out.write(img)

    # Show live preview
    cv2.imshow("👋 Recording - Virtual Painter", img)

    # Quit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()
ws.close()
