import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key = 'SecretKey'
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3308
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'tpo-python-flask'

mysql.init_app(app)

FOLDER = os.path.join('uploads')
app.config['FOLDER'] = FOLDER


@app.route('/')
def index():
    sql = "SELECT * FROM `tpo-python-flask`.`membership`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    memberships = cursor.fetchall()
    print(memberships)
    return render_template('membership/index.html', memberships=memberships)


@app.route('/create')
def create():
    return render_template('membership/create.html')


@app.route('/store', methods=['POST'])
def storage():
    _firstName = request.form['txtFirstName']
    _lastName = request.form['txtLastName']
    _dni = request.form['txtDni']
    _address = request.form['txtAddress']
    _city = request.form['txtCity']
    _country = request.form['txtCountry']
    _province = request.form['txtProvince']
    _postalCode = request.form['txtPostalCode']
    _phone = request.form['txtPhone']
    _email = request.form['txtEmail']
    _picture = request.files['txtPicture']
    _payment = request.form['radioPay']
    _privacyPolicy = 'checkPrivacyPolicy' in request.form

    if not _privacyPolicy:
        flash('Debe aceptar la política de privacidad')
        return redirect(url_for('create'))

    if _firstName == '' or _lastName == '' or _picture.filename == '' or _dni == '':
        flash('Recuerda llenar los datos de los campos que son obligatorios')
        return redirect(url_for('create'))

    now = datetime.now()
    time = now.strftime("%Y%H%M%S")
    if _picture.filename != '':
        pictureFileName = time + _picture.filename
        _picture.save("uploads/" + pictureFileName)

    data = (_firstName, _lastName, _dni, _address, _city, _country, _province, _postalCode, _phone, _email,
            pictureFileName, _payment)
    sql = "INSERT INTO `tpo-python-flask`.`membership` (`id`, `firstname`, `lastname`, `dni`, `address`, `city`," \
          " `country`, `province`, `postalcode`, `phone`, `email`, `picture`, `payment`) " \
          "VALUES (NULL, %s, %s, %s, %s, %s, %s,  %s, %s, %s,  %s, %s, %s);"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    return redirect('/')


@app.route('/destroy/<int:id>')
def destroy(id):
    sql = "DELETE FROM `tpo-python-flask`.`membership` WHERE id = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT picture FROM `tpo-python-flask`.`membership` WHERE `id` = %s;", id)
    pictureOldFileName = cursor.fetchone()
    if pictureOldFileName:
        os.remove(os.path.join(app.config['FOLDER'], pictureOldFileName[0]))

    cursor.execute(sql, id)
    conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):
    sql = "SELECT * FROM `tpo-python-flask`.`membership` WHERE id = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, id)
    membership = cursor.fetchone()
    print(membership)
    return render_template('membership/edit.html', membership=membership)


@app.route('/update', methods=['POST'])
def update():
    _firstName = request.form['txtFirstName']
    _lastName = request.form['txtLastName']
    _dni = request.form['txtDni']
    _address = request.form['txtAddress']
    _city = request.form['txtCity']
    _country = request.form['txtCountry']
    _province = request.form['txtProvince']
    _postalCode = request.form['txtPostalCode']
    _phone = request.form['txtPhone']
    _email = request.form['txtEmail']
    _picture = request.files['txtPicture']
    _payment = request.form['radioPay']
    _id = request.form['txtID']

    data = (_firstName, _lastName, _dni, _address, _city, _country, _province, _postalCode, _phone, _email,
            _payment, _id)
    sql = "UPDATE `tpo-python-flask`.`membership` SET `firstname` = %s, `lastname` = %s, `dni` = %s, \
                    `address` = %s, `city` = %s, `country` = %s, `province` = %s, `postalcode` = %s, `phone` = %s, \
                    `email` = %s, `payment` = %s WHERE `id` = %s;"
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    time = now.strftime("%Y%H%M%S")

    if _picture.filename != '':
        pictureFileName = time + _picture.filename
        _picture.save("uploads/" + pictureFileName)
        cursor.execute("SELECT picture FROM `tpo-python-flask`.`membership` WHERE `id` = %s;", _id)
        pictureOldFileName = cursor.fetchone()

        if pictureOldFileName:
            os.remove(os.path.join(app.config['FOLDER'], pictureOldFileName[0]))

        cursor.execute("UPDATE `tpo-python-flask`.`membership` SET `picture` = %s WHERE `id` = %s;",
                       (pictureFileName, _id))
        conn.commit()

    cursor.execute(sql, data)
    conn.commit()
    return redirect('/')


@app.route('/uploads/<string:pictureFileName>')
def uploads(pictureFileName):
    return send_from_directory(app.config['FOLDER'], pictureFileName)


if __name__ == '__main__':
    app.run(debug=True)
