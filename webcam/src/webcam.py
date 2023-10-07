import pyvirtualcam
from pyvirtualcam import PixelFormat
import cv2
import os
import socketio
import threading

sio = socketio.Client()

@sio.on('message')
def on_message(message):  
    if message == "on":
        with open("./src/light_state_on", "w") as file:
            file.write("on")
    elif message == "off":
        with open("./src/light_state_off", "w") as file:
            file.write("off")

@sio.event
def connect():
    print('Connecté au serveur WebSocket Node.js')

@sio.event
def disconnect():
    print('Déconnecté du serveur WebSocket Node.js')

def websocket_thread():
    sio.connect('http://localhost:3000')
    sio.wait()

if __name__ == "__main__":
    websocket_thread = threading.Thread(target=websocket_thread)
    websocket_thread.start()

    # Votre code principal ici
    video = cv2.VideoCapture("./src/videos/off.mp4")
    if not video.isOpened():
        raise ValueError("error opening video")
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    stateFileOn = "./src/light_state_on"
    stateFileOff = "./src/light_state_off"

    with pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR,
                            device=None, print_fps=False) as cam:
        count = 0
        state = 0

        while True:
            # Restart video on last frame.
            if count == length:
                count = 0
                # On vérifie en fonction des fichiers
                if os.path.exists(stateFileOn):
                    state = 1
                elif os.path.exists(stateFileOff):
                    state = 3
                # on allume les lumieres
                if state == 1 :
                    video = cv2.VideoCapture("./src/videos/goon.mp4")
                    state = 2
                    os.remove(stateFileOn)
                # les lumieres sont allumées
                elif state == 2 :
                    video = cv2.VideoCapture("./src/videos/on.mp4")
                # on éteint les lumieres
                elif state == 3 :
                    video = cv2.VideoCapture("./src/videos/gooff.mp4")   
                    state = 0
                    os.remove(stateFileOff)
                else :
                    video = cv2.VideoCapture("./src/videos/off.mp4")
                video.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # lecture de la vidéo.
            ret, frame = video.read()
            if not ret:
                raise RuntimeError('Error fetching frame')

            cam.send(frame)
            cam.sleep_until_next_frame()
            
            count += 1

    # Attendez que le thread de la connexion WebSocket se termine (si nécessaire)
    websocket_thread.join()



