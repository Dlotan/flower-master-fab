from app import db, appbuilder

db.create_all()
role_admin = appbuilder.sm.find_role(appbuilder.sm.auth_role_admin)
appbuilder.sm.add_user('Dlotan', 'Admin', 'User', 'florian.groetzner@gmail.com', role_admin, 'dlotan')
