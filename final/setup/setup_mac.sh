echo "INSTALLING BREW AND PYENV"
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
#TODO find the post-install commands and run them as well

brew install pyenv
#https://github.com/pyenv/pyenv?tab=readme-ov-file#b-set-up-your-shell-environment-for-pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
exec "$SHELL"

pyenv install 3.10
pyenv local 3.10

python -m venv env
source env/bin/activate

pip install pillow==9.0
pip install numpy==1.26.4 matplotlib==3.8.4 pandas==2.2.2
pip install opencv-python==4.10.0.84
pip install python-osc
pip install cyndilib
curl https://github.com/openPupil/PyPupilEXT/releases/download/v0.0.1-beta/PyPupilEXT-0.0.1-cp310-cp310-macosx_14_0_universal2.whl
pip install PyPupilEXT-0.0.1-cp310-cp310-macosx_14_0_universal2.whl

pip install ndi-python
# pip install typing_extensions click