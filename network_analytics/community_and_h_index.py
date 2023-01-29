import pandas as pd
import networkx as nx
import networkx.algorithms.community as nx_comm

G = nx.read_gpickle(f"data/graph_output/graph.gpickle")

# apply louvain algo and output multiple versions of communities
optimal_partition_idx = 0 # record the index
partitions = nx_comm.louvain_partitions(G, weight='weight', resolution=0.8, seed=42)
for i, partition in enumerate(partitions):
    print(f'########## step {i} #########')
    print(f"modularity: {nx_comm.modularity(G, communities = partition, weight='weight')}")
    print(f"coverage and performance: {nx_comm.partition_quality(G, partition)}")
    print(f'community count: {len(partition)}')
    if i !=0: # do not print the 1st pass because too large
        print('community sizes:', ', '.join([str(j) for j in sorted([len(i) for i in partition])]))

    # choose a suitable number as the optimal output
    if len(partition) >= 100 and len(partition) < 300:
        print('chose this partition because it falls between a optimal range')
        optimal_partition_idx = i

# produce the partitions again using the same parameters, save the optimal communities TODO: learn generator behaviour
partitions = nx_comm.louvain_partitions(G, weight='weight', resolution=0.8, seed=42)
for i, partition in enumerate(partitions):
    if i == optimal_partition_idx:
        communities = partition
        break

print(f'########## Optimal communities #########')
print(f"modularity: {nx_comm.modularity(G, communities = communities, weight='weight')}")
print(f"coverage and performance: {nx_comm.partition_quality(G, partition)}")
print(f'community count: {len(communities)}')
print('community sizes:', ', '.join([str(j) for j in sorted([len(i) for i in communities])]))
communities = sorted([[len(i), i] for i in communities], key=lambda x: x[0], reverse=True) # sort by community size
# community dict format: {label: [community size, {nodes}]}, e.g {1:[2, {5232,5245}]} 
communities = {idx+1: communities[idx] for idx in range(len(communities))} 

print(f'########## Large communities #########')
# large_communities -> final output of the algo
large_communities = nx_comm.louvain_communities(G, weight='weight', resolution=0.8, seed=42) # same parameters as above
print(f"modularity: {nx_comm.modularity(G, communities = large_communities, weight='weight')}")
print(f"coverage and performance: {nx_comm.partition_quality(G, large_communities)}")
print(f'community count: {len(large_communities)}')
print('community sizes:', ', '.join([str(j) for j in sorted([len(i) for i in large_communities])]))
large_communities = sorted([[len(i), i] for i in large_communities], key=lambda x: x[0], reverse=True) # sort by community size
# community dict format: {label: [community size, {nodes}]}, e.g {1:[2, {5232,5245}]} 
large_communities = {idx+1: large_communities[idx] for idx in range(len(large_communities))} 

# calculate H index in the community setting (considering local influence and global influence)
G_inter = G.copy() # create a graph with only inter-community edges
h_score_intra, h_score_inter = {}, {}
dict_community_label, dict_large_community_label = {}, {}

def calculate_h_score(G, node): # h_score = max of n, where n = number of connections with degree >= n
    neighbors = sorted([G.degree(i) for i in nx.neighbors(G, node)], reverse=True)
    h_score = 0
    for i, v in enumerate(neighbors):
        if v < i + 1:
            break
        h_score = i+1
    return h_score

lst_info_community = []
for i, item in communities.items():
    size, community = item
    G_community = G.subgraph(community) # create a subgraph for this cummunity
    community_edge_cnt = [[sorted(i) for i in nx.edges(G, node)] for node in community] # get all edges (intra + inter)
    community_edge_cnt = [i for v in community_edge_cnt for i in v] # flatten the list
    community_edge_cnt = len(set([str(i[0]) + str(i[1]) for i in community_edge_cnt])) # calculate unique edge cnt
    community_intra_edge_cnt = G_community.number_of_edges()
    community_inter_edge_cnt = community_edge_cnt - community_intra_edge_cnt # all the going out edges
    community_intra_edge_cnt = community_intra_edge_cnt * 2 # * 2 for intra edges
    community_intra_edge_ratio = round(community_intra_edge_cnt/(community_intra_edge_cnt + community_inter_edge_cnt), 3)
    community_avg_intra_edge_cnt = round(community_intra_edge_cnt/ size, 3)
    community_avg_inter_edge_cnt = round(community_inter_edge_cnt/ size, 3)
    lst_info_community.append([i, size, community_intra_edge_cnt, community_inter_edge_cnt,
        community_intra_edge_ratio, community_avg_intra_edge_cnt, community_avg_inter_edge_cnt])

    G_inter.remove_edges_from(G_community.edges()) # remove all intra-edges of this community from G_inter

    # calculate h-index for nodes in this community, considering only intra-community edges
    for node in community:
        dict_community_label[node] = i
        h_score_intra[node] = calculate_h_score(G_community, node)

lst_info_large_community = []
for i, item in large_communities.items():
    size, community = item
    G_community = G.subgraph(community) # create a subgraph for this cummunity
    community_edge_cnt = [[sorted(i) for i in nx.edges(G, node)] for node in community] # get all edges (intra + inter)
    community_edge_cnt = [i for v in community_edge_cnt for i in v] # flatten the list
    community_edge_cnt = len(set([str(i[0]) + str(i[1]) for i in community_edge_cnt])) # calculate unique edge cnt
    community_intra_edge_cnt = G_community.number_of_edges()
    community_inter_edge_cnt = community_edge_cnt - community_intra_edge_cnt # all the going out edges
    community_intra_edge_cnt = community_intra_edge_cnt * 2 # * 2 for intra edges
    community_intra_edge_ratio = round(community_intra_edge_cnt/(community_intra_edge_cnt + community_inter_edge_cnt), 3)
    community_avg_intra_edge_cnt = round(community_intra_edge_cnt/ size, 3)
    community_avg_inter_edge_cnt = round(community_inter_edge_cnt/ size, 3)

    lst_info_large_community.append([i, size, community_intra_edge_cnt, community_inter_edge_cnt,
        community_intra_edge_ratio, community_avg_intra_edge_cnt, community_avg_inter_edge_cnt])
    
    for node in community:
        dict_large_community_label[node] = i

# calculate h-index for all nodes, considering only inter-community edges.
for node in G_inter.nodes:
    h_score_inter[node] = calculate_h_score(G_inter, node)
print(len(h_score_intra), len(h_score_inter))

df_info_community = pd.DataFrame(lst_info_community, columns=['community_label', 'community_size', 
    'community_intra_edge_cnt', 'community_inter_edge_cnt', 'community_intra_edge_ratio',
    'community_avg_intra_edge_cnt', 'community_avg_inter_edge_cnt'])
df_info_large_community = pd.DataFrame(lst_info_large_community, columns=['large_community_label', 'large_community_size', 
    'large_community_intra_edge_cnt', 'large_community_inter_edge_cnt', 'large_community_intra_edge_ratio',
    'large_community_avg_intra_edge_cnt', 'large_community_avg_inter_edge_cnt'])

attrs = pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient='index')
attrs['node'] = attrs.index
attrs['community_label'] = attrs['node'].apply(lambda x: dict_community_label[x])
attrs['large_community_label'] = attrs['node'].apply(lambda x: dict_large_community_label[x])
attrs['h_index_intra'] = attrs['node'].apply(lambda x: h_score_intra.get(x,0))
attrs['h_index_inter'] = attrs['node'].apply(lambda x: h_score_inter.get(x,0))
# create weighted score based on h_index_intra and h_index_inter
attrs['h_index_community_weighted'] = 0.2 * attrs['h_index_intra'] + 0.8 * attrs['h_index_inter']
