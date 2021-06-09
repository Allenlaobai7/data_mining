#! /usr/bin/env python3

import sys
import os
import argparse
import glob
import logging

from utils_web.web import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

def get_filenames(dirname):
    filenames = glob.glob(os.path.join(dirname, '*.txt'))
    return sorted(filenames)

def process(args):
    filenames1 = get_filenames(args.input1)
    base1 = (os.path.basename(filename) for filename in filenames1)
    filenames2 = get_filenames(args.input2)
    base2 = (os.path.basename(filename) for filename in filenames2)
    all_bases = set(base1) | set(base2)

    urls = get_urls(args.url)

    html = get_html_compare(all_bases, args.input1, args.input2, urls)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write('{}\n'.format(html))

def main():
    parser = argparse.ArgumentParser(description='Generate HTML output.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input1', help='Input directory 1')
    parser.add_argument('input2', help='Input directory 2')
    parser.add_argument('url', help='URL file')
    parser.add_argument('output', help='Output filename')
    args = parser.parse_args()
    process(args)
    return 0

if __name__ == '__main__':
    sys.exit(main())
