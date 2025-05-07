import mido
import csv

def convert_midi_to_csv(midi_filename, csv_filename):
    midi = mido.MidiFile(midi_filename)

    tempo = 500000  # default tempo (μs per beat)
    ticks_per_beat = midi.ticks_per_beat
    current_time = 0
    last_event_time = 0

    events = []

    def ticks_to_seconds(ticks, tempo):
        return mido.tick2second(ticks, ticks_per_beat, tempo)

    for msg in midi:
        delta_time_sec = ticks_to_seconds(msg.time, tempo)
        current_time += delta_time_sec

        if msg.type == 'set_tempo':
            tempo = msg.tempo

        elif msg.type == 'note_on' and msg.velocity > 0:
            if current_time - last_event_time > 0:
                rest_duration = round(current_time - last_event_time, 3)
                events.append((0, rest_duration))
            freq = round(440.0 * (2.0 ** ((msg.note - 69) / 12)), 2)
            events.append((freq, 0))  
            last_event_time = current_time

        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            if events and events[-1][1] == 0:
                freq, _ = events.pop()
                note_duration = round(current_time - last_event_time, 3)
                events.append((freq, note_duration))
                last_event_time = current_time

    with open(csv_filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["frequency", "duration"])
        for freq, dur in events:
            writer.writerow([freq, dur])

    print(f"✅ Saved {csv_filename}")


for i in range(1, 7):
    midi_file = f"melody{i}.mid"
    csv_file = f"melody{i}.csv"
    convert_midi_to_csv(midi_file, csv_file)

print("\n✅✅ All 6 MIDI files converted to CSVs!")
