def concat_columns(data, col1, col2, out_col):
    data[out_col] = data[col1].astype(str) + ' ' + data[col2].astype(str)
    return data