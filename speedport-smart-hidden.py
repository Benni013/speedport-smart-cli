#!/usr/bin/python
import argparse
import getpass
import hashlib
import json
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


url = 'http://192.168.2.1'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Language': 'en-GB,en;q=0.5',
           'Accept-Encoding': 'gzip, deflate',
           'DNT': '1',
           'Connection': 'close'}
headersJson = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
               'Accept': 'application/json, text/javascript, */*',
               'Accept-Language': 'en-GB,en;q=0.5',
               'Accept-Encoding': 'gzip, deflate',
               'Content-Type': 'application/x-www-form-urlencoded',
               'X-Requested-With': 'XMLHttpRequest',
               'DNT': '1',
               'Connection': 'close'}
purl = '127.0.0.1:8080'
p = {'http': 'http://%s' % purl,
     'https': 'https://%s' % purl,
     'ftp': 'ftp://%s' % purl}


def main():
    parser = argparse.ArgumentParser(description='Speedport Smart - Expert Mode Readout%s\nWarning: Every session logged into the router will be closed!%s' % (colors.fg.red, colors.reset), formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version='0.0.1 beta')
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
    global url
    url = args.url[0]
    password = getpass.getpass("Enter password: ")
    if int(args.refresh[0]) >= 4:
        refresh = int(args.refresh[0])
    else:
        refresh = 4
    session = dict(SessionID_R3=login(password)[13:])
    if args.memcpu:
        printUtilizationInfo(session, args.dynamic, refresh)
    elif args.dev:
        printInterfaceInfo(session, args.dynamic, refresh)
    elif args.wifi:
        printWLANInfo(session, args.dynamic, refresh)
    elif args.dsl:
        printDSLInfo(session, args.dynamic, refresh)
    elif args.arp:
        printARPInfo(session, args.dynamic, refresh)
    elif args.all:
        printAll(session, args.dynamic, refresh)
    else:
        printVersionInfo(session)


def sha256(val):
    m = hashlib.sha256()
    m.update(val)
    return m.hexdigest()


def login(password):
    lg = requests.get(url=url, headers=headers, verify=False, allow_redirects=True)
    chalpos = lg.text.find('challenge = \"')
    challengev = lg.text[chalpos:chalpos + 80].split('\"')[1]
    hashvalue = sha256(('%s:%s' % (challengev, password)).encode())
    data = {'csrf_token': 'nulltoken',
            'password': hashvalue,
            'showpw': '0',
            'challengev': challengev}
    lp = requests.post(url='%s/data/Login.json' % url, headers=headersJson, data=data, verify=False, allow_redirects=True)
    try:
        return lp.headers['Set-Cookie']
    except KeyError:
        print('%sError: wrong password%s' % (colors.fg.red, colors.reset))
        exit(2)


def requestJson(urlTarget, cookie):
    uri = requests.get(url=urlTarget, headers=headersJson, cookies=cookie, verify=False, allow_redirects=True)
    try:
        jsonText = json.loads(uri.text)
        return jsonText
    except json.decoder.JSONDecodeError:
        print('%sError: invalid JSON file%s' % (colors.fg.red, colors.reset))
        exit(1)


def printUtilizationInfo(cookie, dynamic, refresh):
    print('%s-- Memory/CPU utilization --%s' % (colors.fg.magenta, colors.reset))
    js = requestJson('%s/engineer/data/memcpu.json' % url, cookie)
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
    print('%sCPU-Load:\t\t\t%s%s' % (colors.fg.green, CPULoad, colors.reset))
    print('%sAvailable Main Memory:\t\t%s%s' % (colors.fg.green, MainMem, colors.reset))
    print('%sUsed- vs. Free Main Memory:\t%s%s' % (colors.fg.green, usedVsFreeMainMem, colors.reset))
    print('%sAvailable Flash Memory:\t\t%s%s' % (colors.fg.green, FlashMem, colors.reset))
    print('%sUsed- vs. Free Flash Memory:\t%s%s' % (colors.fg.green, usedVsFreeFlashMem, colors.reset))
    if dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[1A\x1B[2K' * 6)
            sys.stdout.flush()
            printUtilizationInfo(cookie, dynamic, refresh)
        except KeyboardInterrupt:
            print(' Exiting...')
            return


def printInterfaceInfo(cookie, dynamic, refresh):
    print('%s-- Link Layer --%s' % (colors.fg.magenta, colors.reset))
    js = requestJson('%s/engineer/data/linklayer.json' % url, cookie)
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
        print('%sInterface: %s\tMAC: %s\tInterface status: %s\tMedia: %s\tSpeed: %s%s' % (colors.fg.green, interfacename, macAddr, interfacestatus, mediaval, speed, colors.reset))
    if dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[1A\x1B[2K' * (len(interface) + 1))
            sys.stdout.flush()
            printInterfaceInfo(cookie, dynamic, refresh)
        except KeyboardInterrupt:
            print(' Exiting...')
            return


def printWLANInfo(cookie, dynamic, refresh):
    print('%s-- Wi-Fi --%s' % (colors.fg.magenta, colors.reset))
    js = requestJson('%s/engineer/data/wlan.json' % url, cookie)
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
    print('%s-- Wi-Fi Information 2.4G --%s' % (colors.fg.magenta, colors.reset))
    print('%sBSSID: %s\tSSID: %s\tChannel: %s\tOutput Power: %s\tDatarate: %s%s' % (colors.fg.green, bssid2G, ssid2G, channel2G, output_power2G, data_rate2G, colors.reset))
    print('%s-- Wi-Fi clients 2.4G --%s' % (colors.fg.magenta, colors.reset))
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
        print('%sMAC: %s\tIP: %s\tSignal: %s\tHostname: %s%s' % (colors.fg.green, macAddr, ipAddr, signal, hostname, colors.reset))
    print('%s-- Wi-Fi Information 5G --%s' % (colors.fg.magenta, colors.reset))
    print('%sBSSID: %s\tSSID: %s\tChannel: %s\tOutput Power: %s\tDatarate: %s%s' % (colors.fg.green, bssid5G, ssid5G, channel5G, output_power5G, data_rate5G, colors.reset))
    print('%s-- Wi-Fi clients 5G --%s' % (colors.fg.magenta, colors.reset))
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
        print('%sMAC: %s\tIP: %s\tSignal: %s\tHostname: %s%s' % (colors.fg.green, macAddr, ipAddr, signal, hostname, colors.reset))
    if dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[1A\x1B[2K' * (7 + len(client2G) + len(client5G)))
            sys.stdout.flush()
            printWLANInfo(cookie, dynamic, refresh)
        except KeyboardInterrupt:
            print(' Exiting...')
            return


def printDSLInfo(cookie, dynamic, refresh):
    print('%s-- DSL --%s' % (colors.fg.magenta, colors.reset))
    js = requestJson('%s/engineer/data/dsl.json' % url, cookie)
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
    print('%sActual Data Rate\nUpstream:\t%s MiB/s\nDownstream:\t%s MiB/s%s' % (colors.fg.green, int(ActualDataUp) / 8192, int(ActualDataDown) / 8192, colors.reset))
    print('%sAttainable Data Rate\nUpstream:\t%s MiB/s\nDownstream:\t%s MiB/s%s' % (colors.fg.green, int(AttainDataUp) / 8192, int(AttainDataDown) / 8192, colors.reset))
    if dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[1A\x1B[2K' * 7)
            sys.stdout.flush()
            printDSLInfo(cookie, dynamic, refresh)
        except KeyboardInterrupt:
            print(' Exiting...')
            return


def printARPInfo(cookie, dynamic, refresh):
    print('%s-- ARP Table --%s' % (colors.fg.magenta, colors.reset))
    js = requestJson('%s/engineer/data/arp.json' % url, cookie)
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
        print('%sMAC: %s\tIP: %s\tAge: %s%s' % (colors.fg.green, macAddr, ipAddr, age, colors.reset))
    if dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[1A\x1B[2K' * (len(grid) + 1))
            sys.stdout.flush()
            printARPInfo(cookie, dynamic, refresh)
        except KeyboardInterrupt:
            print(' Exiting...')
            return


def printVersionInfo(cookie):
    print('%s-- Module Versions --%s' % (colors.fg.magenta, colors.reset))
    js = requestJson('%s/engineer/data/version.json' % url, cookie)
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
    print('%sOperating System Type:\t\t%s%s' % (colors.fg.green, OpeSysType, colors.reset))
    print('%sOperating System Version:\t%s%s' % (colors.fg.green, OpeSysVer, colors.reset))
    print('%sOperating System Patch Level:\t%s%s' % (colors.fg.green, OpeSysPaLev, colors.reset))
    print('%sWeb-UI:\t\t\t%s%s' % (colors.fg.green, WebUi, colors.reset))
    print('%sSoftware Version:\t%s%s' % (colors.fg.green, SoftwareVersion, colors.reset))
    print('%sWiFi Chip Version:\t%s%s' % (colors.fg.green, WlanChipVer, colors.reset))


def printAll(session, dynamic, refresh):
    printVersionInfo(session)
    printUtilizationInfo(session, False, refresh)
    printInterfaceInfo(session, False, refresh)
    printWLANInfo(session, False, refresh)
    printDSLInfo(session, False, refresh)
    printARPInfo(session, False, refresh)
    if dynamic:
        try:
            time.sleep(refresh)
            sys.stdout.write('\x1B[2J\x1B[H')
            printAll(session, dynamic, refresh)
        except KeyboardInterrupt:
            print(' Exiting...')
            return


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' Exiting...')
        exit(130)
