import config
import utils


# get the list of dicts where each dict contains the URls to bp.tf listings of the item and
# it's relevant properties(paint, spell(s), strange part(s))
def get_stats(items):
    # initializing the final list which later will be filled with url dicts
    stats = []

    # iterates over each item dict
    for item in items:
        item_url = create_url(item)

        # initializing properties and setting them to None, in case the item dict does not contain info regarding them
        paint_url = None
        spell_urls = []
        part_urls = []

        # creating a url for each spell applied to the item
        if item["spell(s)"] is not None:
            for spell in item["spell(s)"]:
                spell_urls.append(add_spell_param_to_url(spell))
        # ==================================

        # creating a url for each part applied to the item
        if item["part(s)"] is not None:
            for part in item["part(s)"]:
                part_urls.append(add_part_param_to_url(part))
        # ==================================

        # creating a url for the paint applied to the item
        if item["paint"] is not None:
            paint_url = add_paint_param_to_url(item["paint"])
        # ==================================

        stat = {
            "name": item["name"],
            "item_url": item_url,
            "paint_url": paint_url,
            "spells_url": spell_urls,
            'parts_url': part_urls,
        }
        stats.append(stat)
    return stats


# creates the base url and oversees the addition of correct params
def create_url(item):
    url = 'https://backpack.tf/classifieds?item='
    url = add_slot_param_to_url(item["slot"], url)
    url = add_name_param_to_url(item["name"], url)
    url = add_quality_param_to_url(item['quality'], url)

    if item['particle_effect'] is not None:
        url = add_particle_effect_param_to_url(item['particle_effect'], url)
    if item["killstreak"] is not None or item['slot'] == 'primary' or item['slot'] == 'secondary' or item['slot'] == 'melee':
        url = add_killstreak_param_to_url(item["killstreak"], url)
    # url = add_base_params(url, item)
    return url


# add a slot param to the url
def add_slot_param_to_url(slot, url):
    if slot == 'taunt':
        url = url + 'Taunt%3A%20'
    return url


# add a name param to the url
def add_name_param_to_url(name, url):
    return url + utils.format_name_for_url(name)


# add a quality param to the url
def add_quality_param_to_url(quality, url):
    return url + "&quality=" + quality


# add a killstreak param to the url
def add_killstreak_param_to_url(killstreak, url):
    return url + '&killstreak_tier=' + utils.convert_killstreak_tier(killstreak)


# add a particle param to the url
def add_particle_effect_param_to_url(particle_effect, url):
    return url + '&particle=' + str(config.particles_dict[particle_effect])


# add a spell param to the url
def add_spell_param_to_url(spell_name):
    return 'https://backpack.tf/classifieds?item=Halloween%20Spell%3A%20' + utils.format_name_for_url(spell_name)


# add a part param to the url
def add_part_param_to_url(part_name):
    if part_name in config.strange_part_inconsistencies:
        part_name = config.strange_part_inconsistencies[part_name]
    return 'https://backpack.tf/classifieds?item=Strange%20Part%3A%20' + utils.format_name_for_url(part_name)


# add a paint param to the url
def add_paint_param_to_url(paint_name):
    return 'https://backpack.tf/classifieds?item=' + utils.format_name_for_url(paint_name)
