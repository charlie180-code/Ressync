from ..extensions import socketio

def register_socket_handlers():
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
        
    @socketio.on('subscribe_employees')
    def handle_subscribe(data):
        company_id = data.get('company_id')
        if company_id:
            join_room(f'company_{company_id}')