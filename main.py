from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Cookie

from fakeDB import sample_products
from model import User, Feedback, Item, UserCreate

app = FastAPI(title="Return HTML")
all_users: list[UserCreate] = []
test_user: User = User(name="John Doe", id=1)
feedbacks = []


@app.get("/", name="Возвращаем html файл")
def index():
    with open('file.txt', 'r', encoding='utf-8') as file:
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


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
