import re

import requests
from bs4 import BeautifulSoup as Bs

hero_names = ['D.Va', 'Orisa', 'Reinhardt', 'Roadhog', 'Sigma', 'Winston', 'Wrecking_Ball', 'Zarya', 'Ashe', 'Bastion',
              'Doomfist', 'Echo', 'Genji', 'Hanzo', 'Junkrat', 'Mccree', 'Mei', 'Pharah', 'Reaper',
              'Soldier:_76', 'Sombra', 'Symmetra', 'Torbjörn', 'Tracer', 'Widowmaker', 'Ana', 'Baptiste', 'Brigitte',
              'Lúcio', 'Mercy', 'Moira', 'Zenyatta']


def get_hero_url(hero_name, source=False):
    if source:
        url = f'https://overwatch.gamepedia.com/{hero_name}?action=edit'
    else:
        url = f'https://overwatch.gamepedia.com/{hero_name}'

    return url


def fetch_content(url):
    print(f'Scraping {url}')
    page = requests.get(url)
    soup = Bs(page.content, 'html.parser')
    return soup


def fetch_hero_details(name):
    url = get_hero_url(name, source=True)
    soup = fetch_content(url)
    source_text = soup.find('textarea', {'id': 'wpTextbox1'}).text

    # Finds role
    role = re.search(r'role = ?(\[\[)?(\w+)[]\n]', source_text)
    if role: role = role.group(2)
    else: print('ERROR: role not found')

    # Finds description
    desc = re.search(r'== ?Overview ?==\n+(.*)\n', source_text)
    if desc: desc = desc.group(1)
    else: print('ERROR: description not found')

    # Finds HP
    hp = re.search(r'health = ?(.+)\n', source_text)
    if hp: hp = hp.group(1)
    else: print('ERROR: hp not found')

    # Finds armor
    armor = re.search(r'armor = ?(\d+.+)\n', source_text)
    if armor:
        armor = armor.group(1)

    # Finds shield
    shield = re.search(r'shield = ?(\d+)\n', source_text)
    if shield:
        shield = shield.group(1)

    return role, desc, hp, armor, shield


def fetch_ability_details(soup):
    # TODO fix passive abilities showing keybind as M1
    # TODO fix bastion showing guns as M2
    ability_dets = []
    keybinds = ['SPACE', 'E', 'Q', 'LSHIFT', 'LCONTROL']
    # Finds all ability name divs
    ability_names = soup.findAll('div', class_="abilityHeader")
    # Extracts the text for the ability names
    ability_names = [name.text for name in ability_names]
    # The keybind is included in the name, so it is removed
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


def replace_template_strings(name, role, desc, hp, armor, shield, ability_dets):
    # ability dets is a list of tuples. in each tuple, 1st elem is ability name, 2nd elem is list of ability stat names,
    # 3rd elem is list of corresponding ability stat numbers

    template = open('templates/hero.html')
    temp_str = template.read()
    template.close()

    if name == 'Soldier:_76':
        display_name = 'soldier-76'
    elif name == 'D.Va':
        display_name = 'dva'
    elif name == 'Wrecking_Ball':
        display_name = 'wrecking-ball'
    else:
        display_name = name

    temp_str = temp_str.replace('{hero_name_title}', display_name)
    temp_str = temp_str.replace('{hero_name}', display_name)

    # TODO find cleaner way to do this
    if role == 'Tank':
        temp_str = temp_str.replace('{tank_active}', 'active-nav')
        temp_str = temp_str.replace('{damage_active}', '')
        temp_str = temp_str.replace('{support_active}', '')
    elif role == 'Damage':
        temp_str = temp_str.replace('{tank_active}', '')
        temp_str = temp_str.replace('{damage_active}', 'active-nav')
        temp_str = temp_str.replace('{support_active}', '')
    elif role == 'Support':
        temp_str = temp_str.replace('{tank_active}', '')
        temp_str = temp_str.replace('{damage_active}', '')
        temp_str = temp_str.replace('{support_active}', 'active-nav')
    else:
        print('ERROR: ROLE NOT FOUND')

    if name == 'Soldier:_76':
        pic_name = 'soldier-76'
    elif name == 'D.Va':
        pic_name = 'dva'
    elif name == 'Wrecking_Ball':
        pic_name = 'wrecking-ball'
    else:
        pic_name = name.lower()

    temp_str = temp_str.replace('{hero_pic}', pic_name)
    temp_str = temp_str.replace('{hero_name_alt}', name)
    temp_str = temp_str.replace('{hero_description}', desc)
    temp_str = temp_str.replace('{hero_hp}', hp)

    if armor:
        armor_str = f'<li><b>Armor</b>: {armor}</li>'
    else:
        armor_str = ''
    temp_str = temp_str.replace('{armor}', armor_str)

    if shield:
        shield_str = f'<li><b>Shield</b>: {shield}</li>'
    else:
        shield_str = ''
    temp_str = temp_str.replace('{shield}', shield_str)

    abilities_str = ''
    for i in range(len(ability_dets)):
        ability_template = open('templates/ability.html')
        abil_temp = ability_template.read()
        ability_template.close()

        abil_name = ability_dets[i][0]
        abil_temp = abil_temp.replace('{ability_pic}', abil_name.lower().replace(' ', '-').replace(':', ''))
        abil_temp = abil_temp.replace('{ability_name}', abil_name)
        abil_temp = abil_temp.replace('{ability_keybind}', ability_dets[i][3])

        ability_stats_str = ''
        for j in range(len(ability_dets[i][1])):
            ability_stats_str += f'<b>{ability_dets[i][1][j]}</b>: {ability_dets[i][2][j]}<br>\n\t\t\t\t\t\t\t'

        abil_temp = abil_temp.replace('{ability_stats}', ability_stats_str)
        abilities_str += abil_temp

    temp_str = temp_str.replace('{abilities}', abilities_str)
    # print(temp_str)
    return temp_str


def write_to_file(hero_name, html):
    if hero_name == 'Soldier:_76':
        hero_name = 'soldier-76'
    elif hero_name == 'D.Va':
        hero_name = 'dva'
    elif hero_name == 'Wrecking_Ball':
        hero_name = 'wrecking-ball'

    filename = f'{hero_name.lower()}.html'

    print(f'Writing to out/{filename}\n')
    # with open(f'out/{filename}', 'w', encoding='utf-8') as newfile:
    #     print(f'Writing to out/{filename}\n')
    #     newfile.write(html)


def main():
    for hero_name in hero_names:
        page_url = get_hero_url(hero_name)
        page_soup = fetch_content(page_url)
        hero_role, hero_desc, hero_hp, hero_armor, hero_shield = fetch_hero_details(hero_name)
        ability_details = fetch_ability_details(page_soup)
        hero_html = replace_template_strings(hero_name, hero_role, hero_desc, hero_hp, hero_armor, hero_shield,
                                             ability_details)
        write_to_file(hero_name, hero_html)


if __name__ == '__main__':
    main()

# TODO profile to see how to speed up
