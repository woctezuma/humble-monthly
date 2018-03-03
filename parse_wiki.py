import re


def load_wiki_file(filename):
    relevant_prefix = '{{Bundle'

    with open(filename, encoding='utf8') as f:
        lines = [l.strip() for l in f.readlines() if l.startswith(relevant_prefix)]

    return lines


def parse_bundle_name(wiki_str):
    # Tokenize
    wiki_tokens = re.split('\|', wiki_str)

    bundle_name_prefix = 'Bundle='

    # Find the token corresponding to the bundle name
    bundle_token = [s for s in wiki_tokens if s.startswith(bundle_name_prefix)]

    # Extract the bundle name
    bundle_name = re.split('\'\'\'', bundle_token[0])[1]

    return bundle_name


def parse_game_name(wiki_str, verbose=False):
    # Tokenize and strip
    wiki_tokens = [s.strip() for s in re.split('\|', wiki_str)]

    game_name_prefix = 'title'
    game_name_suffix = 'Developer'

    # Check whether there is a game name among the tokens
    if any(s.startswith(game_name_prefix) for s in wiki_tokens):

        # Find the tokens corresponding to the game name
        ind_start = [count for (count, s) in enumerate(wiki_tokens) if s.startswith(game_name_prefix)]
        ind_end = [count for (count, s) in enumerate(wiki_tokens) if s.startswith(game_name_suffix)]

        if len(ind_end) > 0:
            game_token = ' | '.join(wiki_tokens[ind_start[0]:ind_end[0]])
        else:
            game_token = ' | '.join(wiki_tokens[ind_start[0]:])

        # Extract the game name
        game_element = re.split('title=', game_token)
        game_name = game_element[-1]

        # Remove any hyperlink
        hyperlink_tokens = re.split('\|', game_name)
        if len(hyperlink_tokens) > 1:
            if verbose:
                print(hyperlink_tokens)
            game_name = hyperlink_tokens[-1]

        # Further strip the game name
        game_name = game_name.replace('\'\'', '')
        game_name = game_name.replace('[', '')
        game_name = game_name.replace(']', '')
        game_name.strip()

    else:
        game_name = None

    return game_name


def build_dictionary(filename):
    bundles = dict()
    bundle_name = None

    bundle_entry_prefix = '{{BundleFirstRow'
    game_entry_prefix = '{{Bundle|'

    lines = load_wiki_file(filename)

    for wiki_str in lines:
        if wiki_str.startswith(bundle_entry_prefix):
            bundle_name = parse_bundle_name(wiki_str)

            game_name = parse_game_name(wiki_str)

            bundles[bundle_name] = []
            if game_name is not None:
                bundles[bundle_name].append(game_name)

        elif wiki_str.startswith(game_entry_prefix):
            game_name = parse_game_name(wiki_str)
            bundles[bundle_name].append(game_name)
        else:
            continue

    return bundles


if __name__ == '__main__':
    filename = 'wiki_humble_monthly.txt'
    bundles = build_dictionary(filename)
    print(bundles)
