import re, copy

import tldextract
from phonenumbers import PhoneNumber, PhoneNumberFormat, is_valid_number, format_number


def _obscure_email_part(part):
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

    user = _obscure_email_part(user)
    subdomain = _obscure_email_part(subdomain)
    domain = _obscure_email_part(domain)
    suffix = re.sub('[^.]', '*', suffix)  # always obscure the TLD and SLD

    return f'{user}@{subdomain}{"." if subdomain and domain else ""}{domain}{"." if domain and suffix else ""}{suffix}'


def obscure_phone(phone, output_format=PhoneNumberFormat.E164):
    if not isinstance(phone, PhoneNumber):
        raise ValueError
    if not is_valid_number(phone):
        raise ValueError
    if output_format not in (PhoneNumberFormat.E164,
                             PhoneNumberFormat.INTERNATIONAL,
                             PhoneNumberFormat.NATIONAL,
                             PhoneNumberFormat.RFC3966):
        raise ValueError

    # If phone has an extension, we remove it and save it so we can append it later
    extension = None
    if phone.extension is not None:
        # Save the extension
        extension = phone.extension
        # Clear the extension in phone
        phone = copy.copy(phone)
        phone.extension = None

    # Convert phone to a string
    phone_string = format_number(phone, output_format)

    # Replace all but the last two digits of phone_string with asterisks
    digit_count = sum(c.isdigit() for c in phone_string)
    phone_string_obscured = re.sub(r'\d', '*', phone_string, count=digit_count - 2)

    # If phone had an extension, append it to phone_string_obscured
    if extension is not None:
        if output_format == PhoneNumberFormat.INTERNATIONAL or output_format == PhoneNumberFormat.NATIONAL:
            phone_string_obscured = f'{phone_string_obscured} x{extension}'
        elif output_format == PhoneNumberFormat.RFC3966:
            phone_string_obscured = f'{phone_string_obscured};ext={extension}'

    return phone_string_obscured
