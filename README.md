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
