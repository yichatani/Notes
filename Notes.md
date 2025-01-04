## CREATE SSH KEY:
```sh
ls -al ~/.ssh
```
```sh
ssh-keygen -t ed25519 -C "yichatma@gmail.com"
```
```sh
cat ~/.ssh/id_ed25519.pub
```

## TEST SSH CONNECTION
```sh
ssh -T git@github.com
```

## 检查密钥是否已经正确添加到 SSH Agent
```sh
# 启动 SSH agent
eval "$(ssh-agent -s)"

# 添加 ED25519 私钥到 agent
ssh-add ~/.ssh/id_ed25519
```

```sh
ssh -vT git@github.com
```

## github上传大于100mb文件
```sh
# 使用 Git LFS
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
