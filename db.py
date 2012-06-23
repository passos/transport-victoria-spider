import sqlite3

conn = None
cur = None

cache_conn = None
cache_cur = None

def init():
    global conn, cur, cache_conn, cache_cur

    # initialize database connection
    conn = sqlite3.connect("transport.db")
    conn.row_factory = sqlite3.Row
    conn.text_factory = lambda x: unicode(x, 'utf-8', 'replace')
    cur = conn.cursor()

    cache_conn = sqlite3.connect("cache.db")
    cache_conn.row_factory = sqlite3.Row
    cache_conn.text_factory = lambda x: unicode(x, 'utf-8', 'replace')
    cache_cur = cache_conn.cursor()


def close():
    conn.close()


def get_param(key, default=None):
    try:
        cur.execute("SELECT value FROM params WHERE key=?;", (key,))
        row = cur.fetchone()
        if (row):
            if row[0] is None:
                return default
            else:
                return row[0]
        else:
            return default
    except:
        return default


def set_param(key, value):
    if get_param(key) is None:
        cur.execute("INSERT INTO params (key, value) VALUES(?,?)", (key, value))
    else:
        cur.execute("UPDATE params SET value=? WHERE key=?", (value, key))
    conn.commit()


def query(SQL, params=(), keyfield=None, default=None):
    return db_query(conn, SQL, params, keyfield, default)

def db_query(connection, SQL, params=(), keyfield=None, default=None):
    cursor = connection.cursor()
    try:
        cursor.execute(SQL, params)
        row = cursor.fetchone()
        if row:
            if keyfield:
                return row[keyfield]
            else:
                return row[0]
        else:
            return default
    except:
        return default


def update_table(table, key, value, **fields):
    update_table_with_dict(table, key, value, fields)

def update_table_with_dict(table, key, value, fields):
    db_update_table_with_dict(conn, table, key, value, fields)


def db_update_table(connection, table, key, value, **fields):
    return db_update_table_with_dict(connection, table, key, value, fields)

def db_update_table_with_dict(connection, table, key, value, fields):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM %s WHERE %s=?" % (table, key), (value,))
    row = cursor.fetchone()

    if row:
        SQL = "UPDATE %s SET %s=?" % (table, key)
        params = [value]

        for k,v in fields.items():
            SQL += ", %s=?" % k
            params.append(v)

        SQL += " WHERE %s=? " % key
        params.append(value)
    else:
        SQL = "INSERT INTO %s (" % (table,) + ', '.join([key] + fields.keys())
        SQL += ") VALUES (?" + ', ?' * len(fields) + ")"
        params = [value] + [fields[k] for k in fields.keys()]

#     print '--', SQL
#     print '  ', params
#     print

    cursor.execute(SQL, tuple(params))
    connection.commit()


def cache_put(key, value, **params):
    params.update({'value': value})

    db_update_table_with_dict(cache_conn, 'cache', 'key', key, params)

def cache_get(key):
    return db_query(cache_conn, "SELECT value FROM cache WHERE key=?", (key,))

def cache_del(key, delete=False):
    if delete:
        cache_cur.execute("DELETE cache WHERE key=?", (key,))
    else:
        cache_cur.execute("UPDATE cache SET done='T' WHERE key=?", (key,))
    cache_conn.commit()











