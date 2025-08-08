import websocket
import json
import time
import random

# Connect to Spring Boot WebSocket
ws = websocket.WebSocket()
ws.connect("ws://localhost:8080/draw")

# Send random dots every 50ms
try:
    while True:
        x = random.randint(100, 700)
        y = random.randint(100, 500)
        ws.send(json.dumps({"x": x, "y": y}))
        time.sleep(0.05)
except KeyboardInterrupt:
    ws.close()
