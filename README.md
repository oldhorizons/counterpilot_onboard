# Overview
This project implements the [PyPupilEXT](https://github.com/openPupil/PyPupilEXT) library with wrappers for OSC communication, NDI stream interfacing, visualisation, some algorithm changes, and (ideally) easier setup on mac. 

It also includes some support for pupil detection onboard a raspberry pi 5 running Bookworm, but that's extremely not recommended. I've left the code in there in case there ends up being a use case, but it's super slow and the installation is incredibly fragile. This just seems to be the case for working on Pis in general.

# Getting Started
## Mac
- Run setup_mac.sh from within the repository folder. You should then be able to simply run app.py.
- Change the values in appConstants.py to configure things like NDI stream name, tolerance hyperparameters, and target OSC address.
- Changing the NDI stream name to None (no quotation marks) will cause the program to connect to the first available NDI stream.

## Raspberry Pi (NDI streaming)
- starting with a fresh install of raspberry pi os
- see RPI streaming options

## Raspberry Pi (onboard)
- run pi-onboard-setup.sh
- good luck.

# IMPROVEMENTS
- multi-camera implementation
- threading (for multi-cam)
- get NDI streaming working from the pi T_T

# RPI STREAMING OPTIONS - NONE FOUND TO WORK (YET)
- [Via HTTP](https://raspberrypi.stackexchange.com/questions/23182/how-to-stream-video-from-raspberry-pi-camera-and-watch-it-live)
- [Via NDI: Bookworm OS (latest)](https://github.com/SBCV-apegram/RasPi-NDI-HDMI?tab=readme-ov-file)
    - as far as I can tell this doesn't work on the pi 5. No errors come up, it just doesn't create an NDI stream.
- [Via NDI: Bullseye OS (earlier)](https://github.com/raspberry-pi-camera/raspindi)
- [Via NDI: Dicaffeine](https://dicaffeine.com/)
- [Via NDI: NDI SDK](https://community.ptzoptics.com/s/article/NDI-Discovery-Server-on-a-Raspberry-Pi)
- it may be that these ^ libraries are made to work on pi 3s / bullseye - I couldn't find a specific pi / os combination that was guaranteed to work for any. I tried Dicaffeine on pi 4 and 5 with 64-bit bookworm, and the git repository for bookworm os on pi 4 and 5, with no luck (and, annoyingly, no error message.)