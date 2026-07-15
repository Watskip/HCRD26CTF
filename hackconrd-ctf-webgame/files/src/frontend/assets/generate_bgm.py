import wave, struct, math

def generate_cyber_loop(filename):
    sample_rate = 44100
    bpm = 130
    beat_duration = 60.0 / bpm
    sixteenth = beat_duration / 4.0
    
    # Bassline notes frequencies: D2(73.42), F2(87.31), C2(65.41), A#1(58.27)
    # A classic dark synthwave progression
    seq = [73.42]*4 + [87.31]*4 + [65.41]*4 + [58.27]*4
    
    with wave.open(filename, 'w') as wavef:
        wavef.setnchannels(1)
        wavef.setsampwidth(2)
        wavef.setframerate(sample_rate)
        
        # Loop the sequence 4 times to make a slightly longer file
        for _ in range(4):
            for idx, freq in enumerate(seq):
                for i in range(int(sixteenth * sample_rate)):
                    # Sawtooth wave
                    period = sample_rate / freq
                    val = 2.0 * (i % period) / period - 1.0
                    
                    # Kick drum effect on the first beat of every 4
                    kick = 0
                    if idx % 4 == 0:
                        kick_env = math.exp(-15.0 * i / sample_rate)
                        kick_freq = 150.0 * kick_env
                        kick_period = sample_rate / max(kick_freq, 1.0)
                        kick = math.sin(2.0 * math.pi * i / kick_period) * kick_env * 1.5
                    
                    # Synth Envelope (decay)
                    env = math.exp(-4.0 * i / (sixteenth * sample_rate))
                    
                    # Combine kick and bass
                    combined = (val * env * 0.6) + kick
                    
                    # Clip to prevent distortion
                    combined = max(min(combined, 1.0), -1.0)
                    
                    value = int(15000 * combined)
                    wavef.writeframesraw(struct.pack('<h', value))

generate_cyber_loop("/home/leury/Desktop/ctf/hackconrd-ctf-webgame/files/src/frontend/assets/bgm.wav")
