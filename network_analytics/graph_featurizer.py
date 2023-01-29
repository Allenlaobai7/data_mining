from logging import raiseExceptions
import networkx as nx
import pandas as pd
import argparse
from collections import Counter
from datetime import datetime

class GraphFeaturizer(object):
    def __init__(self):
        pass

    def run(self, graph_input_path, feature_type='default', suffix=''):
        # suffix: suffix to be added for output columns. default metric name will be returned if no suffix given
        G = nx.read_gpickle(graph_input_path)
        attrs = pd.DataFrame(G.nodes(), columns=['node'])
        print(f'time: {datetime.now()}, start adding attributes.')
        if feature_type == 'default':
            attrs = self.add_default_graph_attributes(attrs, G)
        elif feature_type == 'directed':
            attrs = self.add_directed_graph_attributes(attrs, G)
        else:
            raiseExceptions('wrong feature type. should be default or directed')
            return
        if suffix != '': # add suffix to column names
            attrs.columns = ['node'] + [f'{i}_{suffix}' for i in list(attrs.columns)[1:]]
        attrs = attrs.set_index('node').to_dict('index')
        nx.set_node_attributes(G, attrs)
        print(f'time: {datetime.now()}, completed all.')
        nx.write_gpickle(G, graph_input_path) # overwrite inputpath
        return G

    def add_default_graph_attributes(self, df, G, weight="weight"):  
        degree_dict = dict(G.degree())
        df['degree'] = df['node'].apply(lambda x: degree_dict[x])

        clustering_coe_dict = nx.clustering(G)
        df['clustering_coe'] = df['node'].apply(lambda x: clustering_coe_dict[x])
        print(f'time: {datetime.now()}, completed degree + clustering coe.')

        def calculate_median(a):
            a = sorted(a)
            if len(a) % 2 ==0:
                return (a[int(len(a) / 2 -1)] + a[int(len(a) / 2)])/2
            else:
                return a[int(len(a) // 2)]

        def get_path_related(row, G):
            shortest_path_length = [v for k, v in nx.shortest_path_length(G, row.node).items() if k != row.node]

            row['avg_shortest_path'] = None
            row['eccentricity'] = None
            row['radius'] = None
            row['median_path'] = None
            if len(shortest_path_length)>0:
                row['avg_shortest_path'] = sum(shortest_path_length) / len(shortest_path_length)
                row['eccentricity'] = max(shortest_path_length)
                row['radius'] = min(shortest_path_length)
                row['median_path'] = calculate_median(shortest_path_length)
            return row
        df = df.apply(lambda x: get_path_related(x, G), axis=1)
        df = df.fillna({'avg_shortest_path': max(df['avg_shortest_path']),
                                            'eccentricity': max(df['eccentricity']),
                                            'radius': max(df['radius']),
                                            'median_path': max(df['median_path'])})
        
        print(f'time: {datetime.now()}, completed path related attributes.')

        connected_component_size_dict = {key: len(comp) for comp in nx.connected_components(G) for key in comp}
        df['connected_component_size'] = df['node'].apply(lambda x: connected_component_size_dict[x])
        
        degree_centrality_dict = nx.degree_centrality(G)
        df['degree_centrality'] = df['node'].apply(lambda x: degree_centrality_dict[x])
        
        closeness_centrality_dict = nx.closeness_centrality(G)
        df['closeness_centrality'] = df['node'].apply(lambda x: closeness_centrality_dict[x])

        betweenness_centrality_dict = nx.betweenness_centrality(G)
        df['betweenness_centrality'] = df['node'].apply(lambda x: betweenness_centrality_dict[x])

        # TODO: figure out how to shorten the run time for vitality
        # closeness_vitality_dict = nx.closeness_vitality(G)
        # df['closeness_vitality'] = df['node'].apply(lambda x: closeness_vitality_dict[x])

        def calculate_h_score(G, node): # h_score = max of n, where n = number of connections with degree >= n
            neighbors = sorted([G.degree(i) for i in nx.neighbors(G, node)], reverse=True)
            h_score = 0
            for i, v in enumerate(neighbors):
                if v < i + 1:
                    break
                h_score = i+1
            return h_score
        df['h_score'] = df['node'].apply(lambda x: calculate_h_score(G, x))

        # Coreness
        bridges = list(nx.bridges(G))
        node_bridge_cnt_dict = Counter([i for v in bridges for i in v]) # how many bridges the node is in
        df['node_bridge_cnt'] = df['node'].apply(lambda x: node_bridge_cnt_dict.get(x, 0))

        core_number_dict = nx.core_number(G)
        df['core_number'] = df['node'].apply(lambda x: core_number_dict.get(x, 0))

        # Structural hole (heavy compute. 1h each)
        esize_dict = nx.effective_size(G, weight=weight)
        efficiency_dict = {n: v / G.degree(n) for n, v in esize_dict.items()}
        df['effective_size'] = df['node'].apply(lambda x: esize_dict.get(x, 0))
        df['efficiency'] = df['node'].apply(lambda x: efficiency_dict.get(x, 0))

        constraint_dict = nx.constraint(G, weight=weight)
        df['constraint'] = df['node'].apply(lambda x: constraint_dict.get(x, 0))
        return df

    def add_directed_graph_attributes(self, df, G, weight="weight"):
        assert nx.is_directed(G)
        in_degree_dict = dict(G.in_degree())
        df['in_degree'] = df['node'].apply(lambda x: in_degree_dict[x])

        out_degree_dict = dict(G.out_degree())
        df['out_degree'] = df['node'].apply(lambda x: out_degree_dict[x])

        in_degree_centrality_dict = nx.in_degree_centrality(G)
        df['in_degree_centrality'] = df['node'].apply(lambda x: in_degree_centrality_dict[x])

        out_degree_centrality_dict = nx.out_degree_centrality(G)
        df['out_degree_centrality'] = df['node'].apply(lambda x: out_degree_centrality_dict[x])

        print(f'time: {datetime.now()}, completed in/out degree and degree centrality.')

        pr_dict = nx.pagerank(G, alpha=0.9, weight=weight)
        df['pagerank_weighted'] = df['node'].apply(lambda x: pr_dict[x])

        print(f'time: {datetime.now()}, completed pagerank.')
        
        hits_dict = nx.hits(G)
        df['hits_auth'] = df['node'].apply(lambda x: hits_dict[0][x])
        df['hits_hub'] = df['node'].apply(lambda x: hits_dict[1][x])
        return df
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='add node attributes to graph and save back to same location')
    parser.add_argument('graph_input', type=str)
    parser.add_argument('--feature_type', default='default', type=str, help='default or directed')
    parser.add_argument('--suffix', default='', type=str)
    args = parser.parse_args()
    graphfeaturizer = GraphFeaturizer()
    graphfeaturizer.run(args.graph_input, args.feature_type, args.suffix)