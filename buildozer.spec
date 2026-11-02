[app]
title = German Video Creator
package.name = germanvideocreator
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3==3.11.9,hostpython3==3.11.9,kivy,pillow,gtts,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a


[buildozer]
log_level = 2
warn_on_root = 1
