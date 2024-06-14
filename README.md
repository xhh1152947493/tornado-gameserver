# tornado_server
基于tornado搭建的小游戏服务端
- 程序为单线程的,如果一个请求阻塞了会导致所有的http请求都阻塞[避免耗时的数据库操作,我们需要的就是单线程顺序的数据库操作]
- 客户端->服务器的http请求是异步的,由tornado把网络连接加入到队列中,等待事件处理时间到达后处理
- 在一个请求里面，服务器可以通过async来异步进行网络http请求。避免网络阻塞卡顿。

ps：类名和函数名统一用大驼峰命名法把，局部变量用小驼峰，以类型前缀开头。成员变量以m_开头。不对外暴露的私有函数可以以
_+小驼峰的形式命名。不对外暴露的局部变量以_+小驼峰的形式命名。

必要的安装环境
- MySQL 5.7.42
- Redis 4.0.9
- Python 3.7
  - 第三方库的安装
    - venv\Scripts\activate 激活虚拟环境
    - pip freeze > requirements.txt 写入到文件
    - pip install -r requirements.txt 安装第三方库
- Nginx 1.14.0


虚拟机安装VMware Tools && 与windows互相粘贴复制
- VMware的菜单栏选择 虚拟机 -> 安装VMware Tools
- 双击桌面的 VMware Tolls
- 解压并提取里面的压缩包到桌面
- 运行：sudo ./vmware-install.pl
- 安装open-vm-tools：sudo apt-get install open-vm-tools
- 安装open-vm-tools-desktop：sudo apt-get install open-vm-tools-desktop
- 虚拟机设置->选项->客户机隔离，启用粘贴复制与拖放
- 重启系统：sudo reboot

虚拟机与windows互ping
- 设置网络适配器为：NAT模式
- 此时虚拟机可以ping通windows，但是windows不能ping通虚拟机
- 在windows上，右键网络适配器->“打开网络和Internet设置”->点击“更改适配器选项”->启用对应的VMnet
- 启用后一般就能ping通了


安装python3.7
- pyenv是一种管理多个Python版本的优秀工具，特别适合需要在同一系统中切换不同Python版本的场景。
- 安装pyenv的依赖：
  - sudo apt update
  - sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
- 安装pyenv：
  - curl https://pyenv.run | bash
- 配置shell以便pyenv生效：
  - 将以下内容添加到你的~/.bashrc（或~/.zshrc如果你使用的是zsh）文件中：
  - sudo vim ~/.bashrc
  - export PATH="$HOME/.pyenv/bin:$PATH"
  - eval "$(pyenv init --path)"
  - eval "$(pyenv init -)"
  - eval "$(pyenv virtualenv-init -)"
  - 然后重新加载shell配置：
  - source ~/.bashrc  # 或者 source ~/.zshrc
- 安装Python 3.7：
  - pyenv install 3.7.13
- 设置全局或局部使用的Python版本：
  - pyenv global 3.7.13  # 设置全局默认使用的Python版本
  - pyenv local 3.7.13   # 设置当前目录（项目）使用的Python版本.用这个就行，后续可以在这个目录用pip 进行第三方库安装
  - ps：安装完成后在不同的目录使用的就是不同的python版本了
  - 安装完成后在项目目录用：pip install -r requirements.txt命令就可以安装所有的第三方库了
  