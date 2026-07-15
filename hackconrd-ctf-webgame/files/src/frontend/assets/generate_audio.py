import wave
import struct
import math

def generate_beep(filename, freq=440.0, duration=0.1, volume=32767.0):
    sample_rate = 44100.0
    with wave.open(filename, 'w') as wavef:
        wavef.setnchannels(1)
        wavef.setsampwidth(2)
        wavef.setframerate(int(sample_rate))
        for i in range(int(duration * sample_rate)):
            value = int(volume * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
            data = struct.pack('<h', value)
            wavef.writeframesraw(data)

# Generate a coin pickup sound (high pitch, short)
generate_beep("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/coin.wav", freq=880.0, duration=0.1)

# Generate an error/bump sound (low pitch)
generate_beep("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/error.wav", freq=220.0, duration=0.15)
