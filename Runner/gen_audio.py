import wave, struct, math, os

def generate_tone(filename, freq=440.0, duration=0.1, volume=16000, wave_type="sine"):
    sample_rate = 44100
    with wave.open(filename, 'w') as wavef:
        wavef.setnchannels(1)
        wavef.setsampwidth(2)
        wavef.setframerate(sample_rate)
        
        for i in range(int(duration * sample_rate)):
            if wave_type == "sine":
                val = math.sin(2.0 * math.pi * freq * (i / sample_rate))
            elif wave_type == "square":
                val = 1.0 if math.sin(2.0 * math.pi * freq * (i / sample_rate)) > 0 else -1.0
            elif wave_type == "saw":
                period = sample_rate / freq
                val = 2.0 * (i % period) / period - 1.0
            elif wave_type == "noise":
                import random
                val = random.uniform(-1.0, 1.0)
            
            # Envelope (decay)
            env = math.exp(-3.0 * i / (duration * sample_rate))
            
            value = int(volume * val * env)
            wavef.writeframesraw(struct.pack('<h', value))

def generate_bgm(filename):
    sample_rate = 44100
    # Synthwave driving bass
    seq = [65.41, 65.41, 65.41, 73.42, 87.31, 87.31, 87.31, 58.27]
    duration_per_note = 0.2
    
    with wave.open(filename, 'w') as wavef:
        wavef.setnchannels(1)
        wavef.setsampwidth(2)
        wavef.setframerate(sample_rate)
        
        for _ in range(8): # Loop
            for idx, freq in enumerate(seq):
                for i in range(int(duration_per_note * sample_rate)):
                    # Sawtooth
                    period = sample_rate / max(freq, 1)
                    val = 2.0 * (i % period) / period - 1.0
                    env = math.exp(-2.0 * i / (duration_per_note * sample_rate))
                    
                    # Kick on every 2nd note
                    kick = 0
                    if idx % 2 == 0:
                        kick_env = math.exp(-15.0 * i / sample_rate)
                        kick = math.sin(2.0 * math.pi * i / (sample_rate / max(100.0 * kick_env, 1.0))) * kick_env * 1.5
                    
                    combined = max(min((val * env * 0.5) + kick, 1.0), -1.0)
                    value = int(15000 * combined)
                    wavef.writeframesraw(struct.pack('<h', value))

base_dir = "/home/leury/Desktop/ctf/hackconrd-ctf-runner/src/assets"
os.makedirs(base_dir, exist_ok=True)

# Jump sound (quick rise)
generate_tone(os.path.join(base_dir, "jump.wav"), freq=400.0, duration=0.15, wave_type="sine")

# Crash sound (noise)
generate_tone(os.path.join(base_dir, "crash.wav"), freq=100.0, duration=0.4, wave_type="noise")

# BGM
generate_bgm(os.path.join(base_dir, "bgm.wav"))
