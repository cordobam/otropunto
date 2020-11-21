from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime , func 
from sqlalchemy.orm import defer 
from datetime import datetime , date , timedelta 
from sqlalchemy.sql import label

db = SQLAlchemy()

### pais

class Country(db.Model):
    __tablename__ = 'country'
    id_country= db.Column(db.Integer, primary_key=True)
    description= db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Country %r>' % self.description
    
    @staticmethod
    def get_all():
        return Country.query.all()

    @staticmethod
    def get_country_by_id(id):
        return Country.query.filter_by(id_country=id)

#### provincia

class CountryState(db.Model):
    __tablename__ = 'country_state'
    id_country_state= db.Column(db.Integer, primary_key=True)
    id_country= db.Column(db.Integer)
    description= db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Country State %r>' % self.description
    
    @staticmethod
    def get_all():
        return CountryState.query.all()
    
    @staticmethod
    def get_state_by_id(id):
        return Country.query.filter_by(id_country_state=id)

#### roles del usuario

class UserRole(db.Model):
    __tablename__ = 'user_role'
    id_user_role= db.Column(db.Integer, primary_key=True)
    description= db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User Role %r>' % self.description
    
    @staticmethod
    def get_all():
        return UserRole.query.all()
    
    @staticmethod
    def get_role_by_id(id):
        return Country.query.filter_by(id_country_state=id)

#### usuarios

class User(db.Model):
    __tablename__ = 'users'
    id_user= db.Column(db.Integer, primary_key=True)
    id_state= db.Column(db.Integer , db.ForeignKey('country_state.id_country_state'))
    id_country= db.Column(db.Integer , db.ForeignKey('country.id_country'))
    id_user_role= db.Column(db.Integer, db.ForeignKey('user_role.id_user_role'))
    company_name= db.Column(db.String(80), nullable=False)
    email_address= db.Column(db.String(80), unique=True, nullable=False)
    password= db.Column(db.String(80), nullable=False)
    flag_delete= db.Column(db.String(80), nullable=False)
    create_date = db.Column (db.DateTime, default=datetime.utcnow , nullable= False)
    update_date = db.Column (db.DateTime, default=datetime.utcnow , nullable= False)
    config_proyect = db.Column(db.Boolean, default = True) # esto significa si esta acepto recibir notificaciones
    config_task = db.Column(db.Boolean, default = True) # esto significa si esta acepto recibir notificaciones

    _state = db.relationship('CountryState', backref='users')
    _country = db.relationship('Country', backref='users')
    _role = db.relationship('UserRole', backref='users')

    def __repr__(self):
        return '<User %r >' % self._country
    
    @staticmethod
    def get_all():
        return User.query.all()
    @staticmethod
    def get_by_id(id):
        return User.query.filter_by(id_user = id ).first()
    @staticmethod
    def get_for_login(email, password):
        info_user = User.query.filter_by(email_address=email, password=password).first()
        if info_user is None:
            info_user = 0
        else:
            return info_user 

    @staticmethod
    def get_for_email(email):
        info_user = User.query.filter_by(email_address=email).join(Country , User.id_country ==  Country.id_country).join(CountryState, User.id_state == CountryState.id_country_state).join(UserRole, User.id_user_role == UserRole.id_user_role).first()
        if info_user is None:
            info_user = 0
        else:
            return info_user
    
    @staticmethod
    def get_by_user_role(id_user_role):
        return User.query.filter_by(id_user_role=id_user_role).all()
    
##### estado de los proyectos

class ProyectStatus(db.Model):
    __tablename__ = 'proyect_status'
    id_proyect_status= db.Column(db.Integer, primary_key=True)
    description= db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<ProyectStatus %r>' % self.description
    
    @staticmethod
    def get_all():
        proyect_status = ProyectStatus.query.all()
        db.session.remove()
        return proyect_status

#### PAG. PROYECTS

class Proyects(db.Model):
    __tablename__ = 'proyects'
    id_proyect = db.Column(db.Integer, primary_key=True)
    id_user =  db.Column(db.Integer)
    #id_assets = db.Column(db.Integer, db.ForeignKey('assets.id_assets'))
    create_date = db.Column (db.DateTime, default=datetime.utcnow , nullable= False)
    id_proyect_type = db.Column(db.Integer, db.ForeignKey('proyects_types.id_proyect_type'))  
    hours_estimate = db.Column(db.Float, nullable=False) 
    proyect_name = db.Column(db.String(80), nullable=False)
    start_date = db.Column (db.DateTime, nullable= False)
    end_date = db.Column (db.DateTime, nullable= False)
    id_client = db.Column(db.Integer, db.ForeignKey('users.id_user'))  
    id_proyect_status =  db.Column(db.Integer, db.ForeignKey('proyect_status.id_proyect_status'))  

    _proyect_type = db.relationship('ProyectType', backref='proyects')
    _proyect_status = db.relationship('ProyectStatus', backref='proyects')
    _proyect_client = db.relationship('User', backref='proyects')

    def __repr__(self):
        return '<proyects %r>' % self.id_proyect
    
    @staticmethod
    def get_all():
        return Proyects.query.all()
    
    @staticmethod
    def get_all_paginated( page = 1 , per_page = 20 ):
        return Proyects.query.order_by(Proyects.create_date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_all_paginated_id( page = 1 , per_page = 20 , id = id):
        return Proyects.query.filter_by(id_user = id).order_by(Proyects.create_date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_id(id):
        return Proyects.query.filter_by(id_proyect = id).join(ProyectType , ProyectType.id_proyect_type == Proyects.id_proyect_type ).join(ProyectStatus , ProyectStatus.id_proyect_status == Proyects.id_proyect_status).join(User , User.id_user == Proyects.id_client).first()
    
    @staticmethod
    def get_by_name(name):
        return Proyects.query.filter_by(proyect_name = name).first()
    
    @staticmethod
    def get_all_by_user(id):
        return Proyects.query.filter_by(id_user = id).all()
    
    ### PARA REPORTES

    #Cantidad de proyectos por mes y año por tipo de proyectos.

    @staticmethod
    def get_by_count_proyect_report(id_user):
        return Proyects.query.filter_by(id_user=id_user).with_entities(label( 'cantidad', func.count(Proyects.id_proyect)) , label( 'proyect_type' , ProyectType.description)).join(ProyectType , ProyectType.id_proyect_type == Proyects.id_proyect_type).group_by(ProyectType.description).all()
 

    


#### usarios de los proyectos


class ProyectUsers(db.Model):
    __tablename__ = 'proyects_users'
    id_proyect_users = db.Column(db.Integer, primary_key=True)
    id_proyect = db.Column(db.Integer, db.ForeignKey('proyects.id_proyect'))  
    id_user =  db.Column(db.Integer, db.ForeignKey('users.id_user'))  

    _proyect = db.relationship('Proyects', backref='proyects_users')
    _user = db.relationship('User', backref='proyects_users')

    def __repr__(self):
        return '<Proyect Users %r>' % self.id_proyect_users
    
    @staticmethod
    def get_all():
        return ProyectUsers.query.all()
    
    @staticmethod
    def get_by_id(id_proyect_users):
        return ProyectUsers.query.filter_by(id_proyect_users = id_proyect_users).first()

    @staticmethod
    def get_by_proyect_id(id_proyect):
        return ProyectUsers.query.filter_by(id_proyect = id_proyect).join(User , User.id_user == ProyectUsers.id_user)

    @staticmethod
    def get_user_proyect_paginated_id( page  , per_page  ,  id , proyect_status): 
        return  ProyectUsers.query.filter_by(id_user = id).join(Proyects , Proyects.id_proyect == ProyectUsers.id_proyect ).filter(Proyects.id_proyect_status == proyect_status).paginate(page=page, per_page=per_page, error_out=False)
 
    @staticmethod
    def get_user_proyect_paginated( page  , per_page  ,  id ): 
        return  ProyectUsers.query.filter_by(id_user = id).join(Proyects , Proyects.id_proyect == ProyectUsers.id_proyect ).filter_by(id_proyect_status = 1).paginate(page=page, per_page=per_page, error_out=False)
 
    @staticmethod
    def get_by_count_status(id_user):
        return ProyectUsers.query.with_entities(label( 'cantidad', func.count(ProyectUsers.id_proyect)) , label( 'status' , ProyectStatus.description)).filter_by(id_user = id_user).join(Proyects , Proyects.id_proyect == ProyectUsers.id_proyect).join(ProyectStatus , ProyectStatus.id_proyect_status == Proyects.id_proyect_status).group_by(ProyectStatus.description).all()


#### avance en si 



class Advances(db.Model):
    __tablename__ = 'advances'
    id_advance = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    create_date = db.Column (db.DateTime , default = datetime.utcnow , nullable= False)
    id_comment = db.Column(db.Integer, db.ForeignKey('comments_advances.id_comments')) 
    advance_type = db.Column(db.String(254), nullable=False)
    description = db.Column(db.String(254), nullable=False)

    _comment = db.relationship('Comments', backref='Advances')

    def __repr__(self):
        return '<Advance %r>' % self.id_advance
    
    @staticmethod
    def get_all():
        return Advances.query.all()
    
    @staticmethod
    def get_by_id(id_advance):
        return Advances.query.filter_by(id_advance = id_advance)

#### tabla intermedia (many to many) avance de proyecto

class ProyectAdvance(db.Model): 
    __tablename__ = 'advances_proyects'
    id_advance_proyect = db.Column(db.Integer, primary_key=True)
    id_advance =  db.Column(db.Integer, db.ForeignKey('advances.id_advance')) 
    id_proyect =   db.Column(db.Integer, db.ForeignKey('proyects.id_proyect')) 
    id_user =   db.Column(db.Integer, db.ForeignKey('users.id_user')) 
    
    _advance = db.relationship('Advances', backref='ProyectAdvance')
    _proyect = db.relationship('Proyects', backref='ProyectAdvance')
    _user = db.relationship('User', backref='ProyectAdvance')

    def __repr__(self):
        return '<ProyectAdvance %r>' % self.id_advance_proyect
    
    @staticmethod
    def get_all():
        return ProyectAdvance.query.all()
    
    @staticmethod
    def get_by_id(id_advance_proyect):
        return ProyectAdvance.query.filter_by(id_advance_proyect = id_advance_proyect)
    
    @staticmethod
    def get_by_proyect_id(id_proyect):
        return ProyectAdvance.query.filter_by(id_proyect = id_proyect).join(Advances , ProyectAdvance.id_advance == Advances.id_advance).join(User , User.id_user == ProyectAdvance.id_user).order_by(Advances.create_date.asc()).all()
    


#### tabla intermedia (many to many) avance de tareas

class TaskAdvance(db.Model): 
    __tablename__ = 'advances_task'
    id_advance_task = db.Column(db.Integer, primary_key=True)
    id_advance =  db.Column(db.Integer, db.ForeignKey('advances.id_advance')) 
    id_task =   db.Column(db.Integer, db.ForeignKey('tasks.id_task')) 
    id_user =   db.Column(db.Integer, db.ForeignKey('users.id_user')) 
    
    _advance = db.relationship('Advances', backref='TaskAdvance')
    _task = db.relationship('Tasks', backref='TaskAdvance')
    _user = db.relationship('User', backref='TaskAdvance')

    def __repr__(self):
        return '<TaskAdvance %r>' % self.id_advance_task
    
    @staticmethod
    def get_all():
        return TaskAdvance.query.all()
    
    @staticmethod
    def get_by_id(id_advance_task):
        return TaskAdvance.query.filter_by(id_advance_task = id_advance_task)

    @staticmethod
    def get_by_task_id(id_task):
        return TaskAdvance.query.filter_by(id_task = id_task).join(Advances , Advances.id_advance == TaskAdvance.id_advance).join(User , User.id_user == TaskAdvance.id_user).order_by(Advances.create_date.asc()).all()


#### tipos de proyectos


class ProyectType(db.Model):
    __tablename__ = 'proyects_types'
    id_proyect_type= db.Column(db.Integer, primary_key=True)
    description= db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<Proyect Type %r>' % self.description
    
    @staticmethod
    def get_all():
        return ProyectType.query.all()
    
    @staticmethod
    def get_by_id(id_proyect_type):
        return ProyectType.query.all(id_proyect_type = id_proyect_type)

##### materiales 

class AssetsMaterials(db.Model):
    __tablename__ = 'assets'
    id_assets = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(254), nullable=False)
    url_asset = db.Column(db.String(254), nullable=False)
    create_date = db.Column (db.DateTime , default=datetime.utcnow , nullable= False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user')) 

    _user = db.relationship('User', backref='AssetsMaterials')

    def __repr__(self):
        return '<Assets %r>' % self.descriprion
    
    @staticmethod
    def get_all():
        return AssetsMaterials.query.all()
    
    @staticmethod
    def get_by_id(id_assets):
        return AssetsMaterials.query.filter_by(id_assets = d_assets)
    
    @staticmethod
    def get_by_task(id_task):
        return AssetsMaterials.query.join(TaskAssets ,TaskAssets.id_assets == AssetsMaterials.id_assets).join(User, User.id_user == AssetsMaterials.id_user).filter(id_task= TaskAssets.id_task)
    

##### materiales de las tareas - tabla intermedia

class TaskAssets(db.Model):
    __tablename__ = 'task_assets'
    id_task_assets = db.Column(db.Integer, primary_key=True)
    id_assets = db.Column(db.Integer, db.ForeignKey('assets.id_assets')) 
    id_task = db.Column(db.Integer, db.ForeignKey('tasks.id_task')) 

    _assets = db.relationship('AssetsMaterials', backref='TaskAssets')
    _task = db.relationship('Tasks', backref='TaskAssets')

    def __repr__(self):
        return '<Assets %r>' % self.descriprion
    
    @staticmethod
    def get_all():
        return TaskAssets.query.all()
    
    @staticmethod
    def get_by_id(id_task_assets):
        return TaskAssets.query.filter_by(id_task_assets = id_task_assets)
    
    @staticmethod
    def get_by_id_task(id_task_assets):
        return TaskAssets.query.filter_by(id_task_assets= id_task_assets).join(AssetsMaterials ,TaskAssets.id_assets == AssetsMaterials.id_assets).first()

    @staticmethod
    def get_by_task(id_task):
        return TaskAssets.query.filter_by(id_task= id_task).join(AssetsMaterials ,TaskAssets.id_assets == AssetsMaterials.id_assets).join(User , AssetsMaterials.id_user == User.id_user).all()

##### comentarios de las tareas

class Comments(db.Model):
    __tablename__ = 'comments_advances'
    id_comments  = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user')) 
    comments_ = db.Column(db.String(254), nullable=False)
    create_date = db.Column (db.DateTime, default=datetime.utcnow , nullable= False)
    id_task = db.Column(db.Integer, db.ForeignKey('tasks.id_task')) 
    feedback_asset = db.Column(db.String(254), nullable=False)

    _user = db.relationship('User', backref='Comments')
    _task = db.relationship('Tasks', backref='Comments')

    def __repr__(self):
        return '<Assets %r>' % self.comments_
    
    @staticmethod
    def get_all():
        return Comments.query.all()
    
    @staticmethod
    def get_by_id(id_comments):
        return Comments.query.filter_by( id_comments = id_comments).first()
    
    @staticmethod
    def get_by_task_id(id_task):
        return Comments.query.filter_by( id_task = id_task).join(User , User.id_user == Comments.id_user).all()

#### tipos de tarea para tipificacion

class TypeTasks(db.Model):
    __tablename__ = 'type_task'
    id_type_task  = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(254), nullable=False)

    def __repr__(self):
        return '<TypeTasks %r>' % self.description

    @staticmethod
    def get_all():
        return TypeTasks.query.all()
    
    @staticmethod
    def get_by_id(id_type_task):
        return TypeTasks.query.filter_by(id_type_task = id_type_task)

##### estado de las tareas

class Status(db.Model):
    __tablename__ = 'status'
    id_status  = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(254), nullable=False)

    def __repr__(self):
        return '<Assets %r>' % self.description
    
    @staticmethod
    def get_all():
        return Status.query.all()
    
    @staticmethod
    def get_by_id(id_status):
        return Status.query.filter_by(id_status = id_status)
    
##### tareas de los usuarios 

class TaskUser(db.Model):
    __tablename__ = 'task_user'
    id_task_user = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user')) 
    id_task = db.Column(db.Integer, db.ForeignKey('tasks.id_task')) 

    _user = db.relationship('User', backref='TaskUser')
    _task = db.relationship('Tasks', backref='TaskUser')

    def __repr__(self):
        return '<TaskUser %r>' % self.description
    
    @staticmethod
    def get_all():
        return TaskUser.query.all()
    
    @staticmethod
    def get_by_task_id(id_task):
        return TaskUser.query.filter_by(id_task = id_task).join(User , User.id_user == TaskUser.id_user)
    
    @staticmethod
    def get_by_id(id_task_user):
        return TaskUser.query.filter_by(id_task_user = id_task_user).first()

    #self.session.query(func.count(Table.column1),Table.column1, Table.column2).group_by(Table.column1, Table.column2).all()
    @staticmethod
    def get_by_count_status(id_user):
        return TaskUser.query.with_entities(label( 'cantidad', func.count(TaskUser.id_task)) , label( 'status' , Status.description)).filter_by(id_user = id_user).join(Tasks , Tasks.id_task == TaskUser.id_task).join(Status , Tasks.id_status == Status.id_status).group_by(Status.description).all()

    @staticmethod
    def get_by_count_status_all():
        return TaskUser.query.with_entities(label( 'cantidad', func.count(TaskUser.id_task)) , label( 'status' , Status.description)).join(Tasks , Tasks.id_task == TaskUser.id_task).join(Status , Tasks.id_status == Status.id_status).group_by(Status.description).all()


    
##### tareas de cada proyecto

class Tasks(db.Model):
    __tablename__ = 'tasks'
    id_task = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user')) 
    id_proyect = db.Column(db.Integer, db.ForeignKey('proyects.id_proyect')) 
    description = db.Column(db.String(254), nullable=False)
    create_date = db.Column (db.DateTime , default=datetime.utcnow , nullable= False) 
    id_status = db.Column(db.Integer, db.ForeignKey('status.id_status')) 
    title = db.Column(db.String(254), nullable=False)
    end_date = db.Column (db.DateTime , nullable= False) 
    id_type_task = db.Column(db.Integer, db.ForeignKey('type_task.id_type_task')) 

    _user = db.relationship('User', backref='Tasks')
    _proyect = db.relationship('Proyects', backref='Tasks')
    _status = db.relationship('Status', backref='Tasks')
    _type_task =  db.relationship('TypeTasks', backref='Tasks') 

    def __repr__(self):
        return '<Assets %r>' % self.description
    
    @staticmethod
    def get_all():
        return Tasks.query.all()
    
    @staticmethod
    def get_by_id_alone(id_task):
        return Tasks.query.filter_by( id_task = id_task).first()
    
    @staticmethod
    def get_by_task_status(id_task):
        return Tasks.query.join(Status , Status.id_status == Tasks.id_status).all()

    @staticmethod
    def get_all_by_user(id_user):
        return Tasks.query.filter_by(id_user = id_user).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).order_by(Tasks.id_proyect.asc())
    
    @staticmethod
    def get_by_id(id_task):
        return Tasks.query.filter_by( id_task = id_task).join(User , User.id_user == Tasks.id_user).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).join(Status , Status.id_status == Tasks.id_status).join(TypeTasks , TypeTasks.id_type_task == Tasks.id_type_task).first()

    @staticmethod
    def get_by_proyect(id_proyect , x , y , z):
        return Tasks.query.filter_by(id_proyect = id_proyect).join(User , User.id_user == Tasks.id_user).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).join(Status , Status.id_status == Tasks.id_status).filter(Status.id_status.in_((x,y,z))).all()
    
    @staticmethod
    def get_by_proyect_status(id_proyect , x ):
        return Tasks.query.filter_by(id_proyect = id_proyect).join(User , User.id_user == Tasks.id_user).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).join(Status , Status.id_status == Tasks.id_status).filter(Status.id_status == x).all()

    @staticmethod
    def get_by_proyect_board(id_proyect , w , x , y , z):
        return Tasks.query.filter_by(id_proyect = id_proyect).join(User , User.id_user == Tasks.id_user).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).join(Status , Status.id_status == Tasks.id_status).filter(Status.id_status.in_((w,x,y,z))).all()
 
    @staticmethod
    def get_by_user(id_user):
        return Tasks.query.filter_by(id_user = id_user)

    @staticmethod
    def get_all_paginated_by_user( id_user = id_user , page = 1 , per_page = 20 ):
        return Tasks.query.order_by(Tasks.create_date.asc()).filter_by(id_user = id_user).join(Status , Status.id_status == Tasks.id_status).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_user_date(page , per_page , id_user):
        dt= date.today() + timedelta(7)
        now = date.today()
        return Tasks.query.filter_by(id_user = id_user).join(Status , Status.id_status == Tasks.id_status).filter(Tasks.end_date.between(now,dt)).filter(Tasks.id_status != 4).paginate(page=page, per_page=per_page, error_out=False)
    
##### horas trabajadas en cada tarea - poner id_user

class TaskTracking(db.Model):
    __tablename__ = 'time_tasks'
    id_time = db.Column(db.Integer, primary_key=True)
    id_task = db.Column(db.Integer, db.ForeignKey('tasks.id_task')) 
    create_date =  db.Column (db.DateTime ,  default=datetime.utcnow , nullable= False) 
    total_time = db.Column(db.Integer)
    initial_time = db.Column (db.DateTime , nullable= False) 
    final_time = db.Column (db.DateTime , nullable= False) 
    id_user =  db.Column(db.Integer, db.ForeignKey('users.id_user'))
    initial_time_1= db.Column (db.DateTime , nullable= False) 
    final_time_1 = db.Column (db.DateTime , nullable= False) 

    _task = db.relationship('Tasks', backref='TaskTracking')
    _user = db.relationship('User', backref='TaskTracking')

    def __repr__(self):
        return '<TaskTracking %r>' % self.id_time
    
    @staticmethod
    def get_all():
        return TaskTracking.query.all()

    @staticmethod
    def get_by_id(id_time):
        return TaskTracking.query.filter_by(id_time= id_time).first()
    
    @staticmethod
    def get_by_task(id_task):
        return TaskTracking.query.filter_by(id_task = id_task).join(Tasks , TaskTracking.id_task == Tasks.id_task).join(User , User.id_user == TaskTracking.id_user).join(Proyects , Proyects.id_proyect == Tasks.id_proyect).all()
    
    @staticmethod
    def get_by_poyect(id_proyect):
        return TaskTracking.query.join(Tasks , TaskTracking.id_task == Tasks.id_task).join(Proyects , Tasks.id_proyect == Proyects.id_proyect).filter_by(id_proyect = id_proyect).all()

    @staticmethod
    def get_by_poyect_group_by(id_proyect):
        task_track = TaskTracking.query.with_entities(label('id_task',TaskTracking.id_task) , label('id_type_task' , Tasks.id_type_task) ,  label('total_time' ,func.sum(TaskTracking.total_time))).join(Tasks , TaskTracking.id_task == Tasks.id_task).join(Proyects , Tasks.id_proyect == Proyects.id_proyect).filter_by(id_proyect = id_proyect).filter(Tasks.id_status.in_((4 , 5))).group_by(TaskTracking.id_task , Tasks.id_type_task).all()
        db.session.remove()
        return task_track
        #self.session.query(func.count(Table.column1),Table.column1, Table.column2).group_by(Table.column1, Table.column2).all()

    ## para reporte
    
    @staticmethod
    def get_by_type_poyect_time_report(id_user):
        proyect_time = TaskTracking.query.with_entities(label('tipo' , ProyectType.description) , label('cantidad' , func.sum(TaskTracking.total_time))).join(Tasks , TaskTracking.id_task == Tasks.id_task).filter_by(id_user=id_user).join(Proyects , Tasks.id_proyect == Proyects.id_proyect).join(ProyectType , ProyectType.id_proyect_type == Proyects.id_proyect_type).group_by(ProyectType.description).all()
        db.session.remove()
        return proyect_time


###### factura del proyecto 

class Costs(db.Model):
    __tablename__ = 'costs'
    id_costs = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(254), nullable=False)
    price = db.Column(db.Float, nullable=False) 
    id_type_costs = db.Column(db.Integer, db.ForeignKey('proyects.id_proyect'))

    _proyect = db.relationship('Proyects', backref='Costs')

    def __repr__(self):
        return '<Costs %r>' % self.description

    @staticmethod
    def get_all():
        return Costs.query.all()
    
    @staticmethod
    def get_by_id(id_costs):
        return Costs.query.filter_by(id_costs = id_costs).first()

    @staticmethod
    def get_by_plans():
        return Costs.query.filter_by(id_type_costs = 2)

###### 

class TypeCosts(db.Model):
    __tablename__ = 'type_costs'
    id_type_costs = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(254), nullable=False)

    def __repr__(self):
        return '<TypeCosts %r>' % self.description

    @staticmethod
    def get_all():
        return TypeCosts.query.all()
    
    @staticmethod
    def get_by_id(id_type_task):
        return TypeCosts.query.filter_by(id_type_task = id_type_task)

###### 

class ProyectCosts(db.Model):
    __tablename__ = 'proyect_costs'
    id_proyect_costs = db.Column(db.Integer, primary_key=True)
    id_costs = db.Column(db.Integer, db.ForeignKey('costs.id_costs'))
    description = db.Column(db.String(254), nullable=False)
    id_proyect = db.Column(db.Integer, db.ForeignKey('proyects.id_proyect'))
    id_task = db.Column(db.Integer, db.ForeignKey('tasks.id_task'))
    create_date = db.Column (db.DateTime , default=datetime.utcnow, nullable= False) 

    _id_costs = db.relationship('Costs', backref='ProyectCosts')
    _id_proyect =  db.relationship('Proyects', backref='ProyectCosts')
    _id_task =  db.relationship('Tasks', backref='ProyectCosts')

    def __repr__(self):
        return '<ProyectCosts %r>' % self.description

    @staticmethod
    def get_all():
        return ProyectCosts.query.all()
    
    @staticmethod
    def get_by_id(id_proyect_costs):
        return ProyectCosts.query.filter_by(id_proyect_costs = id_proyect_costs)

    @staticmethod
    def get_by_proyect_id(id_proyect):
        return ProyectCosts.query.filter_by(id_proyect = id_proyect).join(Proyects , Proyects.id_proyect == ProyectCosts.id_proyect).first()

###### 

class Invoices(db.Model):
    __tablename__ = 'invoices'
    id_invoice = db.Column(db.Integer, primary_key=True)
    id_proyect = db.Column(db.Integer, db.ForeignKey('proyects.id_proyect'))
    create_date = db.Column (db.DateTime , default=datetime.utcnow, nullable= False) 

    _id_proyect = db.relationship('Proyects', backref='Invoices')

    def __repr__(self):
        return '<Invoices %r>' % self.id_invoice

    @staticmethod
    def get_all():
        return Invoices.query.all()

    @staticmethod
    def get_all_proyect_close():
        return Invoices.query.join(Proyects , Proyects.id_proyect == Invoices.id_proyect).filter_by(id_proyect_status= 2).all()
    
    @staticmethod
    def get_by_id(id_invoice):
        return Invoices.query.filter_by(id_invoice = id_invoice).first()

    @staticmethod
    def get_by_proyect_id(id_proyect):
        return Invoices.query.filter_by(id_proyect = id_proyect).first()

######

class InvoicesDetails(db.Model):
    __tablename__ = 'invoice_detail'
    id_invoice_d = db.Column(db.Integer, primary_key=True)
    id_invoice = db.Column(db.Integer, db.ForeignKey('invoices.id_invoice'))
    id_time_track = db.Column(db.Integer, db.ForeignKey('time_tasks.id_time'))
    total_hours  =  db.Column(db.Float, nullable=False) 
    total_price = db.Column(db.Float, nullable=False) 
    id_proyect_costs = db.Column(db.Integer, db.ForeignKey('proyect_costs.id_proyect_costs'))
    
    _id_invoice = db.relationship('Invoices', backref='InvoicesDetails')
    _id_time_track = db.relationship('TaskTracking', backref='InvoicesDetails')
    _id_proyect_costs = db.relationship('ProyectCosts', backref='InvoicesDetails')


    def __repr__(self):
        return '<InvoicesDetails %r>' % self.total_hours

    @staticmethod
    def get_all():
        return InvoicesDetails.query.all()
    
    @staticmethod
    def get_by_id(id_invoice_d):
        return InvoicesDetails.query.filter_by(id_invoice_d = id_invoice_d)

    @staticmethod
    def get_by_invoice_id(id_invoice):
        return InvoicesDetails.query.filter_by(id_invoice = id_invoice).all()

    ## para reporte

    @staticmethod
    def get_by_facturation():
        return InvoicesDetails.query.with_entities(label( 'proyect_type' , ProyectType.description) , label( 'cantidad', func.sum(InvoicesDetails.total_hours * InvoicesDetails.total_price)) ).join(Invoices , Invoices.id_invoice == InvoicesDetails.id_invoice).join(Proyects , Proyects.id_proyect == Invoices.id_proyect).join(ProyectType , ProyectType.id_proyect_type == Proyects.id_proyect_type).group_by(ProyectType.description).all()
 
    #label( 'cantidad', func.count(Proyects.id_proyect)) , label( 'proyect_type' , ProyectType.description)

###### 

class Notifications(db.Model):
    __tablename__ = 'notifications'
    id_notification = db.Column(db.Integer, primary_key=True)
    id_proyect = db.Column(db.Integer, db.ForeignKey('proyects.id_proyect'))
    description = db.Column(db.String(254), nullable=False)
    create_date = db.Column (db.DateTime , default=datetime.utcnow, nullable= False) 
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    id_task = db.Column(db.Integer, db.ForeignKey('tasks.id_task'))
    read = db.Column(db.Boolean , default = False) # esto significa si lo ha leido o no
    #config = db.Column(db.Boolean, default = True) # esto significa si esta acepto recibir notificaciones

    _proyect =  db.relationship('Proyects', backref='Notifications')
    _user =  db.relationship('User', backref='Notifications')
    _task =  db.relationship('Tasks', backref='Notifications')

    def __repr__(self):
        return '<Notifications %r>' % self.description

    @staticmethod
    def get_all():
        return Notifications.query.all()
    
    @staticmethod
    def get_by_id(id_notification):
        return Notifications.query.filter_by(id_notification = id_notification)
    
    @staticmethod
    def get_by_user_id(id_user , page = 1 , per_page = 20):
        response = Notifications.query.order_by(Notifications.create_date.asc()).filter_by(id_user = id_user).paginate(page=page, per_page=per_page, error_out=False)
        db.session.remove()
        return response