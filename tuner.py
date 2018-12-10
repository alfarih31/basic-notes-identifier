import pyaudio
import numpy as np
from sys import stdout
from argparse import ArgumentParser
from msvcrt import getch, kbhit

ap = ArgumentParser()
ap.add_argument("-m", "--mode", required=True, default='m',
                help="\'a\' for Auto, \'m\' for Manual")
args = vars(ap.parse_args())

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
notes_std = []
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

for i in range(len(notes['C'])-1):
    temp = []
    temp2 = []
    for key, val in notes.items():
        temp.append(notes[key][i])
    for j in range(len(temp)-2):
        temp2.append(temp[j]-temp[j+1])
    notes_std.append(np.std(temp2))
    temp.clear()
    temp2.clear()

print(notes_std)
def get_freq(b_data, fs):
    data = np.frombuffer(b''.join(b_data), dtype=np.int32)
    fft = np.fft.fft(data)
    p = np.absolute(fft)

    freq = np.fft.fftfreq(np.shape(p)[0])*fs

    return(abs(freq[np.argmax(p)]))

def get_note_pitch(freq):
    note = 'n'
    pitch=0
    delta = 9000
    while True:
        for key, val in notes.items():
            for i in range(len(val)):
                if(abs(freq-val[i]) < delta):
                    delta = abs(freq-val[i])
                    note = key
                    pitch=i
        break
    return (note, pitch)

def check_freq(note, pitch, query):
    command = ''

    detected = notes[note][pitch]
    if(args['mode'] == 'a'):
        target = ['',0]
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
    else:
        if (query == 'a' or query == -1): return (note, pitch, ['a','a'], 'a')
        n, p = query
        current = notes[n][p]
        delta = current-detected
        if (delta > 0):
            command = '+'
        elif (delta < 0):
            command = '-'
        else: command = 'OK'
        target = query

    return(note, pitch, target, command)

def get_query(string):
    if(string < 6 and string >= 0):
        return(g_tune[string])
    else: return 'a'

def main():
    CHUNK = 1024
    FORMAT = pyaudio.paInt32
    CHANNELS = 1
    RATE = 44100
    SAMPLING_TIME = 0.1
    q = -1
    p = pyaudio.PyAudio()

    s_freq = [] #List for frequency sampling
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

            #Process Sound Frame
            if(kbhit()):
                q = get_query(abs(48 - ord(getch()))-1)
            freq = get_freq(frames, RATE)
            s_freq.append(freq)
            if(len(s_freq) > 10):
                n, p = get_note_pitch(freq)
                if(np.std(s_freq) <= notes_std[p]*1.2):
                    note = check_freq(n, p, q)
                    stdout.write('Detected: {}, {}{} || Target: {}{}, {}    \r'.format(int(freq), note[0],note[1], note[2][0], note[2][1], note[3]))
                s_freq.clear()
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("CLOSED")



if __name__ == "__main__":
    main()


