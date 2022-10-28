# Code Block 1 Starts
import dash
import dash_html_components as dhtml
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
from pymongo import MongoClient
import pymongo

import time
import plotly

# Creating Dash Application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally=True
# Code Block 1 Ends

host_name = "34.70.106.130"
port_no = "27017"
user_name = "demouser"
password = "demouser"
database_name = "trans_db"

connection_object = MongoClient(host=host_name, port=int(port_no))
db_object = connection_object[database_name]
db_object.authenticate(name=user_name, password=password)

# Code Block 2 Starts
def build_pd_df_from_sql():
    print("Starting build_pd_df_from_sql: " + time.strftime("%Y-%m-%d %H:%M:%S"))
    current_refresh_time_temp = None

    year_total_sales = db_object.year_wise_total_sales_count
    year_total_sales_df = pd.DataFrame(list(year_total_sales.find().sort([("_id", pymongo.DESCENDING)]).limit(100)))
    df1 = year_total_sales_df.groupby(['tran_year'], as_index=False).agg({'tran_year_count': "sum"})

    country_total_sales = db_object.country_wise_total_sales_count
    country_total_sales_df = pd.DataFrame(list(country_total_sales.find().sort([("_id", pymongo.DESCENDING)]).limit(100)))
    df2 = country_total_sales_df.groupby(['nationality'], as_index=False).agg({'tran_country_count': "sum"})
    #print(df2.head(100))

    print("Completing build_pd_df_from_sql: " + time.strftime("%Y-%m-%d %H:%M:%S"))
    return {"df1": df1, "df2": df2}
# Code Block 2 Ends

# Code Block 3 Starts
df1_df1_dictionary_object = build_pd_df_from_sql()
df1 = df1_df1_dictionary_object["df1"]
df2 = df1_df1_dictionary_object["df2"]
# Code Block 3 Ends

# Code Block 4 Starts
# Assign HTML Content to Dash Application Layout
app.layout = dhtml.Div(
    [
        dhtml.H2(
            children="Real-Time Dashboard for Retail Sales Analysis",
            style={
                "textAlign": "center",
                "color": "#34A853",
                'font-weight': 'bold',
                'font-family': 'Verdana'
            }),
        dhtml.Div(
            id = "current_refresh_time",
            children="Current Refresh Time: ",
            style={
                "textAlign": "center",
                "color": "#EA4335",
                'font-weight': 'bold',
                'fontSize': 12,
                'font-family': 'Verdana'
            }
        ),
        dhtml.Div([
            dhtml.Div([
                dcc.Graph(id='live-update-graph-bar')
                ]),

            dhtml.Div([
                    dhtml.Br(),
                    dash_table.DataTable(
                        id='datatable-country-wise',
                        columns=[
                            {"name": i, "id": i} for i in sorted(df2.columns)
                        ],
                        data=df2.to_dict(orient='records')
                    )
                ], className="six columns"),
        ], className="row"),

        dcc.Interval(
            id = "interval-component",
            interval = 10000,
            n_intervals = 0
        )
    ]
)
# Code Block 4 Ends

# Code Block 5 Starts
@app.callback(
    Output("current_refresh_time", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_layout(n):
    # current_refresh_time
    global current_refresh_time_temp
    current_refresh_time_temp = time.strftime("%Y-%m-%d %H:%M:%S")
    return "Current Refresh Time: {}".format(current_refresh_time_temp)
# Code Block 5 Ends

# Code Block 6 Starts
@app.callback(
    Output("live-update-graph-bar", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_graph_bar(n):
    traces = list()
    bar_1 = plotly.graph_objs.Bar(
            x=df1["tran_year"],
            y=df1["tran_year_count"],
            name='Year')
    traces.append(bar_1)
    layout = plotly.graph_objs.Layout(
        barmode='group', xaxis_tickangle=-25, title_text="Yearly Retail Sales Count",
        title_font=dict(
            family="Verdana",
            size=14,
            color="black"
        ),
    )
    return {'data': traces, 'layout': layout}
# Code Block 6 Ends

# Code Block 7 Starts
@app.callback(
    Output('datatable-country-wise', 'data'),
    [Input("interval-component", "n_intervals")])
def update_table(n):
    global df1
    global df2

    print("In update_table")

    df1_df1_dictionary_object = build_pd_df_from_sql()
    df1 = df1_df1_dictionary_object["df1"]
    df2 = df1_df1_dictionary_object["df2"]

    return df2.to_dict(orient='records')
# Code Block 7 Ends

# Code Block 8 Starts
if __name__ == "__main__":
    print("Starting Real-Time Dashboard For  ... ")
    #app.run_server(port=8090, debug=True)
    app.run_server(host="10.128.0.5",port=8090, debug=True)
# Code Block 8 Ends