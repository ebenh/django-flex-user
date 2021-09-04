import re

import tldextract


def _obfuscate_email_part(part):
    """
    For parts longer than three characters, we reveal the first two characters and obscure the rest.

    Parts up to three characters long are handled as special cases.

    We reveal no more than 50% of the characters for any part.

    :param part:
    :return:
    """
    if not part:
        return part  # part is None or the empty string, nothing to obscure

    length = len(part)
    if length == 1:
        return '*'  # 0% revealed, 100% obscured

    if length == 2:
        return part[:1] + '*'  # 50% revealed, 50% obscured

    if length == 3:
        return part[:1] + '**'  # 33% revealed, 66% obscured

    if length > 3:
        return part[:2] + '*' * (length - 2)  # At most 50% revealed, At least 50% obscured


def obscure_email(email):
    if not email:
        return ''

    user, host = email.split('@')
    subdomain, domain, suffix = tldextract.extract(host)

    user = _obfuscate_email_part(user)
    subdomain = _obfuscate_email_part(subdomain)
    domain = _obfuscate_email_part(domain)
    suffix = re.sub('[^.]', '*', suffix)  # always obscure the TLD and SLD

    return f'{user}@{subdomain}{"." if subdomain and domain else ""}{domain}{"." if domain and suffix else ""}{suffix}'
