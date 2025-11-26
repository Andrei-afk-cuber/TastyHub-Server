import socket
import sqlite3
import threading
import json
import os
import base64
from uuid import uuid4

from server.containers import user_service, user_schema, recipe_service, recipes_schema, recipe_schema

# server class
class DatabaseServer:
    def __init__(self, host='0.0.0.0', port=65432):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")

    # method for create database
    def setup_database(self):
        pass

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
            return self.load_recipes(only_confirmed, by_name, by_ingredients)
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

    # method for check user login
    @staticmethod
    def check_login(username: str, password: str) -> dict:
        user = user_service.get_by_username(username)
        if not user:
            return {"status": "error", "message": "User not found"}
        if user['password'] != user_service.get_password_hash(password):
            return {"status": "error", "message": "Incorrect password"}

        return user_schema.dump(user)

    # static method for create new user
    @staticmethod
    def register_user(username: str, password: str) -> dict:
        try:
            user_service.create(user_data={'username': username, 'password': password})
            return {"status": "success", "message": "User created"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start(self):
        self.setup_database()
        print("Server is running and waiting for connections...")
        while True:
            conn, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    # static method for load recipes
    @staticmethod
    def load_recipes(only_confirmed=True, by_name=None, by_ingredients=None):      # update this method finally
        recipes = None

        if by_name:
            recipes = recipe_service.get_by_name(by_name.lower())
        elif by_ingredients:
            recipes = recipe_service.get_by_ingredients(by_ingredients)
        else:
            recipes = recipe_service.get_all(only_confirmed)

        # check: is recipes empty?
        if not recipes:
            return {"status": "error", "message": "No recipes found"}

        return {"status": "success", "recipes": recipes}

    @staticmethod
    def load_users():
        users = user_service.get_all()
        if not users:
            return {"status": "error", "message": "No users found"}

        return {"status": "success", "users": users}

    # method for save recipe
    @staticmethod
    def save_recipe(recipe_data):
        try:
            recipe_service.create(recipe_data)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # static method for update recipe
    @staticmethod
    def update_recipe(recipe_data, by_admin=False):
        try:
            recipe_service.update(recipe_data, by_admin)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # static method for delete recipe
    @staticmethod
    def delete_recipe(recipe_id):
        try:
            recipe = recipe_service.get_one(recipe_id)

            image_path = os.path.join("recipe_images", recipe['picture_path'])
            if os.path.exists(image_path):
                os.remove(image_path)

            recipe_service.delete(recipe_id)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def activate_user(user_id):
        try:
            user_service.activate(user_id)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def deactivate_user(user_id):
        try:
            user_service.activate(user_id, False)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def confirm_recipe(recipe_id):
        try:
            recipe_service.confirm(recipe_id)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def grant_admin_privileges(user_id):
        try:
            user_service.grant_admin(user_id)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def delete_user(user_id: int) -> dict:
        try:
            user_service.delete(user_id)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": "User not found"}

# debugger run
if __name__ == "__main__":
    print(DatabaseServer.grant_admin_privileges(6))
    print(*DatabaseServer.load_users()['users'], sep="\n")