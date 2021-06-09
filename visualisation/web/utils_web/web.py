# import pkg_resources
import os
import pandas as pd
import csv
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

# TEMPLATE_DIR = pkg_resources.resource_filename(__package__, 'resources')
TEMPLATE_DIR = './resources'
file_loader = FileSystemLoader(TEMPLATE_DIR)
env = Environment(loader=file_loader)


def get_html_row(row):
    data = ['<tr>']
    data.append('\t<td>{}</td>'.format(row.col1))
    data.append('\t<td>{}</td>'.format(row.col2))
    data.append('</tr>')

    return data

def get_table_html(df_pred):
    output = []

    for row in df_pred.itertuples(index=False):
        tr = get_html_row(row)
        output += tr

    if len(output) > 0:
        header = []
        header.append('<table class="table table-bordered table-striped">')
        header.append('<tbody>')
        header.append('<tr>')
        header.append('\t<th scope="col">col1</th>')
        header.append('\t<th scope="col">col2</th>')
        header.append('</tr>')
        footer = []
        footer.append('</tbody>')
        footer.append('</table>')
        output = header + output + footer

    return '\n'.join(output)

def get_container_html(row, pred_names):
    df_pred = pd.DataFrame(zip(row.col1, row.col2), columns=pred_names)
    table_html = get_table_html(df_pred)

    if len(table_html) > 0:
        id, url = row.vid, row.vid_url
        if url is None:
            return ''
        container_template = env.get_template('container.html.template')
        container_html = container_template.render(id=id, url=url, table=table_html)

    return container_html

def get_html(df, pred_names):
    df['container_html'] = df.apply(lambda x: get_container_html(x, pred_names), axis=1)
    df = df[df['container_html'].map(lambda x: len(x) > 0)]
    containers = df['container_html'].tolist()

    index_template = env.get_template('index.html.template')
    index_html = index_template.render(containers=containers)

    return index_html

def get_container_html_compare(filename1, filename2, base, urls):
    file1 = Path(filename1)
    if file1.is_file():
        table_html_1 = get_table_html(filename1)

    else:
        table_html_1 = ''

    file2 = Path(filename2)
    if file2.is_file():
        table_html_2 = get_table_html(filename2)

    else:
        table_html_2 = ''

    if table_html_1 == '' and table_html_2 == '':
        return ''
    else:
        if table_html_1 == '':
            table_html_1 = '<p>No keyword</p>'
        if table_html_2 == '':
            table_html_2 = '<p>No keyword</p>'

        id, _ = os.path.splitext(base)
        url = urls.get(id)
        if url is None:
            return ''
        container_template = env.get_template('container.html.compare.template')
        container_html = container_template.render(id=id, url=url, table1=table_html_1, table2=table_html_2)

    return container_html

def get_html_compare(all_bases, input_dir_1, input_dir_2, urls):
    containers = []

    for base in all_bases:
        filename1 = os.path.join(input_dir_1, base)
        filename2 = os.path.join(input_dir_2, base)
        container_html = get_container_html_compare(filename1, filename2, base, urls)
        if len(container_html) > 0:
            containers.append(container_html)

    index_template = env.get_template('index.html.template')
    index_html = index_template.render(containers=containers)

    return index_html
