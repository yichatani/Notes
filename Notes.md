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

### 19. Ubuntu实时内核（RT Kernel）延迟调优

**环境：** Ubuntu + Linux 5.15.x PREEMPT_RT，用于机器人控制（1000Hz）

#### 问题症状

运行 `cyclictest` 后发现最大延迟（Max）高达 **16ms**，平均延迟也在 1.5ms 以上，不满足实时控制要求。

```
T: 0 P:99 I:1000  Min: 1217  Avg: 1633  Max: 16346   ← 异常
T: 1 P:99 I:1500  Min: 1196  Avg: 1539  Max:  8824
```

**根本原因：** CPU 频率调节器默认为 `powersave`，导致 CPU 频率动态变化，引入大量延迟抖动。

#### 诊断步骤

```bash
# 1. 确认是 PREEMPT_RT 内核（输出中应包含 PREEMPT_RT）
uname -a

# 2. 检查 CPU 频率调节器（问题状态：powersave，目标状态：performance）
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 3a. 初始诊断（不限时，手动 Ctrl+C 停止）
sudo cyclictest -p99 -t -i1000

# 3b. 完整基准测试（运行 30 秒，锁内存）
sudo cyclictest -p99 -t4 -i1000 -D 30s -m
```

#### 修复步骤

```bash
# Step 1：设置 CPU 为 performance 模式
# RT 内核没有对应的 linux-tools 包，直接用 sysfs
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $cpu
done

# Step 2：禁用深度 C-states（节能休眠状态，唤醒时引入延迟）
for state in /sys/devices/system/cpu/cpu*/cpuidle/state[1-9]/disable; do
    echo 1 | sudo tee $state 2>/dev/null
done

# Step 3：验证效果
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor  # 应输出 performance
sudo cyclictest -p99 -t4 -i1000 -D 30s -m                 # Max 应在个位数 µs
```

修复后结果：
```
T: 0 P:99 I:1000  Min: 1  Avg: 1  Max:  6   ← 正常
T: 1 P:99 I:1500  Min: 1  Avg: 1  Max:  4
```

#### 永久生效（重启后自动应用）

```bash
sudo tee /etc/systemd/system/rt-tuning.service << 'EOF'
[Unit]
Description=RT Kernel Tuning
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do echo performance > $f; done; for f in /sys/devices/system/cpu/cpu*/cpuidle/state[1-9]/disable; do echo 1 > $f 2>/dev/null; done'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable rt-tuning.service
sudo systemctl start rt-tuning.service

# 重启后验证
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor  # 应为 performance
sudo cyclictest -p99 -t4 -i1000 -D 10s -m                 # Max 应在个位数 µs
```

#### 延迟标准参考

| Max 延迟 | 评价 |
|----------|------|
| < 50 µs  | 优秀，适合机器人实时控制 |
| < 200 µs | 可用 |
| > 1 ms   | 需要排查 |
| > 5 ms   | 不可用 |

#### 其他可选优化（如仍有问题）

```bash
# 隔离 CPU 核心（在 /etc/default/grub 的 GRUB_CMDLINE_LINUX 中添加）
# isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3
# 然后：sudo update-grub && reboot，cyclictest 用 -a 2,3 指定隔离核

# 关闭超线程（HT）
echo off | sudo tee /sys/devices/system/cpu/smt/control

# 检查 SMI（周期性 8~16ms 尖峰可能是 BIOS 触发，内核无法屏蔽）
sudo turbostat --show smi --interval 1
# 若 SMI 频繁，在 BIOS 中禁用 ACPI Thermal、USB legacy 等功能

# 完整 GRUB 推荐参数
# GRUB_CMDLINE_LINUX="preempt=full threadirqs isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3 intel_idle.max_cstate=1 processor.max_cstate=1 nosoftlockup"
```

### 18. Set nvcc (CUDA Toolkit Path)
```bash
vim ~/.bashrc

# Add
export CUDA_HOME=/usr/local/cuda-12.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

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
