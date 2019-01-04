#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from multiprocessing.dummy import Pool

import re
import requests
import sys

ATOM = 'atom'
PUNCT = 'punctuation'
THREADS = 10
TYPE = 'type'
WORD = 'word'
WORD_RE = re.compile('(\w+)', re.UNICODE)
FROM_LANG = 'spa'
DEST_LANG = 'eng'

def usage():
    print('Modo de uso: %s [{enes|esen}] "<frase>"' % sys.argv[0], file=sys.stderr)

def setLangs(langs):
    global FROM_LANG, DEST_LANG
    if langs == 'enes':
        (FROM_LANG, DEST_LANG) = ('eng', 'spa')
    elif langs == 'esen':
        (FROM_LANG, DEST_LANG) = ('spa', 'eng')
    else:
        print('Especificación de lenguajes inválida "%s".\nenes = English -> Espangli(en español), esen = Español -> Espangli(en inglés)' % langs, file=sys.stderr)
        usage()
        sys.exit(-2)

def splitTerms(phrase):
    terms = []
    for term in WORD_RE.split(phrase):
        atom = {ATOM: term}
        if WORD_RE.match(term):
            atom[TYPE] = WORD
        else:
            atom[TYPE] = PUNCT
        terms.append(atom)
    return terms

def translateTerm(term):
    translation = term
    resp = requests.get('https://glosbe.com/gapi/translate', params={'from': FROM_LANG, 'dest': DEST_LANG, 'format': 'json', 'phrase': term.lower()}).json()
    if resp['result'] == 'ok' and len(resp['tuc']) > 0:
        if 'phrase' in resp['tuc'][0] and 'text' in resp['tuc'][0]['phrase']:
            translation = resp['tuc'][0]['phrase']['text']
        elif 'meanings' in resp['tuc'][0] and len(resp['tuc'][0]['meanings']) > 0:
            print('No se pudo traducir "%s", pero se conoce el significado: "%s"' % (term, resp['tuc'][0]['meanings'][0]['text']), file=sys.stderr)
        else:
            print('No se pudo traducir "%s"' % term, file=sys.stderr)
    else:
        print('No se pudo traducir "%s"' % term, file=sys.stderr)
    return translation

def translateAtom(atom):
    translation = atom[ATOM]
    if atom[TYPE] == WORD:
        translation = translateTerm(translation)
    return translation

def main(phrase, threads=THREADS):
    terms = splitTerms(phrase)
    pool = Pool(threads)
    translation = pool.map(translateAtom, terms)
    pool.close()
    pool.join()
    print(''.join(translation).encode('utf-8'))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1].decode('utf-8'))
    elif len(sys.argv) == 3:
        setLangs(sys.argv[1])
        main(sys.argv[2].decode('utf-8'))
    else:
        usage()
        sys.exit(-1)

