# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense, Dropout, LSTM


from tensorflow.keras.preprocessing.image import img_to_array
import imutils
import cv2
from tensorflow.keras.models import load_model
import numpy as np




import time


class CFaceRecognition:
    def __init__(self, cservo):
        self.cservo = cservo

        self.PAN_DELTA = 10  # 팔로우 팬 서보 모터의 조정치 (이 값에 따라 팔로우 각도 정도 결정)
        self.TILT_DELTA = 10 # 팔로우 틸트 서보 모터의 조정치
        self.prob_threshold = 40  # 감정 인식 결정하려는 퍼센트 수치
        self.DETECT_TIME = 1 # 감정 인식 결정하려는 시간. 너무 금방 끝나면 이수치를 늘리고, 너무 인식이 안되면 줄이면될듯?

        # Frame Size. Smaller is faster, but less accurate.
        # Wide and short is better, since moving your head up and down is harder to do.
        # W = 160 and H = 100 are good settings if you are using and earlier Raspberry Pi Version.
        # FRAME_W = 320
        # FRAME_H = 200

        self.FRAME_W = 300
        self.FRAME_H = 225



    def InitModel(self):
        # parameters for loading data and images
        self.detection_model_path = '/home/pi/resource/haarcascade_files/haarcascade_frontalface_default.xml'
        self.emotion_model_path = '/home/pi/resource/models/_mini_XCEPTION.102-0.66.hdf5'

        # hyper-parameters for bounding boxes shape
        # loading models
        self.face_detection = cv2.CascadeClassifier(self.detection_model_path)
        self.emotion_classifier = load_model(self.emotion_model_path, compile=False)
        self.EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]

        # feelings_faces = []
        # for index, emotion in enumerate(EMOTIONS):
        # feelings_faces.append(cv2.imread('emojis/' + emotion + '.png', -1))

        self.camera = cv2.VideoCapture(0)



    def getEmotion(self):
        # starting video streaming

        state = {}
        savetime = {}
        for emotion in self.EMOTIONS:
            state[emotion] = False
            savetime[emotion] = 0


        while True:

            frame = self.camera.read()[1]

            #reading the framez
            frame = imutils.resize(frame,width=300)
            frame=cv2.flip(frame,0)
            # h, w, c = frame.shape
            # print(h, w, c)  # 225, 300
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)

            canvas = np.zeros((250, 300, 3), dtype="uint8")
            frameClone = frame.copy()
            if len(faces) > 0:

                for (x, y, w, h) in faces:
                    # Draw a green rectangle around the face (There is a lot of control to be had here, for example If you want a bigger border change 4 to 8)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)

                    # Track face with the square around it

                    # Get the centre of the face
                    x = x + (w / 2)
                    y = y + (h / 2)

                    # Correct relative to centre of image
                    turn_x = float(x - (self.FRAME_W / 2))
                    turn_y = float(y - (self.FRAME_H / 2))


                    cam_pan = turn_x
                    cam_tilt = -turn_y

                    # print(cam_pan, cam_tilt)

                    self.cservo.pan(int(cam_pan/self.PAN_DELTA))
                    self.cservo.tilt(int(cam_tilt/self.TILT_DELTA))
                    break


                faces = sorted(faces, reverse=True,
                key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
                (fX, fY, fW, fH) = faces
                            # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
                    # the ROI for classification via the CNN
                roi = gray[fY:fY + fH, fX:fX + fW]
                roi = cv2.resize(roi, (64, 64))
                roi = roi.astype("float") / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)


                preds = self.emotion_classifier.predict(roi)[0]  #  tensorflow/core/framework/cpu_allocator_impl.cc:81] Allocation of 230400 exceeds 10% of system memory.
                emotion_probability = np.max(preds)
                label = self.EMOTIONS[preds.argmax()]
                

            else: continue

            for (i, (emotion, prob)) in enumerate(zip(self.EMOTIONS, preds)):
                # construct the label text
                text = "{}: {:.2f}%".format(emotion, prob * 100)

                w = int(prob * 300)
                cv2.rectangle(canvas, (7, (i * 35) + 5),
                (w, (i * 35) + 35), (0, 0, 255), -1)
                cv2.putText(canvas, text, (10, (i * 35) + 23),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                (255, 255, 255), 2)
                cv2.putText(frameClone, label, (fX, fY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),
                              (0, 0, 255), 2)

                
                if prob*100 > self.prob_threshold:
                    if state[emotion] == False:
                        state[emotion] = True
                        savetime[emotion] = time.time()
                        print("save", emotion)
                    else:
                        if time.time() - savetime[emotion] > self.DETECT_TIME:
                            print(emotion, prob*100)

                            # self.camera.release()
                            # cv2.destroyWindow("your_face")
                            cv2.destroyAllWindows()
                            return preds

                        else:
                            print(time.time() - savetime[emotion])


                else:
                    state[emotion] = False
                    savetime[emotion] = 0

            #    for c in range(0, 3):
            #        frame[200:320, 10:130, c] = emoji_face[:, :, c] * \
            #        (emoji_face[:, :, 3] / 255.0) + frame[200:320,
            #        10:130, c] * (1.0 - emoji_face[:, :, 3] / 255.0)

            
            cv2.imshow('your_face', frameClone)            
            cv2.imshow("Probabilities", canvas)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            

        self.camera.release()
        cv2.destroyAllWindows()
        

if __name__ == "__main__":
    obj = CFaceRecognition()
    obj.InitModel()

    obj.getEmotion()
    
            
