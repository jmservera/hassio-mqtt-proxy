from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',name=__name__)

def webApp(port=8080, production=False):
    if production:
        import waitress
        waitress.serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    webApp()
