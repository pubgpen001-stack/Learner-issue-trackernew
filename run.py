from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=False, allow_unsafe_werkzeug=True, host='0.0.0.0', port=5000)
