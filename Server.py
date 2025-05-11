import socket
import sqlite3
import threading
import json
import os
import base64
from uuid import uuid4

class DatabaseServer:
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")

    def setup_database(self):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            admin INTEGER NOT NULL DEFAULT 0,
            authorized INTEGER NOT NULL DEFAULT 0
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_name TEXT NOT NULL,
            recipe_name TEXT NOT NULL,
            description TEXT NOT NULL,
            cooking_time INTEGER NOT NULL,
            products TEXT NOT NULL,
            picture_path TEXT NOT NULL,
            confirmed INTEGER NOT NULL DEFAULT 0
        )
        """)
        db.commit()
        db.close()

    def handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        try:
            data = ""
            while True:
                chunk = conn.recv(4096).decode('utf-8')
                if not chunk:
                    print(f"No more data from {addr}")
                    break
                data += chunk
                print(f"Received chunk of size {len(chunk)} from {addr}")
                if data.endswith('}'):
                    break
            if data:
                try:
                    request = json.loads(data)
                    response = self.process_request(request)
                    response_data = json.dumps(response).encode('utf-8')
                    conn.sendall(response_data)
                except json.JSONDecodeError as e:
                    conn.sendall(json.dumps({"status": "error", "message": f"Invalid JSON: {str(e)}"}).encode('utf-8'))
            else:
                print(f"No data received from {addr}")
        except ConnectionResetError:
            print(f"Client {addr} disconnected unexpectedly")
        except ConnectionAbortedError as e:
            print(f"Connection aborted with {addr}: {e}")
        finally:
            conn.close()
            print(f"Connection with {addr} closed")

    def process_request(self, request):
        action = request.get('action')
        if action == 'check_login':
            username = request.get('username')
            password = request.get('password')
            return self.check_login(username, password)
        elif action == 'register_user':
            username = request.get('username')
            password = request.get('password')
            return self.register_user(username, password)
        elif action == 'load_users':
            return self.load_users()
        elif action == 'load_recipes':
            only_confirmed = request.get('only_confirmed', False)
            limit = request.get('limit', None)
            by_author = request.get('by_author', None)
            by_name = request.get('by_name', None)
            by_ingredients = request.get('by_ingredients', None)
            return self.load_recipes(only_confirmed, limit, by_author, by_name, by_ingredients)
        elif action == 'activate_user':
            user_id = request.get('user_id')
            return self.activate_user(user_id)
        elif action == 'deactivate_user':
            user_id = request.get('user_id')
            return self.deactivate_user(user_id)
        elif action == 'confirm_recipe':
            recipe_id = request.get('recipe_id')
            return self.confirm_recipe(recipe_id)
        elif action == 'delete_recipe':
            recipe_id = request.get('recipe_id')
            return self.delete_recipe(recipe_id)
        elif action == 'save_recipe':
            recipe_data = request.get('recipe_data')
            return self.save_recipe(recipe_data)
        elif action == 'update_recipe':
            recipe_data = request.get('recipe_data')
            by_admin = request.get('by_admin', False)
            return self.update_recipe(recipe_data, by_admin)
        elif action == 'grant_admin_privileges':
            user_id = request.get('user_id')
            return self.grant_admin_privileges(user_id)
        elif action == 'delete_user':
            user_id = request.get('user_id')
            return self.delete_user(user_id)
        else:
            return {"status": "error", "message": "Unknown action"}

    def check_login(self, username, password):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            result = cursor.fetchone()
            if result:
                return {
                    "status": "success",
                    "user": {
                        "id": result[0],
                        "username": result[1],
                        "password": result[2],
                        "admin": bool(result[3]),
                        "authorized": bool(result[4])
                    }
                }
            else:
                return {"status": "error", "message": "Invalid credentials"}
        except sqlite3.Error as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def register_user(self, username, password):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, admin, authorized) VALUES (?, ?, ?, ?)",
                           (username, password, False, False))
            db.commit()
            return {"status": "success"}
        except sqlite3.IntegrityError:
            return {"status": "error", "message": "Username already exists"}
        except sqlite3.Error as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def start(self):
        self.setup_database()
        print("Server is running and waiting for connections...")
        while True:
            conn, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    def load_recipes(self, only_confirmed=True, limit=None, by_author=None, by_name=None, by_ingredients=None):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        recipes = []
        try:
            query = "SELECT * FROM recipes"
            params = []
            conditions = []
            if only_confirmed:
                conditions.append("confirmed = 1")
            if by_author:
                conditions.append("author_name = ?")
                params.append(by_author)
            if by_name:
                conditions.append("recipe_name LIKE ?")
                params.append(f"%{by_name}%")
            if by_ingredients:
                ingredients = [i.strip() for i in by_ingredients.split(",")]
                ing_conditions = []
                for ingredient in ingredients:
                    ing_conditions.append("products LIKE ?")
                    params.append(f"%{ingredient}%")
                conditions.append(f"({' AND '.join(ing_conditions)})")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                image_data = None
                image_path = os.path.join("recipe_images", row_dict['picture_path'])
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        image_data = base64.b64encode(img_file.read()).decode('utf-8')
                recipes.append({
                    "id": row_dict["id"],
                    "author_name": row_dict['author_name'],
                    "recipe_name": row_dict['recipe_name'],
                    "description": row_dict['description'],
                    "cooking_time": row_dict['cooking_time'],
                    "products": row_dict['products'],
                    "picture_path": row_dict['picture_path'],
                    "confirmed": bool(row_dict['confirmed']),
                    "image_data": image_data
                })
            return {"status": "success", "recipes": recipes}
        except sqlite3.Error as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def load_users(self):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        users = []
        try:
            cursor.execute("SELECT * FROM users")
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                users.append({
                    "id": row_dict["id"],
                    "username": row_dict['username'],
                    "password": row_dict['password'],
                    "admin": bool(row_dict['admin']),
                    "authorized": bool(row_dict['authorized'])
                })
            return {"status": "success", "users": users}
        except sqlite3.Error as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def save_recipe(self, recipe_data):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            if not all(key in recipe_data for key in ['image_name', 'image_data']):
                return {"status": "error", "message": "Missing image data"}
            os.makedirs("recipe_images", exist_ok=True)
            image_data = base64.b64decode(recipe_data['image_data'])
            ext = os.path.splitext(recipe_data['image_name'])[1]
            unique_filename = f"{uuid4().hex}{ext}"
            image_path = os.path.join("recipe_images", unique_filename)
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)
            cursor.execute("""
                INSERT INTO recipes (
                    author_name, recipe_name, description, 
                    cooking_time, products, picture_path, confirmed
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                recipe_data['author_name'],
                recipe_data['recipe_name'],
                recipe_data['description'],
                recipe_data['cooking_time'],
                recipe_data['products'],
                unique_filename,
                int(recipe_data.get('confirmed', False))
            ))
            db.commit()
            return {
                "status": "success",
                "recipe_id": cursor.lastrowid,
                "message": "Recipe saved successfully"
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": f"Error saving recipe: {str(e)}"
            }
        finally:
            db.close()

    def update_recipe(self, recipe_data, by_admin=False):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            recipe_id = recipe_data['id']
            if recipe_data['image_data']:
                old_image = os.path.join("recipe_images", recipe_data['old_image'])
                if os.path.exists(old_image):
                    os.remove(old_image)
                image_data = base64.b64decode(recipe_data['image_data'])
                ext = os.path.splitext(recipe_data['image_name'])[1]
                unique_filename = f"{uuid4().hex}{ext}"
                new_image_path = os.path.join("recipe_images", unique_filename)
                with open(new_image_path, 'wb') as img_file:
                    img_file.write(image_data)
            else:
                unique_filename = recipe_data['old_image']
            cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            cursor.execute("""
                INSERT INTO recipes (
                    id, author_name, recipe_name, description, 
                    cooking_time, products, picture_path, confirmed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                recipe_id,
                recipe_data['author_name'],
                recipe_data['recipe_name'],
                recipe_data['description'],
                recipe_data['cooking_time'],
                recipe_data['products'],
                unique_filename,
                int(by_admin)
            ))
            db.commit()
            return {"status": "success"}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def delete_recipe(self, recipe_id):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("SELECT picture_path FROM recipes WHERE id = ?", (recipe_id,))
            result = cursor.fetchone()
            if result:
                image_path = os.path.join("recipe_images", result[0])
                if os.path.exists(image_path):
                    os.remove(image_path)
            cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            db.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def activate_user(self, user_id):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE users SET authorized = 1 WHERE id = ?", (user_id,))
            db.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def deactivate_user(self, user_id):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE users SET authorized = 0 WHERE id = ?", (user_id,))
            db.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def confirm_recipe(self, recipe_id):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE recipes SET confirmed = 1 WHERE id = ?", (recipe_id,))
            db.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def grant_admin_privileges(self, user_id):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("UPDATE users SET admin = 1, authorized = 1 WHERE id = ?", (user_id,))
            db.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def delete_user(self, user_id):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            db.commit()
            return {"status": "success"}
        except sqlite3.Error as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

if __name__ == "__main__":
    server = DatabaseServer()
    server.start()