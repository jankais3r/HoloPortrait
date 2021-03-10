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
- Internet connection required for the first run. Subsequent usage is possible offline.

### PC (only needed for the initial setup)
- [HoloPlay service](https://lookingglassfactory.com/software/holoplay-service)


## Setup
1) Connect the Looking Glass display to a PC with HoloPlay service installed and visit [https://eka.hn/calibration_test.html](https://eka.hn/calibration_test.html)
2) Copy the JSON block provided by the website and use it to replace the hardcoded calibration data on [row 51](https://github.com/jankais3r/HoloPortrait/blob/main/HoloPortrait.py#L51) of `HoloPortrait.py`
3) Transfer `HoloPortrait.py` to Pythonista and run it with a Python 3.x interpreter
4) You will be asked to pick a photo that should be turned into a hologram. If you choose a photo that does not contain a depth map, the depth map will be automatically inferred using a machine learning model. This happens locally on your device, no data is ever sent anywhere.
5) You can disable the ML inferrence by editing [row 81](https://github.com/jankais3r/HoloPortrait/blob/main/HoloPortrait.py#L81) of `HoloPortrait.py`. In this mode you will be allowed to choose only from Portrait photos. If you don't own a device capable of taking Portrait photos, you can download one of the sample photos provided in this repository: [Sample 1](https://github.com/jankais3r/HoloPortrait/raw/main/IMG_1820.HEIC) [Sample 2](https://github.com/jankais3r/HoloPortrait/raw/main/IMG_2053.HEIC)

![Demo](https://github.com/jankais3r/HoloPortrait/blob/main/demo_v2.gif)

![Colormap demo](https://github.com/jankais3r/HoloPortrait/blob/main/demo_colormap.gif)

See it in action [here](https://twitter.com/jankais3r/status/1347337347621400579).

## Legacy version
This is a second generation of HoloPortrait, made possible thanks to the [driverless-HoloPlay.js](https://github.com/jankais3r/driverless-HoloPlay.js) library and [iOS-LookingGlass](https://github.com/jankais3r/iOS-LookingGlass) browser. It performs 30x faster than the first generation and it offers additional improvements like switching between Mesh and Pointcloud modes. To read more about the Legacy version of the script, see [README_legacy.md](https://github.com/jankais3r/HoloPortrait/blob/main/README_legacy.md).

## Credits
The Mesh code is based on a Custom Geometry example by [threejsfundamentals.org](https://threejsfundamentals.org/threejs/lessons/threejs-custom-geometry.html).
