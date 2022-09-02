import pandas as pd
from dash import html

major_groups = {
    'Geo and Pop': ['Economy Development Food', 'Land Use','Population'],

    'Water Resources': ['External Renewable Water Resources', 'Internal Renewable Water Resources', 'Total Renewable Water Resources','Exploitable Wr And Dam Capacity', 'Precipitation'],

    'Water Use': ['Pressure On Water Resources',  'Wastewater', 'Water Withdrawal By Sector', 'Water Withdrawal By Source'],

    'Irrigation and drainage development':['Area Under Agricultural Water Management','Area Equipped For Irrigation By Source Of Water', 'Irrigated Crop Area And Cropping Intensity', 'Irrigated Crop Yield', 'Drainage', 'Power Irrigated Area'],

    'Environment and health': ['Access To Improved Drinking Water Source', 'Enviroment', 'Health'],
    
    'Crop P':['Permanent Crop', 'Temporary Crop'] }

def get_range(dataframe):

    if dataframe.Units.unique()[0] == '%':
        return [0, 100]

    else:
        return [round(dataframe.Value.min()), round(dataframe.Value.max())]

def generate_infos(id, reference):
    return reference[reference.VariableId == id]


def generate_nested_options(group, var_reference, ignore_var=None, exclusive=None, total_only=False):
    group_style = {"color": 'MediumTurqoise', 'font-size': 14, "font-weight": 'bold'}
    var_style = {"color": '#252527', 'font-size': 10}
    options = []

    if exclusive:
        for var in var_reference[exclusive]:
            var_line= {"label": html.Div([var], style = var_style),"value": var}
            options.append(var_line)         
        return options

    if total_only:
        for group_file in major_groups[group]:
            group_line = {"label": html.Div([group_file], style = group_style),"value": "Nope",'disabled': True}
            var_line1 = {"label": html.Div('Total', style = var_style),"value": group_file+'t'}
            var_line2 = {"label": html.Div('Describe', style = var_style),"value": group_file+'d'}
            options.extend([group_line, var_line1, var_line2])
        return options

    for group_file in major_groups[group]:
        if group_file == ignore_var:
            continue

        group_line = {"label": html.Div([group_file], style = group_style),"value": "Nope",'disabled': True}
        options.append(group_line)

        for var in var_reference[group_file]:
            var_line= {"label": html.Div([var], style = var_style),"value": var}
            options.append(var_line)
    
    return options
