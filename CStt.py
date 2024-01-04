# 마이크 스피커 설정
# https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=makepluscode&logNo=221399939583

# https://wdprogrammer.tistory.com/38

# https://fast-it.tistory.com/entry/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%9C%BC%EB%A1%9C-%EC%9D%8C%EC%84%B1%EC%9D%B8%EC%8B%9D-%EB%B4%87-%EB%A7%8C%EB%93%A4%EA%B8%B01
import speech_recognition as sr # pip3 install SpeechRecognition, pip3 install Pyaudio, sudo apt-get install python3-pyaudio

#OSError: libasound.so: cannot open shared object file: No such file or directory
#
#sudo apt-get install flac


import speech_recognition as sr
import sys

class CStt:
    def __init__(self):

        self.AUDIO_FILE = "/home/pi/output.wav"

    def getStt(self):
        # audio file을 audio source로 사용
        r = sr.Recognizer()
        with sr.AudioFile(self.AUDIO_FILE) as source:
            audio = r.record(source)  # 전체 audio file 읽기

        # 구글 웹 음성 API로 인식하기 (하루에 제한 50회? 24시간 동안 1일 최대 60분 무료? 맞나?)
        try:
            #sys.stdout = open('/home/pi/stt.txt', 'w')
            f = open('/home/pi/stt.txt', 'w')
            stt_result = ""
            stt_result = r.recognize_google(audio, language='ko')
            f.write(stt_result)
            f.close()
            # print("Google Speech Recognition thinks you said : " + stt_result)
    
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        
        if not len(stt_result) > 0 :
            return "하루"
        else :
            return stt_result
        
        # 결과
        # Google Speech Recognition thinks you said : 안녕하세요 오늘도 멋진 하루 되세요



if __name__ == "__main__":
    obj = CStt()
    obj.getStt()