# HoloPortrait
Portrait photo to Hologram all-in-one script

## Hardware Requirements
- iPhone/iPad
- PC (only needed for the initial setup)
- [Looking Glass](https://lookingglassfactory.com) holographic display
- [USB-C Digital AV Multiport Adapter](https://www.apple.com/shop/product/MUF82AM/A/usb-c-digital-av-multiport-adapter) (other adapters might work as well, but YMMV)

## Software Requirements
### iOS
- [Pythonista](http://omz-software.com/pythonista/) app

### PC (only needed for the initial setup)
- [HoloPlay service](https://lookingglassfactory.com/software/holoplay-service)


## Setup
1) Connect the Looking Glass display to a PC with HoloPlay service installed and visit [https://eka.hn/calibration_test.html](https://eka.hn/calibration_test.html)
2) Copy the JSON block provided by the website and use it to replace the hardcoded calibration data at the beginning of `holoportrait.py`
3) Transfer `holoportrait.py` to Pythonista and run it with a Python 3.x interpreter
4) You will be asked to pick a Portrait photo that should be turned into a hologram. If you don't have a device capable of taking Portrait photos, you can download one of the sample photos provided in this repository: [Sample 1](https://github.com/jankais3r/HoloPortrait/raw/main/IMG_1820.HEIC) [Sample 2](https://github.com/jankais3r/HoloPortrait/raw/main/IMG_2053.HEIC)
5) All newly created holograms will be automatically saved into a special album called 'Looking Glass' in your Photos app.

![Demo](https://github.com/jankais3r/HoloPortrait/blob/main/demo.gif)

![Colormap demo](https://github.com/jankais3r/HoloPortrait/blob/main/demo_colormap.gif)

See it in action [here](https://twitter.com/jankais3r/status/1329924274686205952) and [here](https://twitter.com/jankais3r/status/1330567422865252352).

### Performance
- The script should work on any iPhone/iPad running at least iOS 13 and Pythonista 3.3
- Benchmarked devices:
    - iPad Air 2: 105s per hologram
    - iPad Pro 12.9" (2018): 31s per hologram
    - iPad Pro 11" (2020): 32s per hologram
    - iPhone 12 Pro: 28s per hologram
- Once the holograms are rendered and saved in the photo album, they can be instantly viewed at any time without the need to re-render them

## Inspiration
Looking Glass Factory ships their own tools for turning Portrait photos into holograms, but their setup unfortunately requires a computer to operate. See [Moments 3D](https://docs.lookingglassfactory.com/Moments3D/) and [Depth Media Player](https://docs.lookingglassfactory.com/DepthMediaPlayer/). When I found out that the latest iPads are capable of driving the Looking Glass holographic displays on their own, I decided to develop an iOS-only solution that does not rely on computers.
