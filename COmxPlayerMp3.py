#https://www.raspberrypi.org/documentation/raspbian/applications/omxplayer.md

from omxplayer.player import OMXPlayer
from pathlib import Path
import time


class COmxPlayerMp3:
    def __init__(self):
        print("Start :", str(self))

    def callback_position(self, a, p):
        print("position event", p)
    
    def TEST_mp3play(self):

        # 상태를 sad로 설정
        VIDEO_PATH = Path("./sad.mp4")

        player = OMXPlayer(VIDEO_PATH, args='--loop -b') # loop
        VIDEO_PATH = "electric.mp3"
        #playerSound = OMXPlayer(VIDEO_PATH, args='--loop -b')  # loop

        print("is playing", player.is_playing())


        #player.set_volume(0.5)
        
        time.sleep(3) # 3초간 슬퍼하고 종료
        player.quit()

        # 상태를 angry로 변경
        VIDEO_PATH = Path("./angry.mp4")
        player = OMXPlayer(VIDEO_PATH, args='--loop -b')  # loop
        
        time.sleep(3)
        player.quit()

    def playVideoLoop(self, path): # 동영상 반복 재생
        player = OMXPlayer(Path(path), args='--loop -b')  # loop
        return player

    def playMp3Once(self, path):
        player = OMXPlayer(Path(path), args='-b')
        return player

    def stopVideo(self, player):
        player.quit()

if __name__ == "__main__":
    obj = COmxPlayerMp3()

    p = obj.playVideoLoop("./angry.mp4")
    m = obj.playMp3Once("electric.mp3")
    time.sleep(5)
    obj.stopVideo(p)

    p2 = obj.playVideoLoop("./sad.mp4")
    time.sleep(1)
    obj.stopVideo(p2)
            
        
        