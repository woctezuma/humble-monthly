import re


def load_wiki_file(filename):
    relevant_prefix = '{{Bundle'

    with open(filename) as f:
        lines = [l.strip() for l in f.readlines() if l.startswith(relevant_prefix)]

    return lines


def parse_bundle_name(wiki_tokens):
    bundle_name_prefix = 'Bundle='

    bundle_token = [s for s in wiki_tokens if s.startswith(bundle_name_prefix)]

    bundle_name = re.split('\'\'\'', bundle_token[0])[1]

    return bundle_name


def parse_game_name(wiki_tokens):
    game_name_prefix = 'title'

    game_token = [s for s in wiki_tokens if s.startswith(game_name_prefix)]

    if len(game_token) == 0:
        game_name = None
    else:

        # Parse Wiki entries for which the game title is a hyperlink
        game_element = re.split('\[\[|\]', game_token[0])
        try:
            game_name = game_element[1]
        except IndexError:
            # Parse Wiki entries for which the game title is NOT a hyperlink
            game_name = re.split('\'', game_element[0])[2]

        # Filter Wiki disambiguation text for video games
        disambiguation_text = '(video game)'
        game_name = game_name.rsplit(disambiguation_text)[0].strip()

    return game_name


def build_dictionary(filename):
    bundles = dict()
    bundle_name = None

    bundle_entry_prefix = '{{BundleFirstRow'
    game_entry_prefix = '{{Bundle|'

    lines = load_wiki_file(filename)

    for l in lines:
        wiki_tokens = re.split('\|', l)

        if l.startswith(bundle_entry_prefix):
            bundle_name = parse_bundle_name(wiki_tokens)

            game_name = parse_game_name(wiki_tokens)

            bundles[bundle_name] = []
            if game_name is not None:
                bundles[bundle_name].append(game_name)

        elif l.startswith(game_entry_prefix):
            game_name = parse_game_name(wiki_tokens)
            bundles[bundle_name].append(game_name)
        else:
            continue

    return bundles


if __name__ == '__main__':
    filename = 'wiki_humble_monthly.txt'
    bundles = build_dictionary(filename)
    print(bundles)
