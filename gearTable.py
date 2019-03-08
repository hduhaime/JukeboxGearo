#Run pipenv shell first!

#--------------------------------#
#                                #
#           IMPORTS              #
#                                #
#--------------------------------#

import code
import time
import threading
import serial
import pygame, sys
import time

#--------------------------------#
#                                #
#           GLOBALS              #
#                                #
#--------------------------------#

#Pygame
pygame.init()
clock = pygame.time.Clock()
white = (255, 255, 255)
pygame.display.set_caption('Basic Sound Example')
size = [640, 480]
screen = pygame.display.set_mode(size)

#Song management
_end = '_end_'
songs = {
    'DDDFFCCGF': ("You Spin Me Round\n", pygame.mixer.Sound('sound/You_Spin_Me.wav')),
    'DEDAGGD': ("Jukebox Hero", pygame.mixer.Sound('sound/Jukebox.wav')),
    'EGEGEAG': ("Rolling in the Deep\n", pygame.mixer.Sound('sound/Deep.wav')),
    'AAGFGF': ('Rollin\' on the River\n', pygame.mixer.Sound('sound/Rolling.wav')),
    'CFFFF': ("The Wheels on the Bus\n", pygame.mixer.Sound('sound/Wheels.wav')),
    'CCDFGA' : ("We Didn't Start the Fire\n", pygame.mixer.Sound('sound/Fire.wav')),
    'GABBGA' : ("Take Me Home, Country Roads\n", pygame.mixer.Sound('sound/Country.wav')),
    'CDEFGAB' : ("TEST_SONG\n", pygame.mixer.Sound('sound/TEST_SONG.wav')),
    'BAGFEDC' : ("TEST_SONG_2\n", pygame.mixer.Sound('sound/TEST_SONG.wav'))
}
songDict = {}
songTrackers = []
maxLen = len(max(songs, key=len))


#songs['DDDFFCCGF'][1].set_volume(0.6)

#Threads
mutex = threading.Lock()
RUNNING = True

#Serial
ser = serial.Serial('COM4', 9600, timeout=1)
lastReading = 0.0
reading = ""

#Notes
C = pygame.mixer.Sound('sound/C.wav')
D = pygame.mixer.Sound('sound/D.wav')
E = pygame.mixer.Sound('sound/E.wav')
F = pygame.mixer.Sound('sound/F.wav')
G = pygame.mixer.Sound('sound/G.wav')
A = pygame.mixer.Sound('sound/A.wav')
B = pygame.mixer.Sound('sound/B.wav')

#--------------------------------#
#                                #
#           SONG MGMT            #
#                                #
#--------------------------------#

#Create data structure for songs
def make_trie(words):
    root = dict()
    for word in words:
        current_dict = root
        for letter in word:
            current_dict = current_dict.setdefault(letter, {})
        current_dict[_end] = word
    return root

#Setup fxn
def setup_songs():
    global songs
    global songDict

    songDict  = make_trie(songs.keys())

#Plays a note, reports sequence (called w mutex)
def playNote(ID, mixerSound):

    global songDict
    global songTrackers
    global _end
    global lastReading
    global songs
    global ser
    global maxLen

    lastReading = time.time()

    songTrackers.append(songDict)

    for index, tracker in enumerate(songTrackers):

        #Found a match
        if ID in tracker:
            songTrackers[index] = tracker[ID]

            #HIT
            if _end in songTrackers[index]:

                foundSong = songs[songTrackers[index][_end]]

                print("\nFound a sequence: " + foundSong[0] + "\n")
                
                ser.write(bytearray(ID.lower(), 'ascii'))
                mixerSound.play()
                
                ser.write(bytearray('A', 'ascii'))

                time.sleep(1)
                ser.write(bytearray('B', 'ascii'))
                foundSong[1].set_volume(0.2)
                foundSong[1].play()

                time.sleep(foundSong[1].get_length())
                ser.write(bytearray('C', 'ascii'))
                songTrackers = []
                
                return

    #popping off list
    if len(songTrackers) > maxLen:
        songTrackers.pop(0)

    #code.interact(local=locals())
    mixerSound.play()

    time.sleep(0.5)
    ser.write(bytearray(ID.lower(), 'ascii'))
    



#--------------------------------#
#                                #
#           TIMEOUT              #
#                                #
#--------------------------------#

def check_time():

    global lastReading
    global songTrackers
    global mutex
    global RUNNING
    global ser

    maxDelay = 7.0

    while RUNNING:
        mutex.acquire()
        if songTrackers and ((time.time() - lastReading) > maxDelay):
            ser.write(bytearray('C', 'ascii'))
            songTrackers = []
        mutex.release()
        time.sleep(0.1)

def setup_timeout():       
    try:
        threading.Thread(target=check_time).start()
    except:
        sys.exit()



#--------------------------------#
#                                #
#         SERIAL READING         #
#                                #
#--------------------------------#


def serial_reader():
    global RUNNING
    global reading
    global mutex

    while RUNNING:
        try:
            locRead = ser.readline()
            
            if locRead:
                locRead = locRead.strip().decode('ascii')
                mutex.acquire()
                reading = locRead
                mutex.release()
        except:
            continue

def setup_serial():
    try:
        threading.Thread(target=serial_reader).start()
    except:
        sys.exit()


#--------------------------------#
#                                #
#         MAIN / SETUP           #
#                                #
#--------------------------------#

def main():
    global mutex
    global screen
    global ser
    global reading
    global clock
    global RUNNING


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                ser.close()
                RUNNING = False
                sys.exit()

        mutex.acquire()
        
        if(reading == "C"):
            #C.play()
            playNote('C', C)
        elif(reading == "D"):
            #D.play()
            playNote('D', D)
        elif(reading == "E"):
            #E.play()
            playNote('E', E)
        elif(reading == "F"):
            #F.play()
            playNote('F', F)
        elif(reading == "G"):
            #G.play()
            playNote('G', G)
        elif(reading == "A"):
            #G.play()
            playNote('A', A)
        elif(reading == "B"):
            #G.play()
            playNote('B', B)
        

        reading = ""

        screen.fill(white)
        pygame.display.update()
        mutex.release()
        clock.tick(20)

def setup():
    setup_songs()
    setup_timeout()
    setup_serial()

if __name__ == '__main__':
    setup()
    main()