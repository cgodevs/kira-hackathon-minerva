import sqlalchemy.exc
from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import *
from math import ceil
from flask_ckeditor import CKEditor
from functools import wraps
import os
from sqlalchemy import or_
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)
app.config['SECRET_KEY'] = "aa" #os.environ.get("SECRET_KEY") #"SECRET_KEY"
bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# SET LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

# CONFIGURAÇÃO DE TABELAS
class Usuario(UserMixin, db.Model): #PAI
    __tablename__ = "usuarios" 
    id = db.Column(db.Integer, primary_key=True) 
    nome_completo = db.Column(db.String(200)) 
    username = db.Column(db.String(100), unique=True) 
    email = db.Column(db.String(200), unique=True) 
    password = db.Column(db.String(100)) 
    pontos = db.Column(db.Integer)
    # ********************** Relações com outras tabelas ****************
    posts = relationship("Post", back_populates="autor_post") 
    comentarios_usuario = relationship("Comentario", back_populates="autor_comentario")
    comunidades_criadas = relationship("Comunidade", back_populates="criador")
    entradas_usuario = relationship("Entrada", back_populates="autor_entrada")
    dms_recebidas = relationship("DirectMessage", back_populates="recipiente")


class Participacao(db.Model):  # tabela para comportar relação M:N
    __tablename__ = "participacao"
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), primary_key=True)
    id_comunidade = db.Column(db.Integer, db.ForeignKey("comunidades.id"), primary_key=True)


class Comunidade(db.Model): #PAI
    __tablename__ = "comunidades" 
    id = db.Column(db.Integer, primary_key=True) 
    id_criador = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    nome = db.Column(db.String(100), nullable=False) 
    descricao = db.Column(db.String(500), nullable=False) 
    data_criacao = db.Column(db.Date, nullable=False)
    # ********************* Relações **************************
    criador = relationship("Usuario", back_populates="comunidades_criadas")
    posts = relationship("Post", back_populates="comunidade")

# TODO criar algumas comunidades padrão aqui

class Post(db.Model): #FILHO
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True) 
    id_autor_post = db.Column(db.Integer, db.ForeignKey("usuarios.id")) 
    id_comunidade = db.Column(db.Integer, db.ForeignKey("comunidades.id"))
    titulo = db.Column(db.String(140), nullable=False)
    data = db.Column(db.Date, nullable=False)
    corpo = db.Column(db.Text, nullable=False)
    eh_artigo = db.Column(db.Boolean,nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    # ***************Parent Relationship*************#
    comentarios = relationship("Comentario", back_populates="parent_post")
    autor_post = relationship("Usuario", back_populates="posts")  
    comunidade = relationship("Comunidade", back_populates="posts")


class Comentario(db.Model):
    __tablename__ = "comentarios"
    id = db.Column(db.Integer, primary_key=True)
    id_autor_comentario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    data = db.Column(db.Date, nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    # ***************Child Relationship*************#
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    autor_comentario = relationship("Usuario", back_populates="comentarios_usuario")
    parent_post = relationship("Post", back_populates="comentarios")


class DirectMessage(db.Model):
    __tablename__ = "dms"
    id = db.Column(db.Integer, primary_key=True)
    id_recipiente = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    autor = db.Column(db.String(250), nullable=False)
    data = db.Column(db.Date, nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    recipiente = relationship("Usuario", back_populates="dms_recebidas")


class Entrada(db.Model):
    __tablename__ = "entradas"
    id = db.Column(db.Integer, primary_key=True)
    id_autor_entrada = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    autor_entrada = relationship("Usuario", back_populates="entradas_usuario")
    titulo = db.Column(db.String(140), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data = db.Column(db.Date, nullable=False)


class Assunto(db.Model):
    __tablename__ = "assuntos"
    id = db.Column(db.Integer, primary_key=True)
    nome_assunto = db.Column(db.String(100), nullable=False)
    kbs = relationship("KB", back_populates="assunto")


class KB(db.Model):
    __tablename__ = "kbs"
    id = db.Column(db.Integer, primary_key=True)
    id_assunto = db.Column(db.Integer, db.ForeignKey("assuntos.id"))   
    assunto = relationship("Assunto", back_populates="kbs") 
    titulo = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)

db.create_all()


@app.route('/')
def home():
    if current_user.is_authenticated:
        return mainpage(1)
    return render_template("blank_start.html")


@app.route('/comunidades/<base>')
def comunidades(base, pagina=1):
    todas_comunidades = db.session.query(Comunidade).all()

    if current_user.is_authenticated:
        inscricoes = db.session.query(Participacao).filter_by(id_usuario=current_user.id).all()
        comunidades_associadas = [db.session.query(Comunidade).get(inscricao.id_comunidade)
                                 for inscricao in inscricoes]  # estas são também as comunidades criadas

        if db.session.query(Post).first():  # se houver algum post
            posts = None
            if base == 'featured':
                posts = db.session.query(Post).filter(Post.upvotes > 0).order_by(Post.upvotes.desc()).all()
            elif base == 'artigos':
                posts = db.session.query(Post).filter(Post.eh_artigo is True).order_by(Post.data.desc()).all()
            elif base == 'recentes':
                # não aparecem posts mais velhos que 10 dias
                posts = db.session.query(Post).order_by(Post.id.desc()).filter(date.today() - Post.data <= 10).all()
            elif base == 'descubra':
                comunidades_de_uma_pagina = todas_comunidades[(pagina - 1) * 4: (pagina - 1) * 4 + 4]
                n_paginas = int(ceil(len(list(todas_comunidades)) / 4)) #TODO aumentar o valor
                return render_template("comunidades.html",
                                       base=base,
                                       pagina=pagina,
                                       comunidades_de_uma_pagina=comunidades_de_uma_pagina,
                                       n_paginas=n_paginas,
                                       todas_comunidades=todas_comunidades,
                                       comunidades_associadas=comunidades_associadas)

            posts_de_uma_pagina = posts[(pagina - 1) * 6: (pagina - 1) * 6 + 6]
            n_paginas = int(ceil(len(list(posts)) / 6))

            return render_template("comunidades.html",
                                   base=base,
                                   pagina=pagina,
                                   posts=posts_de_uma_pagina,
                                   n_paginas=n_paginas,
                                   todas_comunidades=todas_comunidades,
                                   comunidades_associadas=comunidades_associadas)
        else:
            return home()
    if todas_comunidades:  # proteção contra erros no momento inicial em que ainda não existe db
        return render_template("comunidades.html", todas_comunidades=todas_comunidades, comunidades_associadas=todas_comunidades)
    else:
        return home()

@app.route('/artigos')
def artigos():
    if current_user.is_authenticated:
        if db.session.query(Post).first():
            pagination = 1
            all_latest_posts = db.session.query(Post).order_by(Post.id.desc()).filter(date.today() - Post.data <= 10)
            number_of_pages = int(ceil(all_latest_posts.count() / 6))
            page_posts = all_latest_posts[(pagination - 1) * 6: (pagination - 1) * 6 + 6]
            most_upvoted_post = db.session.query(Post).order_by(Post.id.desc()).first()     # last record
            for post in all_latest_posts:
                if post.upvotes > most_upvoted_post.upvotes:
                    most_upvoted_post = post    # featured post is the most upvoted in the last 10 days or the last ever record
            return render_template("artigos.html",
                                   pagination=pagination,
                                   featured_post=most_upvoted_post,
                                   posts=page_posts,
                                   pages=number_of_pages)
    return render_template("artigos.html")

@app.route('/recentes')
def recentes():
    if current_user.is_authenticated:
        if db.session.query(Post).first():
            pagination = 1
            all_latest_posts = db.session.query(Post).order_by(Post.id.desc()).filter(date.today() - Post.data <= 10)
            number_of_pages = int(ceil(all_latest_posts.count() / 6))
            posts = all_latest_posts[(pagination - 1) * 6: (pagination - 1) * 6 + 6]
            return render_template("recentes.html",
                                   pagination=pagination,
                                   posts=posts,
                                   pages=number_of_pages)
    return render_template("recentes.html")

@app.route('/calendario')
def calendario():
    return render_template("calendario.html")

@app.route('/diario')
def diario():
    return render_template("diario.html")

@app.route('/adicionar-entrada', methods=['GET', 'POST'])
def escrever_diario():
    form_entrada_diario = EntradaForm()
    if form_entrada_diario.validate_on_submit():
        autor_entrada = Usuario.query.get(current_user.id)
        nova_entrada = Entrada(
            id_autor_entrada = current_user.id,
            autor_entrada = autor_entrada,
            titulo = form_entrada_diario.titulo_form.data,
            texto = form_entrada_diario.corpo_form.data,
            data = date.today(),
        )
        db.session.add(nova_entrada)
        db.session.commit()
        return diario()
    return render_template("escrever-diario.html", form=form_entrada_diario)

@app.route('/conhecimento')
def conhecimento():
    return render_template("conhecimento.html")

@app.route('/shopping')
def shopping():
    return render_template("shopping.html")


@app.route('/mainpage/<int:pagination>')
def mainpage(pagination):
    if current_user.is_authenticated:
        comunidades_recentes = db.session.query(Comunidade).order_by(Comunidade.data_criacao.desc())
        return render_template("full_homepage.html", comunidades=comunidades_recentes)
    return home()


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form_registro = FormRegistro()
    if form_registro.validate_on_submit():
        database_email_match = Usuario.query.filter_by(email=form_registro.email_form.data).first()
        if database_email_match:
            error = 'E-mail already exists'
            flash('This e-mail adress is already registered. Try another one.')
            return redirect(url_for('register', error=error))
        database_username_match = Usuario.query.filter_by(username=form_registro.username_form.data).first()
        if database_username_match:
            error = 'Username already exists'
            flash('This username is already in use. Try another one.')
            return redirect(url_for('register', error=error))
        novo_usuario = Usuario(
            nome_completo = form_registro.nomecompleto_form.data,
            username=form_registro.username_form.data,
            email=form_registro.email_form.data,
            password=generate_password_hash(form_registro.senha_form.data, method='pbkdf2:sha256', salt_length=8),
            pontos=0       
        )
        db.session.add(novo_usuario)
        db.session.commit()
        load_user(novo_usuario.id)
        login_user(novo_usuario)
        return redirect(url_for('home'))
    return render_template("register.html", form=form_registro)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = FormLogin()
    if login_form.validate_on_submit():
        email = login_form.email_form.data
        password = login_form.senha_form.data
        database_match = Usuario.query.filter_by(email=email).first()
        if not database_match:
            error = 'Invalid credentials'
            flash('E-mail adress not registered, please try again or sign up.')
            return redirect(url_for('login', error=error))
        elif not check_password_hash(database_match.password, password):
            error = 'Password incorrect'
            flash('Password incorrect, please try again.')
            return redirect(url_for('login', error=error))
        else:
            load_user(database_match.id)
            login_user(database_match)
            return redirect(url_for('home'))
    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# TODO volta aqui após criar comunidades
@app.route('/novo-post', methods=['GET', 'POST'])
def novo_post():
    relacoes_comunidades = db.session.query(Participacao).filter_by(id_usuario=current_user.id).all()
    comunidades_usuario = [Comunidade.query.get(participacao.id_comunidade) for participacao in relacoes_comunidades]
    form_post = FormPost()
    form_post.comunidade_form.choices = [(comunidade.id, comunidade.nome) for comunidade in comunidades_usuario]

    if form_post.comunidade_form.choices is None:  #TODO retirar isso, tornar opção de postar inativa
        return render_template("Você não se cadastrou em nenhum comunidade ainda.")

    if form_post.validate_on_submit():
        titulo = form_post.titulo_form.data
        corpo = form_post.corpo_form.data
        id_comunidade = int(form_post.comunidade_form.data)
        comunidade = Comunidade.query.get(id_comunidade)
        autor_post = Usuario.query.get(current_user.id)
        post = Post(autor_post=autor_post,
                    id_autor_post=autor_post.id,
                    titulo=titulo,
                    data=date.today(),  # .strftime("%B %d, %Y")
                    comunidade=comunidade,
                    id_comunidade=id_comunidade,
                    corpo=corpo,
                    eh_artigo=False)

        autor_post.pontos += 20
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('comunidades', base='recentes'))
    return render_template('novo-post.html', form=form_post)


@app.route('/nova-comunidade', methods=['GET', 'POST'])
def nova_comunidade():
    nova_comu_form = CriarComunidadeForm()
    if nova_comu_form.validate_on_submit():
        nome = nova_comu_form.nome_comunidade_form.data
        descricao = nova_comu_form.descricao_comunidade_form.data
        criador = Usuario.query.get(current_user.id)
        comunidade_nova = Comunidade(
                            id_criador=current_user.id,
                            criador=criador,
                            nome=nome,
                            descricao=descricao,
                            data_criacao=date.today()  # .strftime("%B %d, %Y")
                        )
        db.session.add(comunidade_nova)
        db.session.commit()

        criador.pontos += 30

        nova_relacao = Participacao(
            id_usuario=current_user.id,
            id_comunidade=comunidade_nova.id
        )
        db.session.add(nova_relacao)
        db.session.commit()
        #usuario_logado = Usuario.query.get(current_user.id)
        #usuario_logado.pontos += 35
        return redirect(url_for('comunidades', base='recentes')) # TODO Retornar para a página de recentes desta comunidade
    return render_template("criar-comunidade.html", form=nova_comu_form)


@app.route('/minhas_comunidades_criadas')
def minhas_comunidades_criadas():
    comunidades_criadas = current_user.comunidades_criadas
    return render_template("comunidades-criadas.html", comunidades_criadas=comunidades_criadas)


@app.route('/unir-se/<int:id_comunidade>')
def unir_se(id_comunidade):
    try:
        nova_inscricao = Participacao(id_usuario=current_user.id,
                                      id_comunidade=id_comunidade)
        db.session.add(nova_inscricao)
        db.session.commit()
    except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
        return comunidades('descubra', pagina=1)
    return busca_comunidade(id_comu=id_comunidade)

@app.route('/my-profile/<menu_action>', methods=['GET', 'POST'])
def my_profile(menu_action):
    if menu_action == 'reset-pw':
        if request.method == 'POST':
            old_pw = request.form.get("old-pw")
            new_pw = request.form.get("new-pw")
            database_match_pw = Usuario.query.filter_by(email=current_user.email).first().password
            if old_pw == "" or new_pw == "":
                pass
            elif not check_password_hash(database_match_pw, old_pw):
                flash('Password incorrect.')
            elif check_password_hash(database_match_pw, new_pw):
                flash('New password cannot be equal to the last one.')
            else:
                Usuario.query.filter_by(email=current_user.email).first().password = generate_password_hash(new_pw, method='pbkdf2:sha256', salt_length=8)
                db.session.commit()
                flash('Password changed successfully!.')
        return render_template('reset-pw.html')
    elif menu_action == 'reset-address':
        if request.method == 'POST':
            new_address = request.form.get("new-address")
            Usuario.query.filter_by(email=current_user.email).first().email = new_address
            db.session.commit()
            flash('Address  changed successfully')
        return render_template('reset-address.html')
    elif menu_action == 'posts-de-usuario':
        user_posts = Post.query.filter_by(autor_post=current_user)
        return render_template('posts-de-usuario.html', posts=user_posts)
    elif menu_action == 'dms':
        return render_template('dms.html')
    elif menu_action == 'pontos':
        return render_template('pontos.html')


@app.route('/user/<int:id_usuario>')
def user_page(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    return render_template('perfil-usuario.html', usuario=usuario)


@app.route('/send-dm/<id_usuario>', methods=['GET', 'POST'])
def send_dm(id_usuario):

    usuario_recebendo = Usuario.query.get(id_usuario)
    form_dm = FormDM()
    if form_dm.validate_on_submit():
        mensagem = form_dm.corpo_form.data
        new_dm = DirectMessage(recipiente=usuario_recebendo,
                               id_recipiente=usuario_recebendo.id,
                               autor=current_user,
                               data=date.today(),   #.strftime("%B %d, %Y")
                               mensagem=mensagem)
        db.session.add(new_dm)
        db.session.commit()
        return render_template('perfil-usuario.html', usuario=usuario_recebendo)
    return render_template('send-dm.html', usuario=usuario_recebendo, form=form_dm)


@app.route("/delete-dm/<int:dm_id>")
def delete_dm(dm_id):
    dm_to_delete = DirectMessage.query.get(dm_id)
    db.session.delete(dm_to_delete)
    db.session.commit()
    return redirect(url_for('my_profile', menu_action='dms'))


@app.route("/post/<int:q_id>", methods=['GET', 'POST'])
def show_post(q_id):
    form_comentario = FormComentario()
    db_post = Post.query.get(q_id)
    if db_post:
        if form_comentario.validate_on_submit():
            texto_comentario = form_comentario.corpo_form.data
            novo_comentario = Comentario(id_autor_comentario=current_user.id,
                                  data=date.today(),    # .strftime("%B %d, %Y")
                                  mensagem=texto_comentario,
                                  post_id=q_id,
                                  autor_comentario=current_user,  
                                  parent_post=db_post)
            Usuario.query.get(current_user.id).pontos += 15
            db.session.add(novo_comentario)
            db.session.commit()
        return render_template('post.html', post=db_post, form_comentario=form_comentario)
    else:
        return abort(404)


@app.route("/upvote/<int:q_id>")
def upvote_post(q_id):
    post = Post.query.get(q_id)
    post.upvotes += 1
    autor_post = Post.query.get(post.id).autor_post
    if current_user.id != autor_post.id:
        Usuario.query.get(autor_post.id).pontos += 1
    db.session.commit()
    return redirect(url_for('show_post', q_id=q_id))


@app.route("/delete-post/<int:q_id>")
def delete_post(q_id):
    post_para_deletar = Post.query.get(q_id)
    db.session.delete(post_para_deletar)
    db.session.commit()
    return my_profile('posts-de-usuario')


@app.route("/delete-comment/<int:q_id>/<int:comment_id>")
def delete_comment(q_id, comment_id):
    comment_to_delete = Comentario.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('show_post', q_id=q_id))


@app.route("/busca/<id_comu>")
def busca_comunidade(id_comu: int):
    comunidade_escolhida = Comunidade.query.get(id_comu)
    all_category_posts = db.session.query(Post) \
        .filter_by(comunidade=comunidade_escolhida) \
        .order_by(Post.id.desc())
    todas = db.session.query(Comunidade).all()
    if current_user.is_authenticated:
        inscricoes = db.session.query(Participacao).filter_by(id_usuario=current_user.id).all()
        todas = [db.session.query(Comunidade).get(inscricao.id_comunidade)
                                  for inscricao in inscricoes]
    return render_template('posts-comunidade.html',
                           posts=all_category_posts,
                           comunidade=comunidade_escolhida,
                           comunidades=todas)


@app.route("/busca/por-palavras", methods=['GET', 'POST'])
def busca():
    if request.method == 'POST':
        search_keys = request.form.get("search-keys")
        match_posts = db.session.query(Post) \
            .filter(or_(Post.corpo.contains(search_keys),Post.titulo.contains(search_keys))) \
            .order_by(Post.id.desc())
    return render_template('busca.html', posts=match_posts)


@app.route("/buscar/todas-comunidades")
def todas_comunidades():  # TODO ?!!
    return render_template('todas-comunidades.html', comunidades=COMUNIDADES)


if __name__ == "__main__":
    app.run(debug=True)

