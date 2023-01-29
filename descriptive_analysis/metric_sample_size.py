import pandas as pd
import itertools

def check_benchmarking_feasibility(df, dimensions, func, metric_name, col1, col2=None):
    # func: which operation to perform depending on the metrics. currently only supports 'division', 'ratio', 'median', 'mean'
    # col1, col2: input for the func
    # dimensions: all the dimensions used as slicers in the dashboard. the user might use 1 to n slicers at the same time. slicer only supports single select
    
    # check if all inputs are valid
    assert [i in list(df) for i in dimensions + [col1]]
    if col2 is not None:
        assert col2 in list(df)
    for dimension in dimensions:
        df[dimension] = df[dimension].fillna('')     # fillna for all dimensions used in groupby
    df_out = pd.DataFrame()  # init output df
    
    def apply_formula(grouped_df, func, metric_name, col1, col2=None):
        # need to ensure the combinations of dimension end up having >=5 samples, else do not calculate and output None
        d = {}
        d[f'{metric_name}_sample_size'] = len(grouped_df)
        if d[f'{metric_name}_sample_size'] >= 5:
            def safe_divide(a, b):
                if b == 0:
                    return 0.0
                else:
                    return round(a/b, 3)
            if func == 'division':
                d[metric_name] = safe_divide(grouped_df[col1].sum(), grouped_df[col2].sum())
            elif func == 'ratio':
                d[metric_name] = safe_divide(grouped_df[col1].sum(), len(grouped_df))
            elif func == 'median':
                d[metric_name] = grouped_df[col1].median()
            elif func == 'mean':
                d[metric_name] = grouped_df[col1].mean()
        else:
            d[metric_name] = None
        return pd.Series(d)

    # groupby and compute metrics for each combination of dimensions
    df_gb = df.groupby(dimensions).apply(lambda x: apply_formula(x, func, metric_name, col1, col2)).reset_index()
    df_out = df_gb

    # case when 1 or more dimensions are 'All':
    dimensions_all = [itertools.combinations(dimensions, i+1) for i in range(len(dimensions))]
    dimensions_all = [i for v in dimensions_all for i in v]
    for cols_all in dimensions_all:
        df2 = df.copy()
        for col in cols_all:
            df2.loc[:, col] = 'All'
        df2_gb = df2.groupby(dimensions).apply(lambda x: apply_formula(x, func, metric_name, col1, col2)).reset_index()
        df_out = pd.concat([df_out, df2_gb])
    df_out[f'{metric_name}_sample_size'] = df_out[f'{metric_name}_sample_size'].astype(int)
    print(f"Total combinations: {len(df_out)}, is_NA(sample_size <5): {len(df_out[df_out[metric_name].isna()])}")
    return df_out


df_benchmarking = check_benchmarking_feasibility(df, dimensions, func='ratio', metric_name=metric_name, col1='oa')
