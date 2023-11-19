from flask import Flask, render_template, redirect,request
import psycopg2

utype=-1
uid=-1

app = Flask(__name__)

@app.route('/')
def mover():
    return redirect('/login')

@app.route('/home')
def home():
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT club_name,image,club_id FROM clubs;')
    clubs= cur.fetchall()
    cur.execute('Select a.type_name,b.event_name,b.event_date from events b,event_type a where b.event_type=a.type_id order by b.event_id desc limit 5')
    events=cur.fetchall()
    conn.commit()
    conn.close()
    return render_template('home.html',club=clubs,u_type=utype,events=events)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',message='Please register')
    if request.method == 'POST':
        email=request.form['email']
        passwd=request.form['password']
        name=request.form['username']
        c_passwd=request.form['c_password']

        conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
        cur = conn.cursor()
        cur.execute(f'SELECT passwd,u_type FROM user_info WHERE u_email = \'{email}\';')
        f_passwd=cur.fetchone()

        if passwd!=c_passwd:
            return render_template('register.html',message="passwords don't match")
        
        if f_passwd is None:
            conn.commit()
            cur.execute(f'Insert into user_info(u_name,u_email,passwd) values(\'{name}\',\'{email}\',\'{passwd}\'); ')
            conn.commit()
            conn.close()
            return render_template('login.html',message="Account created!Login to continue")
        else:
            return render_template('login.html',message="Account already exists!Login to continue")


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',message='Login to Continue')
    if request.method == 'POST':
        email=request.form['email']
        passwd=request.form['password']

        conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
        cur = conn.cursor()
        cur.execute(f'SELECT passwd,u_type,u_id FROM user_info WHERE u_email = \'{email}\';', )
        info=cur.fetchone()
        cur.execute('SELECT club_name,image,club_id FROM clubs;')
        clubs= cur.fetchall()
        conn.commit()
        conn.close()

        if info is None:
            return render_template('login.html',message='No such account exists')

        if (info[0]==passwd):
            global utype,uid
            uid=info[2]
            utype=info[1]
            return redirect('/home')
        else:
            return render_template('login.html',message='Wrong Password ! try again')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/club/<int:club_id>')
def club(club_id):
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT club_name, club_description,image FROM clubs WHERE club_id = %s;', (club_id,))
    club_info = cur.fetchone()
    conn.close()
    
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT event_id,event_name,event_date FROM events WHERE club_id = %s;', (club_id,))
    events = cur.fetchall()
    conn.close()

    return render_template('club_page.html', club_info=club_info, events=events,u_type=utype)

@app.route('/add_event')
def add_event():
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT club_name FROM clubs;')
    club_names = cur.fetchall()
    cur.execute('SELECT * FROM event_type;')
    event_types = cur.fetchall()
    conn.close()
    return render_template('add_event.html',clubs=club_names,types=event_types,u_type=utype)

@app.route('/submit_event',methods=['GET','POST'])
def submit_event():
    if request.method == 'POST':
        eventName=request.form['eventName']
        eventImage=request.form['eventImage']
        eventDescription=request.form['eventDescription']
        eventDate=request.form['eventDate']
        clubSelection=request.form['clubSelection']
        eventType=request.form['eventType']
        conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
        cur = conn.cursor()
        cur.execute(f'SELECT type_id FROM event_type where type_name=\'{eventType}\';')
        type_id = cur.fetchall()
        cur.execute(f'SELECT club_id FROM clubs where club_name=\'{clubSelection}\';')
        club=cur.fetchall()
        cur.execute(f"insert into events (event_name,event_date,club_id,event_type,event_description,event_image) values(\'{eventName}\',\'{eventDate}\',{club[0][0]},{type_id[0][0]},\'{eventDescription}\',\'{eventImage}\');")
        conn.commit()
        conn.close()
        return redirect('/home')

@app.route('/event/<int:event_id>')
def event(event_id):
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    cur.execute(f"SELECT e.event_name,e.event_description,e.event_image,e.event_date,c.club_name FROM events e,clubs c where e.event_id={event_id} and c.club_id=e.club_id")
    event_data=cur.fetchone()
    conn.close()
    
    return render_template('events.html',events=event_data)

if __name__ == '__main__':
    app.run(debug=True)
