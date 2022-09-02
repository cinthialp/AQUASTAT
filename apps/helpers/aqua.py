import pandas as pd


def get_aqua_files(aquastat_files, folder):
    """
    Recebe uma lista com todos os arquivos a serem acessados e o nome da pasta onde estão.
    Retorna dois dicionários: [1] {"nome da subcategoria": dataframe com variáveis da subcategoria}
    [2] {"nome da subcategoria": lista com todas as variáveis que estão no dataframe}
    """

    aquastat_dfs = {}
    aquastat_variables = {}
    group_df = []
    current_group = None

    multiple_parts = [i for i in aquastat_files if i[-5].isnumeric()] # número de partes fica imediatamente antes do .csv
    single_parts = [i for i in aquastat_files if not i[-5].isnumeric()]
    
    for part in multiple_parts: # adicionar subcategorias separadas como um único dataframe
        key = part.split(".")[0].replace("_", " ").replace("aquastat", "").title().strip()[:-2]

        if current_group != key:        
            if current_group:
                aquastat_dfs[current_group] = pd.concat(group_df)
                aquastat_variables[current_group] = aquastat_dfs[current_group]['VariableName'].unique().tolist()

            current_group = key        
            group_df = [] 

        if key == current_group:
            csv_file = folder + part
            group_df.append(pd.read_csv(csv_file))

        aquastat_dfs[current_group] = pd.concat(group_df) 
        aquastat_variables[current_group] = aquastat_dfs[current_group]['VariableName'].unique().tolist()

    for aqua_file in single_parts:    # adicionar subcategorias que são arquivos únicos
        csv_file = folder + aqua_file
        key = aqua_file.split(".")[0].replace("_", " ").replace("aquastat", "").title().strip()

        aquastat_dfs[key] = pd.read_csv(csv_file)
        aquastat_variables[key] = aquastat_dfs[key]['VariableName'].unique().tolist()

    
    # ----- creating new var ---- # 
    df = aquastat_dfs['Irrigated Crop Area And Cropping Intensity']
    dfp = df[df.VariableName.str.contains('Harvested irrigated permanent crop area: ')].loc[:]
    dfp['VariableName'] = [get_crop(x, 'Harvested irrigated permanent crop area: ') for x in dfp['VariableName'].tolist()]

    dft = df[df.VariableName.str.contains('Harvested irrigated permanent crop area: ')].loc[:]
    dft['VariableName'] = [get_crop(x, 'Harvested irrigated temporary crop area: ') for x in dfp['VariableName'].tolist()]

    aquastat_dfs['Permanent Crop'] = dfp
    aquastat_dfs['Temporary Crop'] = dft

    aquastat_variables['Permanent Crop'] = dfp['VariableName'].unique().tolist()
    aquastat_variables['Temporary Crop'] = dft['VariableName'].unique().tolist()
    #---- 

    return aquastat_dfs, aquastat_variables

def get_crop(x, y):
    crop = x.replace(y, '')
    return crop

def inv_dic(base): # ᴀʀᴍᴀɴ solution
    new_dic = {}
    for k,v in base.items():
        for x in v:
            new_dic.setdefault(x,[]).append(k)   
    return new_dic

def make_options(reference_dict, key, base = 0):
    """
    Recebe um dicionário com todas as variáveis de cada grupo (chave)
    e retorna [lista] + valor serem utilizados como atributos em um Dropdown.
    """
    return [reference_dict[key], reference_dict[key][base]]



def match_time(x):  

    # retorna o intervalo de anos (YYYY, YYYY) em que um ano x se encontra

    years_mean = range(1960,2023,5) # from AQUASTAT website
    years_period = [(i-2, i+2) for i in years_mean]

    for period in years_period:
        if x >= period[0] and x <= period[1]:
            return str(period)