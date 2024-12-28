import mysql.connector

def connect_to_database():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="yumshare"
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def search_recipes(ingredients=None, serving_size=None, cook_time=None):
    db = connect_to_database()
    if db is None:
        return []

    cursor = db.cursor()
    query = "SELECT id, title, ingredients, steps, image FROM recipes WHERE 1=1"
    params = []

    if ingredients:
        query += " AND ingredients LIKE %s"
        params.append(f"%{ingredients}%")
    if serving_size:
        query += " AND serving_size = %s"
        params.append(serving_size)
    if cook_time:
        query += " AND cook_time <= %s"
        params.append(cook_time)

    try:
        cursor.execute(query, tuple(params))
        recipes = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        recipes = []
    finally:
        cursor.close()
        db.close()

    return recipes