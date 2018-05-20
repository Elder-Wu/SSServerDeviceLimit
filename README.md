# SSServerDeviceLimit
This tool only used for ss-server not ssr-server.     
可以让你的SS服务器限制某个端口的设备连接数，防止有人恶意分享账号，亲测有效，不是SSR服务器!
<p>原理:Linux中通过iptables进行端口和IP的过滤，俗称防火墙

# 使用方法
使用前提：你的Linux服务器已经安装了SS server端，还需要安装iptables

## 1.配置Shadowsocks服务
在/etc目录下创建文件shadowsocks.json，文件内容如下:
```json
{
  "server":"你的服务器ip地址，这里必须填写具体的，比如17.170.120.130，不可以是0.0.0.0或者127.0.0.1",
  "local_address": "127.0.0.1",
  "local_port":1080,
  "port_password":{
    "1111": "sfaewgsav",
    "2222": "sgervthss",
    "3333": "htehsdhst",
    "端口号": "密码",
    "端口号": "密码",
    "端口号": "密码",
    "端口号": "密码",
    "端口号": "密码"
  },
  "timeout":300,
  "method":"aes-256-cfb",
  "fast_open": false,
  "device_limit":{
    "1111":5,
    "端口号":限制的设备数量
  }
}
```
<p>在port_password中配置多个端口号和对应的密码，端口号最好不要选用特殊端口，比如22(ssh)，80(http)，记住，这里的端口号一旦分配，就不要轻易删除。否则就要自己通过iptables来删除掉无用的规则
<p>device_limit中填写需要限制的端口号和设备数量，上面写的意思就是1111端口号最多只能有5个设备同时登录，可以不写，默认就是1

##### 需要注意的是，device_limit中填写的端口号必须出现在port_password中

## 2.重启Shadowsocks服务
##### 配置开机启动，在/etc/rc.local中加入下面的内容
```commandline
ssserver -c /etc/shadowsocks.json --user nobody -d start
```
<p>-c ss配置文件的路径
<p>--user 非root用户运行ss服务，确保服务器安全
<p>-d daemon运行模式

##### 切换到命令行，输入如下命令
```commandline
ssserver -d stop

ssserver -c /etc/shadowsocks.json --user nobody -d start
```

## 3.配置Linux的crontab任务列表
先将本项目中的ssdevicelimit.py拷贝到本地，放到/etc目录下，与shadowsocks.json在同一个目录
##### 编辑Linux中的crontab任务
```commandline
crontab -e
```
##### 输入如下内容
```commandline
#解决crontab报错：service: commond not found,是因为环境变量的问题
PATH=/sbin:/bin:/usr/sbin:/usr/bin

#每天0点清空root用户的mail邮件
0 0 * * * rm -f /var/mail/root

#每分钟都更新一下ss的端口限制
* * * * * cd /etc/; python3.6 ssdevicelimit.py
```
<p>必须使用python3.x版本，因为我的服务器上python3的环境变量是python3.6，所以上面我写成了python3.6，请根据你自己的python环境变量名来改

##### 最后保存，然后你就等着那些恶意分享SS账号的人抱怨吧：
# 为什么账号不能用了，之前不是好好的吗，FUCK！！！

## 后续
1. 以上操作都确保无误的话，想限制某个端口的设备数量，只要修改```shadowsocks.json```中的内容就可以了，1分钟就能生效，其他的什么都不要干！！！
2. 通过 ```tail -n 100 /var/mail/root``` 查看当前各端口的使用情况，以及使用端口的设备IP
3. 有其他问题请提issue
