from datetime import datetime, timedelta
import time
from collections import deque
import threading

monitoring_active = False
monitoring_thread = None

voltage_data = {1: deque(maxlen=100), 2: deque(maxlen=100), 3: deque(maxlen=100)}
time_data    = {1: deque(maxlen=100), 2: deque(maxlen=100), 3: deque(maxlen=100)}

def monitor_voltage(instrument, current_channel, connected):
    global monitoring_active
    while monitoring_active:
        try:
            if instrument and connected:
                instrument.write(f"INST:NSEL {current_channel}")
                voltage = float(instrument.query("MEAS:VOLT?").strip())

                now = datetime.now()
                voltage_data[current_channel].append(voltage)
                time_data[current_channel].append(now)

                # expire old points
                cutoff = now - timedelta(minutes=5)
                while time_data[current_channel] and time_data[current_channel][0] < cutoff:
                    time_data[current_channel].popleft()
                    voltage_data[current_channel].popleft()

        except Exception as e:
            print(f"[MONITOR ERROR] {e}")
        time.sleep(1)

def start_monitoring(instr, channel, connected):
    global monitoring_active,_monitor_thread
    # kill any existing loop first
    if monitoring_active:
      monitoring_active = False
      _monitor_thread.join()
    # now start fresh
    monitoring_active = True
    _monitor_thread = threading.Thread(target=monitor_voltage, args=(instr,channel,connected), daemon=True)
    _monitor_thread.start()


def stop_monitoring():
    global monitoring_active
    monitoring_active = False

def clear_data():
    for ch in voltage_data:
        voltage_data[ch].clear()
        time_data[ch].clear()


def get_latest_reading(channel):
    if not time_data[channel] or not voltage_data[channel]:
        raise ValueError(f"no data for channel {channel}")
    t = time_data[channel][-1]
    v = voltage_data[channel][-1]
    return {
        "time": int(t.timestamp()),
        "voltage": v,
        "channel": channel
    }