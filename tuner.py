import pyaudio
import numpy as np
from sys import stdout

notes = {'C': [],
        'C#':[],
        'D':[],
        'D#':[],
        'E':[],
        'F':[],
        'F#':[],
        'G':[],
        'G#':[],
        'A':[],
        'A#':[],
        'B':[],
        }
g_tune = [['E', 2],
            ['A', 2],
            ['D', 3],
            ['G', 3],
            ['B', 3],
            ['E', 4]]
with open('notes.dat', 'r') as f:
    line = f.readlines()
    for x in line:
        k = x.rstrip().split(',')
        if (len(k) >= 2):
            notes[k[0]].append(int(k[1]))

def get_freq(b_data, fs):
    data = np.frombuffer(b''.join(b_data), dtype=np.int32)
    fft = np.fft.fft(data)
    p = np.absolute(fft)

    freq = np.fft.fftfreq(np.shape(p)[0])*fs

    return(abs(freq[np.argmax(p)]))

def check_freq(freq):
    note = 'n'
    command = ''
    delta = 9000
    pitch=0
    target = ['',0]
    while True:
        for key, val in notes.items():
            for i in range(len(val)):
                if(abs(freq-val[i]) < delta):
                    delta = abs(freq-val[i])
                    note = key
                    pitch=i
        break

    detected = notes[note][pitch]
    d = 9000
    rd = 0
    for n, p in g_tune:
        current = notes[n][p]
        delta = current-detected
        if(abs(delta) < d):
            d = abs(delta)
            rd = delta
            target[0] = n
            target[1] = p
    if (rd > 0):
        command = '+'
    elif (rd < 0):
        command = '-'
    else: command = 'OK'

    return(note,pitch, target, command)

def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt32
    CHANNELS = 1
    RATE = 44100
    SAMPLING_TIME = 0.1

    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        while True:
            frames = []
            for i in range(0, int(RATE / CHUNK * SAMPLING_TIME)):
                data = stream.read(CHUNK)
                frames.append(data)
            freq = get_freq(frames, RATE)
            note = check_freq(int(freq))
            stdout.write('Detected: {}, {}{} || Target: {}{}, {}    \r'.format(int(freq), note[0],note[1], note[2][0], note[2][1], note[3]))
    except KeyboardInterrupt:
        print("CLOSED")
        stream.stop_stream()
        stream.close()
        p.terminate()



if __name__ == "__main__":
    main()


