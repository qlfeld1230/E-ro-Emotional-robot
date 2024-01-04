from COmxPlayerMp3 import COmxPlayerMp3
from CMpu6050 import CMpu6050
from CFaceRecognition import CFaceRecognition
from CSpeechEmotion import CSpeechEmotion
from CAudioRecorder import CAudioRecorder
from CServoControlsmoo import CServoControl
from CStt import CStt

import random
import time
import threading
import RPi.GPIO as GPIO
import pandas as pd

button_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=[ CDetect 라는 클래스 정의 ]


class CDetector:
    
    def __init__(self):

        self.FACE_WEIGHT = 55        # 표정인식에 대한 가중치
        self.VOICE_WEIGHT = 38       # 음색인식에 대한 가중치
        self.WORD_WEIGHT = 7         # 문장인식에 대한 가중치

        self.player = COmxPlayerMp3() # [영상, 음성 재생 인스턴스]
        self.p_prev = None  # [이전 재생 플레이어 인스턴스]
        self.p_curr = None  # [현재 재생 플레이어 인스턴스]

        self.sensor = CMpu6050()         # [가속도 센서 인스턴스]
        self.sensor.MPU_Init()           # 가속도 센서를 초기화

        self.stt = CStt()                # [STT 클래스 인스턴스]

        self.servo = CServoControl()     # [서보모터 제어 인스턴스]

        self.emot_list = ["sad", "happy", "angry", "scared", "neutral","diff"]     # 감정 종류

       
       
        self.motor_seq = {}
       
        for e in self.emot_list:  # self.motor_seq 딕셔너리를 초기화 (서보 모터 시퀀스 초기화)
            self.motor_seq[e] = []
            
            for ix in range(6):   # self.motor_seq 딕셔너리에 값을 추가( [90, 90, 90] )
                self.motor_seq[e].append([90, 90, 90])

            

        '''
        0:leftarm forward&back <90 backward 1:leftarm purluck <90 out
        2:rightarm forward&back <90 forward 3:rightarm purluck <90 in
        4:neck right&left <90 right 5:neck down&up <90 down
        '''
        self.motor_seq['sad'][0] = [90,90,90, 90, 90,90]
        self.motor_seq['sad'][1] = [90,90,120, 120, 90,90]
        self.motor_seq['sad'][2] = [90,90,90, 90, 90,90]
        self.motor_seq['sad'][3] = [90,90,60, 60, 90,90]
        self.motor_seq['sad'][4] = [90,90,90, 90, 90,90]
        self.motor_seq['sad'][5] = [90,90,80, 80, 90,90]
        #neck updown,arm purluck
       
        self.motor_seq['happy'][0] = [90,90, 45, 135, 90,90]
        self.motor_seq['happy'][1] = [90,90, 90, 90,90,90]
        self.motor_seq['happy'][2] = [90,90, 130, 45, 90,90]
        self.motor_seq['happy'][3] = [90,90, 90, 90,90,90]
        self.motor_seq['happy'][4] = [90,90, 90, 90,90,90]
        self.motor_seq['happy'][5] = [90,90, 120, 120,100,100]
        #par shake , neck up

        self.motor_seq['angry'][0] = [90,30, 30, 30,90,90]
        self.motor_seq['angry'][1] = [90,110, 110,110,90,90]
        self.motor_seq['angry'][2] = [90,150, 150,150 ,90,90]
        self.motor_seq['angry'][3] = [90,70, 70,70 ,90,90]
        self.motor_seq['angry'][4] = [90,90, 90, 90,90,90]
        self.motor_seq['angry'][5] = [90,120, 120,120 ,100,100]
        #par open, neck updown

        self.motor_seq['scared'][0] = [90,90, 60,120, 90,90]
        self.motor_seq['scared'][1] = [90,90, 90,90, 90,90]
        self.motor_seq['scared'][2] = [90,90, 120,60,90,90]
        self.motor_seq['scared'][3] = [90,90, 90,90, 90,90]
        self.motor_seq['scared'][4] = [90,70, 120,70, 90,90]
        self.motor_seq['scared'][5] = [90,90, 90, 90,90,90]
        #neck leftright,arm updown

        self.motor_seq['neutral'][0] = [90,90, 90, 90,90,90]
        self.motor_seq['neutral'][1] = [90,90, 90, 90,90,90]
        self.motor_seq['neutral'][2] = [90,90, 90, 90,90,90]
        self.motor_seq['neutral'][3] = [90,90, 90, 90,90,90]
        self.motor_seq['neutral'][4] = [90,70, 120, 100,90,90]
        self.motor_seq['neutral'][5] = [90,90, 90,90, 90,90]
        #neck leftright
        
        self.motor_seq['diff'][0] = [90,30, 30, 30,90,90]
        self.motor_seq['diff'][1] = [90,110, 110,110,90,90]
        self.motor_seq['diff'][2] = [90,150, 150,150 ,90,90]
        #self.motor_seq['diff'][2] = [90,120, 120,120 ,90,90]
        self.motor_seq['diff'][3] = [90,70, 70,70 ,90,90]
        self.motor_seq['diff'][4] = [90,70, 120, 100,90,90]
        self.motor_seq['diff'][5] = [90,90, 90, 90,90,90]
        #par open, neck leftright

        self.InitModules()     # 감정 인식 모듈 초기화
    
    #=== [ InitModules 라는 함수(메서드) 정의 ] -> 감정 인식 모듈을 초기화 시키기 위한 함수(메서드)
    def InitModules(self):                   # 각 모듈 초기화
        self.fr = CFaceRecognition(self.servo)
        self.fr.InitModel()
        self.se = CSpeechEmotion()
    
    #=== [ PlayTTS 라는 함수(메서드) 정의 ] -> 음성을 출력하는 함수(메서드)
    def PlayTTS(self, filename):             # 음성 출력 함수
        self.player.playMp3Once("/home/pi/resource/"+filename)
    
    #=== [ PlayVideo 라는 함수 정의 ] -> 영상을 출력하는 함수
    def PlayVideo(self, filename):
       
        resourcepath = "/home/pi/resource/" # "resourcepath" 변수에 동영상 파일이 저장된 경로를 지정
        self.p_curr = self.player.playVideoLoop(resourcepath+filename)
        
        print("PlayVideo", resourcepath + filename, self.p_curr) 

        time.sleep(0.3)   # 0.3초 딜레이

        if self.p_prev is not None:   # "self.p_prev" 변수가 None이 아니라면( = 이전에 재생 중인 동영상이 있다면 ) 아래 코드 실행
            print("stop ", self.p_prev)
            self.player.stopVideo(self.p_prev)   # 이전 재생중인 영상을 종료
        self.p_prev = self.p_curr # 이제는 현재 재생한 동영상의 ID인 self.p_curr가 self.p_prev에 할당됨

    #=== [ GetFaceEmotion 라는 함수 정의 ] -> 표정 감정 인식 함수(메서드) : CFaceRecognition.py 의 
    def GetFaceEmotion(self):
        preds = self.fr.getEmotion()     # 표정 감정인식 진행, 결과값을 "preds" 변수에 할당. 참고 : 각 감정에 대한 확률 리스트(0~1.0)
        print("getEmotion")
        print(preds)
        return preds                     # 결과 리턴(리턴값 : 각 감정에 대한 확률 리스트(0~1.0))
    
    #=== [ AudioRecThread 라는 함수 정의 ] -> 음성 검출 및 저장 함수(메서드) : CAudioRecorder.py 이용해 음성검출해 저장(output.wav)
    def AudioRecThread(self, req_end, q):      # 오디오 레코드 쓰레드
        self.ar = CAudioRecorder()             # CAudioRecorder 클래스의 인스턴스를 생성하여 self.ar 변수에 할당
        self.ar.record()                # self.ar 인스턴스( = CAudioRecorder() )의 record 메소드를 호출해 목소리 녹음해 인식되면 저장(output.wav)
                                               # 참고로 req_end 인자는 CAudioRecorder.py 의 record 메소드를 종료시킬 떄 사용되는 객체임
        print("end audio rec thread")
    
    #=== [ updateValues 라는 함수 정의 ] -> 리스트 자료형인 "self.values"의 값을 업데이트
    def updateValues(self, value):
        del self.values[0]        #  "self.values" 리스트의 첫 번째 값(인덱스 0)을 삭제.
                                  # (참고 : 리스트의 첫 번째 값을 삭제하고, 모든 값이 왼쪽으로 한 칸씩 이동해 리스트의 길이가 1 감소)
        self.values.append(value) # value 변수에 저장된 값을 리스트의 끝 부분에 추가

    #=== [ detectSensor 라는 함수 정의 ] -> 가속도와 음성 검출 함수 / 강한충격 한번 2, 약한충격 두번 1, 음성 0 return
    def detectSensor(self, t):

        self.Minimum = 3.0      # 최초 검출을 위한 최소 센서수치
        self.arraynum = 20      # 평균 값을 구하기 위한 배열 갯수
        self.values = [0 for i in range(self.arraynum)]
        self.SMALL = 2          # 약한 가속도의 기준 수치
        
        self.LARGE = 4         # 강한 가속도의 기준 수치
        self.array2rate = 2     # 두번째 검출하는 배열의 배율

        while True:  # 무한루프
            if not t.is_alive():
                print("something is recorded")
                return 0

            v = self.sensor.getSensorTotal()
            if v > self.Minimum:
                print('hit')
                for ix in range(self.arraynum):
                    self.updateValues(self.sensor.getSensorTotal())
                maxvalue = max(self.values)
                print(maxvalue)
                if maxvalue > self.LARGE:
                    return 2  # 강한 충격
                elif maxvalue > self.SMALL:
                    time.sleep(0.2)
                    print("start 2nd input1")
                    self.values = [0 for i in range(self.arraynum*self.array2rate)]
                    for ix in range(self.arraynum*self.array2rate):
                        self.updateValues(self.sensor.getSensorTotal())
                    print("end 2nd input1")
                    maxvalue = max(self.values)
                    if maxvalue > self.SMALL:
                        return 1  # 약한 충격

                self.values = [0 for i in range(self.arraynum)]
   
    #=== [ CheckWaitMode 라는 함수 정의 ] -> 오디오 쓰레드 및 가속도 센서 체크 / 음성이 인식됨 + "전원꺼"포함 이면 0 , 강한충격 한번 2 , 약한충격 두번 1 출력
    def CheckWaitMode(self):

        self.req_end = threading.Event()
        
        while True:  

            t = threading.Thread(target=self.AudioRecThread, args=(self.req_end, "",))
            
            t.start() 

            res = self.detectSensor(t)  

            input_state = GPIO.input(button_pin)
            
            if input_state == False:
                return 0
        
            # 충격감지
            if res!= 0:
                self.req_end.set()   # 객체인 self.req_end  "설정(set)" 상태로 설정함
                                     # 참고로 req_end 인자는 CAudioRecorder.py 의 record 메소드를 종료시킬 떄 사용되는 객체임
                t.join()            # 스레드 t가 종료될 때까지 대기, 대상 스레드가 종료되면 다음 코드를 실행
                
                break                           # 무한루프 탈출


        return res     # 결과적으로...  res는 음성이 인식됨 + "전원꺼"포함 이면 0 , 강한충격 한번 2 , 약한충격 두번 1
    
    #=== [ getSttResult 라는 함수 정의 ] -> 문장내에 단어 포함여부 출력. word 포함이면 1, 포함X이면 0
    def getSttResult(self, word):

        f = open('/home/pi/stt.txt')
        line = f.readline()

        if word in line:
            return True # word가 포함되어 있다면 true
        else:
            return False # word가 포함되어 있지 않다면 false
    
    #=== [ main 이라는 함수 정의 ]
    def main(self):

        sad_mp3 = ["sad1.mp3", "sad2.mp3", "sad4.mp3", "sad5.mp3"]
        happy_mp3 = ["happy1.mp3", "happy2.mp3", "happy3.mp3", "happy4.mp3", "happy5.mp3"]
        angry_mp3 = ["angry1.mp3", "angry2.mp3", "angry3.mp3", "angry4.mp3", "angry5.mp3"]
        scared_mp3 = ["scared1.mp3", "scared2.mp3", "scared3.mp3", "scared4.mp3"]
        neutral_mp3 = ["neutral1.mp3", "neutral2.mp3", "neutral3.mp3", "neutral4.mp3"]
        waiting_mp3 = ["waiting.mp3"]
        recognizing_mp3 = ["recognizing.mp3"]
        shock_mp3 = ["shocked.mp3"]
        diff_mp3 = ["diff.mp3"]

        emotion_dict = {"sad": sad_mp3, "happy": happy_mp3, "angry": angry_mp3,
                        "scared": scared_mp3, "neutral": neutral_mp3, "waiting": waiting_mp3,
                        "recognizing": recognizing_mp3, "shock": shock_mp3, "diff": diff_mp3}
        
        try:
            
            self.mode = "대기"  # 최초 모드 설정 : [[[ 대기모드 ]]] : 각 감정 초기화
            
            i=0
            self.PlayTTS("waiting.mp3")   # standby.mp3(대기모드 음성) 재생
            
           
                    
            while True:                  
                self.result = {}         # 0을 값으로 갖는 딕셔너리 self.result를 생성
                for e in self.emot_list:
                    self.result[e] = 0   # 각 감정의 결과값 초기화(emot_list 라이브러리 값들을 0으로 초기화해 self.result 딕셔너리에 저장)

            
            # -------------------------------------------------------
                if self.mode == "절전": #        [[[ 절전모드 ]]] : 절전모드 영상 재생 / 가속도 센서 - 약한 가속도에 대기모드로, 강한 가속도에 충격감지 음성 재생
                    self.PlayVideo("off.mp4")   # sleep.mp4(절전모드 영상) 재생                
                    time.sleep(1)
                    self.PlayVideo("silent.mp4")
                    
                    print('현재 모드 : 절전 모드')
                    
                    res = self.CheckWaitMode() # self.CheckWaitMode() 함수를 호출해 그 결과를 res 변수에 저장

                         
                    if res != 0:   # 약한 가속도 -> 대기모드
                        self.mode = "대기"
                        self.PlayTTS("waiting.mp3")   # standby.mp3(대기모드 음성) 재생
                        
            # -------------------------------------------------------
                if self.mode == "대기": #        [[[ 대기모드 ]]] : 대기모드 음성과 영상 재생 / 마이크 - "전원 꺼"에 절전모드로 / 가속도센서 - 약한 가속도에 감정인식모드로            
                    print('현재 모드 : 대기 모드')
                    self.PlayVideo("on.mp4") # standby.mp4(대기모드 영상) 재생
                    
                    for i in range(0,6):
                        self.servo.setMotorAngle(4,90,90)
                    
                    time.sleep(2)  # 2초간 대기

                    res = self.CheckWaitMode() # self.CheckWaitMode() 함수를 호출해 그 결과를 res 변수에 저장
                    
                    if res == 0:
                        self.mode = "절전"
                    if res == 1: # 가속도센서:약한 가속도 인식된 경우 -> 감정인식모드
                        self.mode = "인식"
                        
                    elif res == 2: # 강한 가속도 -> shock.mp3(충격감지 음성) 재생
                        self.PlayTTS("shocked.mp3")
                        self.PlayVideo("shocked.mp4")
                        
                        self.servo.setMotorAngle(5,110,90)
                        for i in range(0,2):
                            self.servo.setMotorAngle(0,60,90)
                            self.servo.setMotorAngle(2,120,90)
                            time.sleep(0.15)
                            self.servo.setMotorAngle(0,120,60)
                            self.servo.setMotorAngle(2,60,120)
                            time.sleep(0.15)
                        self.servo.setMotorAngle(0,90,120)
                        self.servo.setMotorAngle(2,90,60)
                         
            # -------------------------------------------------------
                elif self.mode == "인식": #      [[[ 감정인식모드 ]]] : 문장, 음색, 표정 감정 인식
                    print('현재 모드 : 인식 모드')
                    self.PlayTTS("recognizing.mp3")   # detect.mp3(감정인식모드 음성) 재생
                    self.PlayVideo("recognizing.mp4") # detect.mp4(감정인식모드 영상) 재생


                    time.sleep(3)
                    
                    self.req_end = threading.Event()
                   
                    t = threading.Thread(target=self.AudioRecThread, args=(self.req_end, "",)) 
                    
                    t.start()

                    f_preds = self.GetFaceEmotion()

                    if t.is_alive():        # t가 true이면( = 음성 검출이 안되고 있으면 )  <- is_alive() 이용해 스레드 t가 실행 중인지 여부를 확인

                        print("음성 검출 안됨")
                        bAudioRecorded = False # bAudioRecorded 가 false임

                        self.req_end.set()  # 객체인 self.req_end  "설정(set)" 상태로 설정함
                                            # 참고로 req_end 인자는 CAudioRecorder.py 의 record 메소드를 종료시킬 떄 사용되는 객체임
                        t.join()   # 스레드 t가 종료될 때까지 대기, 대상 스레드가 종료되면 다음 코드를 실행

                    else:                   # 그렇지 않으면 ( = 음성 검출이 되고 있으면 )
                        bAudioRecorded = True  # bAudioRecorded 가 true임


                    if bAudioRecorded:      # 만약 bAudioRecorded가 True이면( = 음성 검출이 되었으면 )
                        s_preds = self.se.getEmotion()  
                        data = self.stt.getStt()
         
                        csv = pd.read_csv('emotiondata3.csv', names=['emotions', 'words'], encoding='UTF-8')
                        nth = 0
                        a = 0
                        
                        
                        raredata = data.split(' ')

                        word = csv['words']  # 워드라고 이름 붙인 행, 즉 두번째 열을 워드라고 지정.
                        word_val = word.values.tolist()  # values로 특정 열 값 추출. 이 경우, 단어가 적힌 열.
                        
                        for i in range(0, len(word_val)):
                            if word_val[i] in raredata:
                                a = 1
                                nth = i
                            else:
                                pass

                            if a == 1:
                                enum = csv.loc[nth, 'emotions']
                            else:
                                enum = 0

                            if enum == 1:  
                                self.result['sad'] = self.WORD_WEIGHT
                            elif enum == 2:
                                self.result['happy'] = self.WORD_WEIGHT
                            elif enum == 3:
                                self.result['angry'] = self.WORD_WEIGHT
                            elif enum == 4:
                                self.result['scared'] = self.WORD_WEIGHT
                            elif enum == 5:
                                self.result['neutral'] = self.WORD_WEIGHT
                            else:
                                pass


                        # {{{{{ 음색 감정인식}}}}}---------------------------------------------------------------
                        print("s_preds: ", s_preds)

                        for (i, (emotion, prob)) in enumerate(zip(self.se.y, s_preds)):
                            if 'angry' in emotion:              # 'angry' in emotion가 true면 ( = emotion이 'angry'를 포함하면 )
                                self.result["angry"] = self.result["angry"] + (prob * self.VOICE_WEIGHT / 2)
                            elif 'calm' in emotion:
                                self.result["neutral"] = self.result["neutral"] + (prob * self.VOICE_WEIGHT / 2)
                            elif 'fearful' in emotion:
                                self.result["scared"] = self.result["scared"] + (prob * self.VOICE_WEIGHT / 2)
                            elif 'happy' in emotion:
                                self.result["happy"] = self.result["happy"] + (prob * self.VOICE_WEIGHT / 2)
                            elif 'sad' in emotion:
                                self.result["sad"] = self.result["sad"] + (prob * self.VOICE_WEIGHT / 2)

                    # {{{{{ 표정 감정 인식 }}}}}----------------------------------------------------
                    for (i, (emotion, prob)) in enumerate(zip(self.fr.EMOTIONS, f_preds)):
                        if emotion in self.result:  # self.result 딕셔너리에 emotion이 있다면
                            self.result[emotion] = self.result[emotion] + prob * self.FACE_WEIGHT
                            
                    print("self.result", self.result)

                    total = sum(self.result.values())
                    normalized_result = {k: v / total for k, v in self.result.items()}

                    # 가장 큰 확률 두 개를 뽑아냅니다.
                    top_two_emotions = sorted(normalized_result, key=normalized_result.get, reverse=True)[:2]

                    # 두 감정의 확률 차이를 계산합니다.
                    diff = abs(normalized_result[top_two_emotions[0]] - normalized_result[top_two_emotions[1]])

                    # 확률 차이가 0.05 미만이면 특정 메시지를 출력합니다.
                    if diff < 0.05:
                        selected_mp3 = random.sample(emotion_dict["diff"], 1)[0]  # "diff" mp3 선택
                        emotion = "diff"
                    else:
                        emotion = max(normalized_result, key=normalized_result.get)
                        selected_mp3 = random.sample(emotion_dict[emotion], 1)[0]  # 최상의 감정에 해당하는 mp3 선택
                    
                    print("emotion = "+emotion)
                    
                    self.PlayVideo(emotion + ".mp4")
                    
                    # 모터 구동
                    for ix in range(6):
                        if ix == 5:
                            break
                        for jx in range(6):
                            self.servo.setMotorAngle(jx, self.motor_seq[emotion][jx][ix + 1], self.motor_seq[emotion][jx][ix])
                            # setMotorAngle 함수: 각 서보 모터 채널별 각도를 설정하는 함수
                            # num: 채널 번호, angle: 각도

                    time.sleep(0.05)
                    
                    selected_mp3 = random.sample(emotion_dict[emotion], 1)[0]
                    self.PlayTTS(selected_mp3)  # 선택된 mp3 재생
                    self.PlayVideo(emotion + ".mp4")  # 해당 감정에 맞는 영상 출력

                    # 판정된 감정에 맞춰 모터 구동
                    for ix in range(6):
                        if ix==5:
                            break
                        for jx in range(6):
                            self.servo.setMotorAngle(jx, self.motor_seq[emotion][jx][ix+1],self.motor_seq[emotion][jx][ix])
                             
                    time.sleep(0.05)
                        
            # -------------------------------------------------------
                    
                    for i in range(6):
                        if i==3: A=85
                        elif i==5: A=100
                        else:
                            A=90
                            self.servo.setMotorAngle(i,A,90)
                    
                    
                    time.sleep(1)
                    i=1

                    self.mode = "대기"
                    
                    
    #=============================================================================================================================================================

        except KeyboardInterrupt:
            if self.p_curr is not None:
                self.player.stopVideo(self.p_prev)

        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            print("EXCEPTION:", err_msg)


obj = CDetector()
obj.main()
GPIO.cleanup()  
