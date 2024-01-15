import json

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from dash.dependencies import ALL, State

from pydofus2.sniffer.network.DofusSniffer import DofusSniffer


class DofusSnifferApp:
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.sniffer = DofusSniffer("DofusSnifferApp", on_crash=self.handle_sniffer_crash)
        
        self.setup_layout()
        self.setup_callbacks()

    def handle_sniffer_crash(error):
        # Define what to do when the sniffer crashes
        # For example, log the error and alert the user
        print(f"Sniffer crashed with error: {error}")

    def setup_layout(self):
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("Dofus Sniffer Interface"), width=12),
                dbc.Col(dbc.Button("Start", id="start-btn", color="success", className="me-1"), width='auto'),
                dbc.Col(dbc.Button("Stop", id="stop-btn", color="danger", className="me-1"), width='auto')
            ]),
            dbc.Tabs(id="connection-tabs", active_tab=None),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0)  # Interval for periodic UI updates
        ], fluid=True)

    def setup_callbacks(self):
        @self.app.callback(
            Output('connection-tabs', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_ui(_):
            return self.generate_tabs()

        @self.app.callback(
            [Output('start-btn', 'disabled'), Output('stop-btn', 'disabled')],
            [Input('start-btn', 'n_clicks'), Input('stop-btn', 'n_clicks')]
        )
        def control_sniffer(start_clicks, stop_clicks):
            if start_clicks:
                self.sniffer.start()
                return True, False
            if stop_clicks:
                self.sniffer.stop()
                return False, True
            return dash.no_update

        @self.app.callback(
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

            if conn_id in self.sniffer.messagesRecord:
                self.sniffer.messagesRecord[conn_id].clear()

            updated_containers = []
            for container_id in ids:
                container_conn_id = container_id['index']
                container_content = self.generate_message_layout(self.sniffer.messagesRecord[container_conn_id]) if container_conn_id == conn_id else dash.no_update
                updated_containers.append(container_content)

            return updated_containers

    def generate_tabs(self):
        tabs = []
        for conn_id, messages in self.sniffer.messagesRecord.items():
            clear_button_id = f"clear-btn-{conn_id}"
            messages_container_id = f"messages-container-{conn_id}"
            tab_content = html.Div([
                dbc.Button("Clear", id=clear_button_id, className="mb-2"),
                html.Div(id=messages_container_id, children=[self.generate_message_layout(msg) for msg in messages])
            ])
            tab = dbc.Tab(label=f"Connection {conn_id}", tab_id=f"tab-{conn_id}", children=tab_content)
            tabs.append(tab)
        return tabs


    def generate_message_layout(self, msg):
        direction = msg["__direction__"]
        color_class = "text-success" if direction == 'snd' else "text-primary"
        return html.Details([
            html.Summary(f"{msg['__receptionTime__']} - {direction} - {msg['__type__']}", className=color_class),
            html.Pre(json.dumps(msg, indent=4))
        ])

    def run(self):
        self.app.run(debug=True)


if __name__ == '__main__':
    sniffer_app = DofusSnifferApp()
    sniffer_app.run()
