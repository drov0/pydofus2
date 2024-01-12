import json

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash.dependencies import ALL, State
from pydofus2.sniffer.network.DofusSniffer import DofusSniffer



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

sniffer = DofusSniffer()

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dofus Sniffer Interface"), width=12),
        dbc.Col(dbc.Button("Start", id="start-btn", color="success", className="me-1"), width='auto'),
        dbc.Col(dbc.Button("Stop", id="stop-btn", color="danger", className="me-1"), width='auto')
    ]),
    dbc.Tabs(id="connection-tabs", active_tab=None),
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Interval for periodic UI updates
], fluid=True)

@app.callback(
    Output('connection-tabs', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_ui(_):
    return generate_tabs()

def generate_tabs():
    tabs = []
    for conn_id, messages in sniffer.messagesRecord.items():
        clear_button_id = f"clear-btn-{conn_id}"
        messages_container_id = f"messages-container-{conn_id}"
        tab_content = html.Div([
            dbc.Button("Clear", id=clear_button_id, className="mb-2"),
            html.Div(id=messages_container_id, children=[generate_message_layout(msg) for msg in messages])
        ])
        tab = dbc.Tab(label=f"Connection {conn_id}", tab_id=f"tab-{conn_id}", children=tab_content)
        tabs.append(tab)
    return tabs

@app.callback(
    [Output('start-btn', 'disabled'), Output('stop-btn', 'disabled')],
    [Input('start-btn', 'n_clicks'), Input('stop-btn', 'n_clicks')]
)
def control_sniffer(start_clicks, stop_clicks):
    if start_clicks:
        sniffer.start()
        return True, False  # Disable start button, enable stop button
    if stop_clicks:
        sniffer.stop()
        return False, True  # Enable start button, disable stop button
    return dash.no_update

def generate_message_layout(msg):
    direction = msg["__direction__"]
    color_class = "text-success" if direction == 'snd' else "text-primary"
    return html.Details([
        html.Summary(f"{msg['__receptionTime__']} - {direction} - {msg['__type__']}", className=color_class),
        html.Pre(json.dumps(msg, indent=4))
    ])

@app.callback(
    Output({'type': 'messages-container', 'index': ALL}, 'children'),
    Input({'type': 'clear-btn', 'index': ALL}, 'n_clicks'),
    State({'type': 'messages-container', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def clear_messages(n_clicks, ids):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    conn_id = button_id.split('-')[-1]

    if conn_id in sniffer.messagesRecord:
        sniffer.messagesRecord[conn_id].clear()

    # Update the specific message container related to the clicked clear button
    updated_containers = []
    for container_id in ids:
        container_conn_id = container_id['index']
        container_content = generate_message_layout(sniffer.messagesRecord[container_conn_id]) if container_conn_id == conn_id else dash.no_update
        updated_containers.append(container_content)

    return updated_containers


if __name__ == '__main__':
    app.run_server(debug=True)
