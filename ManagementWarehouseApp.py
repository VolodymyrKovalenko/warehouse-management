from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

from forms import LoginForm, RegisterForm, ReceiptForm, NewTypeForm
from management_warehouseDB import User, Application_receipt, Complect, Type, Sort, Manufacturer, Sklad

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)


@app.route('/SignUp', methods=['GET', 'POST'])
def registration():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        login = form.login.data
        password = sha256_crypt.encrypt(str(form.password.data))
        email = form.email.data
        username = form.username.data

        admin = User(login, password, email, username)
        db.session.add(admin)
        db.session.commit()
        session['curent_user'] = admin.login

        return redirect(url_for('main_page'))
    return render_template('registration.html', form=form)


@app.route('/LogIn', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_form = request.form['login']
        password_form_candidate = request.form['password']
        user = User.query.filter_by(login=login_form).first()
        session['curent_user'] = user.login

        if sha256_crypt.verify(password_form_candidate, user.password):
            if user.login == 'Admin99':
                return redirect(url_for('AdminPage'))
            return redirect(url_for('main_page'))
    return render_template('singIn.html')


@app.route('/')
def start_page():
    session.clear()
    return render_template('startPage.html')


@app.route('/main', methods=['GET', 'POST'])
def main_page():
    conn = db.engine.connect()

    sesion_user_login = session['curent_user']  # counterpart for session
    curent_id = User.query.filter(User.login == sesion_user_login).first()
    curent_id = curent_id.id

    join_table = db.session \
        .query(Application_receipt, Complect, Manufacturer, Sort, Type) \
        .filter(Application_receipt.provider_id == curent_id) \
        .join(Complect) \
        .filter(Application_receipt.complect_id == Complect.id) \
        .join(Manufacturer) \
        .filter(Complect.manufacturer_id == Manufacturer.id) \
        .join(Sort) \
        .filter(Complect.sort_id == Sort.id) \
        .join(Type) \
        .filter(Sort.types_id == Type.id)

    conn.close()

    return render_template('mainPage.html', curent_user=sesion_user_login
                           , second_table=join_table
                           )


@app.route('/receipt', methods=['GET', 'POST'])
def receipt_application():
    form = ReceiptForm(request.form)
    conn = db.engine.connect()
    session_user_login = session['curent_user']

    types_names = db.session.query(Type)
    sort_names = db.session.query(Sort)

    if request.method == 'POST' and form.validate():

        id_type = request.form['typ']
        type_price = Type.query.filter_by(id=id_type).first().price
        name_sort = request.form['sort']

        manufacture_name = form.manufacturer.data
        if db.session.query(Manufacturer).filter_by(name=manufacture_name).scalar() == None:
            brand_app = Manufacturer(manufacture_name)
            db.session.add(brand_app)
        db.session.commit()

        complect_sort_id = db.session.query(Sort.id).filter_by(name=name_sort)
        complect_manufacture_id = db.session.query(Manufacturer.id).filter_by(name=manufacture_name)

        complect_app = Complect(complect_sort_id, complect_manufacture_id)
        db.session.add(complect_app)
        db.session.commit()

        app_complect_id = conn.execute('select id from complect order by id desc limit 1')
        app_complect_id = app_complect_id.fetchone()
        app_complect_id = app_complect_id[0]
        app_quantity = form.quantity.data
        app_date_adoption = form.date_adoption.data
        app_date_issue = form.date_issue.data
        app_provider_id = User.query.filter_by(login=session_user_login).first().id
        app_price = app_quantity * type_price
        app_confirmed = False

        # date_adoption = now().format('YYYY-MM-DD')
        receipt_app = Application_receipt(app_complect_id, app_quantity, app_date_adoption, app_date_issue,
                                          app_provider_id, app_price, app_confirmed)
        db.session.add(receipt_app)
        db.session.commit()
        conn.close()

        return redirect(url_for('main_page'))

    return render_template('applicationForReceipt.html', form=form, TypeHtml=types_names, sort_html=sort_names)


@app.route('/admin', methods=['GET', 'POST'])
def AdminPage():
    conn = db.engine.connect()
    join_table_admin = db.session \
        .query(Application_receipt, Complect, Manufacturer, Sort, Type, User) \
        .join(Complect) \
        .filter(Application_receipt.complect_id == Complect.id) \
        .join(Manufacturer) \
        .filter(Complect.manufacturer_id == Manufacturer.id) \
        .join(Sort) \
        .filter(Complect.sort_id == Sort.id) \
        .join(Type) \
        .filter(Sort.types_id == Type.id) \
        .join(User) \
        .filter(Application_receipt.provider_id == User.id)

    conn.close()

    if request.method == 'POST':
        conn = db.engine.connect()
        app_id = request.form['but1']
        app_id = app_id[7:]
        # confirmed_button = Application_receipt(confirmed=True)
        # print(confirmed_button)
        db.session.query(Application_receipt).filter(Application_receipt.id == app_id). \
            update({'confirmed': True})
        db.session.commit()
        sklad_application_id = app_id
        sklad_issued = False
        sklad_appl = Sklad(sklad_application_id, sklad_issued)
        db.session.add(sklad_appl)
        db.session.commit()
        conn.close()

        return redirect(url_for('AdminPage'))

    return render_template('adminPage.html', admin_table=join_table_admin)


@app.route('/adminIssue', methods=['GET', 'POST'])
def IssuedPage():
    conn = db.engine.connect()
    join_table_admin = db.session \
        .query(Application_receipt, Complect, Manufacturer, Sort, Type, User, Sklad) \
        .join(Complect) \
        .filter(Application_receipt.complect_id == Complect.id) \
        .join(Manufacturer) \
        .filter(Complect.manufacturer_id == Manufacturer.id) \
        .join(Sort) \
        .filter(Complect.sort_id == Sort.id) \
        .join(Type) \
        .filter(Sort.types_id == Type.id) \
        .join(User) \
        .filter(Application_receipt.provider_id == User.id) \
        .filter(Application_receipt.confirmed == True) \
        .join(Sklad) \
        .filter(Application_receipt.id == Sklad.application_id)

    conn.close()

    if request.method == 'POST':
        conn = db.engine.connect()
        app_id = request.form['but2']
        app_id = app_id[10:]
        print(app_id)
        db.session.query(Sklad).filter(Sklad.application_id == app_id). \
            update({'issued': True})
        db.session.commit()
        conn.close()
        return redirect(url_for('IssuedPage'))

    return render_template('IssuedPage.html', admin_table=join_table_admin)


@app.route('/newType', methods=['GET', 'POST'])
def TypePage():
    form = NewTypeForm(request.form)
    conn = db.engine.connect()
    if request.method == 'POST' and form.validate():
        type_name = form.type.data
        type_price = form.price.data

        if db.session.query(Type).filter_by(name= type_name).scalar() == None:

            type_db = Type(type_name,type_price)
            db.session.add(type_db)
            db.session.commit()

        sort_name = form.sort.data
        if db.session.query(Sort).filter_by(name=sort_name).scalar() == None:

            types_id = db.session.query(Type.id).filter_by(name=type_name)
            sort_db = Sort(sort_name,types_id)
            db.session.add(sort_db)
            db.session.commit()
        conn.close()
        return redirect(url_for('AdminPage'))
    return render_template('AddNewType.html')


# @app.route('/handler1',methods=['POST'])
# def AjaxCategory():
#     id_category = request.form['categor']
#     return json.dumps({'status': 'OK','brand': id_category})

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True, port=12345, use_reloader=True)
