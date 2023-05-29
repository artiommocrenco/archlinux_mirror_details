#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(
                    prog='archlinux_mirror_details',
                    description='Outputs archlinux mirror details in prometheus format')

parser.add_argument('-s', '--server', help='server name as at https://archlinux.org/mirrors/', required=True)

args = parser.parse_args()

import requests

mirror_url = f'https://archlinux.org/mirrors/{args.server}/'

r = requests.get(mirror_url)

if r.status_code != 200:
        raise Exception(f'Error getting mirror details, response status code for {mirror_url} is {r.status_code}')

from bs4 import BeautifulSoup

soup = BeautifulSoup(r.text, 'html.parser')

available_urls = soup.find('table', id='available_urls').find('tbody').find_all('tr')

print('# TYPE archlinux_mirror_completion gauge')
print('# TYPE archlinux_mirror_delay gauge')
print('# TYPE archlinux_mirror_score gauge\n')
print('# HELP archlinux_mirror_completion The number of mirror checks that have successfully connected and disconnected from the given URL')
print('# HELP archlinux_mirror_delay The calculated average mirroring delay in minutes; e.g. the mean value of last check − last sync')
print('# HELP archlinux_mirror_score A very rough calculation for ranking mirrors. It is currently calculated as (hours delay + average duration + standard deviation) / completion percentage.\n')

for url in available_urls:
        url_details = url.find_all('td')

        url_server = url_details[0].string
        url_protocol = url_details[1].string
        url_ipv4 = url_details[3].string
        url_ipv6 = url_details[4].string
        url_completion = float(url_details[6].string.replace('%', ''))

        url_delay = url_details[7].string.split(':')
        url_delay = int(url_delay[0]) * 60 + int(url_delay[1])

        url_score = float(url_details[10].string)

        print(f'archlinux_mirror_completion{{server="{args.server}",url="{url_server}",protocol="{url_protocol}",ipv4="{url_ipv4}",ipv6="{url_ipv6}"}} {url_completion}')
        print(f'archlinux_mirror_delay{{server="{args.server}",url="{url_server}",protocol="{url_protocol}",ipv4="{url_ipv4}",ipv6="{url_ipv6}"}} {url_delay}')
        print(f'archlinux_mirror_score{{server="{args.server}",url="{url_server}",protocol="{url_protocol}",ipv4="{url_ipv4}",ipv6="{url_ipv6}"}} {url_score}')
