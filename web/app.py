@app.route('/')
def index():
    return 'Hello world'

def webApp(port=8080, production=False):
    from flask import Flask

    app = Flask(__name__)

    if production:
        import waitress
        waitress.serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    webApp()
