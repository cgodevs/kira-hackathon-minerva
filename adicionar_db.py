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

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Criando as primeiras comunidades
try:
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Gravidez", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Menstruação", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Saúde e Bem Estar", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Sexualidade", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Ciclo Menstrual", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Sororidade", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Questionando Estigmas", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Produtos Intimus", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Positivade Corporal", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.add(Comunidade(id_criador=1, criador=Usuario.query.get(id=1), nome="Dicas de Moda", descricao="Descrição da Comunidade", data_criacao=date.today()))
    db.session.commit()
except:
    pass


# tópicos são: "Gravidez", "Menstruação", "Saúde e Bem Estar", "Sexualiade", "Ciclo Menstrual", "Sororidade", "Questionando Estigmas", "Produtos Intimus", "Positivade Corporal", "Dicas de Moda"