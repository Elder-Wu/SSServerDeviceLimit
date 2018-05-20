# -*- coding: utf-8 -*-

import re
import os
import json
import time

if __name__ == '__main__':

    print('\033[1;33;44m 更新时间  %s \033[0m' % time.strftime("%H:%M", time.localtime()))

    with open("shadowsocks.json", "r", encoding="utf-8") as f:
        dict = json.load(f)

    server_ip = dict["server"]
    port_dict = dict["port_password"]
    device_limit_dict = dict["device_limit"]

    for server_port in port_dict:
        # os.system("netstat -np | grep tcp | grep %s:%s | grep ESTAB" % (server_ip, server_port))
        # os.popen("netstat -np | grep tcp | grep %s:%s | grep ESTAB" % (server_ip, server_port))
        # ss命令效率高
        # -t tcp协议 -a 所有 -n 显示成数字
        shell_result = os.popen("ss -t -a -n | grep %s:%s | grep ESTAB" % (server_ip, server_port))
        info = shell_result.readlines()
        ip_list = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "".join(info))
        connected_ip_set = set(ip_list)
        connected_ip_set.discard(server_ip)

        info = os.popen("iptables -L -n --line-numbers | grep %s" % server_port)
        info = info.readlines()
        if (len(info) != 0):
            print("\n清除[%s]端口的INPUT规则......" % server_port)
            for line in info:
                print(line, end="")
            index = info[0][0]
            for line in info:
                os.system("iptables -D INPUT %s" % index)

        device_limit_count = device_limit_dict.get(server_port, 1)
        cur_connected_ip_count = len(connected_ip_set)

        if (device_limit_count == 0):
            print('端口:[%s] \033[1;33m不允许所有设备接入，请核实情况\033[0m' % server_port)
            os.system("iptables -A INPUT -p tcp --dport %s -j DROP" % server_port)
            print("设备限制数量:%s  已连接设备:%s" % (device_limit_count, device_limit_count))

        if (device_limit_count != 0 and len(connected_ip_set) < device_limit_count):
            if (len(connected_ip_set) == 0):
                print('端口:[%s] 未使用' % server_port)
            else:
                print('端口:[%s] \033[1;32m正常使用中\033[0m' % server_port)
            print("设备限制数量:%s  已连接设备:%s" % (device_limit_count, len(connected_ip_set)))
            for connected_ip in connected_ip_set:
                print("设备IP:%s" % connected_ip)

        if (device_limit_count != 0 and len(connected_ip_set) >= device_limit_count):
            print('端口:[%s] \033[1;31m设备已满\033[0m' % server_port)
            print("设备限制数量:%s  已连接设备:%s" % (device_limit_count, device_limit_count))
            count = 0
            for connected_ip in connected_ip_set:
                print("设备IP:%s" % connected_ip)
                os.system("iptables -A INPUT -p tcp -s %s --dport %s -j ACCEPT" % (connected_ip, server_port))
                count += 1
                if (count == device_limit_count):
                    break
            os.system("iptables -A INPUT -p tcp --dport %s -j DROP" % server_port)

        os.system("service iptables save > /dev/null")
        print("\n")

    os.system("iptables -L -n --line-number")
