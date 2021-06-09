import re, sys
import pandas as pd

def write_html_page(df, type, subtype, url_type='video'):
    html = '<html>\n<body>\n'
    html += '<meta charset="utf-8">\n'
    html += '<p>\n'
    html += "<h1>%s</h1>" % (subtype)
    html += '<a href="index.html"><h2>back</h2></a>'

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
                           info="id:{} type:{}".format(row['vid'], type))

        if cnt % 5 == 4:
            html += "</tr>\n"

    html += "</table>\n"
    html += "</p>\n"
    html += "</body>\n</html>"
    return html


def write_index(df):
    types = list(df['type'].unique())
    html = """<html><body>
        <meta charset="utf-8">
        <h1>Index:</h1>"""
    for type in types:
        html += "<h2>%s</h2>" % (type)
        subtypes = list(set(df[df['type'] == type]['subtype'].tolist()))
        html += "<p style=\"word-wrap: break-word;white-space:pre-wrap;\">"
        for subtype in subtypes:
            html += "<a href=\"%s_%s.html\">%s</a>&nbsp&nbsp" % (type, subtype, subtype)
        # html += "</p>"
    html += "</body></html>"
    return html


if __name__ == '__main__':
    df = pd.read_csv('1.csv', encoding='utf-8-sig')
    df.columns=['type', 'subtype', 'vid', 'img_url', 'vid_url']
    html = write_index(df)
    with open('html/index.html', 'w') as f:
        f.write(html)

    types = list(df['type'].unique())
    for type in types:
        dftmp = df[df['type'] == type]
        subtypes = list(dftmp['subtype'].unique())
        for subtype in subtypes:
            html = write_html_page(dftmp[dftmp['subtype'] == subtype], type, subtype)
            with open('html/%s_%s.html' % (type, subtype), 'w') as f:
                f.write(html)
