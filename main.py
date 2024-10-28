# Importar
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Para manejar sesiones de usuario

# Conectando SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creando una base de datos
db = SQLAlchemy(app)

# Creación de una tabla para las cartas
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relación con User

    def __repr__(self):
        return f'<Card {self.id}>'

# Tabla para los usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    cards = db.relationship('Card', backref='user', lazy=True)  # Relación uno a muchos

    def __repr__(self):
        return f'<User {self.id}>'


# Ruta de inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']

        user = User.query.filter_by(login=form_login, password=form_password).first()
        if user:
            session['user_id'] = user.id  # Guardar el id del usuario en la sesión
            return redirect('/index')
        else:
            error = 'Nombre de usuario o contraseña incorrectos'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Ruta de registro de usuarios
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        login = request.form['email']
        password = request.form['password']

        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/')
    else:
        return render_template('registration.html')

# Ruta principal que muestra las cartas del usuario logueado
@app.route('/index')
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/')

    # Visualización de las entradas del usuario logueado
    cards = Card.query.filter_by(user_id=user_id).order_by(Card.id).all()
    return render_template('index.html', cards=cards)

# Ruta para mostrar una carta específica del usuario logueado
@app.route('/card/<int:id>')
def card(id):
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/')

    card = Card.query.get_or_404(id)
    if card.user_id != user_id:
        return "No tienes permiso para ver esta carta.", 403

    return render_template('card.html', card=card)

# Ruta para crear una nueva carta
@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('create_card.html')

# Ruta para manejar el formulario de creación de cartas
@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if user_id is None:
            return redirect('/')

        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        # Creación de una carta asignada al usuario logueado
        card = Card(title=title, subtitle=subtitle, text=text, user_id=user_id)
        db.session.add(card)
        db.session.commit()

        return redirect('/index')
    else:
        return render_template('create_card.html')

# Cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')




#para correr o iniciar la pagina web en forma local
if __name__ == "__main__":
    app.run(debug=True)


#los comandos para crear una base de datos son:
#primero escribir en la terminal 'python'
#from main import app, db
#app.app_context().push()
#db.create_all()