from machine import Pin, PWM
import uasyncio as asyncio
import time

# Setup buzzers
buzzers = [PWM(Pin(i)) for i in range(1, 5)]

TICKS_PER_BEAT = 480
DEFAULT_TEMPO = 500000

def ticks_to_seconds(ticks, tempo):
    return (tempo / 1_000_000) * (ticks / TICKS_PER_BEAT)

def play_note(buzzer, freq):
    if freq > 0:
        buzzer.freq(int(freq))
        buzzer.duty_u16(32768)
    else:
        buzzer.duty_u16(0)

def stop_note(buzzer):
    buzzer.duty_u16(0)

async def play_melody_from_raw(buzzer, filename, start_time):
    try:
        with open(filename) as f:
            lines = f.readlines()

        current_tick = 0
        tempo = DEFAULT_TEMPO

        # 🛑 WAIT until the synchronized start time
        now = time.ticks_us()
        wait_us = time.ticks_diff(start_time, now)
        if wait_us > 0:
            await asyncio.sleep(wait_us / 1_000_000)  # Convert microseconds to seconds

        for line in lines:
            parts = line.strip().split(",")
            if len(parts) < 3:
                continue

            event_type = parts[2].strip()

            if event_type == "Header":
                TICKS_PER_BEAT = int(parts[5])

            elif event_type == "Tempo":
                tempo = int(parts[3])

            elif event_type == "Note_on_c":
                track = int(parts[0])
                tick = int(parts[1])
                channel = int(parts[3])
                note = int(parts[4])
                velocity = int(parts[5])

                delta_ticks = tick - current_tick
                if delta_ticks > 0:
                    delay = ticks_to_seconds(delta_ticks, tempo)
                    await asyncio.sleep(delay)

                current_tick = tick

                if velocity > 0:
                    freq = 440.0 * (2.0 ** ((note - 69) / 12))
                    play_note(buzzer, freq)
                else:
                    stop_note(buzzer)

    except Exception as e:
        print(f"⚠️ Error playing {filename}: {e}")

async def main():
    start_time = time.ticks_add(time.ticks_us(), 2_000_000)

    await asyncio.gather(
        play_melody_from_raw(buzzers[0], "melody1.csv", start_time),
        play_melody_from_raw(buzzers[1], "melody2.csv", start_time),
        play_melody_from_raw(buzzers[2], "melody3.csv", start_time),
        play_melody_from_raw(buzzers[3], "melody4.csv", start_time)
    )

try:
    asyncio.run(main())
except Exception as e:
    print("⚡ Error during execution:", e)

