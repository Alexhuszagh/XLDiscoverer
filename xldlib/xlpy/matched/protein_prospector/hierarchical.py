'''
    XlPy/Matched/Protein_Prospector/hierarchical
    _____________________________________________

    Parses the hierarchical mod format from Protein Prospector.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# SINGLE LEVEL
# ------------


def level(string, lst=None):
    '''
    Parse new level by extracting paired ().
    :
        >>> level"(1&(18|22))|(13&22)"
        ['1&(18|22)', '13&22']
    '''

    if lst is None:
        lst = []

    while '(' in string:
        i = string.find('(')+1
        index = i
        step = 1

        while step != 0:
            if string[index] == '(':
                step += 1
            elif string[index] == ')':
                step -= 1
            index += 1

        lst.append(string[i:index - 1])
        string = string[index:]

    return lst


def amp(string):
    '''
    Combine integer preceeding '&' with all of level.
    :
        >>> amp('1&(18|22)')
        ['1&18|22']
    '''

    lst = []

    i = string.find('&(')
    tmp = string[0:i]
    child = []
    level(string[i:], child)

    lst.extend('{0}&{1}'.format(tmp, i) for i in child)

    return lst


def pipe(string):
    '''
    Splits pipe and combines amp with all in pipe.
    :
        >>> pipe('1&18|22')
        ['1&18', '1&22']
    '''

    lst = []

    if '&' not in string:
        lst += string.split('|')

    else:
        i = string.rfind('&')
        tmp = string[:i]
        child = string[i+1:].split('|')
        lst.extend('{0}&{1}'.format(tmp, e) for e in child)

    return lst


# PARSER
# ------


def parse(string):
    '''
    Processes current level, with '(' starting new level,
    '&(' starting new level with hierarchy, while '|' being
    within a level.
    '''

    if string[0] == '(':
        return level(string)

    elif '&(' in string:
        return amp(string)

    else:
        return pipe(string)


# RECURSE
# -------


def flatten(string):
    '''
    Recursively flattens clustered levels.
        string -- mod position string in hierarchical format

        >>> flatten("((1&(18|22))|(13&22))")
        ['1&18', '1&22', '13&22']
    '''

    if (string[0] != '(') and not ('&(' in string or '|' in string):
        return [string]

    else:
        child = parse(string)
        lst = []
        for string in child:
            lst.extend(flatten(string))
        return lst
