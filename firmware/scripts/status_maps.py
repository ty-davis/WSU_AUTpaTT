import pandas as pd

def c_code(df, sym_col, stat_col):
    df['c_code'] = df.apply(lambda row: f"    {row[sym_col]} = {int('0x' + str(row[stat_col]), 16)},", axis=1)
    max_length = df['c_code'].str.len().max()
    df['c_comment'] = df.apply(lambda row: f"{(2 + (max_length - len(row['c_code']))) * ' '}// 0x{row[stat_col]}\n", axis=1)

def py_file(df):
    df['py_code'] = df.apply(lambda row: f"    {row['SYMBOL']} = 0x{row['Status']}", axis=1)
    df['params_list'] = df.apply(lambda row: [x for x in str(row['params']).split(',') if x != 'nan'], axis=1)

def main():
    status_df = pd.read_csv("status.csv")
    response_df = pd.read_csv("response.csv")

    # C code
    c_code(status_df, "SYMBOL", "Status")
    c_code(response_df, "SYMBOL", "Status")
    
    with open("c_status", 'w') as c_out:
        c_out.write("enum status\n{\n")
        for _, row in status_df.iterrows():
            c_out.write(f"{row['c_code']}{row['c_comment']}")
        c_out.write("};")

        c_out.write("\n\n")
        c_out.write("enum response\n{\n")
        for _, row in response_df.iterrows():
            c_out.write(f"{row['c_code']}{row['c_comment']}")
        c_out.write("};")

    # python code
    py_file(status_df)
    print(status_df)
    print(status_df[pd.isna(status_df['params'])])
    with open("codes.py", 'w') as py_out:
        py_out.write("STATUS_CODES = {\n")
        for _, row in status_df.iterrows():
            py_out.write(f"""    "{row['SYMBOL']}":  {{
        "code": 0x{row['Status']},
        "alias": '{row['Alias']}',
        "params": {row['params_list']},
        "scalar": {[int(x) for x in str(row['scalar']).split(',')] if not pd.isna(row['scalar']) else None},
        "response_params": {[x for x in str(row['response_params']).split(',')] if not pd.isna(row['response_params']) else None},
        "response_scalar": {[int(x) for x in str(row['response_scalar']).split(',')] if not pd.isna(row['response_scalar']) else None},
        "response_names": {[x for x in str(row['response_names']).split(',')] if not pd.isna(row['response_names']) else None}
    }},
""")
        py_out.write("}\n\nRESPONSE_CODES = {\n")
        for _, row in response_df.iterrows():
            py_out.write(f"""    "{row['SYMBOL']}": {{
        "code": 0x{row['Status']},
        "description": "{row['Description']}",
    }},
""")
        py_out.write("}\n")






if __name__ == '__main__':
    main()
