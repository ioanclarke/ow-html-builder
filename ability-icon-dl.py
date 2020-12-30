import urllib.request
import os

import requests
from bs4 import BeautifulSoup as Bs

hero_names = ['Ashe', 'Bastion', 'Doomfist', 'Echo', 'Genji', 'Hanzo', 'Junkrat', 'Mccree', 'Mei', 'Pharah', 'Reaper',
              'Soldier-76', 'Sombra', 'Symmetra', 'Torbjorn', 'Tracer', 'Widowmaker', 'Ana', 'Baptiste', 'Brigitte',
              'Lucio', 'Mercy', 'Moira', 'Zenyatta']


def get_url(hero):
    url = f'https://playoverwatch.com/en-gb/heroes/{hero.lower()}/'
    return url


def fetch_content(url):
    print(f'\nDownloading from {url}\n')
    page = requests.get(url)
    soup = Bs(page.content, 'html.parser')
    return soup


def dl_icons(soup):
    os.chdir('./out')
    icons = soup.findAll('img', class_='HeroAbility-iconInner')
    leng = int(len(icons) / 2)
    icons = icons[:leng]
    abil_names = soup.findAll('h4', class_='h5')
    for icon, name in zip(icons, abil_names):
        icon_url = icon['src']
        filename = name.text.lower().replace(' ', '-') + '.png'
        print(f'Downloading {icon_url} as {filename}')
        urllib.request.urlretrieve(icon_url, filename)


if __name__ == '__main__':
    for hero in hero_names:
        page_url = get_url(hero)
        page_soup = fetch_content(page_url)
        dl_icons(page_soup)
