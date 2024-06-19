# tornado_server
基于tornado搭建的小游戏服务端
- 程序为单线程的,如果一个请求阻塞了会导致所有的http请求都阻塞[避免耗时的数据库操作,我们需要的就是单线程顺序的数据库操作]
- 客户端->服务器的http请求是异步的,由tornado把网络连接加入到队列中,等待事件处理时间到达后处理
- 在一个请求里面，服务器可以通过async来异步进行网络http请求。避免网络阻塞卡顿。

ps：
- 类名和函数名统一用大驼峰命名法把，局部变量用小驼峰，以类型前缀开头。成员变量以m_开头。不对外暴露的私有函数可以以
_+大驼峰的形式命名。不对外暴露的局部变量以_+大驼峰的形式命名。
- 单下划线（如 _function）：表示该函数或变量是内部使用的，但不会真正阻止外部访问，只是一种命名约定。
- 双下划线（如 __function）：触发名称改写机制，以避免在子类中产生名称冲突，用于实现类内部的“私有”成员。

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


安装Python3.7
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
  

安装Mysql 5.7
 - https://blog.csdn.net/qq233325332/article/details/132339173
 - sudo apt update
 - sudo apt install mysql-server-5.7 mysql-client-5.7
 - 启动MySQL：sudo systemctl start mysql
 - 设置Mysql root密码：sudo mysql_secure_installation
   - 不要禁止root用户远程登录，其他都选yes即可
 - 修改文件：/etc/mysql/mysql.conf.d/mysqld.cnf
   - bind-address = 0.0.0.0
 - 创建远程访问用户【这是一个新用户，专门在远程访问的，与本地的root用户不是同一个用户】
   - CREATE USER 'remote_user'@'%' IDENTIFIED BY 'password';
 - 为新建的这个远程用户添加所有访问权限
   - GRANT ALL PRIVILEGES ON *.* TO 'remote_user'@'%' WITH GRANT OPTION;
 - FLUSH PRIVILEGES;
 - sudo systemctl restart mysql
 - 然后在windows上，使用navicat。用remote_user+password登录
 - 新建查询，执行init.sql，完成数据库的初始化

安装Redis 4.0.9【默认就是这个版本】
 - sudo apt update
 - sudo apt install redis-server
 - sudo systemctl status redis-server
 - 运行远程访问
   - vim /etc/redis/redis.conf，修改为 bind 0.0.0.0
   - sudo systemctl restart redis-server

安装Nginx 1.14.0
 - sudo apt update
 - sudo apt install nginx
 - sudo systemctl status nginx
 - 把configs目录下的.conf文件修改过去到/etc/nginx/nginx.conf目录
   - /etc/nginx$ rm -rf nginx.conf
   - ~/work/tornado_server/configs$ sudo cp nginx.conf /etc/nginx/nginx.conf
   - ~/work/tornado_server/configs$ sudo cp tornado.conf /etc/nginx/conf.d/tornado.conf
 - sudo nginx -t
 - sudo systemctl reload nginx  测试通过后重新加载
 - sudo systemctl restart nginx 或者重新启动

查看被占用的端口：
 - netstat -tuln

安装Django
- pip install django
- 安装mysqlclient
  - sudo apt-get update
  - sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
  - pip install mysqlclient
