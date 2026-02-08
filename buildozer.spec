title = Mobile Money
package.name = mobilemoney
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db
version = 1.0.0
requirements = python3,kivy==2.2.1,pillow,pandas,numpy,pygal,cairosvg,lxml
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #FFFFFF
