import os
import pyaudio
import time
import threading
import time
from queue import Queue, Empty
from google.cloud import speech
from google.cloud import speech_v1p1beta1 as speech
import pygame.mixer
from response_db import JsonResponseLoader
from time import sleep
import sys
import tty
import termios
from pathlib import Path
import random
import subprocess

home_path = os.path.expanduser('~')
response_json_file_name = "response.json"
WAIT_GENDER_STATE = 5
WAIT_RESPONSE_2_STATE = 4
WAIT_RESPONSE_1_STATE = 3
ANSWER_STATE = 2
LISTEN_STATE = 1
STANDBY_STATE = 0
QUIT_TIMEOUT = (60*5)  # 30 seconds timeout
SENTENCE_RECEIVED_TIMEOUT = 5  # Timeout for no sentences received

# Define global parameters
stop_event = threading.Event()
sentence_event = threading.Event()  # Event to signal the receipt of a sentence
def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def empty_queue(q):
    result = []
    try:
        while True:
            result.append(q.get_nowait())
    except Empty:
        pass  # The queue is empty now
    print(f"empty_queue {result}")
    return result


def play_audio(key_word, q, ext):
    try:
        print(home_path)
        mp3_folder = Path(home_path)/'Music'/'spider_mp3'
        wav_folder = Path(home_path)/'Music'/'spider_wav'
        pygame.mixer.init()
        if ext == 'wav' :
            file = wav_folder/key_word/get_random_file(wav_folder / key_word)
        else:
            file = mp3_folder/key_word/get_random_file(mp3_folder / key_word)
        if file is not None:
            try:
                pygame.mixer.music.load(Path(file))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)  # Adjust the sleep duration as needed
            except Exception as e:
                print(f"{e}")
        else:
            print(f'Not playing_file {file}')
        pygame.mixer.music.load(wav_folder/'quiet'/'quiet.wav')
        pygame.mixer.music.play()
        #while pygame.mixer.music.get_busy():
        #    time.sleep(0.1)  # Adjust the sleep duration as needed
        if q is not None:
            empty_queue(q)
    except Exception as e:
        print(f"{e}")



# Set your Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "speect-to-text-410506-647b0e63c4eb.json"#'/home/raz/ros2_ws/src/voice_command/scripts/credentials.json'
# Instantiates a client
client = speech.SpeechClient()

def running_loop( result_queue, config, requests, up_counter, stop_counter, last_up_time, last_stop_time):

    responses = client.streaming_recognize(config=config, requests=requests)
    prev_result = ""
    for response in responses:
        for result in response.results:
            current_time = time.time()
            #print(f"running_loop: {result.alternatives[0].transcript.lower()}")
            if prev_result != result.alternatives[0].transcript.lower():
                result_queue.put(result.alternatives[0].transcript.lower())
                prev_result = result.alternatives[0].transcript.lower()

    return up_counter, stop_counter, last_up_time, last_stop_time

def get_random_file(directory_name):
    if os.path.exists(directory_name) and os.path.isdir(directory_name):
        files = [file for file in os.listdir(directory_name) if os.path.isfile(os.path.join(directory_name, file))]
        if files:
            return random.choice(files)
    return None

# Example usage:
# print(get_random_file("/path/to/directory"))

def get_results(q):
    result = []
    try:
        while True:
            r = q.get_nowait()
            result.append(r)
    except Empty:
        pass  # The queue is empty now
    return " ".join(r)



def play_wav_mp3_for_a_text(test_text, result_queue):
    loader = JsonResponseLoader(response_json_file_name)
    for emo in loader.keys():
        if loader.is_key_found(emo,test_text):
            print(f"{emo}")
            play_audio(emo, result_queue, "wav")
            play_audio(emo, result_queue, 'mp3')
            return True
    return False

def play_wav_for_a_text_if_key_found(key_word, test_text, result_queue):
    loader = JsonResponseLoader(response_json_file_name)
    if loader.is_key_found(key_word, test_text):
        print(f"found {key_word} in {test_text}")
        #play_audio(key_word,result_queue,'wav')
        play_audio(key_word,result_queue, 'wav')
        return True
    else:
        return False

def play_wav_for_a_key(key_word,result_queue):
    play_audio(key_word,result_queue,'wav')


def wait_for_shalom(result_queue, state):
    loader = JsonResponseLoader(response_json_file_name)
    sleep(2)
    while True:
        try:
            text = str(result_queue.get())
            empty_queue(result_queue)
            text_list = text.split(' ')  # Split by spaces
            print(f"standby_state: {text_list}")
            if play_wav_for_a_text_if_key_found('hello',['שלם'], None):
                print("Wait for shalom => WAIT_RESPONSE_1_STATE")
                return WAIT_RESPONSE_1_STATE
            else:
                print('Waiting for שלום ')
                pass#play_audio(f"call-my-name.wav", result_queue)
        except Exception as e:
            print(f"{e}")


def wait_response_1_state(result_queue, state):
    try:
        sleep(0.2)
        empty_queue(result_queue)
        # שואלים מה את מרגישה או איזה צבע בא לך
        text = str(result_queue.get())
        empty_queue(result_queue)
        text_list = text.split(' ')  # Split by spaces
        print(f"wait_response_1_state wait for any response: {text_list}")
        sleep(2)
        play_wav_for_a_key('ask_mood',result_queue)
        sleep(1)
    except Exception as e:
        print(f"{e}")
    return WAIT_RESPONSE_2_STATE




def wait_response_2_state(result_queue, state):
    loader = JsonResponseLoader(response_json_file_name)
    retry = 0
    while True:
        try:
            if retry != 0:
                print("try again")
            text0 = empty_queue(result_queue)
            text = str(result_queue.get())
            text2 = empty_queue(result_queue)
            text_list = text.split(' ')  # Split by spaces
            text_list = text_list + text2 + text0
            print(f"WAIT_RESPONSE_2_STATE got response : {text_list}")
            if play_wav_mp3_for_a_text(text_list, result_queue):
                return STANDBY_STATE
            else:
                retry += 1
                if retry < 3:
                    play_wav_for_a_key('not_understand', result_queue)
                    print(f"Not Understood retry{retry}")
                    continue
                else:
                    print("play sorry-didnt-understand-exit.wav")
                    play_wav_for_a_key("not_understand_exit", result_queue)
                    return STANDBY_STATE
        except Exception as e:
            print(f'{e}')
    print(f"WAIT_RESPONSE_2_STATE => STANDBY_STATE ")
    return STANDBY_STATE



def worker(result_queue):
    global sentence_event

    state = STANDBY_STATE
    """Function running in the worker thread."""
    woman = '-woman'
    print('worker starts ..')
    while True:
        try:
            if state == STANDBY_STATE:
                state = wait_for_shalom(result_queue, state)
            elif state == WAIT_RESPONSE_1_STATE:
                state = wait_response_1_state(result_queue, state)
            elif state == WAIT_RESPONSE_2_STATE:
                state = wait_response_2_state(result_queue, state)
            sentence_event.set()
        except Exception as e:
            print(f"{e}")


def key_worker(result_queue):
    result_queue.put('woman')
    while True:
        char = get_char()
        if char == 'g':
            result_queue.put('man')
        else:
            result_queue.put('woman')
        sleep(1)
def monitor_thread():
    global stop_event
    global sentence_event
    print("monitor starts")
    start_time = time.time()
    while True:
        if sentence_event.wait(SENTENCE_RECEIVED_TIMEOUT):
            print("monitor .")
            sentence_event.clear()  # Clear the event after handling
            start_time = time.time()  # Reset the timer upon receiving a sentence
        else:
            if time.time() - start_time > QUIT_TIMEOUT:
                print("No input received for 30 seconds. Exiting...")
                os.system("touch /tmp/a.txt")
                stop_event.set()
                os.abort()
                break
        time.sleep(1)


def main():

    p = pyaudio.PyAudio()
    result_queue = Queue()
    global stop_event

    stop_event.clear()
    worker_thread = threading.Thread(target=worker, args=(result_queue,))
    worker_thread.start()
    print('start monitor')
    xmonitor_thread = threading.Thread(target=monitor_thread)
    xmonitor_thread.start()
    # xmonitor_thread.join()
    # worker_thread.join()
    print("Available audio input devices:")

    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    for i in range(0, num_devices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

    up_counter = 0
    stop_counter = 0
    last_up_time = 0
    last_stop_time = 0

    audio_stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
        #,input_device_index=4
    )

    audio_generator = (audio_stream.read(1024) for _ in range(0, int(16000 / 1024 * 60 * 5)))  # 5 minutes duration


    requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

    #phone_call, command_and_search
    config = speech.StreamingRecognitionConfig(
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            #language_code='en-US',
            language_code='he-IL',  # Hebrew language code
            use_enhanced=True,
            #model='command_and_search'  # Using the command_and_search model
            #model='phone_call'  # Optimizing for phone call audio
        ),
        interim_results=False
    )
    running_loop(result_queue, config, requests,  up_counter, stop_counter, last_up_time, last_stop_time)
    sleep(3)



if __name__ == '__main__':
    #check_and_kill_ffmpeg_process()
    #play_wav_mp3_for_a_text(['שמח'])
    #play_wav_mp3_for_a_text(['טוב'], None)
    #if play_wav_for_a_text_if_key_found('lonely',[' בודד', ' בודדה' ]  , None):
    #    print('found happy')
    #if play_wav_for_a_text_if_key_found('hello',['שלם'], None):
    #    print('found hello')
    #play_wav_for_a_key('sad', None)
    #play_audio('ask_mood.wav',None)
    #play_audio('happy',None)
    main()
