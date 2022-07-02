from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField


COMUNIDADES = [ "Gravidez", "Menstruação", "Saúde e Bem Estar", "Sexualiade", "Ciclo Menstrual", "Sororidade", "Questionando Estigmas", "Produtos Intimus", "Positivade Corporal", "Dicas de Moda"]


class FormRegistro(FlaskForm):
    nomecompleto_form = StringField("Nome Completo", validators=[DataRequired()])
    username_form = StringField("Username", validators=[DataRequired()])
    email_form = EmailField("E-mail", validators=[DataRequired(), Email()])
    senha_form = PasswordField("Senha", validators=[DataRequired()])
    submit_form = SubmitField("Registrar")


class FormLogin(FlaskForm):
    email_form = EmailField("E-mail", validators=[DataRequired(), Email()])
    senha_form = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class FormPost(FlaskForm):
    titulo_form = StringField("Título do Post", validators=[DataRequired()])
    comunidade_form = SelectField("Escolha uma Comunidade")
    corpo_form = CKEditorField("Mensagem", validators=[DataRequired()])
    submit = SubmitField("Enviar")


class FormDM(FlaskForm):
    corpo_form = TextAreaField("Mensagem", validators=[DataRequired()])
    submit = SubmitField("Enviar")


class FormComentario(FlaskForm):
    corpo_form = CKEditorField("", validators=[DataRequired()])
    submit = SubmitField("Enviar Comentário")


class EntradaForm(FlaskForm):
    titulo_form = StringField("Título")
    corpo_form = CKEditorField("Conte seus pensamentos", validators=[DataRequired()])
    submit = SubmitField("Enviar")


class CriarComunidadeForm(FlaskForm):
    nome_comunidade_form = StringField("Qual o nome da comunidade?", validators=[DataRequired()])
    descricao_comunidade_form = TextAreaField("Descreva sobre o que deseja falar na comunidade", validators=[DataRequired()])
    submit = SubmitField("Criar")


class CriarArtigo(FlaskForm):  # para admins, por enquanto
    titulo_form = StringField("Qual o título do artigo?", validators=[DataRequired()])
    corpo_form = CKEditorField("Escrever Artigo", validators=[DataRequired()])
    submit = SubmitField("Enviar")
