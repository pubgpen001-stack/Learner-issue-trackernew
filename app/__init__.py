from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
socketio = SocketIO()

@login_manager.user_loader
def load_user(user_id):
    from app.models import get_user_by_id
    return get_user_by_id(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    socketio.init_app(app)

    from app.models import close_db
    app.teardown_appcontext(close_db)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.boards import boards_bp
    from app.routes.issues import issues_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(boards_bp)
    app.register_blueprint(issues_bp)

    from app.routes import chat  # registers socketio events

    return app