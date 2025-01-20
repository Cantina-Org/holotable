from Utils.Administration.User.create_user import create_user
from Utils.verify_login import verify_login
from flask import redirect, url_for, request, render_template


def add_user_cogs(database):
    # Vérification de si l'utilisateur est bien connecté et n'a pas un compte désactivé
    if verify_login(database) and verify_login(database) != 'desactivated':
        # On récupère les modules afin de pouvoir faire une redirection sur la page via la sidebar
        modules_info = database.select("""SELECT * FROM cantina_administration.modules""", None)

        # On récupère le thème de l'utilisateur afin de pouvoir l'afficher
        local_user_theme = database.select('''SELECT theme FROM cantina_administration.user WHERE token= %s''',
                                           (request.cookies.get('token')), 1)

        # On récupère les permission de l'utilisateur afin de pouvoir afficher les options qui correspondent
        local_user_permission = database.select('''SELECT * FROM cantina_administration.permission 
                    WHERE user_token = %s''', (request.cookies.get('token')), 1)

        if not local_user_permission[19] and not local_user_permission[32]:
            return redirect(url_for("home"))

        if request.method == 'POST':  # Si il fait une requete de type POST
            _create_user = create_user(database)  # Création de l'utilisateur
            return redirect(url_for('show_user', user_token=_create_user))
        elif request.method == 'GET':  # Si il fait une requete de type GET
            return render_template('Administration/add_user.html', modules_info=modules_info, local_user_theme=local_user_theme, user_permission=local_user_permission)

    elif verify_login(database) == "desactivated":
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
