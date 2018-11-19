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
    delta = 9000
    pitch=0
    while True:
        for key, val in notes.items():
            for i in range(len(val)):
                if(abs(freq-val[i]) < delta):
                    delta = abs(freq-val[i])
                    note = key
                    pitch=i
        break
    return(note,pitch)

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
            stdout.write('{}, {}{}  \r'.format(int(freq), note[0],note[1]))
            stdout.flush()
    except KeyboardInterrupt:
        print("CLOSED")
        stream.stop_stream()
        stream.close()
        p.terminate()



if __name__ == "__main__":
    main()


