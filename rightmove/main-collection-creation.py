from write import Write
from load import Load

if __name__ == '__main__':

    # Load rightmove collection as df
    coll_name = 'rightmove'
    df_rightmove = Load(coll_name).read_db()

    # Drop all columns apart from home id, price, number of bedrooms and coordinates
    # (coordinates are to calculate time to work afterwards)
    list_cols_to_keep = ['id', 'number_bedrooms', 'price', 'coordinates', 'area']
    list_all_columns = df_rightmove.columns
    for col in list_all_columns:
        if col not in list_cols_to_keep:
            df_rightmove.drop(col, axis=1, inplace=True)

    # Create home_vectors collection
    coll_name = 'home_vectors'
    Write(coll_name).write_df(df_rightmove)


