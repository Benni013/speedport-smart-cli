#!/usr/bin/env python3
import argparse
import getpass
import hashlib
import json
import re
import sys
import time
import requests


class colors:
    reset = '\033[0m'
    bold = '\033[01m'
    dim = '\033[02m'
    italic = '\033[03m'
    underline = '\033[04m'
    slowblink = '\033[05m'
    fastblink = '\033[06m'
    invert = '\033[07m'
    hide = '\033[08m'
    strike = '\033[09m'

    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        yellow = '\033[33m'
        blue = '\033[34m'
        magenta = '\033[35m'
        cyan = '\033[36m'
        white = '\033[37m'
        brightblack = '\033[90m'
        brightred = '\033[91m'
        brightgreen = '\033[92m'
        brightyellow = '\033[93m'
        brightblue = '\033[94m'
        brightmagenta = '\033[95m'
        brightcyan = '\033[96m'
        brightwhite = '\033[97m'

    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        yellow = '\033[43m'
        blue = '\033[44m'
        magenta = '\033[45m'
        cyan = '\033[46m'
        white = '\033[47m'
        brightblack = '\033[100m'
        brightred = '\033[101m'
        brightgreen = '\033[102m'
        brightyellow = '\033[103m'
        brightblue = '\033[104m'
        brightmagenta = '\033[105m'
        brightcyan = '\033[106m'
        brightwhite = '\033[107m'


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Language': 'en-GB,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate',
           'DNT': '1',
           'Connection': 'close'}
headersJson = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
               'Accept': 'application/json, text/javascript, */*',
               'Accept-Language': 'en-GB,en;q=0.5',
               'Accept-Encoding': 'gzip, deflate',
               'Content-Type': 'application/x-www-form-urlencoded',
               'X-Requested-With': 'XMLHttpRequest',
               'DNT': '1',
               'Connection': 'close'}


def main():
    parser = argparse.ArgumentParser(description=f'Speedport Smart - Expert Mode Readout{colors.fg.red}\nWarning: Every session logged into the router will be closed!{colors.reset}', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version='0.0.1')
    parser.add_argument('-u', '--url', default=['http://192.168.2.1'], help='set your Speedport URL', nargs=1)
    parser.add_argument('-d', '--dynamic', default=False, help='set dynamic mode (refreshes data at given time interval)', action='store_true')
    parser.add_argument('-r', '--refresh', default=['10'], help='set refresh rate in dynamic mode in seconds (default=10, min=4).', nargs=1)
    parser.add_argument('--memcpu', default=False, help='print utilization information', action='store_true')
    parser.add_argument('--dev', default=False, help='print interface information', action='store_true')
    parser.add_argument('--wifi', default=False, help='print Wi-Fi information', action='store_true')
    parser.add_argument('--dsl', default=False, help='print DSL information', action='store_true')
    parser.add_argument('--arp', default=False, help='print ARP table information', action='store_true')
    parser.add_argument('--all', default=False, help='print all information', action='store_true')
    args = parser.parse_args()
    if re.match(r'^http://\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$', args.url[0]) is not None:
        url = args.url[0]
    else:
        print(f'URL doesn\'t exist. Perhaps you meant http://{args.url[0]}?')
        exit(1)
    password = getpass.getpass('Enter password: ')
    if args.refresh[0].isdigit() and int(args.refresh[0]) >= 4:
        refresh = int(args.refresh[0])
    else:
        refresh = 4
    session = dict(SessionID_R3=login(url, password)[13:])
    out((args.memcpu, args.dev, args.wifi, args.dsl, args.arp), args.all, url, session, args.dynamic, refresh)


def sha256(val):
    m = hashlib.sha256()
    m.update(val)
    return m.hexdigest()


def login(url, password):
    lg = requests.get(url=url, headers=headers, verify=False, allow_redirects=True)
    chalpos = lg.text.find('challenge = \"')
    challengev = lg.text[chalpos:chalpos + 80].split('\"')[1]
    hashvalue = sha256(f'{challengev}:{password}'.encode())
    data = {'csrf_token': 'nulltoken',
            'password': hashvalue,
            'showpw': '0',
            'challengev': challengev}
    lp = requests.post(url=f'{url}/data/Login.json', headers=headersJson, data=data, verify=False, allow_redirects=True)
    try:
        return lp.headers['Set-Cookie']
    except KeyError:
        print(f'{colors.fg.red}Error: wrong password{colors.reset}')
        exit(2)


def requestJson(urlTarget, cookie):
    uri = requests.get(url=urlTarget, headers=headersJson, cookies=cookie, verify=False, allow_redirects=True)
    try:
        jsonText = json.loads(uri.text)
        return jsonText
    except json.decoder.JSONDecodeError:
        print(f'{colors.fg.red}Error: invalid JSON file{colors.reset}')
        exit(1)


def printUtilizationInfo(url, cookie):
    print(f'{colors.fg.magenta}-- Memory/CPU utilization --{colors.reset}')
    js = requestJson(f'{url}/engineer/data/memcpu.json', cookie)
    CPULoad = MainMem = usedVsFreeMainMem = FlashMem = usedVsFreeFlashMem = '--'
    for x in range(len(js)):
        varid = js[x]['varid']
        if varid == 'MainMem':
            MainMem = js[x]['varvalue']
        if varid == 'usedVsFreeMainMem':
            usedVsFreeMainMem = js[x]['varvalue']
        if varid == 'FlashMem':
            FlashMem = js[x]['varvalue']
        if varid == 'usedVsFreeFlashMem':
            usedVsFreeFlashMem = js[x]['varvalue']
        if varid == 'CPULoad':
            CPULoad = js[x]['varvalue']
    print(f'{colors.fg.green}CPU-Load:\t\t\t{CPULoad}{colors.reset}')
    print(f'{colors.fg.green}Available Main Memory:\t\t{MainMem}{colors.reset}')
    print(f'{colors.fg.green}Used- vs. Free Main Memory:\t{usedVsFreeMainMem}{colors.reset}')
    print(f'{colors.fg.green}Available Flash Memory:\t\t{FlashMem}{colors.reset}')
    print(f'{colors.fg.green}Used- vs. Free Flash Memory:\t{usedVsFreeFlashMem}{colors.reset}')
    return 6


def printInterfaceInfo(url, cookie):
    print(f'{colors.fg.magenta}-- Link Layer --{colors.reset}')
    js = requestJson(f'{url}/engineer/data/linklayer.json', cookie)
    interfacename = macAddr = interfacestatus = mediaval = speed = '--'
    interface = []
    for x in range(2, len(js)):
        interface.append(js[x]['varvalue'])
        for y in range(len(interface[x - 2])):
            varid = interface[x - 2][y]['varid']
            if varid == 'interfacename':
                interfacename = interface[x - 2][y]['varvalue']
            if varid == 'physical_address':
                macAddr = interface[x - 2][y]['varvalue']
            if varid == 'interfacestatus':
                interfacestatus = interface[x - 2][y]['varvalue']
            if varid == 'mediaval':
                mediaval = interface[x - 2][y]['varvalue']
            if varid == 'speed':
                speed = interface[x - 2][y]['varvalue']
        print(f'{colors.fg.green}Interface: {interfacename}\tMAC: {macAddr}\tInterface status: {interfacestatus}\tMedia: {mediaval}\tSpeed: {speed}{colors.reset}')
    return len(interface) + 1


def printWLANInfo(url, cookie):
    print(f'{colors.fg.magenta}-- Wi-Fi --{colors.reset}')
    js = requestJson(f'{url}/engineer/data/wlan.json', cookie)
    bssid2G = ssid2G = channel2G = output_power2G = data_rate2G = '--'
    bssid5G = ssid5G = channel5G = output_power5G = data_rate5G = '--'
    macAddr = ipAddr = signal = hostname = '--'
    client2G = []
    client5G = []
    for x in range(len(js)):
        varid = js[x]['varid']
        if varid == 'ssid2G':
            ssid2G = js[x]['varvalue']
        if varid == 'ssid5G':
            ssid5G = js[x]['varvalue']
        if varid == 'bssid2G':
            bssid2G = js[x]['varvalue']
        if varid == 'bssid5G':
            bssid5G = js[x]['varvalue']
        if varid == 'channel2G':
            channel2G = js[x]['varvalue']
        if varid == 'channel5G':
            channel5G = js[x]['varvalue']
        if varid == 'output_power2G':
            output_power2G = js[x]['varvalue']
        if varid == 'output_power5G':
            output_power5G = js[x]['varvalue']
        if varid == 'data_rate2G':
            data_rate2G = js[x]['varvalue']
        if varid == 'data_rate5G':
            data_rate5G = js[x]['varvalue']
        if varid == 'WLAN_client2G':
            client2G.append(js[x]['varvalue'])
        if varid == 'WLAN_client5G':
            client5G.append(js[x]['varvalue'])
    print(f'{colors.fg.magenta}-- Wi-Fi Information 2.4G --{colors.reset}')
    print(f'{colors.fg.green}BSSID: {bssid2G}\tSSID: {ssid2G}\tChannel: {channel2G}\tOutput Power: {output_power2G}\tDatarate: {data_rate2G}{colors.reset}')
    print(f'{colors.fg.magenta}-- Wi-Fi clients 2.4G --{colors.reset}')
    for x in range(len(client2G)):
        for y in range(len(client2G[x])):
            varid = client2G[x][y]['varid']
            if varid == 'macAddr':
                macAddr = client2G[x][y]['varvalue']
            if varid == 'ipAddr':
                ipAddr = client2G[x][y]['varvalue']
            if varid == 'signal':
                signal = client2G[x][y]['varvalue']
            if varid == 'hostname':
                hostname = client2G[x][y]['varvalue']
        print(f'{colors.fg.green}MAC: {macAddr}\tIP: {ipAddr}\tSignal: {signal}\tHostname: {hostname}{colors.reset}')
    print(f'{colors.fg.magenta}-- Wi-Fi Information 5G --{colors.reset}')
    print(f'{colors.fg.green}BSSID: {bssid5G}\tSSID: {ssid5G}\tChannel: {channel5G}\tOutput Power: {output_power5G}\tDatarate: {data_rate5G}{colors.reset}')
    print(f'{colors.fg.magenta}-- Wi-Fi clients 5G --{colors.reset}')
    for x in range(len(client5G)):
        for y in range(len(client5G[x])):
            varid = client5G[x][y]['varid']
            if varid == 'macAddr':
                macAddr = client5G[x][y]['varvalue']
            if varid == 'ipAddr':
                ipAddr = client5G[x][y]['varvalue']
            if varid == 'signal':
                signal = client5G[x][y]['varvalue']
            if varid == 'hostname':
                hostname = client5G[x][y]['varvalue']
        print(f'{colors.fg.green}MAC: {macAddr}\tIP: {ipAddr}\tSignal: {signal}\tHostname: {hostname}{colors.reset}')
    return len(client2G) + len(client5G) + 7


def printDSLInfo(url, cookie):
    print(f'{colors.fg.magenta}-- DSL --{colors.reset}')
    js = requestJson(f'{url}/engineer/data/dsl.json', cookie)
    ActualDataUp = ActualDataDown = AttainDataUp = AttainDataDown = '--'
    for x in range(len(js)):
        varid = js[x]['varid']
        if varid == 'AttainDataUp':
            AttainDataUp = js[x]['varvalue']
        if varid == 'AttainDataDown':
            AttainDataDown = js[x]['varvalue']
        if varid == 'ActualDataUp':
            ActualDataUp = js[x]['varvalue']
        if varid == 'ActualDataDown':
            ActualDataDown = js[x]['varvalue']
    print(f'{colors.fg.green}Actual Data Rate\nUpstream:\t{int(ActualDataUp) / 8192} MiB/s\nDownstream:\t{int(ActualDataDown) / 8192} MiB/s{colors.reset}')
    print(f'{colors.fg.green}Attainable Data Rate\nUpstream:\t{int(AttainDataUp) / 8192} MiB/s\nDownstream:\t{int(AttainDataDown) / 8192} MiB/s{colors.reset}')
    return 7


def printARPInfo(url, cookie):
    print(f'{colors.fg.magenta}-- ARP Table --{colors.reset}')
    js = requestJson(f'{url}/engineer/data/arp.json', cookie)
    macAddr = ipAddr = age = '--'
    grid = []
    for x in range(2, len(js)):
        grid.append(js[x]['varvalue'])
        for y in range(len(grid[x - 2])):
            varid = grid[x - 2][y]['varid']
            if varid == 'macAddr':
                macAddr = grid[x - 2][y]['varvalue']
            if varid == 'ipAddr':
                ipAddr = grid[x - 2][y]['varvalue']
            if varid == 'age':
                age = grid[x - 2][y]['varvalue']
        print(f'{colors.fg.green}MAC: {macAddr}\tIP: {ipAddr}\tAge: {age}{colors.reset}')
    return len(grid) + 1


def printVersionInfo(url, cookie):
    print(f'{colors.fg.magenta}-- Module Versions --{colors.reset}')
    js = requestJson(f'{url}/engineer/data/version.json', cookie)
    OpeSysType = OpeSysVer = OpeSysPaLev = WebUi = SoftwareVersion = WlanChipVer = '--'
    for x in range(len(js)):
        varid = js[x]['varid']
        if varid == 'OpeSysType':
            OpeSysType = js[x]['varvalue']
        if varid == 'OpeSysVer':
            OpeSysVer = js[x]['varvalue']
        if varid == 'OpeSysPaLev':
            OpeSysPaLev = js[x]['varvalue']
        if varid == 'WebUi':
            WebUi = js[x]['varvalue']
        if varid == 'SoftwareVersion':
            SoftwareVersion = js[x]['varvalue']
        if varid == 'WlanChipVer':
            WlanChipVer = js[x]['varvalue']
    print(f'{colors.fg.green}Operating System Type:\t\t{OpeSysType}{colors.reset}')
    print(f'{colors.fg.green}Operating System Version:\t{OpeSysVer}{colors.reset}')
    print(f'{colors.fg.green}Operating System Patch Level:\t{OpeSysPaLev}{colors.reset}')
    print(f'{colors.fg.green}Web-UI:\t\t\t{WebUi}{colors.reset}')
    print(f'{colors.fg.green}Software Version:\t{SoftwareVersion}{colors.reset}')
    print(f'{colors.fg.green}WiFi Chip Version:\t{WlanChipVer}{colors.reset}')
    return 7


# function to process the options
def out(args, setall, url, session, dynamic, refresh):
    line_count = 0
    memcpu, dev, wifi, dsl, arp = args
    if setall:
        memcpu = dev = wifi = dsl = arp = True
    if not any([memcpu, dev, wifi, dsl, arp]):
        printVersionInfo(url, session)
        exit()
    if memcpu: line_count += printUtilizationInfo(url, session)
    if dev: line_count += printInterfaceInfo(url, session)
    if wifi: line_count += printWLANInfo(url, session)
    if dsl: line_count += printDSLInfo(url, session)
    if arp: line_count += printARPInfo(url, session)
    while dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[1A\x1B[2K' * line_count)
            sys.stdout.flush()
            line_count = 0
            if memcpu: line_count += printUtilizationInfo(url, session)
            if dev: line_count += printInterfaceInfo(url, session)
            if wifi: line_count += printWLANInfo(url, session)
            if dsl: line_count += printDSLInfo(url, session)
            if arp: line_count += printARPInfo(url, session)
        except KeyboardInterrupt:
            print('\nExiting...')
            exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupt signal received')
        exit(130)
