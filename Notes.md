## I. Python tips: 

### 8. Force Python to use only the env site-packages
```bash
# Write the code below in the activate file.
# Backup the original PYTHONPATH
export OLD_PYTHONPATH=$PYTHONPATH

# Force Python to use only dp3_env's site-packages
export PYTHONPATH=/home/ani/reinflow_env/lib/python3.8/site-packages

echo "PYTHONPATH set to reinflow_env."

export CUDA_HOME=/usr/local/cuda-11.8
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

### 7. Create a venv environment
```bash
python -m venv latent_env
```

### 6. Output env requirements.txt
```bash
pip freeze > requirements.txt
```

### 5. Isolate env, write the code below in the activate file
```bash
export PYTHONNOUSERSITE=1
export PYTHONPATH=""
```

### 4. python_env: as a way to isolate the env
```bash
vim ~/.bashrc
alias python_env="PYTHONPATH=/home/ani/policy_env/lib/python3.10/site-packages:$PYTHONPATH /home/ani/policy_env/bin/python"
```
```python
python_env scripts.py
```

### 3. tmux
```python
tmux new -s newsession
tmux attach -t newsession

tmux new -s bert_bin -d "python main.py --model bert --binary --epochs 3"
tmux new -s bert_ag  -d "python main.py --model bert --epochs 2"
tmux new -s gru_bin  -d "python main.py --model gru --binary --epochs 6"
tmux new -s gru_ag   -d "python main.py --model gru --epochs 8"

tmux ls
tmux attach -t bert_bin
tmux kill-session -t bert_bin
```

### 2. Reinforce updating to a new version regardless of the outside
```python
source /home/ani/policy_env/bin/activate
pip install --upgrade pip
pip install --upgrade --force-reinstall --no-cache-dir plotly
```

### 1. Clean sys path
```python
import sys
sys.path = [p for p in sys.path if "isaac-sim" not in p]
```

---


## II. Other Notes:

### 17. Downgrade huggingface version
```bash
pip install huggingface_hub==0.10.0
```

### 16. FRANKA Static IP wirse
```bash
# You can connect to the Internet via WiFi and control Franka via a wired connection.
# Your computer has two network interfaces:
# wlo1 → wireless network card (WiFi, for internet access)
# enp5s0 → wired network card (connected to the Franka control cabinet)
# The problem is:
# When a system has two networks, Linux will default to one "default route," potentially ignoring the other.
# So, we need to tell the system:
# Internet traffic should go via WiFi;
# Traffic destined for Franka (172.16.0.2) should go via the wired network.

# 1. Make sure your WiFi is connected (Internet access)
nmcli radio wifi on

# 2. Manually configure a static IP for the wired network card (if not already configured)
sudo nmcli con add type ethernet ifname enp5s0 con-name franka \ ipv4.addresses 172.16.0.1/24 ipv4.method manual autoconnect yes

# 3. Start the connection
sudo nmcli con up franka

# 4. Add a static route to the Franka network segment
sudo ip route add 172.16.0.0/24 dev enp5s0

# 5. Check
ip route

# 6. Permanently (Exists when restart.)
sudo nmcli connection modify franka +ipv4.routes "172.16.0.0/24 0.0.0.0"
sudo nmcli connection up franka
```

### 15. LIBERO rendering problem
```bash
# change mujoco version
mujoco 2.3.7 -> 3.3.6
```

### 14. Github
```bash
git fetch origin
git checkout -b branch
git diff main origin/main
git add .
git commit -m "Messages."
git push
git push origin branch

git remote remove origin
git remote add origin https://huggingface.co/datasets/yichat/smol-libero

git pull
git pull origin branch
```

### 13. Hugging Face
```bash
hf auth login
hf auth logout
hf auth whoami
hf repo create my_smolvla --type=model

hf upload yichat/my_smolvla .

hf repo create yichat/smol-libero --repo-type dataset
cd ~/smol-libero
git init
git lfs install
git remote add origin https://huggingface.co/datasets/yichat/smol-libero
git checkout -b v2.1
git add .
git commit -m "upload smol-libero v2.1 dataset"
git push origin v2.1
```

### 12. Compress Video and PDF files

```bash
# Video
ffmpeg -i icra_pre.mp4 -vcodec libx264 -crf 18 -preset slow -acodec aac icra_video.mp4

# PDF
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dDownsampleColorImages=false \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=3D_LOT_nodownsample.pdf 3D_LOT.pdf
```

### 11. Solve the problem of github account name error

```bash
# global
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

# local 
git config user.name "Your Name"
git config user.email "your_email@example.com"

git commit --amend --reset-author
```

<img src="./images/account_error.png" alt="account_error" width="400"/>


### 10. Can't find device for rendering
Update and change nvidia driver to solve it. 


### 9. linux ln modulefinder.py to env
```python
ln -s /home/ani/.local/share/ov/pkg/isaac-sim-4.2.0/kit/python/lib/python3.10/modulefinder.py \
      /home/ani/isaac_env/lib/python3.10/modulefinder.py
```

### 8. Create ssh key
```sh
ls -al ~/.ssh
```
```sh
ssh-keygen -t ed25519 -C "yichatma@gmail.com"
```
```sh
cat ~/.ssh/id_ed25519.pub
```

### 7. Test the SSH connection
```sh
ssh -T git@github.com
```

### 6. Check if the key is sent successfully to the SSH Agent
```sh
# launch SSH agent
eval "$(ssh-agent -s)"

# Add ED25519 private key to agent
ssh-add ~/.ssh/id_ed25519
```

```sh
ssh -vT git@github.com
```

### 5. github upload files larger than 100mb
```sh
# use Git LFS
sudo apt-get install git-lfs
```
```sh
git lfs install
git lfs track "*.zip"
git add .gitattributes
git add path/to/your/largefile.zip
git commit -m "Add large file with Git LFS"
git push origin main
```

### 4. fishros
```sh
wget http://fishros.com/install -O fishros && . fishros
```

### 3. Error: ./license_checker: error while loading shared libraries: libcrypto.so.1.1: cannot open shared object file: No such file or directory
 ```sh
ldd ./license_checker
```
make sure the openssl version is right
```sh
wget https://www.openssl.org/source/openssl-1.1.1u.tar.gz
tar -xzf openssl-1.1.1u.tar.gz
cd openssl-1.1.1u
./config
make
sudo make install
# check
/usr/local/bin/openssl version
```
Don't forget to check the symbolic link.
**This can be found in asking the history of ChatGPT.**


### 2. The path to put .vscode for Isaac
```sh
[INFO] Setting up vscode settings...
[WARN] Could not find Isaac Sim VSCode settings: /home/ani/anaconda3/envs/any_isaac/lib/python3.10/site-packages/isaacsim/.vscode/settings.json.
	This will result in missing 'python.analysis.extraPaths' in the VSCode
	settings, which limits the functionality of the Python language server.
	However, it does not affect the functionality of the Isaac Lab project.
	We are working on a fix for this issue with the Isaac Sim team.
```

### 1. Disable Auto-Activation of the Base Environment
```sh
conda config --set auto_activate_base false
```
----

```sh
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:~/ur_grasp_driver/yc_ws/install/my_ur_driver/share
```

