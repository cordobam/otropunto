from flask import Flask , render_template  , redirect , url_for , flash , request , session , make_response
from flask_sqlalchemy import SQLAlchemy 
from models import  Country , CountryState , UserRole , User , Proyects , ProyectType , ProyectUsers , Tasks , Status , TaskUser , ProyectStatus , ProyectUsers , Comments , AssetsMaterials , TaskAssets , TaskTracking , TypeTasks , TaskAdvance , ProyectAdvance , Advances, TypeCosts, ProyectCosts , Costs , Invoices , InvoicesDetails , Notifications
from flask_bootstrap import Bootstrap
from forms import LoginForm , ContactForm , SignUpForm , UserCreateForm , UserUpdateForm , DeleteForm , PasswordForm , SearchForm , ProyectTypeForm , ProyectForm , UsersProyectsForm , TaskForm , TaskFormUser  , CommentForm , AssetForm ,TaskTrackForm , TaskHourForm , ConfigForm, UserSelectForm , DateSelectForm
from config import Config
from flask_mail import Message , Mail
import re
from datetime import datetime , date 
from dateutil.relativedelta import relativedelta
import sys
import pdfkit



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

##########################
##### INICIALIZACION #####
##########################

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

app = Flask(__name__, static_folder='static', template_folder='templates')  
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
mail = Mail(app)

##########################
###### CONEXION ##########
##########################

POSTGRES_USER = 'postgres'
POSTGRES_PW =  'yo_mec1987'
POSTGRES_URL = '127.0.0.1:5432'
POSTGRES_DB = 'otropunto'

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

##########################
######  SESSION ##########
##########################

# some_engine = create_engine(DB_URL)
# Session = sessionmaker(bind=some_engine)
# s = Session()

##########################
#####  INICIALIZACON #####
##########################

users_dict = {}
task_dict = {}

##########################
######## RUTAS ###########
##########################

## PAG. PRINCIPAL 
@app.route('/')
def index():
    contact_form = ContactForm()

    context = {
        'contact_form': contact_form
    } 
    return render_template('index.html' , **context)

## PAG. LOGUEO
@app.route('/login' , methods=['GET', 'POST'])
def login():
    db.get_engine(app).dispose()

    login_form = LoginForm()
    context = {
        'login_form': login_form
    }

    if request.method == 'POST':
        if login_form.validate_on_submit():
            email = login_form.username.data
            password = login_form.password.data

            info_user = User.get_for_login(email , password)

            if info_user is None:
                flash('Datos de email o password incorrectos', 'error')
            elif info_user.flag_delete == 'inactivo':
                flash('Cuenta dada de baja comunicarse con el administrador', 'error')
            else:
                if info_user.email_address == email and info_user.password == password:
                    ## SESSION
                    session['email_address'] = info_user.email_address
                    session['id_user'] = info_user.id_user
                    session['id_user_role'] = info_user.id_user_role
                    return redirect(url_for('dashboard' , action = 'none')) 
        else:
            flash('Coloque un email valido', 'error')


    return render_template('login.html', **context)

## PAG. CHANGE PASSWORD
@app.route('/password/<string:email>' , methods=['GET', 'POST'])
def password(email):
    db.get_engine(app).dispose()
    #Session.close()()

    email = email 
    password_form = PasswordForm()
    user_modif = User.get_for_email(email)

    if request.method == 'POST' and email != 'none':
        user_modif.password = password_form.password.data  
        current_db_sessions = db.object_session(user_modif)
        current_db_sessions.add(user_modif)
        current_db_sessions.commit()
        flash('Se cambio correctamente la contraseña')
        return redirect(url_for('login'))  

    if request.method == 'POST' and email == 'none':
        valid_email = check(password_form.username.data )
        if valid_email == 'valid':
            mail_modf =  password_form.username.data

            user_email = User.get_for_email(password_form.username.data)  

            if user_email:
                msg = Message('Cambio de contraseña OtroPunto', sender='cordobam1987@gmail.com', recipients = ['cordobam1987@gmail.com'])
                msg.html ='<!DOCTYPE html> <html><head><meta charset="utf-8"></head><body><p>Email: {}  </p><p><a class="dropdown-item" href="http://127.0.0.1:5000/password/{}">Cambiar Contraseña</a></p></body></html>'.format(mail_modf, mail_modf)
                mail.send(msg)

                flash('Se le envio un correo electronico')
                return redirect(url_for('login' ))
            else:
                flash('Email inexistente')
        else:
            flash('Cargar un email valido')
    
    context = {
        'password_form': password_form,
        'email': email,
        'user_modif': user_modif
    }

    return render_template('config_password.html', **context)


## PAG. DASHBOARD
@app.route('/dashboard' , methods=['GET', 'POST'])
@app.route('/dashboard/<string:action>' , methods=['GET', 'POST'])
def dashboard(action):
    db.get_engine(app).dispose()
    #Session.close()()

    if action == 'archive':
        proyect_status = 3
    elif action == 'over':
        proyect_status = 2
    else:
        proyect_status = 1

    u = session['id_user']
    page = int(request.args.get('page', 1))
    page_task = int(request.args.get('page_task', 1))

    tareas_x_status = TaskUser.get_by_count_status(u)
    proyectos_x_status = ProyectUsers.get_by_count_status(u)
    notifications = Notifications.get_by_user_id(u)
    user_proyects = ProyectUsers.get_user_proyect_paginated(page , 3 , u )   
    user_task = Tasks.get_by_user_date(page_task , 3 , u)

    ## tareas
    labels_list = []
    for pt in tareas_x_status:
        labels_list.append(pt.status)
        
    labels_task = labels_list

    values_list = []
    for pt in tareas_x_status:
        values_list.append(pt.cantidad)

    values_task = values_list

    colors_task = [
        "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500"
    ]

    ## proyectos
    labels_list = []
    for pt in proyectos_x_status:
        labels_list.append(pt.status)
        
    labels_proyects = labels_list

    values_list = []
    for pt in proyectos_x_status:
        values_list.append(pt.cantidad)

    values_proyects = values_list

    colors_proyects = [
        "#DDDDDD", "#ABCABC", "#4169E1"
    ]

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True

    context = {
        'u':u,
        'user_proyects': user_proyects,
        'user_task':user_task,
        'notifications':notifications,
        'tareas_x_status':tareas_x_status,
        'proyectos_x_status':proyectos_x_status,
        'flag_read':flag_read
    }
    return render_template('dashboard.html' , set_task=zip( values_task , labels_task,colors_task) , set_proyect=zip( values_proyects , labels_proyects  , colors_proyects) , max=100 , **context)

## PAG. CONFIGURACIONES
@app.route('/configuration' , methods=['GET', 'POST'])
@app.route('/configuration/<string:action>/<string:email>' , methods=['GET', 'POST'])
def configuration(action, email):
    db.get_engine(app).dispose()
    #Session.close()()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True
    ## PAGE
    action = action
    email = email
    ## FORMS
    user_create = UserCreateForm()
    user_update = UserUpdateForm()
    delete_form = DeleteForm()
    ## ENVIO DATA
    users = User.get_all()
    roles = UserRole.get_all()
    country = Country.get_all()
    state = CountryState.get_all()
    if email == 'none':
        user_modif = User.get_for_email(session['email_address'])
    elif email == 'buscar':
        user_modif = User.get_for_email(delete_form.email_to_modif.data)
    else:
        user_modif = User.get_for_email(email)
    ## CARGO EL  USUARIO
    if request.method == 'POST' and action == 'crear': 
        try:
            valid_email = check(user_create.username.data)
            if valid_email == 'valid':
                u = User(
                    id_state  = request.form.get('ddlstate'),
                    id_country = request.form.get('ddlcountry'),
                    id_user_role = request.form.get('ddlroles'),
                    company_name = user_create.company_name.data,
                    email_address = user_create.username.data,
                    password = user_create.password.data,
                    flag_delete = 'activo'
                    )
                db.session.add(u)
                db.session.commit()
                flash('Usuario creado correctamente')
                return redirect(url_for('configuration' , action='crear' , email='none' ))
            else:
                flash('Cargar un email valido')
        except Exception as e:
            flash('No se pudieron cargar los datos')
    ## ACTUALIZO EL USUARIO
    if request.method == 'POST' and action == 'modificar':
        try:
            valid_email = check(user_modif.email_address)
            if valid_email == 'valid':
                user_modif.id_state  = request.form.get('ddlstate')
                user_modif.id_country = request.form.get('ddlcountry')
                #user_modif.id_user_role = request.form.get('ddlroles')
                user_modif.company_name = user_create.company_name.data
                #user_modif.email_address = user_create.username.data
                user_modif.flag_delete = 'activo'
                user_modif.update_date = datetime.date.today()
                current_db_sessions = db.object_session(user_modif)
                current_db_sessions.add(user_modif)
                current_db_sessions.commit()
                flash('Usuario actualizado correctamente')
            else:
                flash('Cargar un email valido')
        except Exception as e:
	        #flash(str(e))
            flash('No se pudieron modificar los datos')
    ## ELIMINO EL USUARIO
    if request.method == 'POST' and action == 'eliminar' and email != 'none' and email != 'buscar':
        try:
            user_modif.flag_delete = 'inactivo'
            current_db_sessions = db.object_session(user_modif)
            current_db_sessions.add(user_modif)
            current_db_sessions.commit()
            if session['id_user_role'] != 1:
                flash('Se dio de baja correctamente el usuario')
                return redirect(url_for('login'))
            else:
               email = 'none' 
               flash('Se dio de baja correctamente el usuario')
               return redirect(url_for('configuration' , action='eliminar' , email = 'buscar'))
        except Exception as e:
            flash('No se pudo eliminar el usuario')

    context = {
        'user_modif':user_modif,
        'user_create': user_create,
        'user_update': user_update,
        'delete_form': delete_form,
        'action':action,
        'email':email,
        'users':users,
        'roles': roles,
        'country': country,
        'state': state,
        'notifications':notifications,
        'flag_read':flag_read
    }
    return render_template('config.html' , **context)

## PAG. PROYECTS
@app.route('/proyect' , methods=['GET', 'POST'])
@app.route('/proyect/<string:page>' , methods=['GET', 'POST'])
@app.route('/proyect/<string:page>/<int:id>' , methods=['GET', 'POST'])
def proyect(page, id):
    db.get_engine(app).dispose()
    #Session.close()()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True
    
    page = page
    id = id 
    ## para buscar proyectos y mostrar los proyectos
    if page == 'index' and id == 0:

        action = request.args.get('action')
        if action == 'archive':
            proyect_status = 3
        elif action == 'over':
            proyect_status = 2
        else:
            proyect_status = 1

        search_form = SearchForm()
        page_ = int(request.args.get('pages', 1))
        proyect_data = Proyects.get_by_name(search_form.name_to_search.data)
        print(search_form.name_to_search.data)
        proyect_user = ProyectUsers.get_user_proyect_paginated_id(page_ , 3 ,session['id_user'] , proyect_status)
        proyect_update = None

        context_index = { 
            'search_form': search_form,
            'page': page ,
            'proyect_data': proyect_data  ,
            'proyect_user':proyect_user,
            'proyect_update':proyect_update,
            'notifications':notifications,
            'flag_read':flag_read
        }
        return render_template('proyect_search.html' , **context_index)
    
    ## una vez que ingresamos el proyecto a buscar
    elif page == 'buscar':
        search_form = SearchForm()
        clients = User.get_by_user_role(2)
        if search_form.name_to_search.data != None:
            proyect_data = Proyects.get_by_name(search_form.name_to_search.data)
            if proyect_data is None:
                proyect_data = Proyects.get_by_id(id)
                flash('No se encontro el proyecto')
                return redirect(url_for('proyect' , page='index' , id=0 , action='none' ))
        else:
            proyect_data = Proyects.get_by_id(id)
        proyect_update = None
        context_search = { 
            'search_form': search_form,
            'page': page,
            'proyect_data': proyect_data,
            'proyect_update': proyect_update,
            'clients':clients,
            'notifications':notifications,
            'flag_read':flag_read
            
        }
        return render_template('proyect_search.html', **context_search)   
    
    ## muestra el proyecto con todas las tareas 
    elif page == 'ver_index':
        action = request.args.get('action')

        task_dict.clear()
        if action == 'archive':
            task_proyect = Tasks.get_by_proyect_status(id , 5)
        elif action == 'over':
            task_proyect = Tasks.get_by_proyect_status(id , 4)
        elif action == 'active':
            task_proyect = Tasks.get_by_proyect(id , 1, 2,3)
        else:
            task_proyect = None

        proyect_data = Proyects.get_by_id(id)
        my_task = Tasks.get_by_user(session['id_user'])
        proyect_users = ProyectUsers.get_by_proyect_id(id)

        now = datetime.date(datetime.now())
        end_date = proyect_data.end_date
        
        if end_date > now:
            final_days = abs(end_date - now).days
        else:
            final_days = 0

        context_view_index = { 
            'page': page,
            'id': id,
            'proyect_data': proyect_data,
            'task_proyect': task_proyect,
            'my_task':my_task,
            'final_days':final_days,
            'proyect_users':proyect_users,
            'notifications':notifications,
            'flag_read':flag_read,
            'action': action
        }
        return render_template('proyect_details.html', **context_view_index)

    ## todos aquellos que son admin y usuarios, para crear proyectos
    else:
        
        p = request.args.get('p')
        proyect_type_form = ProyectTypeForm()
        proyect_form = ProyectForm()
        delete_form = DeleteForm()
        proyect_type_data = ProyectType.get_all()
        clients = User.get_by_user_role(2)
        status_proyect = ProyectStatus.get_all()
        users = User.get_all()
        type_costs = TypeCosts.get_all()
        costs = Costs.get_by_plans()
        if request.form.get('ddlUsers') != None:
            user = User.get_by_id(request.form.get('ddlUsers'))
        else:
            user = User()
        if page == 'update' or page == 'update_proyect' or page == 'delete_proyect' or page == 'delete':
            proyect_update = Proyects.get_by_id(id)
            start_date = proyect_update.start_date
            end_date = proyect_update.end_date
            users_proyect = ProyectUsers.get_by_proyect_id(id)
        else:
            proyect_update = Proyects()
            start_date = proyect_update.start_date
            end_date = proyect_update.end_date
            users_proyect = None
        user_proyect_form = UsersProyectsForm()
        proyect_data = None

        ## definimos el contexto 
        context = {
            'proyect_type_form' : proyect_type_form,
            'proyect_form' : proyect_form,
            'delete_form': delete_form,
            'page': page,
            'id' : id,
            'types' : proyect_type_data,
            'users': users,
            'users_dict':users_dict,
            'user_proyect_form':user_proyect_form,
            'user':user,
            'proyect_update':proyect_update,
            'proyect_data':proyect_data,
            'clients':clients,
            'status_proyect':status_proyect,
            'start_date': start_date,
            'end_date': end_date,
            'users_proyect':users_proyect,
            'type_costs':type_costs,
            'costs':costs,
            'notifications':notifications,
            'flag_read':flag_read
        }
       
        ## una vez que se quieren crear proyectos, tipos de proyectos o eliminar proyectos
        if page == 'create' and id == 0:
            return render_template('proyect_create.html', **context)
        elif page == 'delete_dict': # este elimina del diccionario antes de guardar
            key_to_remove = str(id)
            users_dict.pop(key_to_remove)
            return redirect(url_for('proyect' , page='create' , id=0))
        elif page == 'delete_dict_user': # este elimina del diccionario antes de guardar
            key_to_remove = str(id)
            users_dict.pop(key_to_remove)
            return redirect(url_for('proyect', page='update', id=p))
        elif page == 'delete_user_proyect': # este elimina de la base de datos
            try:
                pu = int(request.args.get('pu'))
                pu_ = ProyectUsers.get_by_id(pu)
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'proyecto',
                        description = 'Se eliminaron algunos los integrantes del proyecto'
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = ProyectAdvance(
                        id_advance = a.id_advance,
                        id_proyect = pu_.id_proyect,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e)
                current_db_sessions = db.object_session(pu_)                
                current_db_sessions.delete(pu_)
                current_db_sessions.commit()
                return redirect(url_for('proyect', page='update', id=p))
            except Exception as e:
                print(e)
                flash('Ha ocurrido un error intentar nuevamente')
        elif page == 'type' and id == 1:
            return render_template('proyect_create.html', **context)
        elif page == 'delete':
            return render_template('proyect_search.html', **context)
        elif page == 'update':
            return render_template('proyect_search.html', **context)
         

        ## cada vez que aprieta el boton
        if request.method == 'POST':
            if page == 'create_proyect' and id == 0:
                try:
                    str_start_date = request.form.get('start_date')
                    str_end_date = request.form.get('end_date')
                    p = Proyects(
                        proyect_name =  proyect_form.proyect_name.data,
                        id_proyect_type = request.form.get('ddlptype'),
                        id_user = session['id_user'],
                        hours_estimate = proyect_form.hours_estimate.data,
                        start_date = datetime.strptime(str_start_date, '%Y-%m-%d'),
                        end_date = datetime.strptime(str_end_date, '%Y-%m-%d'),
                        id_client = request.form.get('ddlclients'),
                        id_proyect_status = 1
                    )
                    db.session.add(p)
                    db.session.commit()
                    db.session.flush()
                    pu = ProyectUsers(
                        id_proyect=p.id_proyect,
                        id_user = session['id_user']
                    )
                    db.session.add(pu)
                    db.session.commit()
                    for id_user_p , email_user_p in users_dict.items():
                        pu_dict = ProyectUsers(
                            id_proyect=p.id_proyect,
                            id_user = id_user_p
                        )
                        db.session.add(pu_dict)
                        db.session.commit()
                        # creamos la notificacion de que se creo el proyecto para cada usuario
                        n = Notifications(
                            id_proyect = p.id_proyect,
                            description = 'Se te asigno al siguiente proyecto {}'.format(p.proyect_name),
                            id_user =  id_user_p
                        )
                        db.session.add(n)
                        db.session.commit()
                    users_dict.clear()
                    # creamos el avance del proyecto
                    a = Advances(
                        status = 'create',
                        advance_type = 'proyecto',
                        description = 'Se creo el proyecto.'
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = ProyectAdvance(
                        id_advance = a.id_advance,
                        id_proyect = p.id_proyect,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit()
                    # creamos el tipo de factuaracion y la factura
                    tc = int(request.form.get('ddltypecosts'))
                    co= int(request.form.get('ddlcosts'))
                    if tc == 1: # facturacion por hora
                        try:
                            pc = ProyectCosts(
                                description = 'Facturacion por horas',
                                id_proyect = p.id_proyect
                            )
                            db.session.add(pc)
                            db.session.commit()
                            i = Invoices(
                                id_proyect = p.id_proyect
                            )
                            db.session.add(i)
                            db.session.commit()
                            flash('Poyecto creado correctmente')
                            return redirect(url_for('proyect' , page='ver_index' , id=p.id_proyect ))
                        except Exception as e:
                            print(e)
                            flash('Hubo un inconveniente intente de nuevo')
                    elif tc == 2: #facturacion por plan
                        try:
                            pc = ProyectCosts(
                                id_costs = co,
                                description = 'Facturacion por plan',
                                id_proyect = p.id_proyect
                            )
                            db.session.add(pc)
                            db.session.commit()
                            i = Invoices(
                                id_proyect = p.id_proyect
                            )
                            db.session.add(i)
                            db.session.commit()
                            flash('Poyecto creado correctmente')
                            return redirect(url_for('proyect' , page='ver_index' , id=p.id_proyect ))
                        except Exception as e:
                            print(e)
                            flash('Hubo un inconveniente intente de nuevo')
                    else: #sin facturacion
                        try:
                            pc = ProyectCosts(
                                description = 'Sin facturacion',
                                id_proyect = p.id_proyect
                            )
                            db.session.add(pc)
                            db.session.commit()
                            i = Invoices(
                                id_proyect = p.id_proyect
                            )
                            db.session.add(i)
                            db.session.commit()
                            flash('Poyecto creado correctmente')
                            return redirect(url_for('proyect' , page='ver_index' , id=p.id_proyect ))
                        except Exception as e:
                            print(e)
                            flash('Hubo un inconveniente intente de nuevo')
                except Exception as e:
                    print(e)
                    flash('No se pudo crear el proyecto')
                    return redirect(url_for('proyect', page='create_type', id=0))
            elif page == 'create_type' and id == 1:
                try:
                    pt = ProyectType(
                        description = proyect_type_form.proyect_type.data
                    )
                    db.session.add(pt)
                    db.session.commit()
                    flash('Tipo de Proyecto creado correctamente')
                    return redirect(url_for('proyect', page='create_type', id=1))
                except Exception as e:
                    flash('No se pudo crear el tipo de proyecto')
                    return redirect(url_for('proyect', page='index', id=0))
            elif page == 'delete_proyect':
                try:
                    proyect_update.id_proyect_status = 3
                    current_db_sessions = db.object_session(proyect_update)
                    current_db_sessions.add(proyect_update)
                    current_db_sessions.commit() 
                    # creamos el avance del proyecto
                    a = Advances(
                        status = 'delete',
                        advance_type = 'proyecto',
                        description = 'Se archivo el proyecto'
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = ProyectAdvance(
                        id_advance = a.id_advance,
                        id_proyect = p.id_proyect,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit()               
                    flash('Se archivo el proyecto correctamente')
                    return redirect(url_for('proyect', page='index', id=0))
                except Exception as e:
                    flash('No se pudo eliminar el proyecto')
                    return redirect(url_for('proyect', page='delete', id=2))
            elif page == 'update_proyect':
                try:
                    str_start_date = request.form.get('start_date')
                    str_end_date = request.form.get('end_date')
                    # creamos el avance del proyecto
                    if proyect_update.proyect_name != proyect_form.proyect_name.data:
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico el nombre del proyecto por {}'.format(proyect_form.proyect_name.data)
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    #######
                    if proyect_update.id_proyect_type != int(request.form.get('ddlptype')):
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico el tipo de proyecto {}'.format(request.form.get('ddlptype'))
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    #######
                    if proyect_update.hours_estimate != float(proyect_form.hours_estimate.data):
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico las horas estimadas de proyecto {}'.format(proyect_form.hours_estimate.data)
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    #######
                    if proyect_update.id_client != int(request.form.get('ddlclients')):
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico el cliente del proyecto {}'.format(request.form.get('ddlclients'))
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    if proyect_update.id_proyect_status != int(request.form.get('ddlpstatus')):
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico el estado del proyecto {}'.format(request.form.get('ddlpstatus'))
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    #######
                    my_time_start = datetime.min.time()
                    my_datetime_start = datetime.combine(proyect_update.start_date, my_time_start)
                    if my_datetime_start != datetime.strptime(str_start_date, '%Y-%m-%d'):
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico la fecha de comienzo del proyecto {}'.format(datetime.strptime(str_start_date, '%Y-%m-%d'))
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    #######
                    my_time_end = datetime.min.time()
                    my_datetime_end = datetime.combine(proyect_update.end_date, my_time_end)
                    if  my_datetime_end != datetime.strptime(str_end_date, '%Y-%m-%d'):
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modifico la fecha de entrega del proyecto {}'.format(datetime.strptime(str_end_date, '%Y-%m-%d'))
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit() 
                        except Exception as e:
                            print(e)
                    #######

                    proyect_update.proyect_name = proyect_form.proyect_name.data
                    proyect_update.id_proyect_type = request.form.get('ddlptype')
                    proyect_update.hours_estimate = proyect_form.hours_estimate.data
                    proyect_update.id_client = request.form.get('ddlclients')
                    proyect_update.id_proyect_status = request.form.get('ddlpstatus')
                    proyect_update.start_date = datetime.strptime(str_start_date, '%Y-%m-%d')
                    proyect_update.end_date = datetime.strptime(str_end_date, '%Y-%m-%d')
                    current_db_sessions = db.object_session(proyect_update)
                    current_db_sessions.add(proyect_update)
                    current_db_sessions.commit()

                    if proyect_update.id_proyect_status == 2:
                        return redirect (url_for('invoice' , page = 'invoice', p=proyect_update.id_proyect , ps = 2))
                    
                    if users_dict:
                        for id_user_p , email_user_p in users_dict.items():
                            pu_dict = ProyectUsers(
                                id_proyect=id,
                                id_user = id_user_p
                            )
                            db.session.add(pu_dict)
                            db.session.commit()
                        try:
                            a = Advances(
                                status = 'update',
                                advance_type = 'proyecto',
                                description = 'Se modificaron los integrantes del proyecto'
                            )
                            db.session.add(a)
                            db.session.commit()
                            db.session.flush()
                            pa = ProyectAdvance(
                                id_advance = a.id_advance,
                                id_proyect = proyect_update.id_proyect,
                                id_user = int(session['id_user'])
                            )
                            db.session.add(pa)
                            db.session.commit()
                            # creamos la notificacion de que se creo el proyecto para cada usuario
                            n = Notifications(
                                id_proyect = proyect_update.id_proyect,
                                description = 'Se te asigno al siguiente proyecto {}'.format(proyect_update.proyect_name),
                                id_user =  id_user_p
                            )
                            db.session.add(n)
                            db.session.commit()
                        except Exception as e:
                            print(e)
                    users_dict.clear()
                    flash('Se modifico el proyecto correctamente')
                    return redirect(url_for('proyect', page='ver_index', id=id , action='active'))
                except Exception as e:
                    print(e)
                    flash('No se pudo modificar el proyecto')
                    return redirect(url_for('proyect', page='ver_index', id=id , action='active'))
            elif page == 'create' and id == 3:
                try:
                    element_list  = request.form.get('ddlUsers')
                    users_dict[element_list] = user.email_address 
                    return redirect(url_for('proyect', page='create', id=0))
                except Exception as e:
                    flash('Se ha producido un error, intentar de nuevo')
                    return redirect(url_for('proyect', page='create', id=0))
            elif page == 'create_user':
                try:
                    element_list  = request.form.get('ddlUsers')
                    users_dict[element_list] = user.email_address 
                    return redirect(url_for('proyect', page='update', id=id))
                except Exception as e:
                    flash('Se ha producido un error, intentar de nuevo')
                    return redirect(url_for('proyect', page='update', id=id))
            else:
                return redirect(url_for('proyect', page='create', id=0))
        else:
            return redirect(url_for('proyect', page='create', id=0))
        



## PAG. TASK
@app.route('/task/' , methods=['GET', 'POST'])
@app.route('/task/<page>/<int:id>' , methods=['GET', 'POST'])
def task(page , id ):
    db.get_engine(app).dispose()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True

    id = id 
    page = page 
    task_form = TaskForm()
    comment_form = CommentForm()
    assets_form = AssetForm()
    user_id = int(session['id_user'])
    user = User.get_by_id(user_id)
    users = User.get_all()
    task = Tasks.get_by_id(id)
    status = Status.get_all()
    delete_form = DeleteForm()
    task_user_form = TaskFormUser()
    p = request.args.get('p')
    type_task = TypeTasks.get_all()
    
    if page =='view_all_tasks':
        u = session['id_user']
        pages = int(request.args.get('pages', 1))
        tasks = Tasks.get_all_paginated_by_user(user_id , pages , 5)
        print(tasks)
    else:
        tasks = None

    if page == 'update': 
        end_date = task.end_date
        text_description = str(task.description)
        users_task = TaskUser.get_by_task_id(task.id_task)
    else:
        end_date = None
        text_description = None
        users_task = None
    
    if page == 'view':
        assets = TaskAssets.get_by_task(task.id_task)
        comments = Comments.get_by_task_id(task.id_task)
        task_users = TaskUser.get_by_task_id(task.id_task)
        p = task.id_proyect
    else:
        comments = None
        assets = None
        task_users = None
    
    if page == 'update':
        task_form.description.data = task.description
    
    c = request.args.get('c')
    if c != None and request.method != 'POST':
        comment = Comments.get_by_id(c)
        comment_form.comments_.data = comment.comments_
    else:
        comment = None
        c = None


    context = {
        'id': id,
        'page': page , 
        'task_form':task_form,
        'task': task,
        'status': status,
        'delete_form':delete_form,
        'p': p,
        'users':users,
        'task_dict': task_dict,
        'task_user_form':task_user_form,
        'end_date':end_date,
        'text_description': text_description,
        'comment_form': comment_form,
        'comments':comments,
        'assets_form':assets_form,
        'assets':assets,
        'tasks':tasks,
        'type_task':type_task,
        'users_task':users_task,
        'comment':comment,
        'c':c,
        'task_users':task_users,
        'notifications':notifications,
        'flag_read':flag_read
    }

    if page == 'create':
        return render_template('task.html' , **context)
    if page == 'view':
        return render_template('task.html' , **context)
    elif page == 'update':
        return render_template('task.html' , **context)
    elif page == 'delete':
        return render_template('task.html' , **context)
    elif page == 'update_comment' and request.method != 'POST': # sirve para actualizar el comentario
        print('paso por aca')
        c = request.args.get('c')
        return redirect(url_for('task' , page='view' , id=id , p=p , c=c))
    elif page == 'delete_dict_task': # este eliminar el usuario en el diccionario cuando creamos la tarea
        key_to_remove = str(id)
        task_dict.pop(key_to_remove)
        return redirect(url_for('task' , page='create' , id=0 , p=p))
    elif page == 'delete_dict_task_': # este elimina el usuario cuando actualizamos
        key_to_remove = str(id)
        task_dict.pop(key_to_remove)
        t = request.args.get('t')
        return redirect(url_for('task' , page='update' , id=t, p=p))
    elif page == 'delete_task_': # este elimina el usuario en la base de datos 
        try:
            tu = request.args.get('tu')
            tu_ = TaskUser.get_by_id(tu)
            # avance/seguimiento de la tarea
            try:
                a = Advances(
                    status = 'delete',
                    advance_type = 'tarea',
                    description = 'Se eliminaron algunos de los integrantes de la tarea'
                )
                db.session.add(a)
                db.session.commit()
                db.session.flush()
                pa = TaskAdvance(
                    id_advance = a.id_advance,
                    id_task = tu_.id_task,
                    id_user = int(session['id_user'])
                )
                db.session.add(pa)
                db.session.commit() 
            except Exception as e:
                print(e)
            current_db_sessions = db.object_session(tu_)
            current_db_sessions.delete(tu_)
            current_db_sessions.commit()
            return redirect(url_for('task' , page='update' , id=id , p=p))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
    if page == 'create_task' and request.method == 'POST':
        try:
            str_end_date = request.form.get('dt')
            t = Tasks(
                id_user = user.id_user,
                id_proyect = id , 
                description = task_form.description.data,
                id_status = 1,
                title = task_form.title.data,
                end_date = datetime.strptime(str_end_date, '%Y-%m-%d'),
                id_type_task = request.form.get('ddltypetask')
            )
            db.session.add(t)
            db.session.commit()
            db.session.flush()
            tu = TaskUser(
                id_user = user.id_user,
                id_task = t.id_task
            )
            db.session.add(tu)
            db.session.commit()
            for id_user_t , email_user_t in task_dict.items():
                t_dict = TaskUser(
                    id_user=id_user_t,
                    id_task = t.id_task
                )
                db.session.add(t_dict)
                db.session.commit()
                # creamos la notificacion de que se creo la tarea para cada usuario
                n = Notifications(
                    id_proyect = id,
                    id_task = t.id_task,
                    description = 'Se te asigno a la siguiente tarea{}'.format(t.description),
                    id_user =  id_user_t
                )
                db.session.add(n)
                db.session.commit()
            task_dict.clear()
            try:
                a = Advances(
                    status = 'create',
                    advance_type = 'tarea',
                    description = 'Se creo la tarea'
                )
                db.session.add(a)
                db.session.commit()
                db.session.flush()
                pa = TaskAdvance(
                    id_advance = a.id_advance,
                    id_task = t.id_task,
                    id_user = int(session['id_user'])
                )
                db.session.add(pa)
                db.session.commit() 
            except Exception as e:
                print(e)            
            return redirect(url_for('proyect', page='ver_index', id=id ,  p=p , action='active'))
        except Exception as e:
            flash('Se ha producido un error, intentar de nuevo')
    elif page == 'create_dict_task' and request.method == 'POST':
        try:
            element_list  = request.form.get('ddlUsers')
            user = User.get_by_id(element_list)
            task_dict[element_list] = user.email_address 
            return redirect(url_for('task' , page='create' , id=0 , p=p))
        except Exception as e:
            flash('Se ha producido un error, intentar de nuevo')
    elif page == 'create_dict_task_' and request.method == 'POST':
        try:
            element_list  = request.form.get('ddlUsers')
            user = User.get_by_id(element_list)
            task_dict[element_list] = user.email_address 
            return redirect(url_for('task' , page='update' , id=task.id_task , p=p  ))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
    elif page == 'update_task' and request.method == 'POST':
        try:
            str_end_date = request.form.get('dt')

            ####### agregamos los avances

            if  task.description != task_form.description.data:
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'tarea',
                        description = 'Se modifico la descripcion de la tarea {}'.format(task_form.description.data)
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = TaskAdvance(
                        id_advance = a.id_advance,
                        id_task = task.id_task,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e)
            #######
            if  task.id_status != int(request.form.get('ddlstatus')):
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'tarea',
                        description = 'Se modifico el estado de la tarea {}'.format(request.form.get('ddlstatus'))
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = TaskAdvance(
                        id_advance = a.id_advance,
                        id_task = task.id_task,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e)
            #######
            if  task.title != task_form.title.data:
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'tarea',
                        description = 'Se modifico el titulo de la tarea {}'.format(task_form.title.data)
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = TaskAdvance(
                        id_advance = a.id_advance,
                        id_task = task.id_task,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e)
            #######
            my_time = datetime.min.time()
            my_datetime = datetime.combine(task.end_date, my_time)
            if  my_datetime != datetime.strptime(str_end_date, '%Y-%m-%d'):
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'tarea',
                        description = 'Se modifico la fecha de entrega de la tarea {}'.format(datetime.strptime(str_end_date, '%Y-%m-%d'))
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = TaskAdvance(
                        id_advance = a.id_advance,
                        id_task = task.id_task,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e)
            #######
            if  task.id_type_task != int(request.form.get('ddltypetask')):
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'tarea',
                        description = 'Se modifico el tipo de tarea {}'.format(request.form.get('ddltypetask'))
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = TaskAdvance(
                        id_advance = a.id_advance,
                        id_task = task.id_task,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e)
            #######

            task.description = task_form.description.data,
            task.id_status = request.form.get('ddlstatus'),
            task.title = task_form.title.data,
            task.end_date = datetime.strptime(str_end_date, '%Y-%m-%d')
            task.id_type_task = request.form.get('ddltypetask'),

            if task_dict:
                for id_user_p , email_user_p in task_dict.items():
                    tu_dict = TaskUser(
                        id_task=task.id_task,
                        id_user = id_user_p
                    )
                    db.session.add(tu_dict)
                    db.session.commit()
                    # cargamos las notificaciones
                    n = Notifications(
                    id_proyect = task.id_proyect,
                    id_task = task.id_task,
                    description = 'Se te asigno a la siguiente tarea{}'.format(task.description),
                    id_user =  id_user_p
                    )
                    db.session.add(n)
                    db.session.commit()
                try:
                    a = Advances(
                        status = 'update',
                        advance_type = 'tarea',
                        description = 'Se modificaron los usuarios de la tarea'
                    )
                    db.session.add(a)
                    db.session.commit()
                    db.session.flush()
                    pa = TaskAdvance(
                        id_advance = a.id_advance,
                        id_task = task.id_task,
                        id_user = int(session['id_user'])
                    )
                    db.session.add(pa)
                    db.session.commit() 
                except Exception as e:
                    print(e) 
            task_dict.clear() 
            flash('Se modifico el proyecto correctamente')
            current_db_sessions = db.object_session(task)
            current_db_sessions.add(task)
            current_db_sessions.commit()
            return redirect(url_for('proyect', page='ver_index', id=task.id_proyect ,  p=p , action='active'))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
    elif page == 'delete_task' and request.method == 'POST':
        try:
            task_ = Tasks.get_by_id(task.id_task)
            task_.id_status = 5
            current_db_sessions = db.object_session(task_)
            current_db_sessions.add(task_)
            current_db_sessions.commit()
            return redirect(url_for('task', page='view', id=task.id_task , p=p))
        except Exception as e:
            flash('Se ha producido un error, intentar de nuevo')
    elif page == 'comment' and request.method == 'POST':
        try:
            task_user = TaskUser.get_by_task_id(task.id_task)
            c = Comments (
                id_user = user.id_user,
                comments_ = comment_form.comments_.data, 
                id_task = task.id_task,
                feedback_asset = request.form.get('ddlassets')
            )
            db.session.add(c)
            db.session.commit()
            for tu in task_user:
                # cargamos las notificaciones
                n = Notifications(
                    id_proyect = task.id_proyect,
                    id_task = task.id_task,
                    description = 'Hay un comentario en la siguiente tarea{}'.format(task.description),
                    id_user =  tu.id_user
                )
                db.session.add(n)
                db.session.commit()              
            return redirect(url_for('task', page='view', id=task.id_task , p=p))
        except Exception as e:
            flash('Se ha producido un error, intentar de nuevo')
            return redirect(url_for('task', page='view', id=task.id_task ,  p=p))
    elif page == 'delete_comment':
        try:
            c = request.args.get('c')
            coment = Comments.get_by_id(c)
            current_db_sessions = db.object_session(coment)
            current_db_sessions.delete(coment)
            current_db_sessions.commit()
            return redirect(url_for('task', page='view', id=task.id_task , p=p))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
            return redirect(url_for('task', page='view', id=task.id_task ,  p=p))
    elif page == 'update_comment' and request.method == 'POST':
        try:
            c = request.args.get('c')
            comment = Comments.get_by_id(c)
            comment.comments_ = comment_form.comments_.data
            current_db_sessions = db.object_session(comment)
            current_db_sessions.add(comment)
            current_db_sessions.commit()
            return redirect(url_for('task', page='view', id=task.id_task , p=p))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
            return redirect(url_for('task', page='view', id=task.id_task ,  p=p))
    elif page == 'assets' and request.method == 'POST':
        try:
            a = AssetsMaterials (
                description = assets_form.tittle.data,
                url_asset = assets_form.asseturl.data,
                id_user = user.id_user
            )
            db.session.add(a)
            db.session.commit()
            db.session.flush()
            au = TaskAssets(
                id_assets = a.id_assets,
                id_task = task.id_task
            )
            db.session.add(au)
            db.session.commit()
            return redirect(url_for('task', page='view', id=task.id_task ,  p=p))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
            return redirect(url_for('task', page='view', id=task.id_task ,  p=p))
    elif page == 'delete_assets':
        try:
            a = request.args.get('a')
            assets = TaskAssets.get_by_id_task(a)
            current_db_sessions = db.object_session(assets)
            current_db_sessions.delete(assets)
            current_db_sessions.commit()
            return redirect(url_for('task', page='view', id=task.id_task , p=p))
        except Exception as e:
            print(e)
            flash('Se ha producido un error, intentar de nuevo')
            return redirect(url_for('task', page='view', id=task.id_task ,  p=p))

    return render_template('task.html' , **context)

## PAG. BOARD
@app.route('/board/' , methods=['GET', 'POST'])
def board():
    db.get_engine(app).dispose()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True

    id = request.args.get('id')
    task_proyect = Tasks.get_by_proyect_board(request.args.get('id') , 1, 2,3 , 4)

    context = {
        'id':id,
        'task_proyect':task_proyect,
        'notifications':notifications,
        'flag_read':flag_read
    }

    return render_template('task_dashboard.html' , **context)

## PAG. TRACKING
@app.route('/tracking/' , methods=['GET', 'POST'])
def tracking():
    db.get_engine(app).dispose()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True

    id = request.args.get('id')
    p = request.args.get('p')
    page = request.args.get('page')
    task_track = TaskTracking.get_by_task(id)

    proyect = Proyects.get_by_id(p)
    total_task_trak = TaskTracking.get_by_poyect(p)

    total_time = 0
    for t in total_task_trak:
        total_time += t.total_time

    total_hours_proyect =  proyect.hours_estimate - total_time

    task = Tasks.get_by_id(id)
    task_track_form = TaskTrackForm()
    task_hour_form = TaskHourForm()


    context = {
        'id': id,
        'page': page,
        'task_track':task_track,
        'task_track_form':task_track_form,
        'task_hour_form':task_hour_form,
        'p':p,
        'notifications':notifications,
        'task':task,
        'flag_read':flag_read,
        'total_hours_proyect':total_hours_proyect
    }

    if page == 'delete_time':
        try:
            time = TaskTracking.get_by_id(id)
            current_db_sessions = db.object_session(time)
            current_db_sessions.delete(time)
            current_db_sessions.commit()
            flash('Se ha eliminado correctamente')
            return redirect(url_for('tracking' , page='proyect' , id=time.id_task , p=p))
        except Exception as e:
            flash('Se ha producido un error, intentar de nuevo')
            return redirect(url_for('tracking' , page='proyect' , id=time.id_task , p=p))


    if page == 'create_time' and request.method == 'POST':
        user = session['id_user']
        tt = TaskTracking(
            id_task = id,
            total_time = task_track_form.hours.data,
            id_user = user
        )
        db.session.add(tt)
        db.session.commit()
        task = Tasks.get_by_id(id)
        return redirect(url_for('tracking' , page = 'proyect',  id=task.id_task , p=p))
    
    if page == 'create_time_hours' and request.method == 'POST':
        if task_hour_form.submit_create.data: 
            task = Tasks.get_by_id_alone(id)
            end_date = task_hour_form.hours_end.data
            start_date = task_hour_form.hours_start.data

            _end_date= datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            _start_date= datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

            diff = relativedelta( _end_date , _start_date )

            user = session['id_user']

            try:
                tt = TaskTracking(
                    id_task = id, 
                    total_time = diff.hours,
                    initial_time = _start_date,
                    final_time = _end_date,
                    id_user = user,
                    initial_time_1 = _start_date,
                    final_time_1 = _end_date
                )
                db.session.add(tt)
                db.session.commit()
                return redirect(url_for('tracking' , page = 'proyect',  id=task.id_task , p=p))
            except Exception as e:
                flash('Se ha producido un error, intentar de nuevo')
                return redirect(url_for('tracking' , page = 'proyect',  id=task.id_task , p=p))

    return render_template('tracking.html' , **context)

## PAG. ADVANCES
@app.route('/advances' , methods=['GET', 'POST'])
def advance():
    db.get_engine(app).dispose()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True

    p = int(request.args.get('p'))

    page = request.args.get('page')
    id = int(request.args.get('id'))

    if page == 'proyect':
        proyect_advance = ProyectAdvance.get_by_proyect_id(id)
    else:
        proyect_advance = None

    if page == 'task':
        task_advance = TaskAdvance.get_by_task_id(id)
    else:
        task_advance = None
    
    context = {
        'page': page,
        'proyect_advance':proyect_advance,
        'task_advance':task_advance,
        'id':id,
        'notifications':notifications,
        'p':p,
        'flag_read':flag_read
    }



    return render_template('advances.html' , **context)

## PAG. INVOICE
@app.route('/invoice' , methods=['GET', 'POST'])
def invoice():
    db.get_engine(app).dispose()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True
 
    p = request.args.get('p')
    proyect_costs = ProyectCosts.get_by_proyect_id(p)
    page = request.args.get('page')
    ps = request.args.get('ps')
    invoices = Invoices.get_all_proyect_close()
    if proyect_costs:
        invoice = Invoices.get_by_proyect_id(p)
        proyect_tasks = TaskTracking.get_by_poyect_group_by(proyect_costs.id_proyect)
        costs = Costs.get_by_id(proyect_costs.id_costs)
        costs_all = Costs.get_all()
        proyect = Proyects.get_by_id(proyect_costs.id_proyect)
        if proyect_tasks:
            suma_cantidad = 0
            total = 0
            suma_cantidad_d = 0
            total_d= 0
            suma_cantidad_qa= 0
            total_qa= 0
            suma_cantidad_pm= 0
            total_pm= 0
            suma_cantidad_a= 0
            total_a= 0
            total_final = 0
            costs_dev = None
            costs_d = None
            costs_t = None
            costs_pm = None
            costs_a = None
            for pt in proyect_tasks:
                if pt.id_type_task == 1: #"Desarrollo"
                    costs_dev = Costs.get_by_id(4)
                    suma_cantidad += pt.total_time
                    total = suma_cantidad * costs_dev.price
                elif pt.id_type_task == 2: #"Diseño"
                    costs_d = Costs.get_by_id(5)
                    suma_cantidad_d += pt.total_time
                    total_d = suma_cantidad_d * costs_d.price
                elif pt.id_type_task ==3: #"QA"
                    costs_t = Costs.get_by_id(6)
                    suma_cantidad_qa += pt.total_time
                    total_qa = suma_cantidad_qa * costs_t.price
                elif pt.id_type_task == 4: #"Proyect Managment"
                    costs_pm = Costs.get_by_id(7)
                    suma_cantidad_pm += pt.total_time
                    total_pm = suma_cantidad_pm * costs_pm.price
                elif pt.id_type_task == 5: #"Analisis"
                    costs_a = Costs.get_by_id(8)
                    suma_cantidad_a += pt.total_time
                    total_a = suma_cantidad_a * costs_a.price
        else:
            suma_cantidad = 0
            total = 0
            suma_cantidad_d = 0
            total_d= 0
            suma_cantidad_qa= 0
            total_qa= 0
            suma_cantidad_pm= 0
            total_pm= 0
            suma_cantidad_a= 0
            total_a= 0
            total_final = 0
            proyect_tasks = None
            costs_dev = None
            costs_d = None
            costs_t = None
            costs_pm = None
            costs_a = None
    else:
        invoice=None
        proyect_tasks = None
        costs = None
        proyect= Proyects.get_by_id(p)
        suma_cantidad = 0
        total = 0
        suma_cantidad_d = 0
        total_d= 0
        suma_cantidad_qa= 0
        total_qa= 0
        suma_cantidad_pm= 0
        total_pm= 0
        suma_cantidad_a= 0
        total_a= 0
        total_final = 0
        costs_all = Costs.get_all()
        costs_dev = None
        costs_d = None
        costs_t = None
        costs_pm = None
        costs_a = None

    total_final = total +  total_d +  total_qa + total_pm + total_a
    
    context = {
        'invoice':invoice,
        'proyect_costs':proyect_costs,
        'proyect_tasks':proyect_tasks,
        'costs':costs,
        'proyect':proyect,
        'suma_cantidad':suma_cantidad,
        'total':total,
        'suma_cantidad_d':suma_cantidad_d ,
        'total_d':total_d,
        'suma_cantidad_qa':suma_cantidad_qa,
        'total_qa':total_qa,
        'suma_cantidad_pm':suma_cantidad_pm,
        'total_pm':total_pm,
        'suma_cantidad_a':suma_cantidad_a,
        'total_a':total_a,
        'costs_all':costs_all,
        'costs_dev': costs_dev,
        'costs_d': costs_d,
        'costs_t': costs_t,
        'costs_pm': costs_pm,
        'costs_a': costs_a,
        'notifications':notifications,
        'ps':ps,
        'total_final':total_final,
        'page': page,
        'invoices':invoices,
        'flag_read':flag_read,
        'p':p
    }

    # if page == 'facturacion':
    #     invoices = Invoices.get_all_proyect_close()
    #     context = {
    #         'page':page,
    #         'invoices':invoices,
    #         'flag_read':flag_read,
    #         'notifications':notifications
    #     }

    if page == 'download':
        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        html = render_template( 'invoice_pdf.html' , **context)  # Renders the template with the context data.
        pdf = pdfkit.from_string(html , False, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'

        return response 
    
    if page == 'close_facturation':
        try:
            flag_invoice_detail = InvoicesDetails.get_by_invoice_id(invoice.id_invoice)
            if flag_invoice_detail:
                flash('La facturacion ya se encuentra cerrada, descargue la factura')
                return redirect(url_for('invoice' , p=proyect.id_proyect , page='invoice'))     
            else:
                if proyect_tasks:
                    for pt in proyect_tasks:
                        if pt.id_type_task == 1:
                            i = InvoicesDetails(
                                id_invoice = invoice.id_invoice,
                                total_hours =  pt.total_time,
                                total_price = costs_dev.price,
                                id_proyect_costs = proyect_costs.id_proyect_costs
                            )
                            db.session.add(i)
                            db.session.commit()
                        elif pt.id_type_task == 2:
                            i = InvoicesDetails(
                                id_invoice = invoice.id_invoice,
                                total_hours =  pt.total_time,
                                total_price = costs_d.price,
                                id_proyect_costs = proyect_costs.id_proyect_costs
                            )
                            db.session.add(i)
                            db.session.commit()
                        elif pt.id_type_task == 3:
                            i = InvoicesDetails(
                                id_invoice = invoice.id_invoice,
                                total_hours =  pt.total_time,
                                total_price = costs_t.price,
                                id_proyect_costs = proyect_costs.id_proyect_costs
                            )
                            db.session.add(i)
                            db.session.commit()
                        elif pt.id_type_task == 4:
                            i = InvoicesDetails(
                                id_invoice = invoice.id_invoice,
                                total_hours =  pt.total_time,
                                total_price = costs_pm.price,
                                id_proyect_costs = proyect_costs.id_proyect_costs
                            )
                            db.session.add(i)
                            db.session.commit()
                        elif pt.id_type_task == 5:
                            i = InvoicesDetails(
                                id_invoice = invoice.id_invoice,
                                total_hours =  pt.total_time,
                                total_price = costs_a.price,
                                id_proyect_costs = proyect_costs.id_proyect_costs
                            )
                            db.session.add(i)
                            db.session.commit()
                    flash('La facturacion del proyecto fue cerrada, descargue su factura', 'error')
                    return redirect(url_for('invoice' , p=proyect.id_proyect , page='invoice'))  
                else:
                    if proyect_costs.description == 'Facturacion por plan':
                        i = InvoicesDetails(
                                id_invoice = invoice.id_invoice,
                                total_hours =  1,
                                total_price = costs.price,
                                id_proyect_costs = proyect_costs.id_proyect_costs
                            )
                        db.session.add(i)
                        db.session.commit()
                    flash('La facturacion del proyecto fue cerrada, descargue su factura', 'error') 
                    return redirect(url_for('invoice' , p=proyect.id_proyect , page='invoice'))  
        except Exception as e:
            return render_template('invoice.html' , **context)

    return render_template('invoice.html' , **context)


## PAG. REPORT
@app.route('/report' , methods=['GET', 'POST'])
def report():
    db.get_engine(app).dispose()
    u = session['id_user']
    notifications = Notifications.get_by_user_id(u)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True

    page = request.args.get('page')

    if page == 'proyect_time':
        proyect_time = TaskTracking.get_by_type_poyect_time_report(u)
    else:
        proyect_time = []

    if page == 'count_proyect':
        count_proyect = Proyects.get_by_count_proyect_report(u)
    else:
        count_proyect = []
        
    if page == 'facturation':
        facturation = InvoicesDetails.get_by_facturation()
        date_form  = DateSelectForm() 
    else:
        facturation = []
        date_form  = DateSelectForm() 


    if page == 'task_user':
        if request.method == 'POST':
            user_new = request.form.get('ddlUsers')
            users = User.get_all()
            user_form = UserSelectForm() 
            tareas_x_status = TaskUser.get_by_count_status(user_new)
            if int(user_new) == 0:
                tareas_x_status = TaskUser.get_by_count_status_all()
        else:
            users = User.get_all()
            user_form = UserSelectForm() 
            tareas_x_status = TaskUser.get_by_count_status(u)
    else:
        tareas_x_status = []
        users = User()
        user_form = UserSelectForm() 
 

    context = {
        'notifications':notifications,
        'page':page,
        'count_proyect':count_proyect,
        'proyect_time':proyect_time,
        'facturation':facturation,
        'flag_read':flag_read,
        'tareas_x_status':tareas_x_status,
        'users':users,
        'user_form':user_form,
        'date_form':date_form
    }


    if request.method == 'POST' and page == 'facturation':
        _start_date =  date_form.between_1.data
        _end_date = date_form.between_2.data

        #start = datetime.strptime( _start_date , '%Y-%m-%d')
        #end = datetime.strptime( _end_date, '%Y-%m-%d')

        facturation = InvoicesDetails.get_by_facturation_date(_start_date , _end_date)
        date_form  = DateSelectForm()            

    if page == 'proyect_time': # Tiempo consumido para finalizar los proyectos por tipo de proyecto. [bar]

        labels_list = []
        for pt in proyect_time:
            labels_list.append(pt.tipo)

        labels = labels_list

        values_list = []
        for pt in proyect_time:
            values_list.append(pt.cantidad)

        values = values_list

        bar_labels=labels
        bar_values=values

        return render_template('report.html', title='Tiempo consumido para finalizar un proyecto', max=100, labels=bar_labels, values=bar_values , **context)

    elif page == 'count_proyect': #Cantidad de proyectos por tipo de proyectos. [pie]
        
        labels_list = []
        for pt in count_proyect:
            labels_list.append(pt.proyect_type)
        
        labels = labels_list

        values_list = []
        for pt in count_proyect:
            values_list.append(pt.cantidad)

        values = values_list

        colors = [
            "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500"
            ]
        

        return render_template('report.html', title='Cantidad de proyectos por tipo de proyecto', max=17000, set=zip(values, labels, colors) , **context)
    
    elif page == 'facturation': #Facturacion por tipo de proyecto [bar]

        labels_list = []
        for f in facturation:
            labels_list.append(f.proyect_type)
        
        labels = labels_list

        values_list = []
        for f in facturation:
            values_list.append(f.cantidad)

        values = values_list

        bar_labels=labels
        bar_values=values

        return render_template('report.html', title='Facturacion por tipo de proyecto', max=10000, labels=bar_labels, values=bar_values , **context)

    elif page == 'task_user': #Cantidad de tareas por usuario [LINE]

        labels_list = []
        for pt in tareas_x_status:
            labels_list.append(pt.status)
            
        labels_task = labels_list

        values_list = []
        for pt in tareas_x_status:
            values_list.append(pt.cantidad)

        values_task = values_list

        colors_task = [
            "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500"
        ]
        
        
        return render_template('report.html',  title='Tareas por estado' , set=zip( values_list , labels_list, colors_task) , max=100 , **context)

    else:
        labels = []
        values = []
        colors = []
    
    return render_template('report.html', **context)


## PAG. NOTIFICATION
@app.route('/notification' , methods=['GET', 'POST'])
def notification():
    db.get_engine(app).dispose()
    #Session.close()()

    u = request.args.get('u')
    page = request.args.get('page')
    pages = int(request.args.get('pages', 1))
    confi_form = ConfigForm()
    user = User.get_by_id(u)

    notifications = Notifications.get_by_user_id(u , pages , 10)

    flag_read = True
    for  n  in notifications.items:
        if n.read == False:
            flag_read = False
        #else:
        #    flag_read = True
    
    #print(flag_read)

    if page != 'update_configuracion' and request.method != 'POST':
        confi_form.check_proyect_notification.data = user.config_proyect
        confi_form.check_proyect_task.data = user.config_task

    context = {
        'notifications': notifications,
        'u': u,
        'page':page,
        'confi_form':confi_form,
        'user':user,
        'flag_read':flag_read
    }
    
    if page == 'marcar_leidas':
        for n in notifications.items:
            n.read = True
            db.session.add(n)
            db.session.commit()
        return redirect(url_for('notification', page = 1 , u = u))
    
    if page == 'configuracion':
        # redirigir
        return redirect(url_for('notification', page='notification_form', u = u))
   
    if page == 'update_configuracion' and request.method == 'POST':
        try:
            if confi_form.check_proyect_notification.data == True:
                user.config_proyect = confi_form.check_proyect_notification.data
                db.session.add(user)
                db.session.commit()
            else:
                user.config_proyect = False
                db.session.add(user)
                db.session.commit()

            if confi_form.check_proyect_task.data == True:
                user.config_task = confi_form.check_proyect_task.data
                db.session.add(user)
                db.session.commit()
            else:
                user.config_task = False
                db.session.add(user)
                db.session.commit()
        except Exception as e:
            print(e)

        #return redirect(url_for('notification', page = 1 , u = u))

    return render_template('notification.html' , **context)

##########################
####### FUNCIONES ########
##########################

def check(email):  

    if(re.search(regex,email)): 
        valid = 'valid'
        return  valid
          
    else: 
        invalid = 'invalid'
        return  invalid 


##########################
######## SERVER ##########
##########################

if __name__ == '__main__':
    app.run(debug=True)
    