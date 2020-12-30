import os

import requests
from bs4 import BeautifulSoup as Bs

hero_names = ['Ashe', 'Bastion', 'Doomfist', 'Echo', 'Genji', 'Hanzo', 'Junkrat', 'Mccree', 'Mei', 'Pharah', 'Reaper',
              'Soldier:_76', 'Sombra', 'Symmetra', 'Torbjörn', 'Tracer', 'Widowmaker', 'Ana', 'Baptiste', 'Brigette',
              'Lúcio', 'Mercy', 'Moira', 'Zenyatta']


def get_hero_url(hero):
    url = f'https://overwatch.gamepedia.com/{hero}'
    return url


def fetch_content(url):
    print(f'\nScraping {url}\n')
    page = requests.get(url)
    soup = Bs(page.content, 'html.parser')
    return soup


def fetch_desc_and_hp(soup):
    temp = soup.find('div', class_='mw-parser-output')
    desc = temp.findAll('p')[3].text
    dets_table = soup.find('table', class_='infoboxtable')
    hp_row = dets_table.findAll('tr')[-1]
    hp = hp_row.text.replace('Health', '').replace('\n', '')

    return desc, hp


def fetch_ability_details(soup):
    ability_dets = []

    keybinds = ['SPACE', 'E', 'Q', 'LSHIFT', 'LCONTROL']
    # Finds all ability name divs
    ability_names = soup.findAll('div', class_="abilityHeader")
    # Extracts the text for the ability names
    ability_names = [name.text for name in ability_names]
    # The keybind is inlcuded in the name, so it is removed
    ability_keybinds = []
    for i, name in enumerate(ability_names):
        key_found = False
        for key in keybinds:
            if name.endswith(key):
                ability_keybinds.append(key)
                ability_names[i] = name[:-len(key)]
                key_found = True
                break
        if not key_found:
            if 'M1' not in ability_keybinds:
                ability_keybinds.append('M1')
            else:
                ability_keybinds.append('M2')

    # Find all the divs that contain the ability headers and stats
    ability_boxes = soup.findAll('div', class_='ability_box')
    for i, box in enumerate(ability_boxes):
        # Finds the box that contains the ability stats
        stats_box = box.find('div', {'style': 'padding:5px;'})
        # Finds all the divs that contain the stats
        ability_stats_divs = stats_box.findAll('div', {'style': 'display:block;'})
        ability_stat_names = []
        ability_stat_numbers = []

        for stat in ability_stats_divs:
            stat_name = stat.text[:stat.text.find(':')]
            stat_numbers = stat.text[stat.text.find(':') + 2:]
            ability_stat_names.append(stat_name)
            ability_stat_numbers.append(stat_numbers)
        ability_dets.append((ability_names[i], ability_stat_names, ability_stat_numbers, ability_keybinds[i]))

    return ability_dets


def write_to_file(hero_name, html):
    os.chdir('./out')
    if hero_name == 'Soldier:_76':
        filename = 'soldier-76.html'
    else:
        filename = f'{hero_name.lower()}.html'
    with open(filename, 'w', encoding='utf-8') as newfile:
        print(f'Writing to {filename}')
        newfile.write(html)


def replace_template_strings(name, desc, hp, ability_dets):
    # ability dets is a list of tuples. in each tuple, 1st elem is ability name, 2nd elem is list of ability stat names,
    # 3rd elem is list of corresponding ability stat numbers
    os.chdir('../')
    template = open('templates/hero.html')
    temp_str = template.read()
    template.close()

    temp_str = temp_str.replace('{hero_name_title}', name)
    temp_str = temp_str.replace('{hero_name}', name)
    temp_str = temp_str.replace('{hero_pic}', name.lower())
    temp_str = temp_str.replace('{hero_name_alt}', name)
    temp_str = temp_str.replace('{hero_description}', desc)
    temp_str = temp_str.replace('{hero_hp}', hp)
    abilities_str = ''

    for i in range(len(ability_dets)):

        ability_template = open('templates/ability.html')
        abil_temp = ability_template.read()
        ability_template.close()

        abil_name = ability_dets[i][0]
        abil_temp = abil_temp.replace('{ability_pic}', abil_name.lower().replace(' ', '-'))
        abil_temp = abil_temp.replace('{ability_name}', abil_name)
        abil_temp = abil_temp.replace('{ability_keybind}', ability_dets[i][3])

        ability_stats_str = ''
        for j in range(len(ability_dets[i][1])):
            ability_stats_str += f'<b>{ability_dets[i][1][j]}</b>: {ability_dets[i][2][j]}<br>\n\t\t\t\t\t\t\t'

        abil_temp = abil_temp.replace('{ability_stats}', ability_stats_str)
        abilities_str += abil_temp

    temp_str = temp_str.replace('{abilities}', abilities_str)
    print(temp_str)
    return temp_str


if __name__ == '__main__':
    for hero in hero_names:
        page_url = get_hero_url(hero)
        page_soup = fetch_content(page_url)
        hero_desc, hero_hp = fetch_desc_and_hp(page_soup)
        ability_details = fetch_ability_details(page_soup)
        hero_html = replace_template_strings(hero, hero_desc, hero_hp, ability_details)
        write_to_file(hero, hero_html)
