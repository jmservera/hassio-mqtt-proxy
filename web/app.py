def webApp(port=8080):
    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello world'

    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    webApp()
