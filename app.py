############################################## import #####################################################
import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, UserMixin, RoleMixin
from flask_login import login_user, logout_user,current_user
from flask_security.utils import hash_password,verify_password
from sqlalchemy.sql import func
import sqlite3
from sqlalchemy.sql.functions import current_timestamp, now

##########################################################################################################

##########################################################################################################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECURITY_PASSWORD_SALT'] = 'thisisasecretsalt'

db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
###########################################################################################################

######################################### create table roles_users  #######################################
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))
###########################################################################################################

#########################################  create table User  #############################################
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    f_name=db.Column(db.String(100),nullable=False)
    l_name=db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    active = db.Column(db.Boolean)
    score = db.Column(db.Integer, default = 0)
    udeck = db.relationship('deck', cascade='all, delete-orphan', backref='deck')
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
############################################################################################################   

######################################### create table Role  ############################################### 
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255))
############################################################################################################

######################################### create table deck #################################################
class deck(db.Model):
    id= db.Column(db.Integer, primary_key=True,autoincrement=True)
    title= db.Column(db.String(255))
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    score = db.Column(db.Integer, default=0)
    last_rev = db.Column(db.DateTime(timezone=True), default=func.now())
    dcard = db.relationship('card', cascade='all, delete-orphan', backref='card')
#############################################################################################################

##########################################  create table card ##############################################
class card(db.Model):
    card_id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String(512), nullable = False)
    back = db.Column(db.String(512), nullable = False)
    score = db.Column(db.Integer, default = 0)
    deck_id = db.Column(db.String, db.ForeignKey('deck.id'), nullable = False)
############################################################################################################

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

############################################  views  #######################################################
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    email=request.form.get('email')
    password=request.form.get('password')
    rep=request.form.get('psw-repeat')
    if password==rep:
        if request.method == 'POST':
            user_datastore.create_user(
                f_name=request.form.get('f_name'),
                l_name=request.form.get('l_name'),
                email=request.form.get('email'),
                password=hash_password(request.form.get('password'))
            )
            db.session.commit()
            user = User.query.filter_by(email=email).first()
            login_user(user, remember=True)
            return render_template('profile.html')
    return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/signin', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        id=user.id
        if user:
            if verify_password(password, user.password):
                login_user(user, remember=True)
                return redirect(url_for('signin',id=id))
            else:
                return render_template('error.html')
        else:
            return render_template('error.html')

    return render_template('signin.html')


@app.route('/signin/<id>',methods = ['GET'])
@login_required
def signin(id):

    conn=None
    try:
        conn=sqlite3.connect('db.sqlite3')
        curr=conn.cursor()
        curr.execute("select score from user where id='%s'"%id)
        rows=curr.fetchone()
        score= rows[0]
        curr.execute("select title,JULIANDAY(?) - JULIANDAY(last_rev),score from deck where user_id=?",(datetime.datetime.now(),id))
        dash=curr.fetchall()
        curr.close() 
        return render_template('profile.html',score=score,dash=dash)
    except (Exception,sqlite3.DatabaseError) as error:
        print(error)
        return '<h1>There is no for this</h1>'
    


@app.route('/signin/deck/<id>',methods = ['GET', 'POST'])
@login_required
def deckk(id):
    if request.method == 'POST':
        dname=request.form.get('dname')
        user=User.query.filter_by(id=id).first()
        Id=user.id
        Deck=deck.query.filter_by(user_id=Id).all()
        if dname:
            for i in Deck:
                if i.title==dname:
                    return render_template("error.html")
            conn=None
            try:
                conn=sqlite3.connect('db.sqlite3')
                curr=conn.cursor()
                now=current_timestamp
                curr.execute("INSERT INTO deck(title, user_id,date_created,last_rev) values(?,?,?,?);",(dname,Id,datetime.datetime.now(),datetime.datetime.now()))
                conn.commit()
                curr.execute("select title from deck where user_id='%s'"%id)
                rows=curr.fetchall()
                curr.close() 
               
                return redirect(url_for('signin',id=id))
            except (Exception,sqlite3.DatabaseError) as error:
                print(error)
                return render_template('error.html') 
  
    else:
        
        conn=None
        
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
            curr.execute("select deck.title,score,JULIANDAY(?) - JULIANDAY(last_rev) from deck where user_id=?",(datetime.datetime.now(),id))
            rows=curr.fetchall()
            curr.close() 
            return render_template('deck.html',rows=rows)
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return render_template('error.html')
    

@app.route('/signin/deck/delete/<id>',methods = ['GET', 'POST'])
@login_required
def deletedeck(id):
    if request.method == 'POST':
        dname=request.form.get('dname1')
        print("dname",dname)
        user=User.query.filter_by(id=id).first()
        print("user",user)
        Id=user.id
        print("Id",Id)
        Deck=deck.query.filter_by(user_id=Id,title=dname).first()
        print("Deck",Deck)
        db.session.delete(Deck)
        db.session.commit()
        return redirect(url_for('signin',id=id))

@app.route('/signin/deck/delete/user/<id>',methods = ['GET', 'POST'])
@login_required
def deleteuser(id):
    if request.method == 'POST':
        dname=request.form.get('dname2')
        print("dname",dname)
        user=User.query.filter_by(id=id).first()
        print("user",user)
        Id=user.id
        print("Id",Id)
        person=User.query.filter_by(id=Id).first()
        print("person",person)
        db.session.delete(person)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/signin/deck/card/<id>/<p>',methods = ['GET', 'POST'])
@login_required
def cards(id,p):
    if request.method == 'POST':
        front=request.form.get("front")
        back=request.form.get("back")
        Deck=deck.query.filter_by(title=p,user_id=id).first()
        Id=Deck.id
        Card=card.query.filter_by(deck_id=Id).all()
        if front and back:
            for i in Card:
                if i.front==front and i.back==back:
                    return render_template("error.html")
            conn=None
            try:
                conn=sqlite3.connect('db.sqlite3')
                curr=conn.cursor()
                
                curr.execute("INSERT INTO card(front,back,deck_id) values(?,?,?);",(front,back,Id))
               
                conn.commit()
               
                curr.execute("select deck.title,score,JULIANDAY(?) - JULIANDAY(last_rev) from deck where user_id=?",(datetime.datetime.now(),id))
                rows=curr.fetchall()
                curr.close() 
                # return render_template('deck.html',rows=rows)
                return redirect(url_for('deckk',id=id))
            except (Exception,sqlite3.DatabaseError) as error:
                print(error)
                return render_template("error.html")
    else:
        Deck=deck.query.filter_by(title=p,user_id=id).one()
        deck_id=Deck.id
        conn=None
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
            curr.execute("select * from card where deck_id='%s'"%deck_id)
            rows=curr.fetchall()
            cscore=0
            for row in rows:
                cscore+=row[3]
            dql="UPDATE deck set score = ?,last_rev = ? where id = ?"
            curr.execute(dql, (cscore,datetime.datetime.now(), deck_id))
            conn.commit()


            curr.execute("select score from deck where user_id='%s'"%id)
            urow=curr.fetchall()
            print(urow)
            #rv=len(urow)
            rscore=0
            for i in urow:
                if i[0] != None:
                    rscore+=i[0]

            uscore=rscore

            uql="update user set score=? where id=?"
            curr.execute(uql,(uscore,id))
            conn.commit()


            curr.close() 
            return render_template("card.html",rows=rows,p=p,cscore=cscore)
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return render_template('error.html')
    

@app.route('/signin/deck/quiz/<id>/<p>',methods = ['GET', 'POST'])
@login_required
def quiz(id,p):
    if request.method == 'GET':
        Deck=deck.query.filter_by(title=p,user_id=id).one()
        deck_id=Deck.id
        conn=None
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
            curr.execute("select * from card where deck_id='%s'"%deck_id)
            rows=curr.fetchall()
            curr.close() 
            return render_template("quiz.html",rows=rows,p=p)
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return render_template('error.html')


@app.route('/signin/deck/quiz/<id>/<p>/card/<r>',methods = ['GET', 'POST'])
@login_required

def score_card(id,p,r):
    if request.method=="POST":
        Deck=deck.query.filter_by(title=p,user_id=id).one()
        deck_id=Deck.id
        dscore=Deck.score
        score=0
        clicks=request.form.get("click")
        if clicks=='easy':#10
            score+=10
        elif clicks=='medium':#7
            score+=7
        elif clicks=='hard':#4
            score+=4
        else:#2
            score+=2
        score=str(score)
     
        conn=None
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
          
            sql="UPDATE card set score = ? where card_id = ?"
            
            curr.execute(sql, (score, r))
            conn.commit()
            curr.close()
            return redirect(url_for('quiz',id=id,p=p))
           
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return render_template('error.html')

##______________________________cARD DELETE ____________________________________#

@app.route('/signin/deck/quiz/<id>/<deckname>/card/<cardid>/delete',methods = ['GET', 'POST'])
@login_required
def carddelete(id,deckname,cardid):
    if request.method=="POST":
        Deck=deck.query.filter_by(title=deckname,user_id=id).one()
        
        deck_id=Deck.id
        conn=None
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
            curr.execute("delete from card where deck_id=? and card_id=?",(deck_id,cardid))
            
            conn.commit()

           
            curr.close() 
            print("bebo----------------------------------------------------------")
            return redirect(url_for("cards",id=id,p=deckname))
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return '<h1>There is no 3 for line 472this</h1>'


#---------------------------------Card Edit-------------------------------------------------------------#
@app.route("/signin/deck/quiz/<user_id>/<deckname>/card/<cardid>/edit",methods = ['GET', 'POST'])
@login_required
def cardadd(user_id,deckname,cardid):
    if request.method=="POST":
        Deck=deck.query.filter_by(title=deckname,user_id=user_id).one()
        front=request.form.get("fronte")
        back=request.form.get("backe")
        deck_id=Deck.id
        conn=None
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
            gql="update  card set front = ?,back = ?  where card_id = ?"
            curr.execute(gql,(front,back,cardid))
            conn.commit()
            curr.close()
            return redirect(url_for("cards",id=user_id,p=deckname))
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return '<h1>There is no 3 for line 49999999999 this</h1>'

#-------------------------------------------Deck Edit------------------------
@app.route("/signin/deck/<id>/<p>/edit" ,methods = ['GET', 'POST'])
@login_required
def  deckedit(id,p):
    if request.method=="POST":
        Deck=deck.query.filter_by(title=p,user_id=id).one()
        front=request.form.get("frontd")
        #back=request.form.get("backd")
        deck_id=Deck.id
        conn=None
        try:
            conn=sqlite3.connect('db.sqlite3')
            curr=conn.cursor()
            gql="update deck set title = ?  where id = ?"
            curr.execute(gql,(front,deck_id))
            conn.commit()
            curr.close()
            return redirect(url_for("deckk",id=id))
        except (Exception,sqlite3.DatabaseError) as error:
            print(error)
            return '<h1>There is no 3 for line 49999999999 this</h1>'


@app.route("/signin/deck/<id>/<p>/delete" ,methods = ['GET', 'POST'])
@login_required
def  deck_delete(id,p):
    if request.method=="POST":
        Deck=deck.query.filter_by(title=p,user_id=id).one()
        # front=request.form.get("frontd")
        #back=request.form.get("backd")
        #deck_id=Deck.id
        # dname=request.form.get('dname1')
        # # print("dname",dname)
        # user=User.query.filter_by(id=id).first()
        # print("user",user)
        # Id=user.id
        # print("Id",Id)
        # Deck=deck.query.filter_by(user_id=Id,title=dname).first()
        print("Deck",Deck)
        db.session.delete(Deck)
        db.session.commit()
        return redirect(url_for("deckk",id=id))








@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
##########################################################################################################################
#################################################  app run ###############################################################
if __name__=='__main__':
    app.run(debug=True)
#########################################################################################################################




