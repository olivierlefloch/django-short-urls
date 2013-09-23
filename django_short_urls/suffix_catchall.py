import re


VALID_REDIRECTIONS = ('recruiter', 'share', 'search')


def get_hash_from(path):
    '''
    Parses the ``path`` and returns a tuple with the hash and the redirection parameter if any
    '''

    match = re.match(r'(.+)/(%s)$' % '|'.join(VALID_REDIRECTIONS), path)

    if not match:
        return path, None

    return match.group(1), match.group(2)
