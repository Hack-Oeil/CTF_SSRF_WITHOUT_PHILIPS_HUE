import pyvirtualcam
from pyvirtualcam import PixelFormat
import cv2
import os
import socketio
import threading
import time

# Obtenir le chemin absolu du script courant
script_directory = os.path.dirname(os.path.abspath(__file__))

# Transformer les chemins relatifs en chemins absolus
def get_absolute_path(relative_path):
    return os.path.join(script_directory, relative_path)


sio = socketio.Client()

@sio.on('message')
def on_message(message):  
    if message == "on":
        with open(get_absolute_path("light_state_on"), "w") as file:
            file.write("on")
    elif message == "off":
        with open(get_absolute_path("light_state_off"), "w") as file:
            file.write("off")

@sio.event
def connect():
    print('Caméra virtuelle activée et connexion au serveur correcte...\nLaissez cette fenetre ouverte le temps du CTF !')

@sio.event
def disconnect():
    print('Déconnecté du serveur')

def websocket_thread():
    try:
        sio.connect('http://localhost:3000')
        sio.wait()
    except Exception as e:
        print("Vous devez lancer les serveurs SSRF avant la caméra !")
        time.sleep(5)  # Pause de 3 secondes
        os._exit(1)  # Ferme l'application

if __name__ == "__main__":
    websocket_thread = threading.Thread(target=websocket_thread)
    websocket_thread.start()

    # Votre code principal ici
    video = cv2.VideoCapture(get_absolute_path("videos/off.mp4"))
    if not video.isOpened():
        raise ValueError("error opening video")
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    stateFileOn = get_absolute_path("light_state_on")
    stateFileOff = get_absolute_path("light_state_off")

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
                    os.remove(stateFileOn)
                elif os.path.exists(stateFileOff):
                    if state == 2 :
                        state = 3
                    os.remove(stateFileOff)
                # on allume les lumieres
                if state == 1 :
                    video = cv2.VideoCapture(get_absolute_path("videos/goon.mp4"))
                    state = 2                    
                # les lumieres sont allumées
                elif state == 2 :
                    video = cv2.VideoCapture(get_absolute_path("videos/on.mp4"))
                # on éteint les lumieres
                elif state == 3 :
                    video = cv2.VideoCapture(get_absolute_path("videos/gooff.mp4"))   
                    state = 0                    
                else :
                    video = cv2.VideoCapture(get_absolute_path("videos/off.mp4"))
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



