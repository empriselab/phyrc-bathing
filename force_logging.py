import serial
import threading
import sys
import time

SERIAL_PORT = '/dev/ttyACM1'
BAUD_RATE = 9600
# log file names with current date and time
LOG_FILE = f'arduino_log_{time.strftime("%Y%m%d_%H%M%S")}.txt'

# log summary file with current date and time
SUMMARY_FILE = f'summary_{time.strftime("%Y%m%d_%H%M%S")}.txt'

recording = False
running = True

def read_serial(ser, stats):
    with open(LOG_FILE, 'w') as f:
        while running:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                print(line)
                if recording:
                    try:
                        value = float(line)
                        f.write(f"{value}\n")
                        f.flush()
                        if value > 0:
                            stats['total'] += 1
                            if value < 20:
                                stats['below_20'] += 1
                    except ValueError:
                        pass  # Ignore non-numeric lines

def main():
    global recording, running
    stats = {'total': 0, 'below_20': 0}

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"Failed to open serial port: {e}")
        sys.exit(1)

    print("Connected to Arduino.")
    print("Press 'r' to start recording, 's' to stop, 'q' to quit.")

    t = threading.Thread(target=read_serial, args=(ser, stats), daemon=True)
    t.start()

    try:
        while True:
            cmd = input().strip().lower()
            if cmd == 'r':
                ser.write(b'r')
                recording = True
                print("[Recording started]")
            elif cmd == 's':
                ser.write(b's')
                recording = False
                print("[Recording stopped]")
            elif cmd == 'q':
                ser.write(b's')
                running = False
                break
    except KeyboardInterrupt:
        running = False
    finally:
        ser.close()
        print("Serial port closed.")

        # Calculate and write summary
        if stats['total'] > 0:
            percent = 100.0 * stats['below_20'] / stats['total']
        else:
            percent = 0.0

        with open(SUMMARY_FILE, 'w') as sf:
            sf.write(f"Percentage of force readings > 0 N that were < 20 N: {percent:.2f}%\n")
            sf.write(f"Total valid samples: {stats['total']}\n")

        print(f"Saved summary to {SUMMARY_FILE}\nExiting...")

if __name__ == '__main__':
    main()