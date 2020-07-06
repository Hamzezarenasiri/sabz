"""
set of utilities to use in apps
"""

maketrans = lambda A, B: dict((ord(a), b) for a, b in zip(A, B))


def normalize_text(input_str):
    """
    function to change farsi characters to standard form.
    :param input_str
    :return: a standard string
    """
    translation = maketrans(u'٤٥٦كي؛٪۱١۲٢۳٣۴۵۶۷٧۸٨۹٩۰٠', u'456کی;%11223345677889900')
    try:
        return input_str.strip().translate(translation)
    except:
        return input_str


def normalize_num(input_str):
    """
    function to change farsi characters to standard form.
    :param input_str
    :return: a standard string
    """
    translation = maketrans(u'٤٥٦۱١۲٢۳٣۴۵۶۷٧۸٨۹٩۰٠', u'45611223345677889900')
    try:
        return input_str.strip().translate(translation)
    except:
        return input_str
