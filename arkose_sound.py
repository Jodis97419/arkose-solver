import speech_recognition as sr
import requests
import random
import time
import os

class Arkose(object):
    def __init__(self, pubkey, host):
        self.pubkey = pubkey
        self.host = host
        self.fulltoken = self.get_token()
        self.session_token = self.fulltoken.split('|')[0]

    def get_token(self):
        r = requests.post(f'https://client-api.arkoselabs.com/fc/gt2/public_key/{self.pubkey}', data={
            'bda': '',
            'public_key': self.pubkey,
            'site': 'https://' + self.host,
            'userbrowser': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
            'rnd': f'0.{random.choice("12334565789")}'
        })
        return r.json()['token']
    
    def get_audio(self):
        r = requests.get(f'https://client-api.arkoselabs.com/fc/get_audio/?session_token={self.session_token}&analytics_tier=40&r=us-east-1&game=1&language=en')
        open('payload.wav', 'wb').write(r.content)
    
    def recognize(self):
        r = sr.Recognizer()
        with sr.AudioFile('payload.wav') as s:
            data = r.record(s)
            raw = r.recognize_google(data)
            answer = ''
            for char in raw:
                if char.isdigit():
                    answer += char
            return answer

    def submit(self):
        r = requests.post('https://client-api.arkoselabs.com/fc/audio/',
            headers = {
                'authority': 'client-api.arkoselabs.com',
                'accept': '*/*',
                'cache-control': 'no-cache',
                'x-newrelic-timestamp': str(round(time.time())),
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://client-api.arkoselabs.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'accept-language': 'en-US,en;q=0.9'
            },
            data={
                'session_token': self.session_token,
                'language': 'en',
                'r': 'us-east-1',
                'audio_type': '2',
                'response': self.recognize(),
                'analytics_tier': '40'
            })
        print(r.text)
        if r.json()['response'] == 'correct':
            return True
        return False
    
    def run(self):
        while True:
            try:
                self.get_audio()
                if self.submit():
                    os.remove('payload.wav')
                    return self.fulltoken
                    break
            except:
                pass