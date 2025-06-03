import mido
import csv

def convert_midi_to_csv(midi_filename, csv_filename):
    midi = mido.MidiFile(midi_filename)

    tempo = 500000  # default tempo in µs per beat
    ticks_per_beat = midi.ticks_per_beat
    current_time = 0

    events = []
    note_start_times = {}
    last_event_time = 0

    def ticks_to_seconds(ticks, tempo):
        return mido.tick2second(ticks, ticks_per_beat, tempo)

    for msg in midi:
        current_time += ticks_to_seconds(msg.time, tempo)

        if msg.type == 'set_tempo':
            tempo = msg.tempo

        elif msg.type == 'note_on' and msg.velocity > 0:
            # Add a rest if needed
            if current_time - last_event_time > 0.001:
                rest = round(current_time - last_event_time, 5)
                events.append((0, rest))

            note_start_times[msg.note] = current_time
            last_event_time = current_time  # advance time to start of note

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in note_start_times:
                note_on_time = note_start_times.pop(msg.note)
                duration = round(current_time - note_on_time, 5)

                if duration > 0.001:
                    freq = round(440.0 * (2.0 ** ((msg.note - 69) / 12)), 2)
                    events.append((freq, duration))
                    last_event_time = current_time

    # Write to CSV
    with open(csv_filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["frequency", "duration"])
        for freq, dur in events:
            writer.writerow([freq, dur])

    print(f"✅ Saved {csv_filename}")


# Batch convert MIDI files
for i in range(1, 5):
    midi_file = f"melody{i}.mid"
    csv_file = f"melody{i}.csv"
    convert_midi_to_csv(midi_file, csv_file)

print("\n✅✅ All 6 MIDI files converted to CSVs!")
