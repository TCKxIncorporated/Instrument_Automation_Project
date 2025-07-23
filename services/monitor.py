from datetime import datetime, timedelta
import time
from collections import deque
import threading

# Single monitor thread, dynamic channel selection
monitoring_active = False
_monitor_thread = None
current_channel = 1  # defaults to channel 1

# per-channel historical buffers (last 5 minutes)
voltage_data = {1: deque(maxlen=300), 2: deque(maxlen=300), 3: deque(maxlen=300)}
time_data    = {1: deque(maxlen=300), 2: deque(maxlen=300), 3: deque(maxlen=300)}


def _monitor_loop(instrument, connected):
    """
    Internal loop: polls the currently selected channel once per second,
    storing up to the last 5 minutes of data.
    """
    global monitoring_active
    while monitoring_active:
        try:
            if instrument and connected:
                # read the dynamic channel
                ch = current_channel
                instrument.write(f"INST:NSEL {ch}")
                raw = instrument.query("MEAS:VOLT?").strip()
                v = float(raw)
                now = datetime.now()

                voltage_data[ch].append(v)
                time_data[ch].append(now)

                # expire older than 5 minutes
                cutoff = now - timedelta(minutes=5)
                buf_time = time_data[ch]
                buf_volt = voltage_data[ch]
                while buf_time and buf_time[0] < cutoff:
                    buf_time.popleft()
                    buf_volt.popleft()
        except Exception as e:
            print(f"[MONITOR ERROR] {e}")
        time.sleep(1)


def start_monitoring(instrument, connected=True):
    """
    Start the single monitor thread. Subsequent calls are no-ops.
    """
    global monitoring_active, _monitor_thread
    if monitoring_active:
        return
    monitoring_active = True
    _monitor_thread = threading.Thread(
        target=_monitor_loop,
        args=(instrument, connected),
        daemon=True
    )
    _monitor_thread.start()


def stop_monitoring():
    """
    Stop the monitor thread (graceful shutdown).
    """
    global monitoring_active
    monitoring_active = False


def set_channel(ch: int):
    """
    Change the channel being monitored. Clears historical data.
    """
    global current_channel
    current_channel = ch
    clear_data()


def clear_data():
    """
    Clear all stored samples for all channels.
    """
    for dq in voltage_data.values():
        dq.clear()
    for dq in time_data.values():
        dq.clear()


def get_latest_reading():
    """
    Return the most recent sample for the current channel,
    as primitives ready for protobuf or JSON.
    """
    ch = current_channel
    buf_t = time_data[ch]
    buf_v = voltage_data[ch]
    if not buf_t or not buf_v:
        raise ValueError(f"no data for channel {ch}")
    t = buf_t[-1]
    v = buf_v[-1]
    # epoch seconds as int64
    return {"time": int(t.timestamp()), "voltage": v, "channel": ch}
