from logging import error

from flask import request, render_template, redirect, url_for
from Utils.email_utils import send_verification_email
from Utils.verify_login import verify_login


def email_verif_cogs(database):
    # Verification si l'utilisateur est connecté
    if not verify_login(database):
        return redirect(url_for('sso_login', error='0'))
    elif verify_login(database) == 'desactivated':  # Si l'utilisateur est connecté mais que son compte est désactivé
        login_url = database.select('''SELECT fqdn FROM cantina_administration.modules WHERE name = 'Olympe' ''', None,
                                    number_of_data=1)[0]
        return redirect(login_url+'/sso/login/?error=2')

    # On récupère les permissions de l'utilisateurs
    user_permission = database.select('''SELECT * from cantina_administration.permission WHERE user_token = %s''',
                                      (request.cookies.get('token')), 1)

    # On récupère les modules afin de pouvoir faire une redirection sur la page via la sidebar
    modules_info = database.select("""SELECT * FROM cantina_administration.modules""", None)

    # On récupère le thème de l'utilisateur afin de pouvoir l'afficher
    local_user_theme = database.select('''SELECT theme FROM cantina_administration.user WHERE token= %s''',
                                       (request.cookies.get('token')), 1)

    if request.method == 'POST':  # Si l'utilisateur envoie le formulaire
        code = request.form['mail-code']  # Récupération du code du formulaire.

        if code == database.select(
                '''SELECT email_verification_code FROM cantina_administration.user WHERE token = %s''',
                (request.cookies.get('token')), number_of_data=1)[0]:  # Si le code est bon
            # Sauvegarde de la confirmation dans la base de données
            database.exec('''UPDATE cantina_administration.user SET email_verification_code = %s, email_verified = 1 
            WHERE token = %s''', ('checked', request.cookies.get('token')))
            return redirect(url_for('home'))
        else:  # Sinon redirection vers la page de verification avec une erreur.
            return render_template('User/email-verif.html', error=1, user_permission=user_permission, modules_info=modules_info, local_user_theme=local_user_theme)

    elif request.method == 'GET':  # Si l'utilisateur visite juste la page
        email = send_verification_email(database)  # Envoie du mail avec le code
        if email == "success":
            return render_template('User/email-verif.html', error=0, user_permission=user_permission, modules_info=modules_info, local_user_theme=local_user_theme)
        elif email.startswith("error1"):
            return render_template('User/email-verif.html', error=2, user_permission=user_permission, modules_info=modules_info, local_user_theme=local_user_theme)
        elif email.startswith("error2"):
            return render_template('User/email-verif.html', error=3, user_permission=user_permission, modules_info=modules_info, local_user_theme=local_user_theme)
        elif email == "already_check":
            return redirect(url_for("home"))
