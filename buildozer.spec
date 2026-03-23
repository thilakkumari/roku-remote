[app]

# App metadata
title = Roku Remote
package.name = rokuremote
package.domain = com.yourname.rokuremote

# Entry point
source.dir = .
source.include_exts = py,kv,png,jpg,atlas
source.main = main.py

version = 1.0

# Python packages required by the app
# List every package your code imports — missing entries = ModuleNotFoundError on device
requirements = python3,kivy,requests,certifi,charset-normalizer,idna,urllib3

# Android permissions
# CHANGE_WIFI_MULTICAST_STATE is required for SSDP device discovery
android.permissions = INTERNET,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE,CHANGE_WIFI_MULTICAST_STATE

# Android settings
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Supported architectures (arm64-v8a covers most modern phones)
android.archs = arm64-v8a

# Screen orientation
orientation = portrait
fullscreen = 0

# Optional: app icon (uncomment and add icon.png to assets/ when ready)
# icon.filename = assets/icon.png


[buildozer]

# Set to 1 for verbose build output — very helpful for debugging build errors
log_level = 2

# Warn before running a potentially dangerous command
warn_on_root = 1
