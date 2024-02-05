
# environment and interpreter
sudo apt install python3.7-minimal 
sudo apt install python3.7-venv 

python3.7 -m venv env

source env/bin/activate 

pip install --upgrade pip setuptools wheel 
pip install docker redis 
pip --no-cache-dir install torch==1.12.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu 
pip install tensorboard six
