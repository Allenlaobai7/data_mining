import re, sys, os
import pandas as pd
import argparse

def write_html_page(df, htg, url_type='video'):
    html = '<html>\n<body>\n'
    html += '<meta charset="utf-8">\n'
    html += '<p>\n'
    html += "<h1>%s</h1>" % (htg)

    html += '<table border="1">\n'

    for cnt, row in df.iterrows():
        if cnt % 5 == 0:
            html += '<tr>\n'

        if url_type == 'video':
            html += """
                <td bgcolor={color}>
                    <video width="180" height="240" controls poster="{poster}" preload="none">
                    <source src="{src}" type="video/mp4"> </video>
                    <br> {info}
                </td>
                """.format(color='white', poster=row['img_url'], src=row['vid_url'],
                           info="id:{}".format(row['vid']))

        if cnt % 5 == 4:
            html += "</tr>\n"

    html += "</table>\n"
    html += "</p>\n"
    html += "</body>\n</html>"
    return html


def process(args):
    df = pd.read_csv(args.inputpath)
    if not os.path.exists(args.output_folder):
        os.mkdir(args.output_folder)
    ids = list(df['id'].unique())
    for id in ids:
        html = write_html_page(df[df['id'] == id], id)
        with open(os.path.join(args.output_folder, "%s.html" % (id)), 'w') as f:
            f.write(html)


def main():
    parser = argparse.ArgumentParser(description='generate web data for review')
    parser.add_argument('inputpath', type=str)
    parser.add_argument('output_folder', help='../html/{}')
    args = parser.parse_args()
    process(args)
    return 0

if __name__ == '__main__':
    main()
