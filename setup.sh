echo "PLEASE ENSURE YOU RUN THIS FROM WITHIN counterpilot_onboard"

echo "INSTALLING DEV REQUIREMENTS"
sudo apt install gh
git config --global user.email "newbrainspace@gmail.com"
git config --global user.name "Michelle Sands"
gh auth login
# generate personal access token here: https://github.com/settings/tokens

echo "INSTALLING PYENV BUILD DEPENDENCIES"
sudo apt update; sudo apt install build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

echo "INSTALLING PYENV"
curl -fsSL https://pyenv.run | bash

echo "SETTING UP PYENV PATH"
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profiles
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init - bash)"' >> ~/.profile

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profileS
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile

exec $SHELL

pyenv install 3.10
pyenv global 3.10

echo "SETTING UP ENVIRONMENT VIA PIP"
pip install pillow==9.0
pip install numpy==1.26.4 matplotlib==3.8.4 pandas==2.2.2
pip install opencv-python==4.10.0.84
pip install python-osc

sudo apt install python3-picamzero

echo "INSTALLING ADDITIONAL REQUIRED LIBRARIES"
sudo apt-get install -y libunwind-dev
sudo apt-get update
sudo apt-get install -y libc++-dev

sudo apt install libcap-dev libatlas-base-dev ffmpeg libopenjp2-7
sudo apt install libcamera-dev
sudo apt install libkms++-dev libfmt-dev libdrm-dev

pip install --upgrade pip
pip install wheel
pip install picamera2 rpi-libcamera
pip install rpi-kms

pip install picamzero

