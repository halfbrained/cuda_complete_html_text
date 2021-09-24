import os
import re
from cudatext import *


LOG = False

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'plugins.ini')
section = 'complete_html_text'
prefix = 'html text'

def bool_to_str(v): return '1' if v else '0'
def str_to_bool(s): return s=='1'

option_min_len = max(1, int(ini_read(fn_config, section, 'min_len', '3')))
option_case_sens = str_to_bool(ini_read(fn_config, section, 'case_sens', '1'))
option_max_lines = int(ini_read(fn_config, section, 'max_lines', '10000'))

pattern_tag_content = '(?<=>)[^<]+(?=<)'
pattern_word = '\w{{{},}}'.format(option_min_len)
pattern_word_c = re.compile(pattern_word)
pattern_word_start_c = re.compile('^\w*')
pattern_gtlt_c = re.compile('[><]')


def is_text_with_begin(s, begin):
    if option_case_sens:
        return s.startswith(begin)
    else:
        return s.lower().startswith(begin.lower())


def get_words_list(ed):
    if ed.get_line_count() > option_max_lines:
        return []

    # get tag content words
    _res = ed.action(EDACTION_FIND_ALL, pattern_tag_content, 'r') or []
    _tags_content = ' '.join(ed.get_text_substr(*r) for r in _res)
    words = set(pattern_word_c.findall(_tags_content))
    # get comment words
    _opts = 'rT1'   # regex + only in comments
    _res = ed.action(EDACTION_FIND_ALL, pattern_word, _opts) or []
    words.update(ed.get_text_substr(*r) for r in _res)

    return list(words)


def get_word(x, y):
    if not 0<=y<ed.get_line_count():
        return
    s = ed.get_text_line(y)
    if not 0<x<=len(s):
        return

    _ltext_rv = s[:x][::-1]
    m = pattern_word_start_c.search(_ltext_rv)
    x0 = x-m.end()  if m else  x

    m = pattern_word_start_c.search(s[x:])
    x1 = x+m.end()  if m else  x

    text1 = s[x0:x]
    text2 = s[x:x1]
    return (text1, text2)


def validate_caret_pos(edt, x, y):
    """ check if caret in tag text content or comment
    """
    if edt.get_token(TOKEN_GET_KIND, x,y) == 'c':
        return True     # caret in comment

    # verify caret inside >...<
    for nline in range(y, ed.get_line_count()):     # search forward for <
        s = edt.get_text_line(nline)
        pos = x  if nline == y else  0
        m = pattern_gtlt_c.search(s, pos)
        if m:
            if m[0] != '<':
                #pass;       LOG and print(f' -- validate 0: wrong match: <? {m[0]!r} @{m.start(), nline}')
                return False
            break

    for nline in range(y, -1, -1):     # search backward for >
        s = edt.get_text_line(nline)
        s = s[::-1]
        pos = len(s)-x  if nline == y else  0
        m = pattern_gtlt_c.search(s, pos)
        if m:
            #pass;       LOG and print(f' -- validate 1: match: >? {m[0]!r} @{m.start(), nline}')
            return m[0] == '>'
    #end for
    #pass;       LOG and print(f' -- validate 2: NO match')
    return False


class Command:

    def on_complete(self, ed_self):
        carets = ed_self.get_carets()
        if len(carets)!=1: return   # no multicaret
        x0, y0, x1, y1 = carets[0]
        if y1>=0: return    # don't allow selection

        # don't work inside CSS/PHP blocks
        lex = ed_self.get_prop(PROP_LEXER_CARET)
        if not 'HTML' in lex: return

        if not validate_caret_pos(ed_self, x0, y0): return   # check if caret in tag text  OR  comment

        # word to complete
        word = get_word(x0, y0)
        print(f' -- word: {word}')
        if not word:    return
        word1, word2 = word
        if not word1:   return # to fix https://github.com/Alexey-T/CudaText/issues/3175

        words = get_words_list(ed_self)
        if not words:   return
        print(f' -- words : {len(words)}')

        words.sort(key=lambda w: w.lower())
        #pass;      LOG and print('word:', word)
        #pass;      LOG and print('list:', words)

        words = [prefix+'|'+w for w in words
                 if is_text_with_begin(w, word1)
                 and w!=word1
                 and w!=(word1+word2)
                 ]

        ed_self.complete('\n'.join(words), len(word1), len(word2))
        return True


    def config(self):
        ini_write(fn_config, section, 'min_len', str(option_min_len))
        ini_write(fn_config, section, 'case_sens', bool_to_str(option_case_sens))
        ini_write(fn_config, section, 'max_lines', str(option_max_lines))
        file_open(fn_config)
