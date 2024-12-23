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

