import socket
import time
from typing import List

from .models import RokuDevice

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_REQUEST = (
    "M-SEARCH * HTTP/1.1\r\n"
    f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
    "MAN: \"ssdp:discover\"\r\n"
    "MX: 3\r\n"
    "ST: roku:ecp\r\n"
    "\r\n"
)


def _acquire_multicast_lock():
    """
    Android blocks UDP multicast by default. This acquires a MulticastLock
    at runtime so SSDP discovery can receive responses.
    On desktop (not Android), this is a no-op.
    """
    try:
        from jnius import autoclass
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        wifi_manager = PythonActivity.mActivity.getSystemService(Context.WIFI_SERVICE)
        lock = wifi_manager.createMulticastLock("roku_ssdp")
        lock.acquire()
        return lock
    except ImportError:
        return None  # Not on Android — skip silently


def discover_rokus(timeout: float = 5.0) -> List[RokuDevice]:
    """
    Broadcast an SSDP M-SEARCH and collect Roku ECP responses.
    Both phone and Roku must be on the same WiFi network.
    Returns a list of discovered RokuDevice objects.
    """
    lock = _acquire_multicast_lock()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)

        sock.sendto(SSDP_REQUEST.encode(), (SSDP_ADDR, SSDP_PORT))

        devices = {}
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                data, addr = sock.recvfrom(1024)
                response = data.decode(errors='ignore')

                if 'roku:ecp' not in response.lower():
                    continue

                ip = addr[0]
                if ip not in devices:
                    devices[ip] = RokuDevice(name=f"Roku @ {ip}", ip=ip)

            except socket.timeout:
                break

        sock.close()
        return list(devices.values())

    finally:
        if lock:
            lock.release()
