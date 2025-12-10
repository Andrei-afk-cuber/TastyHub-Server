# importing the necessary libraries
import socket
import threading
import json
import os
from typing import Optional, List
import logging

# importing my own services and schemas
from server.containers import user_service, user_schema, recipe_service

# set up logger
logging.basicConfig(level=logging.INFO, filename='server.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# server class
class DatabaseServer:
    def __init__(self, host: str ='0.0.0.0', port: int =65432) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")

    def handle_client(self, conn, addr) -> None:
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


    def process_request(self, request: dict) -> dict:
        action = request.get('action')
        if action == 'check_login':
            username = request.get('username')
            password = request.get('password')
            logging.info(f"Checking {username} and {password}")
            return self.check_login(username, password)
        elif action == 'register_user':
            username = request.get('username')
            password = request.get('password')
            logging.info(f"Registering {username} and {password}")
            return self.register_user(username, password)
        elif action == 'load_users':
            logging.info(f"Loading all users")
            return self.load_users()
        elif action == 'load_recipes':
            only_confirmed = request.get('only_confirmed', False)
            limit = request.get('limit', None)
            by_author = request.get('by_author', None)
            by_name = request.get('by_name', None)
            by_ingredients = request.get('by_ingredients', None)
            by_username = request.get('by_username', None)
            logging.info(f"Loading recipes")
            return self.load_recipes(only_confirmed, by_name, by_username, by_ingredients)
        elif action == 'activate_user':
            user_id = request.get('user_id')
            logging.info(f"Activating user by id:{user_id}")
            return self.activate_user(user_id)
        elif action == 'deactivate_user':
            user_id = request.get('user_id')
            logging.info(f"Deactivating user by id:{user_id}")
            return self.deactivate_user(user_id)
        elif action == 'confirm_recipe':
            recipe_id = request.get('recipe_id')
            logging.info(f"Confirming recipe by id:{recipe_id}")
            return self.confirm_recipe(recipe_id)
        elif action == 'delete_recipe':
            recipe_id = request.get('recipe_id')
            logging.info(f"Deleting recipe by id:{recipe_id}")
            return self.delete_recipe(recipe_id)
        elif action == 'save_recipe':
            recipe_data = request.get('recipe_data')
            logging.info(f"Saving recipe data by id:{recipe_data.get('id', None)}")
            return self.save_recipe(recipe_data)
        elif action == 'update_recipe':
            recipe_data = request.get('recipe_data')
            by_admin = request.get('by_admin', False)
            logging.info(f"Updating recipe by id:{recipe_data.get('id', None)}")
            return self.update_recipe(recipe_data, by_admin)
        elif action == 'grant_admin_privileges':
            user_id = request.get('user_id')
            logging.info(f"Granting admin's privileges by id:{user_id}")
            return self.grant_admin_privileges(user_id)
        elif action == 'delete_user':
            user_id = request.get('user_id')
            logging.info(f"Deleting user by id:{user_id}")
            return self.delete_user(user_id)
        else:
            logging.error(f"Unknown action: {action}")
            return {"status": "error", "message": "Unknown action"}

    # method for check user login
    @staticmethod
    def check_login(username: str, password: str) -> dict:
        user = user_service.get_by_username(username)
        if not user:
            logging.exception("User not found")
            return {"status": "error", "message": "User not found"}
        if user['password'] != user_service.get_password_hash(password):
            logging.exception("Wrong password")
            return {"status": "error", "message": "Incorrect password"}

        return {"status":"success", "user": user_schema.dump(user)}

    # static method for create new user
    @staticmethod
    def register_user(username: str, password: str) -> dict:
        try:
            user_service.create(user_data={'username': username, 'password': password})
            return {"status": "success", "message": "User created"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    def start(self) -> None:
        print("Server is running and waiting for connections...")
        while True:
            conn, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.start()

    # static method for load recipes
    @staticmethod
    def load_recipes(only_confirmed: bool =True, by_name: Optional[str] =None, by_username: Optional[str] =None, by_ingredients: Optional[List[str]] =None) -> dict:
        recipes = None
        try:
            if by_name:
                recipes = recipe_service.get_by_name(by_name.lower())
            elif by_ingredients:
                recipes = recipe_service.get_by_ingredients(by_ingredients)
            elif by_username:
                recipes = recipe_service.get_by_username(by_username)
            else:
                recipes = recipe_service.get_all(only_confirmed)
            return {"status": "success", "recipes": recipes}

        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def load_users() -> dict:
        users = user_service.get_all()
        if not users:
            logging.exception("No users found")
            return {"status": "error", "message": "No users found"}

        return {"status": "success", "users": users}

    # method for save recipe
    @staticmethod
    def save_recipe(recipe_data: dict) -> dict:
        try:
            recipe_service.create(recipe_data)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": "save_recipe method error: " + str(e)}

    # static method for update recipe
    @staticmethod
    def update_recipe(recipe_data: dict, by_admin: bool =False) -> dict:
        try:
            recipe_service.update(recipe_data, by_admin)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    # static method for delete recipe
    @staticmethod
    def delete_recipe(recipe_id: int) -> dict:
        try:
            recipe = recipe_service.get_one(recipe_id)

            image_path = os.path.join("recipe_images", recipe['picture_path'])
            if os.path.exists(image_path):
                os.remove(image_path)

            recipe_service.delete(recipe_id)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def activate_user(user_id: int) -> dict:
        try:
            user_service.activate(user_id)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def deactivate_user(user_id: int) -> dict:
        try:
            user_service.activate(user_id, False)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def confirm_recipe(recipe_id: int) -> dict:
        try:
            recipe_service.confirm(recipe_id)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def grant_admin_privileges(user_id: int) -> dict:
        try:
            user_service.grant_admin(user_id)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": str(e)}

    @staticmethod
    def delete_user(user_id: int) -> dict:
        try:
            user_service.delete(user_id)
            return {"status": "success"}
        except Exception as e:
            logging.exception(e)
            return {"status": "error", "message": "User not found"}

# debugger run
if __name__ == "__main__":
    print(DatabaseServer.load_recipes())