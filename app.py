from turtle import width
from numpy import positive
import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
# pip install dash (version 2.0.0 or higher)
from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import dash_daq as daq


from os.path import dirname, abspath
from os import listdir

from apps.helpers.aqua import *
from apps.helpers.ISO_dicts import *
from apps.helpers.datahelper import *

# region carregar dados
csv_folder = dirname(abspath(__file__)) + "\\dataset\\fixed_csvs\\"
dataset_folder = dirname(abspath(__file__)) + "\\dataset\\"
aquastat_files = listdir(csv_folder)

dfs, aqua_var = get_aqua_files(aquastat_files, csv_folder)
var_aqua = inv_dic(aqua_var)
def_and_calc = pd.read_csv(dataset_folder+'def_and_calc.csv', index_col=[0])


# grupo de infos que estarão no mapa
world_map_file = 'Pressure On Water Resources'
water_resources_items = generate_nested_options('Water Resources', aqua_var)
water_use_items = generate_nested_options('Water Use', aqua_var, ignore_var='Pressure On Water Resources')
pressure_items = generate_nested_options('Water Resources', aqua_var, exclusive='Pressure On Water Resources')
crop_itens = generate_nested_options('Crop P', aqua_var, total_only=True)
irrig_items = generate_nested_options('Irrigation and drainage development', aqua_var)
envh_items = generate_nested_options('Environment and health', aqua_var)
geo_items = generate_nested_options('Geo and Pop', aqua_var)
# endregion

card_color = "#FFFFFF"
info_color = "#606060"
plot_colors = {"background": card_color,
                 "text": info_color, "paper": card_color}

country_alert = dbc.Alert([html.I(className="bi bi-exclamation-triangle-fill me-2"), "Select at least one country", ], color="warning", className="d-flex align-items-center",)

def make_outside_header_duo(title1, w1, title2, w2):

    return dbc.Row([
            dbc.Col([ 
                    dbc.Row([
                        dbc.Col(html.Hr(className="title-line"), width=3),
                        dbc.Col(html.Div([title1], className='section-title'), width=6), 
                        dbc.Col(html.Hr(className="title-line"), width=3)
                        ], className="g-0")
                    ], width=w1),

            dbc.Col([ 
                    dbc.Row([
                        dbc.Col(html.Hr(className="title-line"), width=3),
                        dbc.Col(html.Div([title2], className='section-title'), width=6), 
                        dbc.Col(html.Hr(className="title-line"), width=3)
                        ], className="g-0")
                    ], width=w2),
            ])

def make_single_outside_header(title1, w1=12):
    return dbc.Row([
            dbc.Col([ 
                    dbc.Row([
                        dbc.Col(html.Hr(className="title-line"), width=3),
                        dbc.Col(html.Div([title1], className='section-title'), width=6), 
                        dbc.Col(html.Hr(className="title-line"), width=3)
                        ], className="g-0")
                    ], width=w1),
            ])

def make_regular_col(sufix, drop_options, drop_value, size = 6):

    desc_id = sufix + "-desc"
    plot_id = sufix + "-plot"
    
    return dbc.Col([
        dbc.Card(
            dbc.CardBody([       
                # Card Header               
                make_regular_c_header(sufix, drop_options, drop_value),  

                # Variable Description
                html.Hr(className="under-line"),
                html.Div([],id=desc_id,className='var-desc'),
                # Plot
                dbc.Row([
                    html.Div([], id=plot_id)
                ])
            ]), style={"height": "100%"}
        )
    ], width=size, className="h-100")
def make_col_desc_free(sufix, drop_options, drop_value, size = 6):
    plot_id = sufix + "-plot"
    
    return dbc.Col([
        dbc.Card(
            dbc.CardBody([       
                # Card Header               
                make_regular_c_header(sufix, drop_options, drop_value),  

                # Plot
                dbc.Row([
                    html.Div([], id=plot_id)
                ])
            ], style={"height": "100%"})
        )
    ], width=size, className="h-100")

def make_regular_c_header(sufix, drop_options, drop_value):
    var_id = sufix + "_variable"
    gear_id = sufix + "-gear"
    map_id = sufix + "-map"
    drop_id = sufix + "-dropdown"
    collapse_id = sufix + "-collapse"

    return dbc.Row([
        dbc.Col([
            html.Div([], className="variable_title", id=var_id)], width="auto"),

        make_gear(gear_id),
        make_map(map_id),
        make_hidden_dropdown(collapse_id,drop_id, drop_options, drop_value),
        make_off_canvas(sufix),
        
    ])

def make_gear(gear_id):    

    return dbc.Col([
        html.I(
            id=gear_id,
            className="bi bi-gear",
            style={
                "display": "contents", "line-height": "4.5rem!important"},
            n_clicks=0),
        ], width="auto")

def make_map(map_id):

    return dbc.Col([ 
        html.I(
            id=map_id,
            className="bi bi-map",
            style={
                "display": "contents", "line-height": "4.5rem!important"},
            n_clicks=0),
    ], width="auto")

def make_hidden_dropdown(collapse_id, drop_id, drop_options, drop_value):
    if isinstance(drop_value, list):
        multi = True
    else:
        multi = False

    return dbc.Col([
        dbc.Collapse(
            dcc.Dropdown(
                options=drop_options,
                value=drop_value,
                clearable=False,
                multi = multi,
                id=drop_id, className='drop-var'),
            is_open=False,
            id=collapse_id),
    ], width=True, style = {"min-width":"300px"})  

def make_off_canvas(sufix):
    btn1_id = 'btn-' + sufix + '-sl'
    btn2_id = 'btn-' + sufix + '-clr'
    drop_id = sufix + '-drop-countries'
    ofc_id = sufix + '-off-canvas'
    return dbc.Offcanvas([
        html.P("Select Countries"),
        html.Button('Select All', id=btn1_id, n_clicks=0),
        html.Button('Clear', id=btn2_id, n_clicks=0),
        dcc.Dropdown(
            options=[], 
            value=[], 
            id=drop_id,
            className='drop-country', multi=True)], 
        placement="end",
        id=ofc_id,
        title="Only countries with available data are displayed", 
        is_open=False)   

def make_small_card(dataframe, key, infos, Period):
    out_value, calculation = '', ''
    out_unit = 'Not Available'
    standart_tt = 'Not Available For Selected Time Period'

    if len(infos):
        out_unit = dataframe.Units.iloc[0]
        value = dataframe.Value.sum()
        out_value = f'{dataframe.Value.sum():.1f} '
        if value < 1:
            out_value = f'{dataframe.Value.sum():.3f} '
         
        calculation = infos.Calculation.iloc[0]
        standart_tt = "Sum of all available data for the selected time period.\nMay not correspond to actual values."

    return html.Div([
            dbc.Card( 
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.P(key, className="fw-bold card-title",)),
                        dbc.Col(html.I(id = key + '_tooltip', className="bi bi-info-circle-fill me-2",style={"font-size": "1.2rem", "text-align": "left",}), width=1)], className="d-flex w-100 justify-content-between"),

                    dbc.Row([
                        dbc.Col(
                            html.H3(out_value, style = {"margin-top": 8, "margin-bottom": 8}, className="fw-bold"), width="auto"),
                        dbc.Col(
                            html.H6(out_unit, style = {"margin-top": 8, "margin-bottom": 8,"margin-left": 8}, className='fw-light'), width="auto"),
                    ], className="g-0"),
                    html.Small(f'{Period}', className="text-muted"),
                ])
            ),
            
            dbc.Tooltip([
                html.P(standart_tt),
                html.B("Variable Calculation",style = {"text-align": "left",}),
                html.P(calculation), 
            ],autohide=False,target=key + '_tooltip',),
        ])

def make_line_plot(dataframe, countries, year, var):
    mask = (dataframe.Year < year) & (dataframe.VariableName == (var))

    dff = dataframe.loc[mask, :]
    mask2 = dff.Area.isin(countries)
    df = dff.loc[mask2, :]
    df.sort_values(by=['Year'], inplace=True)
    info = generate_infos(df.VariableId.iloc[0], def_and_calc)
    fig = px.line(
        df, x="Period", 
        y="Value",  
        color="ISOCode", 
        labels={"ISOCode": "Country"}, 
        custom_data=["Area", "Year", "Units", "Md1"], markers=True)
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>%{y:.2f}%{customdata[2]}<br><br>Measured in %{customdata[1]}<br>Metadata:<br>%{customdata[3]}<br><extra></extra>')
    fig.update_layout(xaxis_title='Time Period',yaxis_title=df.Units.unique()[0])

    fig.update_layout(
    autosize=True,
    plot_bgcolor=plot_colors["background"],
    paper_bgcolor=plot_colors["paper"],
    font_color=plot_colors["text"])

    fig.update_xaxes(
        showline=True,
        linecolor="#c9c9c9",
        mirror=True
    )

    fig.update_yaxes(
        linecolor="#c9c9c9",
        zerolinecolor="#c9c9c9",
        zerolinewidth=1,
        mirror=True,
    )

    return info.Definition.iloc[0], dcc.Graph(figure=fig)

def make_bar_plot(dataframe, countries, year, var):
    mask = (dataframe.Period == match_time(year)) & (
            dataframe.VariableName == (var))
      
    dff = dataframe.loc[mask, :]
    mask2 = dff.Area.isin(countries)
    df = dff.loc[mask2, :]
    df.sort_values(by=['Value'], inplace=True)
    info = generate_infos(df.VariableId.iloc[0], def_and_calc)
    fig = px.bar(
        df, x='ISOCode', y='Value', hover_data=['Area', 'Md1', 'Units'])
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>%{y:.2f}%{customdata[2]}<br><br>Metadata:<br>%{customdata[1]}<br><extra></extra>')
    fig.update_layout(xaxis_title='Country')   
    fig.update_layout(
        autosize=True,
        plot_bgcolor=plot_colors["background"],
        paper_bgcolor=plot_colors["paper"],
        font_color=plot_colors["text"],
        yaxis_title=df.Units.unique()[0])

    fig.update_xaxes(
        showline=True,
        linecolor="#c9c9c9",
        mirror=True
    )

    fig.update_yaxes(
        linecolor="#c9c9c9",
        zerolinecolor="#c9c9c9",
        zerolinewidth=1,
        mirror=True,
    )  
    return info.Definition.iloc[0], dcc.Graph(figure=fig)

def make_crop_plot(dataframe, countries, year, var, positivematch, type):
    
    mask = dataframe.VariableName == (var)
    vpie = 'Area'
    vlabel = {'Area': 'Country'}

    if not positivematch:
        mask = (dataframe.VariableName != (var))  
        vpie = 'VariableName'
        vlabel = {"VariableName": "Crop"}

    dff = dataframe.loc[mask, :]
    mask2 = dff.Area.isin(countries)
    df1 = dff.loc[mask2, :]

    if type == 'lines':
        df = df1.groupby([vpie,'Period', "Units"], as_index=False)['Value'].sum()
        fig = px.line(
            df, x="Period", 
            y="Value",  
            color=vpie, 
            custom_data=["Units"],
            labels= vlabel, markers=True)      
        info = " - "
        fig.update_traces(hovertemplate='<b>%{y:.2f}%{customdata[0]}')
        fig.update_layout(
        autosize=True,
        plot_bgcolor=plot_colors["background"],
        paper_bgcolor=plot_colors["paper"],
        font_color=plot_colors["text"],
        yaxis_title=df.Units.unique()[0])

        fig.update_xaxes(
            showline=True,
            linecolor="#c9c9c9",
            mirror=True
        )

        fig.update_yaxes(
            linecolor="#c9c9c9",
            zerolinecolor="#c9c9c9",
            zerolinewidth=1,
            mirror=True,
        )  

    if type == 'pie':
        df = df1.groupby([vpie, 'Units'], as_index=False)['Value'].sum()
        fig = px.pie(
            df, values="Value",  
            names=vpie, custom_data=['Units'])  
           
        info = ""
    
    return info, dcc.Graph(figure=fig)

def call_header(b_year, year, prop, dataframe):
    if b_year:
        mask = (dataframe.Year < year) & (
            dataframe.VariableName == (prop))
        df = dataframe.loc[mask, :]
    else:
        mask = (dataframe.Period == match_time(year)) & (
            dataframe.VariableName == (prop))
        df = dataframe.loc[mask, :]
    all_countries = df.Area.unique().tolist()
    return all_countries[0:10], 0, all_countries, prop

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

app.layout = html.Div([

    # Main Header
    html.Div([

        html.Div([

            html.Div("GLOBAL WATER AND AGRICULTURE", className="header_title"),
            html.Div([], className="header_links")
        ], className="header_text"),

    ], className="header_box"), 

    # Body
    html.Div([

        html.Div(
            [
                # L1- Small Cards
                dbc.Row(
                    [
                        dbc.Col(   
                            # Time Selection Card
                            dbc.Card(
                                dbc.CardBody([
                                    # Title
                                    dbc.Row([
                                        dbc.Col(
                                            html.P("Select Period", 
                                            className="fw-bold card-title"), 
                                            style={"margin-left": "40%"}),
                                        dbc.Col(
                                            html.I(id='period_tooltip', 
                                            className="bi bi-info-circle-fill me-2", 
                                            style={"font-size": "1.2rem", "text-align": "left", }), width=1)
                                        ], className="d-flex w-100 justify-content-between"),
                                    # Slider
                                    dbc.Row([
                                        dbc.Col(
                                            dcc.Slider(min=1960, max=2022, step=5, dots=True, value=2022,
                                                       marks={
                                                           1960: '1960', 
                                                           1980: '1980', 
                                                           2000: '2000', 
                                                           2020: '2020'},
                                                       tooltip={"placement": "top","always_visible": False},
                                                       id="year_slider", className="year-slider", 
                                                       included=False), style={"margin-top": 8, "margin-bottom": 8}
                                            ),
                                    ], id='slider-col', className="d-flex w-100 justify-content-between"),
                                    # Radio
                                    dcc.RadioItems(
                                        id='input-radio', 
                                        options=[
                                            {'label': 'Selected period only','value': False},
                                            {'label': 'Include previous values', 'value': True}],
                                        value=False,
                                        inline=True,
                                        labelStyle={'color': 'Gray', 'font-size': 10, 'margin-left': 10},
                                        inputStyle={'margin-left': 10, 'margin-right': 3}),
                                ], className="g-0")
                            ), className="h-100", width=4,
                        ),

                        dbc.Col(id="card1", className="h-100", width=True),
                        dbc.Col(id="card2", className="h-100", width=True),
                        dbc.Col(id="card3", className="h-100", width=True),
                    ], style={"margin-bottom": 25}),

                # L2
                dbc.Row([

                        make_outside_header_duo("WATER RESOURCES BREAKDOWN", 6, "WATER USE BREAKDOWN", 6),
                        # Cards
                        dbc.Row([
                            make_regular_col('wr', water_resources_items, 'Total renewable water resources per capita'),
                            dcc.Store(id='memory-wr'),
                            make_regular_col('wuse', water_use_items, 'Agricultural water withdrawal'),
                            dcc.Store(id='memory-wuse'),
                       
                        ]),
                        ], style={"margin-bottom": 20}),  

                # L3
                dbc.Row([

                    make_single_outside_header("PRESSURE ON WATER RESOURCES"),

                    # Cards
                    dbc.Row([
                        make_col_desc_free('wpres', pressure_items, 'MDG 7.5. Freshwater withdrawal as % of total renewable water resources', 8),
                        dcc.Store(id='memory-wpres'),

                        # Goals Exp
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody(
                                    [
                                        html.H6([], className="goal-title",
                                                id="wpres-card-title"),
                                        html.P([], className="goal-desc",
                                               id="wpres-desc"),
                                    ]),

                                dbc.CardImg(
                                    id="wpres_img", bottom=True,
                                    style={'margin-right': '4px', 'margin-left': '4px', 'width': 'auto', 'margin-bottom': '5px'}),

                            ], style={"height": "100%"}),
                        ], className="h-100", width=4),

                    ]),
                ], style={"margin-bottom": 20}),

                # L4
                dbc.Row([
                    make_outside_header_duo("AREA IRRIGATED BY CROP", 5,"IRRIGATION AND DRAINAGE DEVELOPMENT",7),
                    # -- Cards
                    dbc.Row([
                        # Crop
                        make_regular_col('crop',crop_itens,'Permanent Cropd',5),
                        dcc.Store(id='memory-crop'),
                        make_regular_col('irrig',irrig_items,'Total agricultural water managed area', 7),
                        dcc.Store(id='memory-irrig'),
                    ])

                ], style={"margin-bottom": 20}),

                # L5
                dbc.Row([
                    make_outside_header_duo("GEO INFO", 6,"HEALTH CONDITIONS",6),
                    # -- Cards
                    dbc.Row([
                        # Crop
                        make_regular_col('geo',geo_items,aqua_var['Population'][0], 6),
                        dcc.Store(id='memory-geo'),
                        make_regular_col('envh',envh_items,aqua_var['Access To Improved Drinking Water Source'][0], 6),
                        dcc.Store(id='memory-envh'),
                    ])

                ], style={"margin-bottom": 20}),

                # Footer
                dbc.Row([
                    html.Hr(className="my-line"),
                    html.H4("Sources"),
                    html.Div(["FAO [2018]. AQUASTAT Database. AQUASTAT Website, accessed on [30/08/2022 15:14]"],
                             className="card-text",)
                ], style={"margin-top": 20})

            ]),

    ], className="page-content"),


])
# region callbacks first row
# region callback slider


@app.callback(
    Output(component_id="year_slider", component_property="included"),
    Input(component_id="input-radio", component_property="value"))
def udapte_slider(value):
    return value
# endregion

# region callback info_cards


@app.callback(
    Output(component_id="card1", component_property="children"),
    Output(component_id="card2", component_property="children"),
    Output(component_id="card3", component_property="children"),
    Input(component_id="year_slider", component_property="value"))

def udapte_cards(year):

    info_cards = {
        'Total Renewable Water Resources': ['Total renewable water resources'],
        'Water Withdrawal By Sector': ['Total water withdrawal', 'Agricultural water withdrawal']}
    cards = []
    for file_key in info_cards:

        period = match_time(year)
        mask = (dfs[file_key].Period == period)
        df = dfs[file_key].loc[mask, :]

        for var_key in info_cards[file_key]:
            mask_2 = (df.VariableName == var_key)
            dff = df.loc[mask_2, :]
            info = dff
            if len(dff):
                info = generate_infos(dff.VariableId.iloc[0], def_and_calc)
            cards.append(make_small_card(dff, var_key, info, period))
    return cards[0], cards[1], cards[2]
# endregion

# endregion

# region callbacks second row - water resources
# region callback toggle gear wr
@app.callback(
    Output("wr-collapse", "is_open"),
    [Input("wr-gear", "n_clicks")],
    [State("wr-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvas wr


@app.callback(
    Output("wr-off-canvas", "is_open"),
    [Input("wr-map", "n_clicks")],
    [State("wr-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect all wr
@app.callback(
    Output("wr-drop-countries", "value"),
    [Input("btn-wr-sl", "n_clicks"),
     Input("btn-wr-clr", "n_clicks"),
     Input("wr-drop-countries", "options")], 
    [State("wr-map", "n_clicks"),
     State("wr-drop-countries", "value"),
     State('memory-wr', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-wr-clr" == ctx.triggered_id:
        output = []
    if "btn-wr-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdown wr
@app.callback(
    Output('memory-wr', 'data'),
    Output("wr-map", "n_clicks"),
    Output("wr-drop-countries", "options"),
    Output("wr_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("wr-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = var_aqua[prop][0]
    dataframe = dfs[aqua_file]
    return call_header(b_year, year, prop, dataframe)
# endregion


# region plot and desc wr
@app.callback(
    Output("wr-desc", "children"),
    Output("wr-plot", "children"),
    Input("wr-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("wr-dropdown", "value"),)
def show_plot1(countries, b_year, year, var):
    aqua_file = var_aqua[var][0]

    if len(countries) == 0:
        return '-', country_alert

    if b_year:
        return make_line_plot(dfs[aqua_file], countries, year, var)

    else:
        return make_bar_plot(dfs[aqua_file], countries, year, var) 
# endregion

# endregion

# region callbacks second row - water use
# region callback toggle gear wuse
@app.callback(
    Output("wuse-collapse", "is_open"),
    [Input("wuse-gear", "n_clicks")],
    [State("wuse-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvas wuse
@app.callback(
    Output("wuse-off-canvas", "is_open"),
    [Input("wuse-map", "n_clicks")],
    [State("wuse-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect all wuse
@app.callback(
    Output("wuse-drop-countries", "value"),
    [Input("btn-wuse-sl", "n_clicks"),
     Input("btn-wuse-clr", "n_clicks"),
     Input("wuse-drop-countries", "options")], 
    [State("wuse-map", "n_clicks"),
     State("wuse-drop-countries", "value"),
     State('memory-wuse', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-wuse-clr" == ctx.triggered_id:
        output = []
    if "btn-wuse-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdown wuse
@app.callback(
    Output('memory-wuse', 'data'),
    Output("wuse-map", "n_clicks"),
    Output("wuse-drop-countries", "options"),
    Output("wuse_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("wuse-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = var_aqua[prop][0]
    dataframe = dfs[aqua_file]
    return call_header(b_year, year, prop, dataframe)
# endregion

# region plot and desc wuse
@app.callback(
    Output("wuse-desc", "children"),
    Output("wuse-plot", "children"),
    Input("wuse-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("wuse-dropdown", "value"),)
def show_plot1(countries, b_year, year, var):
    aqua_file = var_aqua[var][0]

    if len(countries) == 0:
        return '-', country_alert

    if b_year:
        return make_line_plot(dfs[aqua_file], countries, year, var)

    else:
       return make_bar_plot(dfs[aqua_file], countries, year, var)       
# endregion

# endregion

# region callback third row - water pressure

# region callback toggle gear wpres
@app.callback(
    Output("wpres-collapse", "is_open"),
    [Input("wpres-gear", "n_clicks")],
    [State("wpres-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvas wpres
@app.callback(
    Output("wpres-off-canvas", "is_open"),
    [Input("wpres-map", "n_clicks")],
    [State("wpres-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect all wpres
@app.callback(
    Output("wpres-drop-countries", "value"),
    [Input("btn-wpres-sl", "n_clicks"),
     Input("btn-wpres-clr", "n_clicks"),
     Input("wpres-drop-countries", "options")], 
    [State("wpres-map", "n_clicks"),
     State("wpres-drop-countries", "value"),
     State('memory-wpres', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-wpres-clr" == ctx.triggered_id:
        output = []
    if "btn-wpres-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdown wpres
@app.callback(
    Output('memory-wpres', 'data'),
    Output("wpres-map", "n_clicks"),
    Output("wpres-drop-countries", "options"),
    Output("wpres_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("wpres-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = var_aqua[prop][0]
    if b_year:
        mask = (dfs[aqua_file].Year < year) & (
            dfs[aqua_file].VariableName == (prop))
        df = dfs[aqua_file].loc[mask, :]
        all_countries = df.Area.unique().tolist()
        output = all_countries
    else:
        mask = (dfs[aqua_file].Period == match_time(year)) & (
            dfs[aqua_file].VariableName == (prop))
        df = dfs[aqua_file].loc[mask, :]
        all_countries = df.Area.unique().tolist()
        output = all_countries[0:10]
    return output, 0, all_countries, prop
# endregion

# region callback second card title and img wpres
@app.callback(
    Output("wpres_img", "src"),
    Output("wpres-card-title", "children"),
    Input("wpres-dropdown", "value"),)
def show_heaer1(var):
    check = var[0:3]
    if check == 'MDG':
        return app.get_asset_url("mdg.jpg"), "Millennium Development Goals"
    elif check == 'SDG':
        return app.get_asset_url("sdg.png"), "Sustainable Development Goals"
    else:
        return app.get_asset_url("agc.png"), "Agricultural Pressure"

# endregion

# region plot and desc wpres
@app.callback(
    Output("wpres-desc", "children"),
    Output("wpres-plot", "children"),
    Input("wpres-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("wpres-dropdown", "value"),)
def show_plot1(countries, b_year, year, var):
    aqua_file = var_aqua[var][0]

    if b_year:

        if len(countries) == 0:
            return '-', dbc.Alert(
                [html.I(className="bi bi-exclamation-triangle-fill me-2"), "Select at least one country", ], color="warning", className="d-flex align-items-center",)
        make_line_plot(dfs[aqua_file], countries, year, var)

    else:
        mask = (dfs[aqua_file].Period == match_time(year)) & (
            dfs[aqua_file].VariableName == (var))
        df = dfs[aqua_file].loc[mask, :]
        empty_c = empty_countries(df)
        info = generate_infos(df.VariableId.iloc[0], def_and_calc)

        fig = px.choropleth(df, locations="ISOCode",
                            color="Value",
                            hover_name="Area",
                            custom_data=["Units"],
                            range_color=get_range(df),
                            color_continuous_scale='dense',
                            labels={'Value': df.Units.unique()[0]})
        fig.data[0].hovertemplate = '<b>%{hovertext}</b><br><br>Value = %{z:.2f}%{customdata[0]}<extra></extra>'

        # Países que não possuem dados ficam em branco no mapa. Vou adicionar um novo traço com
        # esses países, para poder adicionar um hovertext sobre esses países
        empty_map = px.choropleth(empty_c, locations="ISOCode", color_discrete_sequence=[
            "#e2e2e2"], hover_name="Area", hover_data=["Value"])
        new_trace = list(empty_map.select_traces())[0]
        new_trace.hovertemplate = '<b>%{hovertext}</b><br><br>%{customdata[0]}<extra></extra>'
        new_trace.showlegend = False  # select_traces torna showlegend True, por algum motivo
        fig.add_traces(new_trace)

        fig.update_layout(
            autosize=True,
            margin={"r": 50, "t": 60, "l": 0, "b": 10, "autoexpand": True},
            plot_bgcolor=plot_colors["background"],
            paper_bgcolor=plot_colors["paper"],
            coloraxis_colorbar=dict(x=1, xanchor='left', xpad=10),
            geo=dict(
                showframe=False,
                projection_type='equirectangular'))

    return info.Definition.iloc[0], dcc.Graph(figure=fig)
# endregion

# endregion

# region callback fourth row - irrigation
# region callback toggle gear irrig


@app.callback(
    Output("irrig-collapse", "is_open"),
    [Input("irrig-gear", "n_clicks")],
    [State("irrig-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvas irrig


@app.callback(
    Output("irrig-off-canvas", "is_open"),
    [Input("irrig-map", "n_clicks")],
    [State("irrig-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect all irrig

@app.callback(
    Output("irrig-drop-countries", "value"),
    [Input("btn-irrig-sl", "n_clicks"),
     Input("btn-irrig-clr", "n_clicks"),
     Input("irrig-drop-countries", "options")], 
    [State("irrig-map", "n_clicks"),
     State("irrig-drop-countries", "value"),
     State('memory-irrig', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-irrig-clr" == ctx.triggered_id:
        output = []
    if "btn-irrig-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdown irrig
@app.callback(
    Output('memory-irrig', 'data'),
    Output("irrig-map", "n_clicks"),
    Output("irrig-drop-countries", "options"),
    Output("irrig_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("irrig-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = var_aqua[prop][0]
    if b_year:
        mask = (dfs[aqua_file].Year < year) & (
            dfs[aqua_file].VariableName == (prop))
        df = dfs[aqua_file].loc[mask, :]
    else:
        mask = (dfs[aqua_file].Period == match_time(year)) & (
            dfs[aqua_file].VariableName == (prop))
        df = dfs[aqua_file].loc[mask, :]
    all_countries = df.Area.unique().tolist()
    return all_countries[0:10], 0, all_countries, prop
# endregion

# region plot and desc irrig
@app.callback(
    Output("irrig-desc", "children"),
    Output("irrig-plot", "children"),
    Input("irrig-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("irrig-dropdown", "value"),)
def show_plot1(countries, b_year, year, var):
    aqua_file = var_aqua[var][0]

    if len(countries) == 0:
        return '-', country_alert

    if b_year:
        return make_line_plot(dfs[aqua_file], countries, year, var)

    else:
        return make_bar_plot(dfs[aqua_file], countries, year, var)
 
# endregion
# endregion

# region callbacl fourth row - crop
# region callback toggle gear crop
@app.callback(
    Output("crop-collapse", "is_open"),
    [Input("crop-gear", "n_clicks")],
    [State("crop-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvas crop

@app.callback(
    Output("crop-off-canvas", "is_open"),
    [Input("crop-map", "n_clicks")],
    [State("crop-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect all crop
@app.callback(
    Output("crop-drop-countries", "value"),
    [Input("btn-crop-sl", "n_clicks"),
     Input("btn-crop-clr", "n_clicks"),
     Input("crop-drop-countries", "options")], 
    [State("crop-map", "n_clicks"),
     State("crop-drop-countries", "value"),
     State('memory-crop', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-crop-clr" == ctx.triggered_id:
        output = []
    if "btn-crop-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdown crop
@app.callback(
    Output('memory-crop', 'data'),
    Output("crop-map", "n_clicks"),
    Output("crop-drop-countries", "options"),
    Output("crop_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("crop-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = prop[:-1]
    if prop[-1] == 't':
        mask0 = dfs[aqua_file].VariableName == 'Total'
    else:
        mask0 = dfs[aqua_file].VariableName != 'Total'
    if b_year:
        mask = (dfs[aqua_file].Year < year) & (mask0)
        df = dfs[aqua_file].loc[mask, :]
    else:
        mask = (dfs[aqua_file].Period == match_time(year)) & (
            mask0)
        df = dfs[aqua_file].loc[mask, :]
    all_countries = df.Area.unique().tolist()
    return all_countries[0:10], 0, all_countries, prop[:-1]
# endregion

# region plot and description crop

@app.callback(
    Output("crop-desc", "children"),
    Output("crop-plot", "children"),
    Input("crop-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("crop-dropdown", "value"),)
def show_plot1(countries, b_year, year, vars):

    aqua_file = vars[:-1]
    
    match = False
    if vars[-1] == 't':
        match = True
    
    var = 'Total'
    if len(countries) == 0:
        return '-', country_alert

    if b_year:        
        mask = dfs[aqua_file].Year < year
        dataframe = dfs[aqua_file].loc[mask, :]       
        return make_crop_plot(dataframe, countries, year, var, match, 'line')

    else:
        mask = dfs[aqua_file].Period == match_time(year)
        dataframe = dfs[aqua_file].loc[mask, :]
        return make_crop_plot(dataframe, countries, year, var, match, 'pie')

# endregion
# endregion


# region callbacks fifth row - water resources
# region callback toggle gear geo
@app.callback(
    Output("geo-collapse", "is_open"),
    [Input("geo-gear", "n_clicks")],
    [State("geo-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvas geo


@app.callback(
    Output("geo-off-canvas", "is_open"),
    [Input("geo-map", "n_clicks")],
    [State("geo-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect all geo
@app.callback(
    Output("geo-drop-countries", "value"),
    [Input("btn-geo-sl", "n_clicks"),
     Input("btn-geo-clr", "n_clicks"),
     Input("geo-drop-countries", "options")], 
    [State("geo-map", "n_clicks"),
     State("geo-drop-countries", "value"),
     State('memory-geo', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-geo-clr" == ctx.triggered_id:
        output = []
    if "btn-geo-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdown geo
@app.callback(
    Output('memory-geo', 'data'),
    Output("geo-map", "n_clicks"),
    Output("geo-drop-countries", "options"),
    Output("geo_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("geo-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = var_aqua[prop][0]
    dataframe = dfs[aqua_file]
    return call_header(b_year, year, prop, dataframe)
# endregion


# region plot and desc geo
@app.callback(
    Output("geo-desc", "children"),
    Output("geo-plot", "children"),
    Input("geo-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("geo-dropdown", "value"),)
def show_plot1(countries, b_year, year, var):
    aqua_file = var_aqua[var][0]

    if len(countries) == 0:
        return '-', country_alert

    if b_year:
        return make_line_plot(dfs[aqua_file], countries, year, var)

    else:
        return make_bar_plot(dfs[aqua_file], countries, year, var) 
# endregion

# endregion

# region callbacks fifth row - env and health
# region callback toggle gearenvh
@app.callback(
    Output("envh-collapse", "is_open"),
    [Input("envh-gear", "n_clicks")],
    [State("envh-collapse", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback toggle offcanvasenvh
@app.callback(
    Output("envh-off-canvas", "is_open"),
    [Input("envh-map", "n_clicks")],
    [State("envh-off-canvas", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open
# endregion

# region callback select/unselect allenvh
@app.callback(
    Output("envh-drop-countries", "value"),
    [Input("btn-envh-sl", "n_clicks"),
     Input("btn-envh-clr", "n_clicks"),
     Input("envh-drop-countries", "options")], 
    [State("envh-map", "n_clicks"),
     State("envh-drop-countries", "value"),
     State('memory-envh', 'data')],
)
def toggle_collapse1(click1, click2, all, mclick, selected, top):
    output = selected
    if mclick == 0:
        output = top
    if "btn-envh-clr" == ctx.triggered_id:
        output = []
    if "btn-envh-sl" == ctx.triggered_id:
        output = all
    return output

# endregion

# region callback header and countries dropdownenvh
@app.callback(
    Output('memory-envh', 'data'),
    Output("envh-map", "n_clicks"),
    Output("envh-drop-countries", "options"),
    Output("envh_variable", "children"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("envh-dropdown", "value"),)
def show_heaer1(b_year, year, prop):
    aqua_file = var_aqua[prop][0]
    dataframe = dfs[aqua_file]
    return call_header(b_year, year, prop, dataframe)
# endregion

# region plot and descenvh
@app.callback(
    Output("envh-desc", "children"),
    Output("envh-plot", "children"),
    Input("envh-drop-countries", "value"),
    Input("input-radio", "value"),
    Input("year_slider", "value"),
    Input("envh-dropdown", "value"),)
def show_plot1(countries, b_year, year, var):
    aqua_file = var_aqua[var][0]

    if len(countries) == 0:
        return '-', country_alert

    if b_year:
        return make_line_plot(dfs[aqua_file], countries, year, var)

    else:
       return make_bar_plot(dfs[aqua_file], countries, year, var)       
# endregion

# endregion



if __name__ == "__main__":
    app.run_server(debug=False)
