from flask import Flask
from contract import contracts_bp
 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
 
# Register routes
app.register_blueprint(contracts_bp)

if __name__ == '__main__':
    print("HouseWise backend is running! http://localhost:5000")
    app.run(debug=True)


