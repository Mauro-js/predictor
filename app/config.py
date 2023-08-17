


POSTGRES = {
    'user': 'myuser',
    'pw': 'mypassword',
    'db': 'mydb',
    'host': 'localhost',
    'port': '5432',
}


SQLALCHEMY_DATABASE_URI = f"postgres://{POSTGRES['user']}:" \
                          f"{POSTGRES['pw']}@{POSTGRES['host']}:" \
                          f"{POSTGRES['port']}/{POSTGRES['db']}"