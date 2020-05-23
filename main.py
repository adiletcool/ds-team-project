import re
import math
import time
import dash
from dash.dependencies import Output, Input, State
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
from assets.styles import *
from quotes.ricom.config import tickers_id, tfs
from quotes.ricom.get_quotes import Quotes
from news.interfax import get_news, get_content
from news.mfd import mfd_get_content, mfd_get_news

# from news.dost_mood import RuModel
from TextTonalModel.TextTonalAnalyzer import TextTonalAnalyzer

model = TextTonalAnalyzer("NBC")  # Load the model

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
quotes_class = Quotes()

today_wd = datetime.today().weekday()
date_pick = datetime.today() - timedelta(2 if today_wd == 6 else 1 if today_wd == 5 else 0)
time_selected = None  # see spinner dcc.Loading

app.layout = html.Div([
    html.Div([
        html.Div([  # Баннер
            html.H2('Stock price prediction', title='DS Minor Group Project'),
            html.Img(src='/assets/stock-icon-1.png', id='img-id', title='Project Logo'),
        ], className='banner', id='banner-id'),

        html.Div([
            html.Div([
                # ВЕРХНЯЯ ПАНЕЛЬ
                html.Div([
                    html.Div([
                        html.H4('Тикер:', style=h4_style),
                        dcc.Dropdown(
                            id='ticker',
                            options=[{'label': i, 'value': i} for i in tickers_id.keys()],
                            value=list(tickers_id.keys())[0],
                            clearable=False,
                            style=dropdown_style,
                            searchable=False,
                        )
                    ], className='tickerclass'),

                    html.Div([
                        html.H4('Дата:', style=h4_style, className='datelabel'),
                        dcc.DatePickerSingle(
                            id='datepicker',
                            date=date_pick,
                            display_format='MMM Do, YYYY',
                            first_day_of_week=1,
                            max_date_allowed=date_pick,
                            clearable=False,
                            day_size=40,
                            className='datepickerclass',
                        )

                    ], className='datepickerbox'),

                    html.Div([
                        html.H4('Таймфрейм:', style=h4_style),
                        dcc.Dropdown(
                            id='tf',
                            options=[{'label': i, 'value': i} for i in tfs.keys()],
                            value='5 мин.',
                            clearable=False,
                            style=dropdown_style,
                            searchable=False,
                        )
                    ], className='timeframeclass'),

                ], className='mainpanel'),

                # ОБЩИЕ ФИН НОВОСТИ
                html.Div([
                    html.H4('Общие финансовые новости:', style=h4_style, id='newslabel'),
                    html.Div([
                        dcc.Dropdown(
                            id='news',
                            options=[],
                            value=None,
                            searchable=False,
                            className='newsdropdown',
                            placeholder='Выберите новость...'
                        ),
                        dbc.Button("?", id="newsbutton_id", className='newsbutton'),
                        dbc.Modal([  # всплывающее окно с новостью
                            dbc.ModalHeader([
                                html.H4('', id='modal-header-id', className='modal-header-title'),
                                html.H4('time', id='modal-header-time-id', className='modal-header-time')
                            ], className='modal-header'),
                            dbc.ModalBody('', id='modal-body-id', className='modal-body'),
                            dbc.ModalFooter(
                                dbc.Button('close', id='modal-close-id', className='modal-close')
                            )
                        ], scrollable=False, id='modal-body-scroll', className='modal-content')
                    ], className='newsbody'),

                ], className='newsclass'),

                # НОВОСТИ КОМПАНИИ
                html.Div([
                    html.H4(style=h4_style, id='company_newslabel'),
                    html.Div([
                        dcc.Dropdown(
                            id='company_news',
                            options=[],
                            value=None,
                            searchable=False,
                            placeholder='Выберите новость...',
                            className='company_newsdropdown'
                        ),
                        dbc.Button("?", id="newsbutton1_id", className='newsbutton1'),
                        dbc.Modal([  # всплывающее окно с новостью компании
                            dbc.ModalHeader([
                                html.H4('', id='modal1-header-id', className='modal1-header-title'),
                                html.H4('time', id='modal1-header-time-id', className='modal1-header-time')
                            ], className='modal1-header'),
                            dbc.ModalBody('', id='modal1-body-id', className='modal1-body'),
                            dbc.ModalFooter(
                                dbc.Button('close', id='modal1-close-id', className='modal1-close')
                            )
                        ], scrollable=False, id='modal1-body-scroll', className='modal1-content')
                    ], className='company_newsbody'),

                ], className='company_newsclass'),

            ], className='topleft', id='topleft-id'),

            html.Div([
                html.H2('Prediction:', style=h4_style),
                dcc.Loading(type='dot', children=html.Div(id='spinner')),
                html.H2(id='prediction-label-id', className='prediction-class', style=h4_style),
            ], className='bottomleft', id='bottomleft-id'),

        ], className="five columns"),

        # основной график
        html.Div([
            dcc.Graph(id='my-graph', config={'scrollZoom': True}, style={'height': '100%'}, className='mygraph'),
        ], className='seven columns', id='seven-id'),

        # Dark Mode toggle
        html.Div([
            daq.ToggleSwitch(
                id='toggle-theme',
                label=['', 'Dark Theme'],
                color='#1DC690',
                value=False
            )
        ], className='dark-theme-toogle-class'),

        html.Img(src='/assets/hse_logo.png', id='hse-logo-id', title='HSE Logo', className='hse_logo_class')

    ], className='row', style=row_style, id='row-id'),
])


@app.callback([Output('row-id', 'style'),
               Output('topleft-id', 'style'),
               Output('bottomleft-id', 'style'),
               Output('banner-id', 'style'),
               Output('seven-id', 'style'),
               Output('img-id', 'style')],
              [Input('toggle-theme', 'value')])
def edit_theme(value):
    if value:
        border_color = '#2b313b'
        row_id_style = {'background-color': '#1a1a1a', 'color': '#F7F8F8'}
        topleft_style = {'background-color': '#303437', 'border': f'2px solid {border_color}'}
        bottomleft_style = {'background-color': '#303437', 'border': f'2px solid {border_color}'}
        banner_style = {'background-color': '#303437', 'border': f'2px solid {border_color}'}
        seven_style = {'background-color': '#303437', 'border': f'2px solid {border_color}'}
        image_style = {'border': f'2px solid #9CA6B8'}

    else:
        row_id_style = topleft_style = bottomleft_style = banner_style = seven_style = image_style = {}

    return row_id_style, topleft_style, bottomleft_style, banner_style, seven_style, image_style


@app.callback([Output('company_news', 'value'),
               Output('news', 'value')],
              [Input('ticker', 'value'),
               Input('datepicker', 'date')])
def clear_dropdrown_value(ticker, date):  # при смене тикера или даты очищать значение дропдауна
    return [None, None] if ticker or date else [None, None]


@app.callback([Output('my-graph', 'figure'),
               Output('prediction-label-id', 'children')],
              [Input('ticker', 'value'),
               Input('tf', 'value'),
               Input('datepicker', 'date'),
               Input('toggle-theme', 'value'),
               Input('modal1-header-id', 'children'),
               Input('modal1-header-time-id', 'children')])
def update_graph(ticker_value, tf_value, date, dark_toggle, modal1_title, modal1_time):
    global time_selected

    startdate = datetime.strptime(date.split('T')[0], '%Y-%m-%d').replace(hour=10, minute=0)  # 7 -> heroku timezone
    enddate = startdate.replace(hour=18, minute=45)

    prediction_return = None

    quotes = quotes_class.get_quotes(ticker_value, start_date=startdate, end_date=enddate, tf=tf_value)

    # основной график
    fig = dict(data=[go.Candlestick(x=quotes['DATE'],
                                    open=quotes['OPEN'], high=quotes['HIGH'],
                                    low=quotes['LOW'], close=quotes['CLOSE'],
                                    increasing={'line': {'color': '#00CC94'}},
                                    decreasing={'line': {'color': '#F50030'}},
                                    showlegend=False,
                                    name='')],
               layout=dict(dragmode='pan',
                           title=dict(text=ticker_value,
                                      xref='paper',
                                      x=0,
                                      font=dict(family='Times New Roman',
                                                size=18,
                                                color='#0C2D48' if not dark_toggle else '#F7F8F8')),
                           xaxis=dict(type='category',
                                      tickangle=10,
                                      nticks=10,
                                      rangeslider=dict(visible=False),
                                      color='#0C2D48' if not dark_toggle else '#F7F8F8',
                                      gridcolor='rgb(96,96,96)'),
                           yaxis=dict(autorange=True,
                                      color='#0C2D48' if not dark_toggle else '#F7F8F8',
                                      gridcolor='rgb(96,96,96)'),
                           transition=dict(duration=500, easing='cubic-in-out'),
                           autosize=True,
                           margin=dict(l=40, r=40, t=40, b=40),
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)'
                           )
               )

    # маркер новости и предсказание
    if modal1_title is not None:
        hour, minutes = [int(i) for i in re.split(':', modal1_time)]

        if (10 <= hour <= 18) and (not (hour == 18 and minutes > 45)):  # с 10 утра до 18:45
            # Предсказание
            # TO-DO: Если изменился только ТФ, заново предсказывать не нужно
            mood, prob = model.detect_tonal(modal1_title)  # cover in list of RuModel (dostoevsky)
            prediction_return = f"{mood}: {prob}"

            # Маркер
            dmy = '.'.join(list(reversed(re.split('-', re.split('T', date)[0]))))  # %d.%m.%Y
            x_coord = f'{dmy} {modal1_time}'
            y_coord = quotes_class.get_price(x_coord)

            if x_coord not in quotes['DATE'].to_list():
                count_bars_1min = (hour - 10) * 60 + minutes
                count_bars_tf = math.ceil(count_bars_1min / tfs[tf_value])
                count_bars_tf += 1 if count_bars_tf == 0 else 0  # если time -> 10:00, то 1-1=0, т.е. 1ая свеча
                x_coord = quotes['DATE'].to_list()[count_bars_tf - 1]

            title = modal1_title
            marker_color = '#041F60' if not dark_toggle else '#ffbf00'
            fig['data'].append(
                go.Scatter(x=[x_coord], y=[y_coord], mode='markers', name='',
                           marker=dict(size=[24], color=[marker_color], symbol='x-dot'),
                           showlegend=False, hovertemplate=f'{modal1_time}<br>{title} </br>')
            )
        time_selected = modal1_time  # global var for dcc.Loading

    return fig, prediction_return


@app.callback(Output('spinner', 'children'),
              [Input('modal1-header-id', 'children'),
               Input('modal1-header-time-id', 'children')])
def spinner(title, modal1_time):
    if title is not None:
        hour, minutes = [int(i) for i in re.split(':', modal1_time)]
        if (10 <= hour <= 18) and (not (hour == 18 and minutes > 45)):  # с 10 утра до 18:45
            while modal1_time != time_selected:  # зацикливаем спиннер, пока не построится прогноз
                time.sleep(0.3)


@app.callback(Output('news', 'options'), [Input('datepicker', 'date')])
def news_options(date):
    news_date = datetime.strptime(date.split('T')[0], '%Y-%m-%d')
    res = get_news(news_date)
    options = [{'label': f' | '.join([n['time'], n['title']]), 'value': f'{n["href"]}'} for n in res]
    return options


@app.callback(Output('company_news', 'options'), [Input('datepicker', 'date'),
                                                  Input('ticker', 'value')])
def company_news_options(date, company):
    news_date = datetime.strptime(date.split('T')[0], '%Y-%m-%d')
    res = mfd_get_news(news_date, company)
    options = [{'label': f' | '.join([n['time'], n['title']]), 'value': f'{n["href"]}'} for n in res]
    return options


@app.callback(Output('company_newslabel', 'children'), [Input('ticker', 'value')])
def news_label(company):
    return f'Новости компании: {company.split("- ")[-1]}'


@app.callback(Output('modal-body-scroll', 'is_open'), [Input("newsbutton_id", "n_clicks"),
                                                       Input("modal-close-id", "n_clicks")],
              [State('modal-body-scroll', 'is_open')])
def show_modal(n1, n2, is_open):
    return not is_open if n1 or n2 else is_open


@app.callback(Output('modal1-body-scroll', 'is_open'), [Input("newsbutton1_id", "n_clicks"),
                                                        Input("modal1-close-id", "n_clicks")],
              [State('modal1-body-scroll', 'is_open')])
def show_modal1(n1, n2, is_open):
    return not is_open if n1 or n2 else is_open


@app.callback([Output('modal-header-id', 'children'),
               Output('modal-header-time-id', 'children'),
               Output('modal-body-id', 'children'),
               Output('newsbutton_id', 'style'),
               Output('news', 'style')],
              [Input('news', 'value')])
def modal_content(href):
    if href is not None:
        res = get_content(href)
        return [res['title'],
                res['time'],
                [html.P(i, style={"white-space": "normal", "text-indent": "10px"}) for i in res['content']],
                {'display': 'unset'},
                {'width': '100%'}]
    else:
        return [None, None, None, {'display': 'none'}, {'width': '103%'}]


@app.callback([Output('modal1-header-id', 'children'),
               Output('modal1-header-time-id', 'children'),
               Output('modal1-body-id', 'children'),
               Output('newsbutton1_id', 'style'),
               Output('company_news', 'style')],
              [Input('company_news', 'value')])
def modal1_content(href):
    if href is not None:
        res = mfd_get_content(href)
        return [res['title'],
                res['time'],
                [html.P(i, style={"white-space": "normal", "text-indent": "10px"}) for i in res['content']],
                {'display': 'unset'},
                {'width': '100%'}]
    else:
        return [None, None, None, {'display': 'none'}, {'width': '103%'}]


app.scripts.config.serve_locally = True

if __name__ == '__main__':
    app.run_server(debug=True)
