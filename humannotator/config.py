# standard library
import configparser
from collections import namedtuple
from pathlib import Path


PATH_LIB = Path(__file__).resolve().parent.parent
CFG_FILE  = PATH_LIB / 'config.ini'
encoding = 'utf-8' # encoding of ini file only

QUOTECHAR = '"'
SEPARATORS = ['\n', '\t', ',', ';']
BOOLEAN_STATES = {
    'true': True, 'false': False,
    't':    True, 'f':     False,
    '1':    True, '0':     False,
    'yes':  True, 'no':    False,
    'on':   True, 'off':   False,
}


def load_ini(filename):
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(filename, encoding=encoding)
    return ini


def config_from_ini(ini):
    Config = namedtuple('Config', [section for section in ini])
    sections = list()
    for section in ini:
        sections.append(get_section(ini, section))
    return Config._make(sections)


def ntuple_from_section(ini, section):
    return namedtuple(section, [item for item in ini[section]])


def get_section(ini, section, func=None):
    Section = ntuple_from_section(ini, section)
    values = list()
    for item in ini[section]:
        value = parse_value(ini[section][item])
        if func:
            value = func(value)
        values.append(value)
    return Section._make(values)


def parse_value(value):
    value = value.strip('\n ')
    try: return int(value)
    except ValueError: pass
    try: return float(value)
    except ValueError: pass

    if value[:1] == QUOTECHAR and value[-1:] == QUOTECHAR:
        return value.strip(QUOTECHAR)
    if value[:1] == '[' and value[-1:] == ']':
        return get_list(value[1:-1])
    if any(item == value.lower() for item in BOOLEAN_STATES):
        return BOOLEAN_STATES[value.lower()]
    return value


def get_list(value):
    for sep in SEPARATORS:
        value = value.strip('\n').replace(sep, ',')
    lst = [i.strip() for i in value.split(',') if i.strip() is not '']
    if len(lst) > 1:
        return lst
    return value


# easy access to settings and paths
config = load_ini(CFG_FILE)
KEYS      = get_section(config, 'KEYS')
ELEMENTS  = get_section(config, 'ELEMENTS')
PATHS     = get_section(
    config,
    'PATHS',
    func=lambda x: PATH_LIB / x[1:] if x.startswith('/') else Path(x)
)