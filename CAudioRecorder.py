import subprocess
import threading
import wave
import contextlib
import os
import sys
import audioop
import time # time 모듈 추가
# https://stackoverflow.com/questions/36956083/how-can-the-terminal-output-of-executablesrun-by-python-functions-be-silenced-i/36966379#36966379
@contextlib.contextmanager
def ignore_stderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)
        
class CAudioRecorder:
    def record(self):
        # 녹음할 파일의 이름
        WAVE_OUTPUT_FILENAME = "/home/pi/output.wav"
        # arecord 명령 실행
        record_time = "4"
        arecord_command = ["arecord", "-D", "plughw:3,0", "-f", "S16_LE", "-d", record_time,
        WAVE_OUTPUT_FILENAME]
        subprocess.call(arecord_command)
        
        time.sleep(0.5) # 2초 동안 대기
    
if __name__ == "__main__":
    obj = CAudioRecorder()
    obj.record()

