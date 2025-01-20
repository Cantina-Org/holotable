from cantinaUtils.verify_login import verify_login
from flask import redirect, url_for, request, render_template
from datetime import datetime


def show_modules_cogs(database):
    if verify_login(database) and verify_login(database) != 'desactivated':
        user_permission = database.select('''SELECT * from cantina_administration.permission WHERE user_token = %s''',
                                          (request.cookies.get('token')), 1)

        # On récupère les modules afin de pouvoir faire une redirection sur la page via la sidebar
        modules_info = database.select("""SELECT * FROM cantina_administration.modules""", None)

        # On récupère le thème de l'utilisateur afin de pouvoir l'afficher
        local_user_theme = database.select('''SELECT theme FROM cantina_administration.user WHERE token= %s''',
                                           (request.cookies.get('token')), 1)

        if not user_permission[23] and not user_permission[32]:  # Si l'utilisateur n'as pas la permission, redirection vers la page d'accueil
            return redirect(url_for('home'))

        if request.method == 'POST':
            database.exec('''UPDATE cantina_administration.modules SET name = %s, fqdn = %s, socket_url = %s 
            WHERE token = %s''', (request.form["module_name"], request.form["module_url"], request.form["socket_url"],
                                  request.form["token"]))

            return redirect(url_for('show_modules', module_name=request.form["module_name"]))
        else:
            if request.args.get('module_name'):
                selected_module_info = database.select('''SELECT * FROM cantina_administration.modules WHERE name = %s''',
                                              (request.args.get('module_name')), 1)

                time_diff = datetime.now() - datetime.fromtimestamp(selected_module_info[7])

                date = [datetime.fromtimestamp(selected_module_info[7]).strftime("%H:%M:%S - %d/%m/%Y"),
                        [int(time_diff.days),
                         int(time_diff.seconds // 3600),
                         int((time_diff.seconds% 3600) // 60),
                         int(time_diff.seconds % 60)
                         ]
                        ]

                return render_template('Administration/show_one_modules.html',
                                       selected_module_info=selected_module_info, modules_info=modules_info,
                                       user_permission=user_permission, local_user_theme=local_user_theme, date=date)
            else:
                modules_info = database.select('''SELECT * FROM cantina_administration.modules''', None)
            return render_template('Administration/show_modules.html', modules_info=modules_info,
                                   user_permission=user_permission, local_user_theme=local_user_theme)
    elif verify_login(database) == 'desactivated':
        return redirect(url_for('sso_login', error='2'))
    else:
        return redirect(url_for('sso_login'))
