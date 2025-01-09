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

## Check if the key send successfully to SSH Agent
```sh
# launch SSH agent
eval "$(ssh-agent -s)"

# Add ED25519 private key to agent
ssh-add ~/.ssh/id_ed25519
```

```sh
ssh -vT git@github.com
```

## github upload files larger than 100mb
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

## fishros
```sh
wget http://fishros.com/install -O fishros && . fishros
```

## Error: ./license_checker: error while loading shared libraries: libcrypto.so.1.1: cannot open shared object file: No such file or directory
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
**This can be found in asking history of chatgpt.**
