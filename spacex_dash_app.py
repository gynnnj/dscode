'''
Which site has the largest successful launches?
KSC LC-39A

Which site has the highest launch success rate?

Which payload range(s) has the highest launch success rate?
2000 - 4000

Which payload range(s) has the lowest launch success rate?
4000 - 5000

Which F9 Booster version (v1.0, v1.1, FT, B4, B5, etc.) has the highest
launch success rate?
FT
'''

import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
                    {'label': 'All Sites', 'value': 'ALL'}
                ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2 Callback Function
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Aggregate total successful launches by site
        success_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        success_by_site.columns = ['Launch Site', 'Total Successful Launches']
        fig = px.pie(
            success_by_site,
            names='Launch Site',
            values='Total Successful Launches',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter data for the selected site and show success vs. failed launches for that site
        df_filtered = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = df_filtered['class'].value_counts()
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title=f'Success vs. Failed Launches for {selected_site}',
            labels={'index': 'Launch Outcome', 'value': 'Count'}
        )

    return fig


# TASK 4 Callback Function
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(selected_site, payload_range):
    min_payload, max_payload = payload_range

    if selected_site == 'ALL':
        df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= min_payload) & (spacex_df['Payload Mass (kg)'] <= max_payload)]
        fig = px.scatter(
            df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload Mass vs. Success for All Sites'
        )
    else:
        df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                       (spacex_df['Payload Mass (kg)'] >= min_payload) &
                       (spacex_df['Payload Mass (kg)'] <= max_payload)]
        fig = px.scatter(
            df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload Mass vs. Success for {selected_site}'
        )

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(port=8051)
