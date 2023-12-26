import cv2
import mediapipe as mp
import pyautogui
import math
import speech_recognition as sr
import threading
import pygame
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

capture_active = True
listening = False
shutdown = False
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils
pyautogui.FAILSAFE = False
start_sound_path = resource_path("start.wav")
stop_sound_path = resource_path("stop.wav")
exit_sound_path = resource_path("exit.wav")

def play_sound(file_path):
    pygame.init()
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    sound.play()

def listen_for_keyword(keyword, sound_path, fn):
    global listening
    global shutdown
    listening = True
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(f'Listening for the keyword: {keyword}')
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        if keyword in command:
            print(f"Keyword '{keyword}' detected. Processing...")
            play_sound(sound_path)
            listening = False
            fn()
        elif 'exit' in command:
            print("Exiting...")
            play_sound(exit_sound_path)
            listening = False
            shutdown = True
        else:
            print("Keyword not detected")
            listen_for_keyword(keyword, sound_path, fn)
    except sr.UnknownValueError:
        print("Could not understand audio. Please try again.")
        listen_for_keyword(keyword, sound_path, fn)
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")
        listen_for_keyword(keyword, sound_path, fn)

def move_mouse(x, y):
    screen_width, screen_height = pyautogui.size()
    scaled_x = int(screen_width * (x * 1.3 - 0.05))
    scaled_y = int(screen_height * (y * 1.7 - 0.05))
    pyautogui.moveTo(scaled_x, scaled_y)

def drag_mouse(x, y):
    screen_width, screen_height = pyautogui.size()
    scaled_x = int(screen_width * (x * 1.3 - 0.05))
    scaled_y = int(screen_height * (y * 1.7 - 0.05))
    pyautogui.dragTo(scaled_x, scaled_y)

def capture_gestures():
    global capture_active
    global listening
    global start_sound_path
    global stop_sound_path
    global shutdown
    mouse_x, mouse_y = 0.5, 0.5
    prev_mouse_x, prev_mouse_y = 0, 0
    next_mouse_x, next_mouse_y = 0.5, 0.5
    drag = 0
    cap = cv2.VideoCapture(0)

    play_sound(start_sound_path)

    while not shutdown:
        if not capture_active:
            if not listening:
                stop_thread = threading.Thread(target=listen_for_keyword, args=("start", start_sound_path, start_capture))
                stop_thread.start()
            continue
        if not listening:
            restart_thread = threading.Thread(target=listen_for_keyword, args=("stop", stop_sound_path, stop_capture))
            restart_thread.start()

        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:

                for point in landmarks.landmark:
                    x, y = int(point.x * frame.shape[1]), int(point.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                index_finger_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_dip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP]
                middle_finger_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                thumb_finger_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                ring_finger_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_finger_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                z_index = math.fabs(index_finger_tip.z)

                if math.fabs(mouse_x - next_mouse_x) > 0.01 or math.fabs(mouse_y - next_mouse_y) > 0.01:
                    mouse_x = (mouse_x + next_mouse_x) / 2
                    mouse_y = (mouse_y + next_mouse_y) / 2
                    move_mouse(mouse_x, mouse_y)

                if index_finger_tip.y < middle_finger_tip.y and math.fabs(middle_finger_dip.y - index_finger_tip.y) > (z_index * 0.5) and math.fabs(pinky_finger_tip.x - thumb_finger_tip.x) > (z_index * 1.5):

                    if(prev_mouse_x != 0 and prev_mouse_y != 0):

                        x_diff = (prev_mouse_x - index_finger_tip.x) * (2.0 - (z_index * 5))
                        y_diff = (prev_mouse_y - index_finger_tip.y) * (2.0 - (z_index * 5))
                        prev_mouse_x = index_finger_tip.x
                        prev_mouse_y = index_finger_tip.y

                        if math.fabs(x_diff) > 0.003 or math.fabs(y_diff) > 0.003:

                            next_mouse_x = mouse_x - x_diff
                            next_mouse_y = mouse_y - y_diff
                            if mouse_x < 0: mouse_x = 0
                            if mouse_x > 1: mouse_x = 1
                            if mouse_y < 0: mouse_y = 0
                            if mouse_y > 1: mouse_y = 1

                        if math.fabs(thumb_finger_tip.y - ring_finger_tip.y) < (z_index * 0.8) and math.fabs(thumb_finger_tip.x - ring_finger_tip.x) < (z_index * 0.8):
                            pyautogui.click(button='right')

                        if math.fabs(thumb_finger_tip.y - middle_finger_tip.y) < (z_index * 0.8 + 0.01) and math.fabs(thumb_finger_tip.x - middle_finger_tip.x) < (z_index * 0.8 + 0.01):
                            if drag <= 0: pyautogui.mouseDown()
                            drag += 1
                        else:
                            if 0 < drag and drag < 6:
                                pyautogui.click()
                                drag = 0
                            elif drag == 6:
                                pyautogui.mouseUp()
                                drag = 0
                            else: drag -= 1 if drag > 0 else 0
                    else:
                        prev_mouse_x = index_finger_tip.x
                        prev_mouse_y = index_finger_tip.y
                else:
                    prev_mouse_x = 0
                    prev_mouse_y = 0
                    drag = 0
                    pyautogui.mouseUp()

                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

def stop_capture():
    global capture_active
    capture_active = False

def start_capture():
    global capture_active
    capture_active = True

def exit_program():
    global shutdown
    shutdown = True

if __name__ == "__main__":
    capture_thread = threading.Thread(target=capture_gestures, args=())
    capture_thread.start()