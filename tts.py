import io
import os
import subprocess

def play(sentence, speed=105, lang="en-gb"):
    print(sentence)

    proc_tts = subprocess.Popen(['espeak', '-k', '20', '-s', str(speed), '-v', lang], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc_aplay = subprocess.Popen(['aplay'], stdin=proc_tts.stdout)
    text_in = proc_tts.stdin
    text_in.write(sentence)
    text_in.close()

    proc_aplay.communicate()
