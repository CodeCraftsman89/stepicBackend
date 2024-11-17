import random
import string
from http.client import HTTPException
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Cookie, Response
from starlette.requests import Request

from fakeDB import sample_products
from model import User, Feedback, Item, UserCreate, Login

app = FastAPI(title="Return HTML")
all_users: list[UserCreate] = []
test_user: User = User(name="John Doe", id=1)
feedbacks = []
sessions: dict = {}
text = [random.choice(string.ascii_lowercase + string.digits if i != 5 else string.ascii_uppercase) for i in range(10)]

sample_user: dict = {"username": "user123", "password": "password123"}
fake_db: list[Login] = [Login(**sample_user)]


@app.get("/", name="Возвращаем html файл")
def index():
    with open('ingex.html', 'r', encoding='utf-8') as file:
        html = file.read()
    return {"html": html}


@app.get("/users", name="Вывод каrого-то пользователя (хз кто это: name='John Doe', id=1)")
def users():
    return test_user


@app.post("/feedback", name="Вывод отзыва от пользователя")
def feedback(user_feedback: Feedback):
    feedback_message = user_feedback.message + ", " + user_feedback.name
    feedbacks.append(feedback_message)
    return {"message": f"Feedback received. Thank you, {user_feedback.name}!"}


@app.post("/craete_items/", name="Создание товаров (old)")
async def create_item(item: Item) -> Item:
    """Тут мы передали в наш обработчик Pydantic модель,
    чтобы она проверяла все запросы на соответствие этой модели
    (все поля и типы данных в них должны соответствовать модели
    """
    return item


@app.get("/return_items/", name="Вывод товаров (old)")
async def read_items() -> list[Item]:
    """ Тут мы не принимаем никаких данных, но указываем,
     что возвращаться будет список, содержащий в себе Pydantic модели"""
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]


#  Загрузка файла
@app.post("/files/", name="Ввыод размера файла")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/upload file/", name="Вывод размера файла с метадатой")
async def create_upload_file(file: UploadFile):
    return {
        "filename": file.filename,
        "filetype": file.content_type
    }


# Создание пользователя и вывод массива созданных пользователей
@app.post("/create_user", name="Создание пользователя")
async def create_user(new_user: UserCreate) -> UserCreate:
    all_users.append(new_user)
    return new_user


@app.get("/showuser", name="Все пользователи")
async def show_users() -> dict[str, list[UserCreate]]:
    return {"users": all_users}


# Поиск товаров, с помощью id, категории и слова
@app.get("/product/{product_id}", name="Поиск товаров по ID")
async def product(product_id: int):
    marketplace_product = list(filter(lambda item: product_id == item['product_id'], sample_products))
    return marketplace_product


@app.get("/products/search", name="Поиск товаров по названию и категории")
async def products_search(keyword: str, category: str = None, limit: int = 10):
    result = list(filter(lambda item: keyword.lower() in item['name'].lower(), sample_products))
    if category:
        result = list(filter(lambda item: category.lower() in item['category'].lower(), sample_products))
    return result[:limit]


# Отправка уведомлений
def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}


#  Печеньки
@app.get("/items/")
async def read_items(ads_id: str | None = Cookie(default=None)):
    return {"ads_id": ads_id}


@app.get("/last_visit")
def root(last_visit=Cookie()):
    return {"last visit": last_visit}


@app.post("/login")
def login(user_login: Login, response: Response):
    for person in fake_db:  # перебрали юзеров в нашем примере базы данных
        if person.username == user_login.username and person.password == user_login.password:

            session_token = ''.join(text)
            sessions[session_token] = user_login
            response.set_cookie(key="session_token", value=session_token, httponly=True)
            return {
                "message": "куки установлены",
                "session_token": session_token
            }
    return {"message": "Invalid username or password"}


@app.get("/user")
async def user_session(session: str, response: Response):
    # ищем в сессиях был ли такой токен создан, и если был, то возвращаем связанного с ним юзера
    user = sessions.get(session)
    if user:
        return user.dict()
    return {"message": "Unauthorized"}


@app.get("/headers")
async def get_headers(request: Request) -> dict:
    if "User-Agent" not in request.headers:
        raise HTTPException()
    if "Accept-Language" not in request.headers:
        raise HTTPException()
    return {
        "User-Agent": request.headers["user-agent"],
        "Accept-Language": request.headers["accept-language"]
            }


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
