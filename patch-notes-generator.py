import os

import requests
from bs4 import BeautifulSoup as Bs


def fetch_content(url):
    page = requests.get(url)
    soup = Bs(page.content, 'html.parser')
    return soup


def fetch_patch_data(soup):
    patch_no = 0
    patch = soup.findAll('div', class_='PatchNotes-patch')[patch_no]
    patch_date = patch.find('div', class_='PatchNotes-date').text
    print(f'Getting patch data for {patch_date}\n')
    hero_updates = patch.findAll('div', class_='PatchNotesHeroUpdate')
    # print(patch_date)
    updates = []
    for hero_update in hero_updates:
        abil_update_list = []
        gen_update_list = []
        hero_name = hero_update.find('h5', class_='PatchNotesHeroUpdate-name').text.strip()
        # print(name)

        general_updates = hero_update.findAll('div', class_='PatchNotesHeroUpdate-generalUpdates')
        for general_update in general_updates:
            update_desc = general_update.text.strip()
            gen_update_list.append(update_desc)
            # print(update_desc)

        ability_updates = hero_update.findAll('div', class_='PatchNotesAbilityUpdate')
        for ability_update in ability_updates:
            ability_name = ability_update.find('div', class_='PatchNotesAbilityUpdate-name').text.strip()
            ability_desc = ability_update.find('div', class_='PatchNotesAbilityUpdate-detailList').text.strip()
            abil_update_list.append((ability_name, ability_desc))
            # print(ability_name, ability_desc)

        updates.append((hero_name, gen_update_list, abil_update_list))

    return patch_date, updates


def create_patch_html(date, hero_updates):
    with open('templates/wiki.html') as template:
        html = template.read()
    html = html.replace('{patch_date}', date)
    patch_str = ''
    for i, update in enumerate(hero_updates):
        with open('templates/update_header.html') as update_header:
            update_temp = update_header.read()
        hero_name = update[0]
        print(f'Writing patch data for {hero_name}\n')
        update_temp = update_temp.replace('{hero_name_pic}', hero_name.lower().replace(' ', '-').replace('.', ''))
        update_temp = update_temp.replace('{hero_name_alt}', hero_name)
        update_temp = update_temp.replace('{name}', hero_name)

        updates = ''

        for general_update in hero_updates[i][1]:
            with open('templates/general_update.html') as gen:
                gen_temp = gen.read()
                gen_temp = gen_temp.replace('{general_update_desc}', general_update)
            updates += gen_temp

        for ability_update in hero_updates[i][2]:
            with open('templates/ability_update.html') as abil:
                abil_temp = abil.read()
                ability_name = ability_update[0]
                ability_desc = ability_update[1]
                abil_temp = abil_temp.replace('{ability_name_pic}',
                                              ability_name.lower().replace(' ', '-'))
                abil_temp = abil_temp.replace('{ability_name_alt}', ability_name)
                abil_temp = abil_temp.replace('{ability_name}', ability_name)
                abil_temp = abil_temp.replace('{ability_desc}', ability_desc.replace('\n', '<br>\n'))
            updates += abil_temp

        update_temp = update_temp.replace('{updates}', updates)
        patch_str += update_temp
    html = html.replace('{hero_updates}', patch_str)
    return html


def write_to_file(content):
    filename = 'wiki.html'
    with open(f'out/{filename}', 'w', encoding='utf-8') as wiki:
        print(f'Writing to out/{filename}')
        wiki.write(content)


if __name__ == '__main__':
    url = 'https://playoverwatch.com/en-us/news/patch-notes/'
    page_soup = fetch_content(url)
    patch_date, patch_hero_updates = fetch_patch_data(page_soup)
    html = create_patch_html(patch_date, patch_hero_updates)
    write_to_file(html)
