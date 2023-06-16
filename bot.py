import os;
import telebot;
from dotenv import load_dotenv;
import markup as nav
from peewee import *

# python-dotenv library is used for saving telegram token so it will not leak to network
load_dotenv()
db = SqliteDatabase('db.sqlite3')


state_storage=StateMemoryStorage()
bot = telebot.TeleBot(os.getenv("TOKEN"))

class DbOperatorPoll(Model):
    chat_id = IntegerField(primary_key=True)
    zero = CharField(NULL = True)
    operator = CharField(NULL = True)
    rings = CharField(NULL = True)
    rings_time = CharField(NULL = True)
    network = CharField(NULL = True)
    price = CharField(NULL = True)
    
    class Meta:
        database = db
    
    def into_operatorpoll(self) -> OperatorPoll:
        op = OperatorPoll(self.zero)
        op.operator = self.operator
        op.rings = self.rings
        op.rings_time = self.rings_time
        op.network = self.network
        op.price = self.price
        return op


class UsersDict(dict):
    def __getitem__(self, __key: int) -> DbOperatorPoll:
        return DbOperatorPoll.get(DbOperatorPoll.chat_id == __key)
    
    def __setitem__(self, __key: int, __value: DbOperatorPoll) -> None:
        DbOperatorPoll.get_or_create(
            chat_id=__key,
            zero=__value.zero,
            operator=__value.operator,
            rings=__value.rings,
            rings_time=__value.rings_time,
            network=__value.network,
            price=__value.price,
        )

user_dict = {}

# States group.
class OperatorPoll:
    def __init__(self, zero): 
        self.zero = zero
        self.operator = None
        self.rings = None
        self.rings_time = None
        self.network = None
        self.price = None
    
    def into_dboperatorpoll(self, chat_id: int) -> DbOperatorPoll:
        DbOperatorPoll(
            chat_id = chat_id,
            zero = self.zero,
            operator = self.operator,
            rings = self.rings,
            rings_time = self.rings_time,
            network = self.network,
            price = self.price,
)


@bot.message_handler(commands=['life'])
def life(message):
    bot.register_next_step_handler(message, zero_q)
    bot.send_message(message.chat.id, text="Розпочнімо опитування. Питання №0: Яким оператором ви користуєтесь?🤔", reply_markup=nav.zero)


def zero_q(message):
    zero = message.text
    user = OperatorPoll(zero)
    chat_id = message.chat.id
    user_dict[chat_id] = user
    if message.text not in ["Lifecell"]:
        bot.send_message(message.chat.id, text="Ми радимо вам перейти на тарифи від Lifecell😊")
    else:
        bot.send_message(message.chat.id, text="Ми раді, що ви довіряєте нам❤️. Продовжимо опитування, щоб підібрати для вас найкращий тариф")
    bot.send_message(message.chat.id, text="Питання №1.  Чи часто вам потрібно дзвонити на номери інших операторів?📞", reply_markup=nav.operator)
    bot.register_next_step_handler(message, operator_q)


def operator_q(message):
    if message.text == "Назад":
        bot.send_message(message.chat.id, text="Питання №0: Яким оператором ви користуєтесь?🤔", reply_markup=nav.zero)
        bot.register_next_step_handler(message, zero_q)
    elif message.text not in nav.operator_buttons:
        bot.send_message(message.chat.id, text="Перепрошую👻. Я приймаю відповіді тільки такими, якими вони є на кнопках. Використовуйте їх для спілкування зі мною")
        bot.send_message(message.chat.id, text="Питання №1.  Чи часто вам потрібно дзвонити на номери інших операторів?📞", reply_markup=nav.operator)
        bot.register_next_step_handler(message, operator_q)
    else:
        chat_id = message.chat.id
        user_dict[chat_id].operator = message.text
        bot.send_message(message.chat.id, text="Питання №2. Як часто ви дзвоните?📞 \n1. Кілька разів на місяць. \n2. Раз в тиждень. \n3. Кілька разів на тиждень. \n4. Кілька разів на день)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, ring_q)


def ring_q(message):
    if message.text == "Назад":
        bot.send_message(message.chat.id, text="Питання №1.  Чи часто вам потрібно дзвонити на номери інших операторів?📞", reply_markup=nav.operator)
        bot.register_next_step_handler(message, operator_q)
    elif message.text not in nav.rings_buttons:
        bot.send_message(message.chat.id, text="Перепрошую👻. Я приймаю відповіді тільки такими, якими вони є на кнопках. Використовуйте їх для спілкування зі мною")
        bot.send_message(message.chat.id, text="Питання №2. Як часто ви дзвоните?📞 \n1. Кілька разів на місяць. \n2. Раз в тиждень. \n3. Кілька разів на тиждень. \n4. Кілька разів на день)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, ring_q)
    else:
        chat_id = message.chat.id
        user_dict[chat_id].rings = message.text
        bot.send_message(message.chat.id, text="Питання №3. Скільки часу тривають дзвінки?⏱ \n1.До трьох хвилин \n2. Десять хвилин \n3. Півгодини. \n4. Не кладу слухавку)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, ring_time)


def ring_time(message):
    if message.text == "Назад":
        bot.send_message(message.chat.id, text="Питання №2. Як часто ви дзвоните?📞 \n1. Кілька разів на місяць. \n2. Раз в тиждень. \n3. Кілька разів на тиждень. \n4. Кілька разів на день)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, ring_q)
    elif message.text not in nav.rings_buttons:
        bot.send_message(message.chat.id, text="Перепрошую👻. Я приймаю відповіді тільки такими, якими вони є на кнопках. Використовуйте їх для спілкування зі мною")
        bot.send_message(message.chat.id, text="Питання №3. Скільки часу тривають дзвінки?⏱ \n1.До трьох хвилин \n2. Десять хвилин \n3. Півгодини. \n4. Не кладу слухавку)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, ring_time)
    else:
        chat_id = message.chat.id
        user_dict[chat_id].rings_time = message.text
        bot.send_message(message.chat.id, text="Питання №4. Як ви використовуєте мобільні дані?📱 \n1. Месенджері \n2. Дивлюсь відео, фільми. \n3. Роздаю на комп'ютер \n4.Тримаю ботоферму)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, network)


def network(message):
    if message.text == "Назад":
        bot.send_message(message.chat.id, text="Питання №3. Скільки часу тривають дзвінки?⏱ \n1.До трьох хвилин \n2. Десять хвилин \n3. Півгодини. \n4. Не кладу слухавку)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, ring_time)
    elif message.text not in nav.rings_buttons:
        bot.send_message(message.chat.id, text="Перепрошую👻. Я приймаю відповіді тільки такими, якими вони є на кнопках. Використовуйте їх для спілкування зі мною")
        bot.send_message(message.chat.id, text="Питання №4. Як ви використовуєте мобільні дані?📱 \n1. Месенджері \n2. Дивлюсь відео, фільми. \n3. Роздаю на комп'ютер \n4.Тримаю ботоферму)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, network)
    else:
        chat_id = message.chat.id
        user_dict[chat_id].network = message.text
        bot.send_message(message.chat.id, text="Питання №5. Скільки ви готові витратити на послуги мобільного зв'язку?💸 \n1. До 200 грн \n2. 200-400 грн \n3. Стільки, скільки потрібно буде для моїх потреб", reply_markup=nav.price)
        bot.register_next_step_handler(message, price)


def price(message):
    if message.text == "Назад":
        bot.send_message(message.chat.id, text="Питання №4. Як ви використовуєте мобільні дані?📱 \n1. Месенджері \n2. Дивлюсь відео, фільми. \n3. Роздаю на комп'ютер \n4.Тримаю ботоферму)", reply_markup=nav.rings)
        bot.register_next_step_handler(message, network)
        
    elif message.text not in nav.price_buttons:
        bot.send_message(message.chat.id, text="Перепрошую👻. Я приймаю відповіді тільки такими, якими вони є на кнопках. Використовуйте їх для спілкування зі мною")
        bot.send_message(message.chat.id, text="Питання №5. Скільки ви готові витратити на послуги мобільного зв'язку?💸 \n1. До 200 грн \n2. 200-400 грн \n3. Стільки, скільки потрібно буде для моїх потреб", reply_markup=nav.price)
        bot.register_next_step_handler(message, price)
        
    else:
        chat_id = message.chat.id
        user_dict[chat_id].price = message.text
        bot.send_message(message.chat.id, text="Секундочку. Підбираємо тариф, який вам ідеально пасуватиме")
        calculation_result = calculation
        bot.send_message(chat_id, text=f'Вам найкраще підійде: {calculation_result}')


def calculation(chat_id):
    userpoll = user_dict[chat_id]
    userpoll.network
    userpoll.rings_time
    userpoll.rings
    userpoll.price
    userpoll.user
    school = "Шкільний - 150 грн - 7 ГБ - безлім на лайф"
    simple = "Просто - 160 - 8 ГБ - 300 хв"
    smart = "Смарт - 225 - 25 ГБ - 800 хв"
    free = "Вільний 325 - безліміт - 1600 хв"
    platium = "Платинум - 450 грн - безлім - 3000 хв, безлім на лайф"


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text='👋Вітаємо в телеграм боті. Для подальшого використання бота пропишіть команду "/help" ')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, text="""Отже, ось що я вмію:
    /help -- ця команда перекине вас сюди. Тут ви можете дізнатись про мої функції;
    /life -- ця команда розпочне опитування, яке допоможе визначити, який тариф вам підійде
    /support -- """)
    

@bot.message_handler(content_types=['text'])
def text_handler(chat_id):
    bot.send_message(chat_id, text='Будь ласка виберіть один з варіантів')


bot.polling(none_stop=True, interval=0.5)