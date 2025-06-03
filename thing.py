from machine import Pin, PWM
import uasyncio as asyncio
import time
import sys

# Setup buzzers (GPIO 1–4)
buzzers = [PWM(Pin(i)) for i in range(1, 5)]

# Change this to speed up or slow down playback
TEMPO_SCALE = 500.0  # 1.0 = normal speed, 0.5 = twice as fast, 2.0 = half speed

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
        # Wait until global sync time
        now = time.ticks_us()
        wait_us = time.ticks_diff(start_time, now)
        if wait_us > 0:
            await asyncio.sleep(wait_us / 1_000_000)

        with open(filename) as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 2:
                    continue

                try:
                    freq = float(parts[0])
                    raw_duration = float(parts[1]) * TEMPO_SCALE
                    duration = max(raw_duration, 0.002)  # enforce at least 2ms delay

                except ValueError:
                    continue  # skip malformed lines

                play_note(buzzer, freq)
                await asyncio.sleep(duration)
                stop_note(buzzer)

        stop_note(buzzer)

    except Exception as e:
        print(f"⚠️ Error playing {filename}: {e}")
        sys.print_exception(e)

async def main():
    # Sync start time ~2 seconds into the future
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
    sys.print_exception(e)
