import cv2
import mediapipe as mp
import websocket
import json

# Setup websocket connection
ws = websocket.WebSocket()
ws.connect("ws://localhost:8080/draw")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    # Flip and convert frame to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with MediaPipe
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip coordinates
            index_tip = hand_landmarks.landmark[8]
            x = int(index_tip.x * frame.shape[1])
            y = int(index_tip.y * frame.shape[0])

            # Detect finger status: 1 = up, 0 = down
            finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky
            fingers = []
            for tip_id in finger_tips:
                if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # Gesture logic
            mode = None
            if fingers == [1, 0, 0, 0]:         # Only index finger up
                mode = "draw"
            elif fingers == [1, 1, 0, 0]:       # Index + middle finger up
                mode = "erase"
            elif fingers == [1, 1, 1, 1]:       # All 4 fingers up (clear gesture)
                mode = "clear"

            # Send to WebSocket
            if mode == "clear":
                data = json.dumps({"mode": "clear"})
            elif mode:
                data = json.dumps({"x": x, "y": y, "mode": mode})
            else:
                data = None

            if data:
                ws.send(data)
                print("Sent:", data)

    # Show webcam preview with hand tracking
    cv2.imshow("🖐️ Virtual Painter - Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
ws.close()
