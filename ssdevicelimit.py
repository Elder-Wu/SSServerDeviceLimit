# -*- coding: utf-8 -*-

import re
import os
import json
import time
import urllib.request

if __name__ == '__main__':

    print('\033[1;33;44m 更新时间  %s \033[0m' % time.strftime("%H:%M", time.localtime()))

    with open("shadowsocks.json", "r", encoding="utf-8") as f:
        dict = json.load(f)

    # 从指定网站获取IP地址
    with urllib.request.urlopen("https://icanhazip.com") as f:
        body = f.read()  # 报文内容
        server_ip = body.decode('utf-8')
        print("本机公网IP地址:%s", server_ip)

    port_dict = dict["port_password"]
    device_limit_dict = dict["device_limit"]

    os.system("iptables -F")
    for server_port, password in port_dict.items():
        # os.system("netstat -np | grep tcp | grep %s:%s | grep ESTAB" % (server_ip, server_port))
        # os.popen("netstat -np | grep tcp | grep %s:%s | grep ESTAB" % (server_ip, server_port))
        # ss命令效率高
        # -t tcp协议 -a 所有 -n 显示成数字
        shell_result = os.popen("ss -t -a -n | grep '%s:%s ' | grep ESTAB" % (server_ip, server_port))
        info = shell_result.readlines()
        ip_list = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "".join(info))
        connected_ip_set = set(ip_list)
        connected_ip_set.discard(server_ip)

        device_limit_count = device_limit_dict.get(server_port, 1)
        cur_connected_ip_count = len(connected_ip_set)

        if (device_limit_count == 0):
            print('端口:[%s-%s] \033[1;33m不允许所有设备接入，请检查配置文件\033[0m' % (server_port, password))
            os.system("iptables -A INPUT -p tcp --dport %s -j DROP" % server_port)
            os.system("iptables -A INPUT -p udp --dport %s -j DROP" % server_port)
            print("设备限制数量:%s  已连接设备:%s" % (device_limit_count, device_limit_count))

        if (device_limit_count != 0 and cur_connected_ip_count < device_limit_count):
            if (cur_connected_ip_count == 0):
                print('端口:[%s-%s] 未使用' % (server_port, password))
            else:
                print('端口:[%s-%s] \033[1;32m正常使用中\033[0m' % (server_port, password))
            print("设备限制数量:%s  已连接设备:%s" % (device_limit_count, cur_connected_ip_count))
            for connected_ip in connected_ip_set:
                print("设备IP:%s" % connected_ip)

        if (device_limit_count != 0 and cur_connected_ip_count >= device_limit_count):
            print('端口:[%s-%s] \033[1;31m设备已满\033[0m' % (server_port, password))
            print("设备限制数量:%s  已连接设备:%s" % (device_limit_count, device_limit_count))
            count = 0
            for connected_ip in connected_ip_set:
                print("设备IP:%s" % connected_ip)
                os.system("iptables -A INPUT -p tcp -s %s --dport %s -j ACCEPT" % (connected_ip, server_port))
                os.system("iptables -A INPUT -p udp -s %s --dport %s -j ACCEPT" % (connected_ip, server_port))
                count += 1
                if (count == device_limit_count):
                    break
            os.system("iptables -A INPUT -p tcp --dport %s -j DROP" % server_port)
            os.system("iptables -A INPUT -p udp --dport %s -j DROP" % server_port)

        print("\n")

    os.system("service iptables save > /dev/null")
    os.system("iptables -t filter -L INPUT -n --line-number")
