注意事项：

1. Python版本： python 3.12.0

2. 如何运行代码：
    如需要修改配置，则先修改配置，然后运行main.py，
    如需要运行main.py，确保在 ".\antoTable" 路径下，在cmd中（Windows环境）输入 
        python main_bd.py --environment dev,
        python main_platform.py --environment dev,
        如需要指定环境为开发环境： 
            则是 python main_bd.py --environment test, 
            python main_platform.py --environment test,
        如需要指定环境为产品环境： 
            则是 python main_bd.py --environment prod,
            python main_platform.py --environment prod,


3. 如何修改配置：在config文件夹中选择对应环境的 config文件。修改相应配置。 特别的，请修改 config_prod文件中的[mysqlDatabase]信息。

4. 关于config配置文件说明：[environment] 说明环境信息， [mysqlDatabase] 说明 mysql配置信息， [email] 说明邮件收发信息


e.g. 

[environment]
environment = DEV

[mysqlDatabase]
HOST = 172.31.4.181
PORT = 3307
USER = exchange
PASSWORD = exo2It9EqIi7
DATABASE = partner

[email]
sender = da001@3ex.com
receiver = da001@3ex.com; hang.p@logtec.com
password = T!+=%Sx8*feJ"g;Vda001