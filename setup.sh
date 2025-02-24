echo "PLEASE ENSURE YOU RUN THIS FROM WITHIN counterpilot_onboard"

echo "INSTALLING PYENV BUILD DEPENDENCIES"
sudo apt update; sudo apt is
echo "SETTING UP ENVIRONMENT VIA PIP"
../.pyenv/versions/3.10.16/bin/pip install pillow==9.0
../.pyenv/versions/3.10.16/bin/pip install numpy==1.26.4 matplotlib==3.8.4 pandas==2.2.2
../.pyenv/versions/3.10.16/bin/pip install opencv-python==4.10.s0.84
../.pyenv/versions/3.10.16/bin/pip install python-osc

echo "SETTING UP PYENV PATH"
echo 'export PYENV_ROOT="$HsOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profiles
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init - bash)"' >> ~/.profile

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profileS
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile

echo "INSTALLING ADDITIONAL REQUIRED LIBRARIES"
sudo apt-get install -y libunwind-dev
sudo apt-get update
sudo apt-get install -y libc++-dev

sudo apt install libcap-dev libatlas-base-dev ffmpeg libopenjp2-7
sudo apt install libcamera-dev
sudo apt install libkms++-dev libfmt-dev libdrm-dev

../.pyenv/versions/3.10.16/bin/pip install --upgrade pip
../.pyenv/versions/3.10.16/bin/pip install wheel
../.pyenv/versions/3.10.16/bin/pip install rpi-camera rpi-kms picamera2

../.pyenv/versions/3.10.16/bin/pip install picamzero

