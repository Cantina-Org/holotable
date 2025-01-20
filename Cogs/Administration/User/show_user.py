from os import path, remove
from Utils.verify_login import verify_login
from flask import request, render_template, redirect, url_for
from werkzeug.exceptions import BadRequestKeyError
from argon2 import PasswordHasher, exceptions
from werkzeug.utils import secure_filename


def show_user_cogs(database, upload_path):
    # Vérification de si l'utilisateur est bien connecté et n'a pas un compte désactivé
    if verify_login(database) and verify_login(database) != "desactivated":
        if request.method == 'GET':  # Si il fait une requete de type GET
            # On récupère les modules afin de pouvoir faire une redirection sur la page via la sidebar
            modules_info = database.select("""SELECT * FROM cantina_administration.modules""", None)

            # On récupère le thème de l'utilisateur afin de pouvoir l'afficher
            local_user_theme = database.select('''SELECT theme FROM cantina_administration.user WHERE token= %s''',
                                                (request.cookies.get('token')), 1)

            # On récupère les permission de l'utilisateur afin de pouvoir afficher les options qui correspondent
            local_user_permission = database.select('''SELECT * FROM cantina_administration.permission 
            WHERE user_token = %s''', (request.cookies.get('token')), 1)

            # Si l'utilisateur n'a pas les permissions, redirection vers la page d'accueil
            if not local_user_permission[9] and not  local_user_permission[32]:
                return redirect(url_for('home'))

            # Si l'utilisateur souhaite voir un utilisateur en particulier
            if request.args.get('user_token'):
                # Sélectionne les données et permissions de l'utilisateur souhaité
                selected_user_data = database.select('SELECT * FROM cantina_administration.user WHERE token = %s',
                                            (request.args.get('user_token')), number_of_data=1)
                selected_user_permission = database.select_dict('''SELECT * FROM cantina_administration.permission WHERE 
                user_token = %s''', (request.args.get('user_token')), number_of_data=1)

                return render_template('Administration/show_user.html',
                                       multiple_user_info=None,
                                       user_permission=local_user_permission,
                                       local_user_theme=local_user_theme,
                                       selected_user_info=selected_user_data,
                                       selected_user_permission=selected_user_permission,
                                       modules_info=modules_info)

            else:  # Sinon
                # On séléctionne toute la base de données
                users_data = database.select('SELECT * FROM cantina_administration.user', None)
                return render_template('Administration/show_user.html',
                                       multiple_user_info=users_data,
                                       user_permission=local_user_permission,
                                       local_user_theme=local_user_theme,
                                       selected_user_info=None,
                                       selected_user_permission=None,
                                       modules_info=modules_info)

        # Si l'utilisateur fait une requete POST
        elif request.method == 'POST':
            # On séléctionne toute les infos de l'utilisateur
            user_information = database.select("""SELECT * FROM cantina_administration.user WHERE token = %s""",
                                               (request.form['token']), 1)
            try:
                # On vérifie si le username a changé
                if request.form['username'] != user_information[2]:
                    # Modification de l'username
                    database.exec('''UPDATE cantina_administration.user SET username = %s WHERE token = %s''',
                                  (request.form['username'], request.cookies.get('token')))
            except BadRequestKeyError:
                pass  # Permission refusé

            # On regarde si le mot de passe correspond déjà au Hash qui est dans la base de données,
            try:
                if PasswordHasher().verify(user_information[3], request.form['password1']):
                    pass  # Le MDP ne change pas

            # Le mot de passe ne correspond pas au Hash de la base de données
            except exceptions.VerifyMismatchError:
                if request.form['password1'] != '' and request.form['password1'] == request.form['password2']:
                    # Modification du MDP après vérification que les deux entrées sont strictement égal et pas vides
                    database.exec('''UPDATE cantina_administration.user SET password = %s WHERE token = %s''',
                                  (PasswordHasher().hash(password=request.form['password1']),
                                   request.form['token']))
                else:
                    pass  # L'entrée est vide
            except BadRequestKeyError:
                pass  # Permission refusé

            try:
                if request.form['email'] != user_information[4]:
                    # TODO faire l'algo qui envoie un nouveau code.
                    # Modification de l'email. Modification du code de verif & email_verified mis sur 0 car plus vérifié
                    database.exec('''UPDATE cantina_administration.user SET email = %s, email_verification_code = %s, 
                    email_verified = 0 WHERE token = %s''',
                                  (request.form['email'], 'reset', request.form['token']))
            except BadRequestKeyError:
                pass  # Permission refusé

            try:
                if request.form['theme'] != user_information[13]:
                    # Modification du theme si il est différent de celui déjà mis.
                    database.exec('''UPDATE cantina_administration.user SET theme = %s WHERE token = %s''',
                                  (request.form['theme'], request.form['token']))
            except BadRequestKeyError:
                pass  # Permission refusé

            # On vérifie si une photo de profile a été envoyé
            if 'profile_picture' in request.files:
                profile_picture = request.files['profile_picture']  # Récupération de la photo
                if profile_picture.filename != '':
                    # Supression des autres photos de profile
                    for extension in ['png', 'jpg', 'jpeg', 'heic']:
                        filepath = path.join(upload_path, f"{request.form['token']}.{extension}")
                        if path.exists(filepath):
                            remove(filepath)

                    # Sauvegarde de la photo
                    profile_picture.save(path.join(upload_path, secure_filename(request.form['token']) + '.' +
                                                   profile_picture.filename.rsplit('.', 1)[1].lower()))
                    # Modification dans la base de données pour pouvoir utiliser la photo.
                    database.exec('''UPDATE cantina_administration.user SET picture = 1 WHERE token = %s''',
                                  (request.form['token']))

            return redirect(url_for('show_user', user_token=request.form['token']))
        # Si l'utilisateur utilise un autre moyen d'acceder à la page, un easter egg apparait
        else:
            return redirect('https://i.pinimg.com/originals/cd/0d/76/cd0d7619041d1f141d3e6fea29bb2724.jpg')
    elif verify_login(database) == "desactivated":
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
