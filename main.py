from io import BytesIO
from argon2 import PasswordHasher
from flask import Flask, render_template, request, redirect,url_for,send_file,send_from_directory
import database
import mysql.connector
import smtplib
import os
import pandas
import scrape
import sys
# LIST OF WHAT ALL WE NEED
#                                            IMPORTANT logout option    
#   Download file option in search page, customer feedback page working, Career tragectory through WEBSCRAPING

#variable controling global login don't touch 
global access
access = 0
global sta
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thecodex'
ph = PasswordHasher()

mydb = mysql.connector.connect(host="localhost",user="root",password="mysql")
mycursor = mydb.cursor()

database.checkdatabase()
mycursor.execute("use studybuddy;")
database.checktables()


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods = ['POST','GET']) 
def login():
    flag = 0
    try:
        if request.method == 'POST':
            username = request.form['email']
            global user 
            user = username
            password = request.form['password']
            mycursor.execute("select * from login WHERE email_id=\""+username+"\";")
            for x in mycursor:
                if ph.verify(x[2],password):
                    print("correct")
                    global access
                    access = 1
                    global sta
                    sta = x[3]
                    user = username
                    return redirect('home')
                else:
                    print("Incorrect pass")
                    return redirect(request.url)
        if access==1:
            return redirect('home')
        else:    
            return render_template('login.html')
    except:
        return redirect('ERROR')

@app.route('/open_job_offers')
def open_job_offers():
    data1 = pandas.read_csv(r"C:\Users\Aravo\OneDrive\Desktop\website\website\Jobs.csv", nrows=13)
    data2 = pandas.read_csv(r"C:\Users\Aravo\OneDrive\Desktop\website\website\Links.csv", nrows=13)

    company = data1['company']
    joblinks = data2['joblinks']
    l = []
    for i in range(0,13):
        l.append((company[i],joblinks[i]))
        
    return render_template('open job offers.html',data=l)

@app.route('/registation', methods = ['POST','GET']) 
def registation():
    if request.method == 'POST':
        email = request.form.get('email')
        college = request.form.get('college')
        state = request.form.get('state')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if confirm_password==password:
            mycursor.execute("select * from login;")
            flag = 0
            for x in mycursor:
                if x[0]==name:
                    flag = 1
                    break
                if x[1]==email:
                    flag = 1
                    break
            if flag==0:
                password = ph.hash(password)
                mycursor.execute("insert into login values(\""+name+"\",\""+email+"\",\""+password+"\",\""+college+"\",\""+state+"\");")
                mydb.commit()
                return redirect('login')
    return render_template('registation.html')

@app.route('/home')
def home():
    mycursor.execute("select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where college like \'%"+sta+"%\';")
    d = mycursor.fetchall()
    if access!=1:
        return redirect('login')
    else:
        return render_template('home.html',data=d)

@app.route('/college', methods = ['POST','GET']) 
def college():
    if request.method == 'POST':
        if access==0:
            redirect('ERROR')
        else:    
            try:
                req = request.form.get('filename')
                genre = request.form.get('genre')
                college = request.form.get('college')
                #print("\n\n",type(req),type(genre),type(college),"\n\n")
                #print(college=="")
                data = database.search(req,genre,college)
                data2 = database.states() 
                return render_template('college.html', searchresult = data,states = data2)
            except:
                redirect('ERROR')
    return render_template('college.html')

def msg(message):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("araragikun266@gmail.com", "mprmuqkphmxfsmnh")
    s.sendmail("araragikun266@gmail.com", "araragikun266@gmail.com", message)
    s.quit()

@app.route('/contactus',  methods = ['POST','GET'])
def contactus():
    if request.method == 'POST':
        TEXT = request.form.get('subject')
        SUBJECT = request.form.get('firstname') + " " + request.form.get('lastname') 
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        msg(message)
    return render_template('contactus.html')

#app.config["FILE_UPLOADS"] = r"C:\Users\Aravo\OneDrive\Desktop\website\website\static\uploaded_files"
app.config["FILE_UPLOADS"] = os.path.dirname(__file__)+"\\static\\uploaded_files"
app.config["ALLOWED_FILE_TYPES"] = ["PDF","PNG","JPG","DOCX"]

def allowedfiles(filename):
    if not "." in filename:
        return False
    
    ext = filename.rsplit(".",1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_TYPES"]:
        return True
    else:
        return False

@app.route('/fileupload', methods = ['POST','GET'])
def fileupload():
    if request.method == 'POST':
        if request.files:
            file = request.files['file']
            genre = request.form['genre']
            if file.filename == "":
                print("Image Must have filename")
                return redirect(request.url)

            if not allowedfiles(file.filename):
                print("Not an allowed function")
                return redirect(request.url)
            path = app.config["FILE_UPLOADS"]+"\\"+user
            try:
                path1 = os.path.join(path)
                os.mkdir(path1)
            except FileExistsError:
                print("(((((")
                print(user)
            file.save(os.path.join(path, file.filename))
            database.insertfile(user,file.filename,genre)
            print("Image Saved")
            

    return render_template('fileupload.html')

@app.route('/download/<upload_id>')
def download(upload_id):
    upload = database.uploadata(upload_id)
    return send_file(BytesIO(upload[0]), download_name=upload[1],as_attachment=True)

@app.route('/view/<upload_id>')
def view(upload_id):
    if access==1:
        upload = database.view(upload_id)
    else:
        redirect('error')
    return send_from_directory(directory=app.config["FILE_UPLOADS"]+"\\"+upload[2],path=upload[1],mimetype='application/pdf')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/ERROR')
def error():
    return render_template('error.html')

@app.route('/logout')
def logout():
    global access
    access = 0
    return redirect('login')

@app.route('/cse_guide')
def cse_guide():
    return render_template('cse_guide.html')

@app.route('/civil_guide')
def civil_guide():
    return render_template('civil_guide.html')

@app.route('/ece_guide')
def ece_guide():
    return render_template('ece_guide.html')

@app.route('/mech_guide')
def mech_guide():
    return render_template('mech_guide.html')

@app.route('/eng_guide')
def eng_guide():
    return render_template('eng_guide.html')

@app.route('/hst_guide')
def hst_guide():
    return render_template('hst_guide.html')

@app.route('/soc_guide')
def soc_guide():
    return render_template('soc_guide.html')

@app.route('/ir_guide')
def ir_guide():
    return render_template('ir_guide.html')

@app.route('/ecofin_guide')
def ecofin_guide():
    return render_template('ecofin_guide.html')

@app.route('/eco_guide')
def eco_guide():
    return render_template('eco_guide.html')

@app.route('/phy_guide')
def phy_guide():
    return render_template('phy_guide.html')

@app.route('/chemistry_guide')
def chemistry_guide():
    return render_template('chemistry_guide.html')

@app.route('/math_guide')
def math_guide():
    return render_template('math_guide.html')

@app.route('/bms_guide')
def bms_guide():
    return render_template('bms_guide.html')

@app.route('/chem_guide')
def chem_guide():
    return render_template('chem_guide.html')

@app.route('/bio')
def bio():
    return render_template('biotech_guide.html')

@app.route('/Guide')
def Guide():
    return render_template('sliders.html')

@app.route('/searchJob',  methods = ['POST','GET'])
def searchJob():
    if request.method == 'POST':
        search = request.form.get('search')
        print(search)
        scrape.scrape(search)
        return redirect('open_job_offers')
    return render_template('searchbar.html')


if __name__ == '__main__':

     app.run(debug=True)
