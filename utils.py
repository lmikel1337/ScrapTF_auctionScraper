import config


# uf called, forces a user to enter a value the len of an auction id
# Note that it doesn't check whether it's a valid id, only that it has the right len
def set_auction_id():
    for j in range(0, 100):
        user_input = input("Enter AUC_ID: ")
        if user_input == 0:
            break
        elif len(user_input) == 6:
            config.auction_id = user_input
            print('AUC_ID set')
            break


# converts the quality id which both scrap.tf and bp.tf use to their names for easier reading
def get_alt_quality(quality):
    if quality == '11':
        return 'strange'
    elif quality == '5':
        return 'unusual'
    elif quality == '1':
        return 'genuine'
    elif quality == '6':
        return 'unique'
    elif quality == '15':
        return 'decorated weapon'
    else:
        return quality


# converts name of the killstreak tier to the id system bp.tf uses
def convert_killstreak_tier(killstreak_tier):
    if killstreak_tier is None:
        return '0'
    elif killstreak_tier == 'Basic Killstreak':
        return '1'
    elif killstreak_tier == 'Specialized Killstreak':
        return '2'
    elif killstreak_tier == 'Professional Killstreak':
        return '3'


# formats the input string by adding %20 between each word
def format_name_for_url(name):
    name = name.split(' ')
    fin_name = ''
    for word in name:
        if 'Strange' not in word:
            fin_name += word + '%20'
    return fin_name[0:-3]
