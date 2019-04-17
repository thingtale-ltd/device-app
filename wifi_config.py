import io
import os
import subprocess

def list_ssid():
    proc = subprocess.Popen(['/sbin/wpa_cli', 'list_networks'], stdout=subprocess.PIPE)

    ssid_list = []

    line_ctr = 0
    for line in proc.stdout.readlines():
        line_ctr += 1

        if line_ctr == 1: # iface name
            continue

        if line_ctr == 2: # header
            continue

        ssid = line.split("\t")[1]

        ssid_list.append(ssid)

    proc.stdout.close()
    proc.wait()

    return ssid_list

def get_network_id(ssid):
    ssid_list = list_ssid()

    for i in range(len(ssid_list)):
        if ssid_list[i] == ssid:
            return i, True

    # ssid not found, search empty network
    for i in range(len(ssid_list)):
        if ssid_list[i] == '':
            return i, True

    return len(ssid_list), False

def update(wifi_json):
    id, exists = get_network_id(wifi_json["ssid"])

    proc = subprocess.Popen(['/sbin/wpa_cli'], stdin=subprocess.PIPE, stdout=open(os.devnull, 'w'))
    f = proc.stdin

    if not exists:
        f.write("add_network\n")

    f.write('set_network {} ssid "{}"\n'.format(id, wifi_json["ssid"]))
    f.write('set_network {} key_mgmt {}\n'.format(id, wifi_json["key_mgmt"]))
    f.write('set_network {} psk "{}"\n'.format(id, wifi_json["key"]))
    f.write('enable_network {}\n'.format(id))

    f.write("save_config\n")
    f.close()
    proc.wait()
