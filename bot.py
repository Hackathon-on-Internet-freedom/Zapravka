# by krutmaster (telegram: @krutmaster1)
import telebot
import os
import configparser


def createConfig():
    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'token', '')
    config.set('Settings', 'password', '')
    config.set('Settings', 'owner_id', '')
    config.set('Settings', 'admin_id', '')
    config.add_section('List users')
    config.set('List users', 'count', '0')
    letters = {}
    config.set('List users', 'letters', str(letters))
    wait_users = {}
    config.set('List users', 'wait_users', str(wait_users))

    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def str_in_dict(dict_in_str):
    return eval(dict_in_str)


if not os.path.exists('config.ini'):
    createConfig()

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('Settings', 'token')
password = config.get('Settings', 'password')
owner_id = config.get('Settings', 'owner_id')
admin_id = config.get('Settings', 'admin_id')
count = int(config.get('List users', 'count'))
letters = str_in_dict(config.get('List users', 'letters'))
wait_users = str_in_dict(config.get('List users', 'wait_users'))
bot = telebot.TeleBot(token)


@bot.message_handler(commands=["start"])
def start(message):
    if owner_id != str(message.chat.id) and str(message.chat.id) != admin_id:
        bot.send_message(message.chat.id, 'Здравствуйте. Этот бот принимает жалобы на нарушение прав и свобод '
                                          'человека.\nКак пользоваться? Всё просто: отправляйте подряд текстовые '
                                          'сообщения, фото, видео, документы, аудио, которые составят ваше письмо '
                                          'администрации. После того, как всё отправите, нажмите на копку "send"'
                                          ' или отправьте команду /send . Вы получите индивидуальный номер письма, '
                                          'а само письмо отправится администрации.')


@bot.message_handler(commands=["setgroupowner"])
def setgroupowner(message):
    global owner_id, config

    if owner_id != str(message.chat.id):

        try:
            input_password = message.text[15:]

            if input_password == password:
                owner_id = str(message.chat.id)
                config.set('Settings', 'owner_id', owner_id)

                with open('config.ini', 'w') as config_file:
                    config.write(config_file)

                bot.reply_to(message, 'Данная группа установлена по умолчанию для отправки')
            else:
                bot.reply_to(message, 'Неправильный пароль, попробуй ещё раз')
        except:
            bot.reply_to(message, 'Команда введена неправильно, попробуйте ещё раз')


@bot.message_handler(commands=["setgroupadmin"])
def setgroupadmin(message):
    global admin_id, config

    try:

        if str(message.chat.id) != admin_id:
            input_password = message.text[15:]

            if input_password == password:
                admin_id = str(message.chat.id)
                config.set('Settings', 'admin_id', admin_id)

                with open('config.ini', 'w') as config_file:
                    config.write(config_file)

                bot.reply_to(message, 'Данная группа установлена по умолчанию для админов')
            else:
                bot.reply_to(message, 'Неправильный пароль, попробуй ещё раз')
    except:
        bot.reply_to(message, 'Команда введена неправильно, попробуйте ещё раз')


@bot.message_handler(commands=['listletters'])
def listorders(message):
    if admin_id == str(message.chat.id):
        bot.send_message(admin_id, '-------Список неотвеченных писем-------')

        for letter in letters:
            bot.send_message(admin_id, f'Письмо №{letter}')

            if letters[letter] in wait_users:
                bot.send_message(admin_id, 'Отправитель этого письма не ответил на отправленный вопрос')

        bot.send_message(admin_id, '---------------------------------------')


@bot.message_handler(commands=['send'])
def send(message):
    global config, count, wait_users

    if str(message.chat.id) != owner_id and str(message.chat.id) != admin_id\
            and not str(message.chat.id) in wait_users:
        bot.reply_to(message, 'Письмо отправляется, ждите')

        try:
            files = os.listdir(f'temp/{message.chat.id}')
            bot.send_message(owner_id, '--------------')
            count += 1
            bot.send_message(owner_id, f'Письмо №{count}')

            for name in files:
                with open(f'temp/{message.chat.id}/{name}', 'rb') as file:
                    bot.send_document(owner_id, file)

                os.remove(f'temp/{message.chat.id}/{name}')

            bot.send_message(owner_id, '--------------')
            os.rmdir(f'temp/{message.chat.id}')
            letters[count] = str(message.chat.id)
            config.set('List users', 'letters', str(letters))
            config.set('List users', 'count', str(count))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

            bot.reply_to(message, f'Успешно отправлено, ваше письмо под номером {count}.'
                                  f' Ожидайте ответа администрации (он придёт в этой же переписке)')
        except Exception:
            bot.reply_to(message, 'Ничего нет к отправке')

    elif str(message.chat.id) in wait_users:
        bot.reply_to(message, 'Ответ отправляется, ждите')

        try:
            files = os.listdir(f'temp/{message.chat.id}')
            bot.send_message(owner_id, '--------------')
            bot.send_message(owner_id, f'Дополение к письму №{wait_users[str(message.chat.id)]}')

            for name in files:
                with open(f'temp/{message.chat.id}/{name}', 'rb') as file:
                    bot.send_document(owner_id, file)

                os.remove(f'temp/{message.chat.id}/{name}')

            bot.send_message(owner_id, '--------------')
            os.rmdir(f'temp/{message.chat.id}')
            letters[count] = str(message.chat.id)
            del wait_users[str(message.chat.id)]
            config.set('List users', 'wait_users', str(wait_users))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

            bot.reply_to(message, f'Ваш ответ успешно отправлен')
        except Exception:
            bot.reply_to(message, 'Ничего нет к отправке')


@bot.message_handler(commands=['answer'])
def answer(message):

    if str(message.chat.id) == admin_id:

        try:
            letter = int(message.text.split()[1])
            answer = str(message.text.split()[2:]).replace('[', '').replace(']', '').replace(',', '').replace("'", '')
            wait_users[letters[letter]] = letter
            config.set('List users', 'wait_users', str(wait_users))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

            bot.send_message(letters[letter], f'Ответ администрации: {answer}')
            bot.reply_to(message, f'Ответ отправлен автору письма {letter}')
        except Exception:
            bot.reply_to(message, 'Такого письма нет или команда введена неправильно')


@bot.message_handler(commands=['agree'])
def agree(message):

    if str(message.chat.id) == admin_id:

        try:
            letter = int(message.text.split()[1])
            bot.send_message(letters[letter], f'Ваше письмо №{letter} одобренно администрацией,'
                                              ' следите за каналом @zapravka38\nСпасибо за помощь!')
            try:
                del wait_users[letters[letter]]
            except Exception:
                pass

            del letters[letter]
            config.set('List users', 'letters', str(letters))
            config.set('List users', 'wait_users', str(wait_users))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

            bot.reply_to(message, f'Отправитель письма №{letter} получил уведомление о согласии'
                                  f' работать с его письмом. Письмо удалено из списка неотвеченных')
        except Exception:
            bot.reply_to(message, 'Такого письма нет или команда введена неправильно')


@bot.message_handler(commands=['refuse'])
def refuse(message):
    if str(message.chat.id) == admin_id:

        try:
            letter = int(message.text.split()[1])
            bot.send_message(letters[letter], f'Ваше письмо №{letter} не прошло модерацию и не будет рассмотрено'
                                              ' на канале @zapravka38\n')

            try:
                del wait_users[letters[letter]]
            except Exception:
                pass

            del letters[letter]
            config.set('List users', 'letters', str(letters))
            config.set('List users', 'wait_users', str(wait_users))

            with open('config.ini', 'w') as config_file:
                config.write(config_file)

            bot.reply_to(message, f'Отправитель письма №{letter} получил уведомление об отказе'
                                  f' работать с его письмом. Письмо удалено из списка неотвеченных')
        except Exception:
            bot.reply_to(message, 'Такого письма нет или команда введена неправильно')

'''

'''

@bot.message_handler()
def echo(message):
    if str(message.chat.id) != owner_id and str(message.chat.id) != admin_id:

        try:

            if not os.path.exists(f'temp/{message.chat.id}'):
                os.mkdir(f'temp/{message.chat.id}')

            if not os.path.exists(f'temp/{message.chat.id}/message_from_{message.chat.id}.txt'):

                with open(f'temp/{message.chat.id}/message_from_{message.chat.id}.txt', 'w') as new_file:
                    new_file.write(f'{message.text}\n')

            else:

                with open(f'temp/{message.chat.id}/message_from_{message.chat.id}.txt', 'a') as new_file:
                    new_file.write(f'{message.text}\n')

            bot.reply_to(message, 'Сообщение сохранено. Если отправлены все файлы, нажмите кнопку "send"'
                                  ' или отправьте команду /send')
        except Exception as e:
            bot.reply_to(message, e)


@bot.message_handler(content_types=['document'])
def handle_docs(message):

    if str(message.chat.id) != owner_id and str(message.chat.id) != admin_id:

        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            if not os.path.exists(f'temp/{message.chat.id}'):
                os.mkdir(f'temp/{message.chat.id}')

            with open(f'temp/{message.chat.id}/{message.document.file_name}', 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, 'Документ сохранён. Если отправлены все файлы, нажмите кнопку "send"'
                                  ' или отправьте команду /send')
        except Exception as e:
            bot.reply_to(message, e)


@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    if str(message.chat.id) != owner_id and str(message.chat.id) != admin_id:

        try:
            file_info = bot.get_file(message.photo[1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            if not os.path.exists(f'temp/{message.chat.id}'):
                os.mkdir(f'temp/{message.chat.id}')

            with open(f'temp/{message.chat.id}/{message.photo[1].file_id}.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, 'Фото сохранёно. Если отправлены все файлы, нажмите кнопку "send"'
                                  ' или отправьте команду /send')
        except Exception as e:
            bot.reply_to(message, e)


@bot.message_handler(content_types=['video'])
def handle_video(message):

    if str(message.chat.id) != owner_id and str(message.chat.id) != admin_id:

        try:
            file_info = bot.get_file(message.video.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            if not os.path.exists(f'temp/{message.chat.id}'):
                os.mkdir(f'temp/{message.chat.id}')

            with open(f'temp/{message.chat.id}/{message.video.file_id}.mp4', 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, 'Видео сохранёно. Если отправлены все файлы, нажмите кнопку "send"'
                                  ' или отправьте команду /send')
        except Exception as e:
            bot.reply_to(message, e)


@bot.message_handler(content_types=['audio'])
def handle_audio(message):

    if str(message.chat.id) != owner_id and str(message.chat.id) != admin_id:

        try:
            file_info = bot.get_file(message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            if not os.path.exists(f'temp/{message.chat.id}'):
                os.mkdir(f'temp/{message.chat.id}')

            with open(f'temp/{message.chat.id}/{message.audio.title}.mp3', 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, 'Аудио сохранёно. Если отправлены все файлы, нажмите кнопку "send"'
                                  ' или отправьте команду /send')
        except Exception as e:
            bot.reply_to(message, e)


if __name__ == '__main__':
    bot.polling(none_stop=True)
