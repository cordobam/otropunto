from flask_wtf import FlaskForm
from wtforms.fields import StringField , PasswordField , SubmitField  , SelectField , FloatField , TextAreaField , SelectMultipleField , BooleanField
from wtforms.validators import DataRequired , Email , email_validator
from wtforms.fields.html5 import DateField

#### LOGIN 

class LoginForm(FlaskForm):
    username = StringField('Email' , [DataRequired() , Email("Este campo requiere un email valido")])
    password = PasswordField ('Contraseña' , validators=[DataRequired()])
    submit = SubmitField('Enviar')

class PasswordForm(FlaskForm):
    username = StringField('Ingrese su Email' , [DataRequired() , Email("Este campo requiere un email valido")])
    password = PasswordField ('Ingrese Nueva Contraseña' , validators=[DataRequired()])
    submit = SubmitField('Enviar')

class ContactForm(FlaskForm):
    fulltname = StringField('Nombre Completo' , validators=[DataRequired()])
    email = StringField ('Correo Electronico' , validators=[DataRequired()])
    message = StringField ('Mensaje' , validators=[DataRequired()])
    submit = SubmitField('Enviar')

class SignUpForm(FlaskForm):
    username = StringField('Nombre de Usuario' , validators=[DataRequired()])
    password = PasswordField ('Contraseña' , validators=[DataRequired()])
    submit = SubmitField('Enviar')


## USER

class UserCreateForm(FlaskForm):
    company_name = StringField('Nombre de empresa' , validators=[DataRequired()])
    username = StringField('Email' , [DataRequired() , Email("Este campo requiere un email valido")])
    password = PasswordField ('Password' , validators=[DataRequired()])
    country = SelectField('Pais' , [DataRequired()])
    state = SelectField('Provincia' , [DataRequired()])
    role = SelectField('Rol del Usuario' , [DataRequired()])
    submit = SubmitField('Crear Usuario')

class UserUpdateForm(FlaskForm):
    company_name = StringField('Nombre de empresa' , validators=[DataRequired()])
    username = StringField('Email' , [DataRequired() , Email("Este campo requiere un email valido")])
    password = PasswordField ('Password' , validators=[DataRequired()])
    country = SelectField('Pais' , [DataRequired()])
    state = SelectField('Provincia' , [DataRequired()])
    role = SelectField('Rol del Usuario' , [DataRequired()])
    submit = SubmitField('Modificar Usuario')

class DeleteForm(FlaskForm):
    email_to_modif = StringField('')
    submit = SubmitField('Dar de baja cuenta')

class UsersProyectsForm(FlaskForm):
    users = SelectField('Usuarios')
    submit = SubmitField('Invitar Usuarios')

## PROYECTS

class SearchForm(FlaskForm):
    name_to_search = StringField('' , validators=[DataRequired()])
    submit = SubmitField('Buscar')

class UpdateForm(FlaskForm):
    submit_modify = SubmitField('Modificar')
    submit_delete = SubmitField('Eliminar')

class ProyectTypeForm(FlaskForm):
    proyect_type = StringField('' , validators=[DataRequired()])
    submit = SubmitField('Crear')

class ProyectForm(FlaskForm):
    proyect_name = StringField('Nombre de proyecto', validators=[DataRequired()])
    proyect_type = SelectField('Tipo de proyecto')
    hours_estimate = FloatField('Horas estimadas')
    start_date = DateField('Fecha de inicio', format='%d-%m-%Y' , validators=[DataRequired()])
    end_date = DateField('Fecha de entrega', format='%d-%m-%Y' , validators=[DataRequired()])
    id_client = SelectField('Cliente')
    id_proyect_status = SelectField('Status Proyecto')
    type_costs = SelectField('Tipo de facturacion')
    costs = SelectField('Planes')
    submit = SubmitField('Crear proyecto')

# TASK

class TaskForm(FlaskForm):
    title = StringField('Titulo' , validators=[DataRequired()])
    description= TextAreaField('Descripcion' , validators=[DataRequired()])
    status = SelectField('Estado')
    dt = DateField('Fecha de entrega', format='%d-%m-%Y' , validators=[DataRequired()])
    type_task =  SelectField('Tipo de tarea')
    submit = SubmitField('Crear tarea')

class TaskFormUser(FlaskForm):
    user_task = SelectField('Agregar Usuarios a tarea')
    submit = SubmitField('Agregar')

class CommentForm(FlaskForm):
    asset = SelectField('Feedback a')
    comments_ = TextAreaField('Comentario' , validators=[DataRequired()])
    submit = SubmitField('Comentar')

class AssetForm(FlaskForm):
    tittle = StringField('Titulo' , validators=[DataRequired()]) # descripcion
    asseturl = StringField('Url' , validators=[DataRequired()])
    submit = SubmitField('Subir')

class TaskTrackForm(FlaskForm):
    hours = StringField(validators=[DataRequired()])
    submit = SubmitField('Cargar')

class TaskHourForm(FlaskForm):
    hours_start = StringField()
    hours_end = StringField()
    submit_start = SubmitField('Empezar')
    submit_stop = SubmitField('Detener')
    submit_create = SubmitField('Cargar')

## Invoice

class InovoiceForm(FlaskForm):
    download = SubmitField('Descargar Factura')

class ConfigForm(FlaskForm):
    check_proyect_notification = BooleanField(label='Notificaciones de proyecto')
    check_proyect_task = BooleanField(label='Notificaciones de tareas')
    submit = SubmitField('Guardar configuracion')


## reports 

class UserSelectForm(FlaskForm):
    user = SelectField()
    submit = SubmitField('Ver')

