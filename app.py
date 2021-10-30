import os
import utils
import functools
import yagmail as yagmail
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask,
    render_template,
    flash,
    request,
    redirect,
    session,
    url_for,
    jsonify,
    g,
    send_file,
    make_response,
)

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def fcnindex():
    if g.user:
        rol = session.get("rol_id")
        if rol == "USUARIO":
            return redirect(url_for("fcnsessionuser"))
        else:
            return redirect(url_for("fcnsessionsuperadmin"))
    return render_template("login.html")


@app.route("/login/", methods=["GET", "POST"])
def fcnlogin():
    try:
        if request.method == "POST":
            error = None
            username = request.form["user"]
            password = request.form["password"]

            if not username:
                error = "Debes Ingresar El Usuario"
                flash(error)
                return redirect(url_for("fcnlogin"))

            if not password:
                error = "Debes Ingresar La Contraseña"
                flash(error)
                return redirect(url_for("fcnlogin"))

            db = get_db()
            cur = db.cursor()
            consulta = "SELECT u.str_nombre_usuario, e.str_nom_empleado, e.str_ape_empleado, tp.str_nom_tipo_perfil, u.str_password_usuario, u.int_cod_tipo_perfil, e.int_id_empleado FROM tbl_usuario u, tbl_empleado e, tbl_tipo_perfil tp WHERE u.str_nombre_usuario = e.str_nombre_usuario AND u.int_cod_tipo_perfil = tp.int_cod_tipo_perfil AND u.str_nombre_usuario = ?"
            cur.execute(consulta, [username])
            data = cur.fetchone()

            if data is None:
                error = "Usuario no válido"
            else:

                if check_password_hash(data[4], password):

                    session.clear()
                    session["user_id"] = data[0]
                    session["name_id"] = data[1] + " " + data[2]
                    session["rol_id"] = data[3]
                    session["id"] = data[6]

                    if data[5] == 1:

                        resp = make_response(
                            redirect(url_for("fcnsessionuser")))

                    else:

                        resp = make_response(
                            redirect(url_for("fcnsessionsuperadmin")))

                    resp.set_cookie("username", username)
                    return resp

                else:

                    error = "Contraseña no válida"

            flash(error)

        return render_template("login.html")

    except:

        return render_template("login.html")


def login_required(f):
    @functools.wraps(f)
    def decorate_view():
        if g.user is None:
            return redirect(url_for("fcnlogin"))
        return f()

    return decorate_view


@app.route("/sessionuser/", methods=["GET", "POST"])
def fcnsessionuser():
    return render_template("user.html")


@app.route("/sessionsuperadmin/", methods=["GET", "POST"])
def fcnsessionsuperadmin():
    return render_template("superadmin.html")


@app.route("/manageuser/", methods=["GET", "POST"])
def fcnmanageuser():
    return render_template("gestionar.html")


@app.route("/adduser/", methods=["GET", "POST"])
@login_required
def fcnadduser():

    if request.method == "POST":

        fname = request.form["fname"]
        fname = fname.lower()
        lname = request.form["lname"]
        lname = lname.lower()
        sexo = request.form["sexo"]
        fnacimiento = request.form["fnacimiento"]
        cargo = request.form["cargo"]
        tcontrato = request.form["tcontrato"]
        fingreso = request.form["fingreso"]
        email = request.form["email"]
        email = email.lower()
        fterminacion = request.form["fterminacion"]
        dependencia = request.form["dependencia"]
        salario = request.form["salario"]
        rol = request.form["rol"]

        error = None

        if not fname:
            error = "Debes Ingresar El Nombre"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not lname:
            error = "Debes Ingresar El Apellido"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not sexo:
            error = "Debes Escoger El Sexo"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not fnacimiento:
            error = "Debes Ingresar La Fecha de Nacimiento"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not cargo:
            error = "Debes Escoger El Cargo"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not tcontrato:
            error = "Debes Escoger El Tipo de Contrato"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not fingreso:
            error = "Debes Ingresar La Fecha de Ingreso"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not utils.isEmailValid(email):
            error = "Correo invalido"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not fterminacion:
            error = "Debes Ingresar La Fecha de Terminacion"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not dependencia:
            error = "Debes Escoger La Dependencia"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not salario:
            error = "Debes Ingresar El Salario"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        if not rol:
            error = "Debes Escoger El Rol"
            flash(error)
            return redirect(url_for("fcnregisteruser"))

        datos_user = lname + fname[0]

        db = get_db()
        cur = db.cursor()
        consulta = (
            "SELECT MAX(int_cont_usuario) FROM tbl_usuario WHERE str_datos_usuario = ?"
        )
        cur.execute(consulta, [datos_user])
        contU = cur.fetchone()[0]

        if contU is None:

            indU = 1

        else:

            indU = contU + 1

        nameuser = datos_user + str(indU)

        password_temp = generate_password_hash(nameuser)

        db = get_db()
        cur = db.cursor()
        consulta = "INSERT INTO tbl_usuario (str_nombre_usuario, str_password_usuario, int_cod_tipo_perfil, str_datos_usuario, int_cont_usuario) VALUES (?,?,?,?,?)"
        cur.execute(consulta, [nameuser, password_temp, rol, datos_user, indU])
        db.commit()

        db = get_db()
        cur = db.cursor()
        consulta = "INSERT INTO tbl_empleado (str_nom_empleado, str_ape_empleado, int_cod_tipo_sexo, date_fecha_nacimiento, int_cod_tipo_cargo, int_cod_tipo_contrato, date_fecha_ingreso, date_fecha_terminacion, str_correo_empleado, dbl_salario_empleado, str_nombre_usuario, int_cod_tipo_dependencia) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        cur.execute(
            consulta,
            [
                fname,
                lname,
                sexo,
                fnacimiento,
                cargo,
                tcontrato,
                fingreso,
                fterminacion,
                email,
                salario,
                nameuser,
                dependencia,
            ],
        )
        db.commit()

        flash("Usuario Creado Exitosamente")
        return redirect(url_for("fcnregisteruser"))

    return render_template("empleados.html")


@app.route("/dashboard/", methods=["GET", "POST"])
def fcndashboard():
    db = get_db()
    cur = db.cursor()
    consulta = "SELECT COUNT(str_nombre_usuario) FROM tbl_usuario"
    cur.execute(consulta)
    cantuser = cur.fetchone()[0]
    consulta2 = "SELECT COUNT(int_id_evaluacion) FROM tbl_evaluacion WHERE int_puntaje_evaluacion = 10"
    cur.execute(consulta2)
    estrellas = cur.fetchone()[0]
    consulta3 = "SELECT e.str_nom_empleado, e.str_ape_empleado, tc.str_nom_tipo_cargo, tp.str_nom_tipo_perfil, co.str_nom_tipo_contrato, e.str_correo_empleado, e.dbl_salario_empleado FROM tbl_empleado e, tbl_tipo_cargo tc, tbl_tipo_perfil tp, tbl_tipo_contrato co, tbl_usuario u WHERE u.str_nombre_usuario = e.str_nombre_usuario AND u.int_cod_tipo_perfil = tp.int_cod_tipo_perfil AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_contrato = co.int_cod_tipo_contrato"
    cur.execute(consulta3)
    data = cur.fetchall()

    return render_template("dashboard.html", cantuser=cantuser, estrellas = estrellas, data = data)


@app.route("/registeruser/", methods=["GET", "POST"])
@login_required
def fcnregisteruser():

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_sexo"
    cur.execute(consulta)
    sexos = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_contrato"
    cur.execute(consulta)
    contratos = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_dependencia"
    cur.execute(consulta)
    dependencias = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_cargo"
    cur.execute(consulta)
    cargos = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    rol = session.get("rol_id")

    if rol == "ADMINISTRADOR":

        consulta = "SELECT * FROM tbl_tipo_perfil WHERE int_cod_tipo_perfil <> 3"

    else:

        consulta = "SELECT * FROM tbl_tipo_perfil"

    cur.execute(consulta)
    roles = cur.fetchall()

    return render_template(
        "empleados.html",
        sexos=sexos,
        contratos=contratos,
        dependencias=dependencias,
        cargos=cargos,
        roles=roles,
    )


@app.route("/evaluationuser/", methods=["GET", "POST"])
@login_required
def fcnevaluationuser():
    return render_template("evaluacion.html")


@app.route("/registerevaluationuser/", methods=["GET", "POST"])
@login_required
def fcnregisterevaluationuser():
    if request.method == "POST":

        Id = request.form["ID"]
        fechaevaluacion = request.form["fechaevaluacion"]
        recomendaciones = request.form["recomendaciones"]
        puntaje = request.form["puntaje"]

        if not Id:
            error = "Debes Ingresar El ID"
            flash(error)
            return redirect(url_for("fcnregisterevaluationuser"))

        if not fechaevaluacion:
            error = "Debes Ingresar La Fecha de Evaluación"
            flash(error)
            return redirect(url_for("fcnregisterevaluationuser"))

        if not recomendaciones:
            error = "Debes Ingresar Las Recomendaciones"
            flash(error)
            return redirect(url_for("fcnregisterevaluationuser"))

        if not puntaje:
            error = "Debes Ingresar El Puntaje"
            flash(error)
            return redirect(url_for("fcnregisterevaluationuser"))

        db = get_db()
        cur = db.cursor()
        consulta = "SELECT * FROM tbl_empleado e WHERE int_id_empleado = ?"
        cur.execute(consulta, [Id])
        data = cur.fetchone()

        if data is None:

            flash("Usuario No Existe")
            return redirect(url_for("fcnregisterevaluationuser"))

        else:

            db = get_db()
            cur = db.cursor()
            consulta = "INSERT INTO tbl_evaluacion (date_fecha_evaluacion, int_id_empleado, str_comentario_evaluacion, int_puntaje_evaluacion) VALUES (?,?,?,?)"
            cur.execute(consulta, [fechaevaluacion,
                        Id, recomendaciones, puntaje])
            db.commit()

            flash("Evaluación Guardada Exitosamente")
            return redirect(url_for("fcnregisterevaluationuser"))

    return render_template("evaluacion.html")


@app.route("/calificationuser/<int:id>", methods=["GET", "POST"])
def fcncalificationuser(id):

    idE = id
    db = get_db()
    cur = db.cursor()
    consulta = "SELECT e.str_nom_empleado, e.str_ape_empleado, ev.int_puntaje_evaluacion, ev.date_fecha_evaluacion, ev.str_comentario_evaluacion FROM tbl_empleado e, tbl_evaluacion ev WHERE e.int_id_empleado = ev.int_id_empleado AND e.int_id_empleado = ? AND ev.date_fecha_evaluacion = (SELECT MAX(date_fecha_evaluacion) FROM tbl_evaluacion WHERE int_id_empleado = ?)"
    cur.execute(consulta, [idE, idE])
    data = cur.fetchone()

    if data is None:

        error = "Este Usuario No Ha Sido Calificado"
        flash(error)
        return redirect(url_for("fcnsessionsuperadmin"))

    return render_template("calificacion.html", data=data)


@app.route("/mycalification/", methods=["GET", "POST"])
@login_required
def fcnmycalification():

    idE = session.get("id")

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT e.str_nom_empleado, e.str_ape_empleado, ev.int_puntaje_evaluacion, ev.date_fecha_evaluacion, ev.str_comentario_evaluacion FROM tbl_empleado e, tbl_evaluacion ev WHERE e.int_id_empleado = ev.int_id_empleado AND e.int_id_empleado = ? AND ev.date_fecha_evaluacion = (SELECT MAX(date_fecha_evaluacion) FROM tbl_evaluacion WHERE int_id_empleado = ?)"
    cur.execute(consulta, [idE, idE])
    data = cur.fetchone()

    if data is None:

        error = "Este Usuario No Ha Sido Calificado"
        flash(error)
        return redirect(url_for("fcnsessionuser"))

    return render_template("calificacion.html", data=data)


@app.route("/searchuser/", methods=["GET", "POST"])
@login_required
def fcnsearchuser():
    if request.method == "POST":

        consultarpor = request.form["consultarpor"]
        searchcriterio = request.form["searchcriterio"]

        error = None

        if not searchcriterio:
            error = "Debes Ingresar El Criterio de Búsqueda"
            flash(error)
            return redirect(url_for("fcnsearchuser"))

        db = get_db()
        cur = db.cursor()

        rol = session.get("rol_id")

        if rol == "ADMINISTRADOR":

            if consultarpor == "1":

                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_usuario u, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil <> 3 AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.int_id_empleado =?"

            elif consultarpor == "2":
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_usuario u, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil <> 3 AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.str_nom_empleado =?"

            elif consultarpor == "3":
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_usuario u, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil <> 3 AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.str_ape_empleado =?"

            elif consultarpor == "4":
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_usuario u, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil <> 3 AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND tc.str_nom_tipo_cargo =?"

            else:
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_usuario u, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil <> 3 AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND td.str_nom_tipo_dependencia =?"

        else:

            if consultarpor == "1":

                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.int_id_empleado =?"

            elif consultarpor == "2":
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.str_nom_empleado =?"

            elif consultarpor == "3":
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.str_ape_empleado =?"

            elif consultarpor == "4":
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND tc.str_nom_tipo_cargo =?"

            else:
                consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, e.date_fecha_nacimiento, tc.str_nom_tipo_cargo, td.str_nom_tipo_dependencia FROM tbl_empleado e, tbl_tipo_cargo tc, tbl_tipo_dependencia td WHERE e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND td.str_nom_tipo_dependencia =?"

        cur.execute(consulta, [searchcriterio])

        data = cur.fetchall()

        if len(data) == 0:

            error = "No hay Resultado(s) para mostrar"
            flash(error)
            return render_template("gestionar.html")

        return render_template("gestionar.html", data=data)

    return render_template("gestionar.html")


@app.route("/infouser/<int:id>", methods=["GET", "POST"])
def fcninfouser(id):

    idE = id
    db = get_db()
    cur = db.cursor()
    consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, ts.str_nom_tipo_sexo, e.date_fecha_nacimiento, td.str_nom_tipo_dependencia, tc.str_nom_tipo_cargo, co.str_nom_tipo_contrato, e.date_fecha_ingreso, e.date_fecha_terminacion, e.str_correo_empleado,  e.dbl_salario_empleado, u.str_nombre_usuario, tp.str_nom_tipo_perfil FROM tbl_empleado e, tbl_usuario u, tbl_tipo_sexo ts, tbl_tipo_cargo tc, tbl_tipo_dependencia td, tbl_tipo_contrato co, tbl_tipo_perfil tp WHERE e.int_cod_tipo_sexo = ts.int_cod_tipo_sexo AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.int_cod_tipo_contrato = co.int_cod_tipo_contrato AND e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil = tp.int_cod_tipo_perfil AND e.int_id_empleado = ?"
    cur.execute(consulta, [idE])
    data = cur.fetchone()

    return render_template("infousuario.html", data=data)


@app.route("/edituser/<int:id>", methods=["GET", "POST"])
def fcnedituser(id):

    idE = id
    db = get_db()
    cur = db.cursor()
    consulta = "SELECT e.int_id_empleado, e.str_nom_empleado, e.str_ape_empleado, ts.str_nom_tipo_sexo, e.date_fecha_nacimiento, td.str_nom_tipo_dependencia, tc.str_nom_tipo_cargo, co.str_nom_tipo_contrato, e.date_fecha_ingreso, e.str_correo_empleado, e.date_fecha_terminacion, e.dbl_salario_empleado, tp.str_nom_tipo_perfil, e.int_cod_tipo_sexo, e.int_cod_tipo_dependencia, e.int_cod_tipo_cargo, e.int_cod_tipo_contrato, u.int_cod_tipo_perfil FROM tbl_empleado e, tbl_usuario u, tbl_tipo_sexo ts, tbl_tipo_cargo tc, tbl_tipo_dependencia td, tbl_tipo_contrato co, tbl_tipo_perfil tp WHERE e.int_cod_tipo_sexo = ts.int_cod_tipo_sexo AND e.int_cod_tipo_cargo = tc.int_cod_tipo_cargo AND e.int_cod_tipo_dependencia = td.int_cod_tipo_dependencia AND e.int_cod_tipo_contrato = co.int_cod_tipo_contrato AND e.str_nombre_usuario = u.str_nombre_usuario AND u.int_cod_tipo_perfil = tp.int_cod_tipo_perfil AND e.int_id_empleado = ?"
    cur.execute(consulta, [idE])
    data = cur.fetchone()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_sexo"
    cur.execute(consulta)
    sexos = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_contrato"
    cur.execute(consulta)
    contratos = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_dependencia"
    cur.execute(consulta)
    dependencias = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_cargo"
    cur.execute(consulta)
    cargos = cur.fetchall()

    db = get_db()
    cur = db.cursor()
    consulta = "SELECT * FROM tbl_tipo_perfil"
    cur.execute(consulta)
    roles = cur.fetchall()

    return render_template(
        "editarusuario.html",
        data=data,
        sexos=sexos,
        contratos=contratos,
        dependencias=dependencias,
        cargos=cargos,
        roles=roles,
    )


@app.route("/updateuser/<int:id>", methods=["POST"])
def fcnupdateuser(id):
    try:

        if request.method == "POST":

            idE = id
            fname = request.form["fname"]
            lname = request.form["lname"]
            sexo = request.form["sexo"]
            fnacimiento = request.form["fnacimiento"]
            cargo = request.form["cargo"]
            tcontrato = request.form["tcontrato"]
            fingreso = request.form["fingreso"]
            email = request.form["email"]
            fterminacion = request.form["fterminacion"]
            dependencia = request.form["dependencia"]
            salario = request.form["salario"]
            rol = request.form["rol"]

            error = None

            if not fname:
                error = "Debes Ingresar El Nombre"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not lname:
                error = "Debes Ingresar El Apellido"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not sexo:
                error = "Debes Escoger El Sexo"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not fnacimiento:
                error = "Debes Ingresar La Fecha de Nacimiento"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not cargo:
                error = "Debes Escoger El Cargo"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not tcontrato:
                error = "Debes Escoger El Tipo de Contrato"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not fingreso:
                error = "Debes Ingresar La Fecha de Ingreso"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not utils.isEmailValid(email):
                error = "Debes Ingresar El Email"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not fterminacion:
                error = "Debes Ingresar La Fecha de Terminacion"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not dependencia:
                error = "Debes Escoger La Dependencia"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not salario:
                error = "Debes Ingresar El Salario"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            if not rol:
                error = "Debes Escoger El Rol"
                flash(error)
                return redirect(url_for("fcnupdateuser"))

            db = get_db()
            cur = db.cursor()
            consulta = "UPDATE tbl_empleado SET str_nom_empleado=?, str_ape_empleado=?, int_cod_tipo_sexo=?, date_fecha_nacimiento=?, int_cod_tipo_cargo=?, int_cod_tipo_contrato=?, date_fecha_ingreso=?, date_fecha_terminacion=?, str_correo_empleado=?, dbl_salario_empleado=?, int_cod_tipo_dependencia=? WHERE int_id_empleado=?"
            cur.execute(
                consulta,
                [
                    fname,
                    lname,
                    sexo,
                    fnacimiento,
                    cargo,
                    tcontrato,
                    fingreso,
                    fterminacion,
                    email,
                    salario,
                    dependencia,
                    idE,
                ],
            )
            db.commit()

            db = get_db()
            cur = db.cursor()
            consulta = (
                "SELECT str_nombre_usuario FROM tbl_empleado WHERE int_id_empleado=?"
            )
            cur.execute(consulta, [idE])
            nameuser = cur.fetchone()[0]

            db = get_db()
            cur = db.cursor()
            consulta = "UPDATE tbl_usuario SET int_cod_tipo_perfil=? WHERE str_nombre_usuario=?"
            cur.execute(
                consulta,
                [
                    rol,
                    nameuser,
                ],
            )
            db.commit()

            flash("Empleado Actualizado Correctamente")
            return redirect(url_for("fcnmanageuser"))
    except:

        return redirect(url_for("fcnmanageuser"))


@app.route("/deleteuser/<int:id>", methods=["GET", "POST"])
def fcndeleteuser(id):
    try:

        idE = id

        db = get_db()
        cur = db.cursor()
        consulta = (
            "SELECT str_nombre_usuario FROM tbl_empleado WHERE int_id_empleado = ?"
        )
        cur.execute(consulta, [idE])
        data = cur.fetchone()[0]

        if data is None:

            flash("Empleado No Existe")
            return redirect(url_for("fcnindex"))

        else:

            user = data

            db = get_db()
            cur = db.cursor()
            consulta = "DELETE FROM tbl_evaluacion WHERE int_id_empleado = ?"
            cur.execute(consulta, [idE])
            db.commit()

            db = get_db()
            cur = db.cursor()
            consulta = "DELETE FROM tbl_empleado WHERE int_id_empleado = ?"
            cur.execute(consulta, [idE])
            db.commit()

            db = get_db()
            cur = db.cursor()
            consulta = "DELETE FROM tbl_usuario WHERE str_nombre_usuario = ?"
            cur.execute(consulta, [user])
            db.commit()

            flash("Empleado Eliminado Correctamente")

        return redirect(url_for("fcnmanageuser"))

    except:

        return redirect(url_for("fcnmanageuser"))


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db()
            .execute(
                "SELECT * FROM tbl_usuario WHERE str_nombre_usuario = ?", (
                    user_id,)
            )
            .fetchone()
        )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("fcnlogin"))


@app.route("/editpassword/", methods=["GET", "POST"])
def fcneditpassword():
    return render_template("changepassword.html")


@app.route("/updatepassword/<int:id>", methods=["POST"])
def fcnupdatepassword(id):
    if request.method == "POST":

        username = session.get("user_id")
        rol = session.get("rol_id")
        antpwd = request.form["password"]
        newpwd = request.form["passwordn1"]
        confpwd = request.form["passwordn2"]

        db = get_db()
        cur = db.cursor()
        consulta = "SELECT * FROM tbl_usuario WHERE str_nombre_usuario = ?"
        cur.execute(consulta, [username])
        data = cur.fetchone()

        if data is None:
            flash("Usuario no válido")
        else:

            if check_password_hash(data[1], antpwd):

                if newpwd == confpwd:
                    password = generate_password_hash(newpwd)
                    db = get_db()
                    cur = db.cursor()
                    consulta = "UPDATE tbl_usuario SET str_password_usuario=? WHERE str_nombre_usuario=?"
                    cur.execute(
                        consulta,
                        [
                            password,
                            username,
                        ],
                    )
                    db.commit()

                    flash("Contraseña Actualizada Correctamente")

                    if rol == "USUARIO":

                        return redirect(url_for("fcnsessionuser"))

                    else:

                        return redirect(url_for("fcnsessionsuperadmin"))

                else:

                    flash(
                        "La Nueva Contraseña y La Confirmación de La Nueva Contraseña No Coinciden"
                    )
                    return redirect(url_for("fcneditpassword"))

            flash("La Contraseña Anterior No Es Válida")
            return redirect(url_for("fcneditpassword"))

    return render_template("changepassword.html")


if __name__ == "__main__":
    app.run()
