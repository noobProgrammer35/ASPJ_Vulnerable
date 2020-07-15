#this flask version is vulnerable CVE
from flask import jsonify,request,flash,Flask,render_template,redirect,session,url_for
from Form import RegisterForm, LoginForm
import mysql_connect
from mysql import connector
import datetime
import os
import requests
from flask_mail import Mail,Message
import logging
import smtplib
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler
from sqlalchemy import and_, or_, not_
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a'
app.config['UPLOAD_FOLDER'] = 'static\\upload'
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'piethonlee123@gmail.com'
# app.config['MAIL_PASSWORD'] = 'ASPJPYTHON123'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

db = mysql_connect.read_config_file()

with app.app_context():
    import AdminModel
    AdminModel.database.create_all()



@app.route('/')
def home_page():
    test = request.args.get('username')
    r = request.cookies.get('session')
    return render_template('index.html',test=test,r = r)

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        username = form.username.data
        fname = form.fname.data
        lname = form.lname.data
        contact = form.contact.data
        email = form.email.data
        password = form.confirm.data
        answer = request.form['answer']
        #open connection
        conn = connector.MySQLConnection(**db)
        mycursor = conn.cursor()
        #senstive data exposure
        insert_tuple = (username,fname,lname,contact,email,form.password.data,'vulnerable',0,answer)
        sql = "SELECT username,email FROM users WHERE username='"+username +"'or email ='"+email+"'"
        mycursor.execute(sql)
        result = mycursor.fetchall()
        for x,y in result:
            print(x)
        row = mycursor.rowcount
        print(row)
        if row == 0:
            sql = "INSERT INTO users (username,fname,lname,contact,email,password_hash,password_salt,verified,security_qns) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            mycursor.execute(sql,insert_tuple)
            sql = "SELECT userid from users where username ='"+username+"'"
            mycursor.execute(sql)
            userid = mycursor.fetchone()
            print(userid[0])
            sql = 'INSERT into acc_vul (uid) values(%s)'
            mycursor.execute(sql,(userid[0],))
            conn.commit()

            app.logger.info('{0} Registered successfully'.format(username))
            return redirect(url_for('login'))
        else:
            flash('account existed')
            return redirect(url_for('register'))
    else:
        print(form.errors)
    return render_template('register.html',form=form), 200


@app.route('/login',methods=['POST','GET'])
def login():
    errors = 'dddd'
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = connector.MySQLConnection(**db)
        mycursor = conn.cursor()
        # vulnerable code

        sql = "SELECT * FROM users WHERE username='" + username + "' AND password_hash='" + password + "'"
        mycursor.execute(sql)
        account = mycursor.fetchone()
        # conn.commit()
        if account:
            session['logged'] = True
            session['userid'] = account[0]
            session['username'] = account[1]
            session['fname'] = account[2]
            session['lname'] = account[3]
            session['contact'] = account[4]
            session['email'] = account[5]
            session['password_hash'] = account[6]
            print(request.cookies.get('session'))

            app.logger.info('{0} Login success'.format(username))

            return redirect(url_for('home_page',username=username,s = request.cookies.get('session')))
        else:
            return redirect(url_for('login',errors=errors))


    print(errors)

    return render_template('login.html',errors=errors)


@app.route('/logout',methods=['POST',"GET"])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile/<username>/<session>')
def profile(username,session):
    conn = connector.MySQLConnection(**db)
    mycursor = conn.cursor()
    sql = 'SELECT*FROM users WHERE username="'+username+'"'
    mycursor.execute(sql)
    acc = mycursor.fetchone()
    print(acc[0])
    conn.close()
    mycursor.close()
    return render_template('profile.html',account=acc,r =session)


@app.route('/profile/<username>/account/<session>')
def account(username,session):
    conn = connector.MySQLConnection(**db)
    mycursor = conn.cursor()
    sql = 'SELECT*FROM users u INNER JOIN acc_vul a ON u.userid=a.uid WHERE username="' + username + '"'
    mycursor.execute(sql)
    acc = mycursor.fetchone()
    print(acc[0])
    return render_template('account.html',account=acc,r = session)

@app.route('/profile/<username>/account/update/<session>', methods=['POST','GET'])
def accountUpdate(username,session):
    if request.method == 'POST':
        print('dadada')
        address = request.form['address']
        credit_card = request.form['creditcard']
        payment_method = request.form['paymentmethod']
        conn = connector.MySQLConnection(**db)
        mycursor = conn.cursor()
        sql = 'SELECT userid FROM users u INNER JOIN acc_vul a ON u.userid=a.uid WHERE username="' + username + '"'
        mycursor.execute(sql)
        userid = mycursor.fetchone()
        sql = 'UPDATE acc_vul SET address="'+address+'", credit_card ="'+credit_card+'",payment_method="'+payment_method+'" WHERE uid=%s'
        mycursor.execute(sql,(userid[0],))
        conn.commit()
        return redirect(url_for('account',username=username,r=session))
    return render_template('accountUpdate.html' ,username = username)

@app.route('/reset',methods=['POST',"GET"])
def reset():
    if request.method == 'POST':
        username = request.form['username']
        conn = connector.MySQLConnection(**db)
        mycursor = conn.cursor()
        sql = 'SELECT username FROM users where username ="'+username+'"'
        mycursor.execute(sql)
        username = mycursor.fetchone()
        conn.commit()
        if username:
            session['username'] = username
            return redirect(url_for('reset_email'))
    return render_template('reset.html')

@app.route('/reset_email',methods=['POST','GET'])
def reset_email():
    if session.get('username'):
        username = session['username']
        if request.method == 'POST':
            conn = connector.MySQLConnection(**db)
            mycursor = conn.cursor()
            sql = 'SELECT security_qns FROM users where username ="' + username[0] + '"'
            mycursor.execute(sql)
            sec = mycursor.fetchone()
            conn.commit()
            a = request.form['answer']
            if a == sec[0]:
                return redirect(url_for('reset_password'))
        return render_template('reset_email.html')

@app.route('/reset_password',methods=['POST','GET'])
def reset_password():
    if request.method=='POST':
        username = session['username']
        p = request.form['password']
        conn = connector.MySQLConnection(**db)
        mycursor = conn.cursor()
        sql = 'UPDATE users SET password_hash="'+p+'" where username ="'+username[0]+'"'
        mycursor.execute(sql)
        conn.commit()
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/test')
def test():

    return render_template('test.html')


@app.route('/email_send',methods=['POST'])
def email_send():
    if request.method == 'POST':
        sender = request.form['email']
        message = request.form['message']
        subject = request.form['subject']
        to = 'henryboey39@gmail.com'
        Name = request.form['Name']
        # msg = MIMEText(message)
        # msg['Subject'] = subject
        # msg['From'] = sender
        # msg['To'] = 'piethonlee123@gmail.com'
        # msg.add_header('reply-to',sender)
        msg=''
        msg +='To: henryboey39@gmail.com'+'\n'
        msg+='Reply-to: '+sender+'\n'
        msg+="From: "+sender+"\n"
        msg+="Subject: "+subject +"\n"
        msg +="\n"
        msg += message
        send_email(sender,msg)
        return redirect(url_for('login'))

def send_email(sender,template):
    smtpObj = smtplib.SMTP('smtp.gmail.com',587)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.ehlo()
    smtpObj.login('piethonlee123@gmail.com','ASPJPYTHON123')
    smtpObj.sendmail(sender,'henryboey39@gmail.com',template)
    smtpObj.quit()

    # mail = Mail(app)
    # msg = Message(
    #     subject,
    #     recipients=['henryboey39@gmail.com'],
    #     body=template,
    #     sender=name,
    #     reply_to=sender
    # )
    # mail.send(msg)


@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['Name']
        description = request.form['Description']
        stock = request.form['stock']
        price = request.form['price']
        Image = request.files['Image']
        Image2 = request.files['Image2']
        #check weather image or not
        path = os.path.join(app.config['UPLOAD_FOLDER'], Image.filename)
        path2 = os.path.join(app.config['UPLOAD_FOLDER'], Image2.filename)
        p = Image.save(path)
        p2 = Image2.save(path2)
        product = AdminModel.Product(name,description,stock,price,Image.filename,Image2.filename)
        AdminModel.database.session.add(product)
        AdminModel.database.session.commit()
        # try:
        #     AdminModel.database.session.add(product)
        #     AdminModel.database.session.commit()
        # except:
        #     AdminModel.database.session.rollback()

        return redirect(url_for('admin'))

@app.route('/catalog')
def catalog():
    products = AdminModel.database.session.query(AdminModel.Product).all()
    return render_template('shop.html',products=products,itemCount=len(products))


@app.route('/catalog/<productid>' , methods=['POST','GET'])
def single_product_detail(productid):
    product = AdminModel.Product.query.filter_by(productid=productid).first()
    if request.method == 'POST':
        userid = session['userid']
        quantity = request.form['quantity']
        try:
            conn = connector.MySQLConnection(**db)
            cursor = conn.cursor(buffered=True)
            sql = 'select userid,productid from cart where userid = %s' % (userid)
            cursor.execute(sql)
            exist = cursor.fetchone()
            print(exist)
            if exist != None:
                if exist[1] == productid:
                    sql = 'Update cart set quantity="' + quantity + '" WHERE userid="' + userid + '" AND productid="' + productid + '"'
                    cursor.execute(sql)
            else:
                print('d')
                cursor.execute("INSERT INTO cart (userid,productid,quantity) VALUES (%s,%s,%s)",(userid, productid, quantity))
            conn.commit()
            return redirect(url_for('catalog'))
        except connector.Error as errors:
            print(errors)
    return render_template('single_product_details.html',product=product)

@app.route('/search',methods=['POST'])
def search():
    if request.method == 'POST':
        query = request.form['search']

        return redirect(url_for('search_result',query=query))

@app.route('/result')
def search_result():
    query = request.args.get('query')
    search = "%{}%".format(query)
    result = AdminModel.database.session.query(AdminModel.Product).filter(or_(AdminModel.Product.Name.ilike(search), AdminModel.Product.Description.ilike(search))).all()
    print(result)
    return render_template('search.html',product=result,itemCount=len(result),query=query)

@app.route('/cart',methods=['GET','POST'])
def cart():
    conn = connector.MySQLConnection(**db)
    cursor = conn.cursor(buffered=True)
    sql = 'SELECT Name,Description,price,Image,quantity,p.productid from products p inner join cart c ON c.productid = p.productid INNER JOIN users u  ON u.userid =c.userid where u.userid=%s' % (session['userid'])
    cursor.execute(sql)
    product = cursor.fetchall()
    print(product)
    sql = 'SELECT sum(price*quantity) from products p inner join cart c ON c.productid = p.productid INNER JOIN users u  ON u.userid =c.userid where u.userid=%s' % (session['userid'])
    cursor.execute(sql)
    totalPrice = cursor.fetchone()
    print(totalPrice)
    conn.commit()

    return render_template('cart.html',product=product,totalPrice=totalPrice)

@app.route('/updateCart/<productid>',methods=['POST','GET'])
def updateCart(productid):
    if request.method == 'POST':
        q = request.form['quantity']
        userid = session['userid']
        conn = connector.MySQLConnection(**db)
        sql = 'Update cart set quantity=%s WHERE userid=%s AND productid=%s' % (q,userid,productid)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return redirect(url_for('cart'))

@app.route('/deleteCart/<productid>',methods=['POST',"GET"])
def deleteCart(productid):
    if request.method == 'POST':
        userid = session['userid']
        conn = connector.MySQLConnection(**db)
        sql = 'DELETE FROM cart  WHERE userid=%s AND productid=%s' % (userid, productid)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return redirect(url_for('cart'))

if __name__ == '__main__':
    #vulnerable to javascript maniuplation, consider as security misconfiguation?
    app.config.update(
        SESSION_COOKIE_HTTPONLY = False,
        SESSION_COOKIE_SAMESITE=None
    )
    logging.basicConfig(level=logging.DEBUG)
    file_handler = RotatingFileHandler('logging.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    # file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    app.run(debug=True,port=5002)