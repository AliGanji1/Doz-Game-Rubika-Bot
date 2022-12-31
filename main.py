from pyrubi import Bot_async, Tools
from json import load, dump
from time import time

# Author : Ali Ganji zadeh
# Rubika : @Persian_PyThon
# Copyright (C) 2023 Ali Ganji zadeh (MIT License)

auth = 'kjdiwjlfgolkoreijkfepkllkgkor'
bot = Bot_async(auth)

async def read_data():
    with open('data.json', 'r') as read:
        return load(read)

async def write_data(data):
    with open('data.json', 'w') as write:
        return dump(data, write, indent = 4)

class Doz:
    def __init__(self, data):
        self.m = Tools.message(data)
        self.msg = data
        del data

    async def start_game(self):
        data = await read_data()
        if not self.m.chat_id() in data.keys():
            data[self.m.chat_id()] = {
                'name': self.m.chat_title(),
                'status': True,
                'timer': time(),
                'players': {
                    self.m.author_id(): {
                        'name': self.m.author_title(),
                        'turn_status': True,
                        'piece': '❌'
                    }
                }
            }
        else:
            if not data[self.m.chat_id()]['status']:
                if data[self.m.chat_id()]['timer'] < time():
                    data[self.m.chat_id()]['status'] = True
                    data[self.m.chat_id()]['players'] = {
                        self.m.author_id(): {
                            'name': self.m.author_title(),
                            'turn_status': True,
                            'piece': '❌'
                        }
                    }
                else:
                    remaining = str(data[self.m.chat_id()]['timer'] - time()).split('.')[0]
                    return await bot.reply(self.msg, f'امکان ایجاد بازی تا {remaining} ثانیه دیگر امکان پذیر نیست !')
            else:
                return await bot.reply(self.msg, 'یک بازی در حال اجرا است لطفا تا پایان آن صبر کنید !')
        await write_data(data)
        text = 'بازی ایجاد شد ❗\n\n کاربران با ارسال دستور\n /join\n می توانند در بازی شرکت کنند.'
        await bot.reply(self.msg, text)

    async def save_player2_info(self):
        try:
            data = await read_data()
            if data[self.m.chat_id()]['status']:
                if not self.m.author_id() in data[self.m.chat_id()]['players'].keys():
                    if len(data[self.m.chat_id()]['players']) < 2:
                        data[self.m.chat_id()]['players'][self.m.author_id()] = {
                            'name': self.m.author_title(),
                            'turn_status': False,
                            'piece': '⭕'
                        }
                        await write_data(data)
                        await self.send_game_table()
                    else:
                        await bot.reply(self.msg, 'ظرفیت بازیکنان پر است !')
                else:
                    await bot.reply(self.msg, 'شما قبلا وارد بازی شده اید !')
            else:
                await bot.reply(self.msg, 'هیچ بازی در حال اجرا نیست !')
        except KeyError:
            await bot.reply(self.msg, 'هیچ بازی در حال اجرا نیست !')

    async def send_game_table(self):
        data = await read_data()
        players = []
        for i in data[self.m.chat_id()]['players'].keys():
            players.append(data[self.m.chat_id()]['players'][i]['name'])
        msg = f'بازی شروع شد ❗\n\nبازیکنان: {players[0]}, {players[1]}\nاکنون نوبت {players[0]} است.'
        game_table = '├  ①  ┼  ②  ┼  ③  ┤\n\n├  ④  ┼  ⑤  ┼  ⑥  ┤\n\n├  ⑦  ┼  ⑧  ┼  ⑨  ┤'
        await bot.reply(self.msg, msg)
        await bot.send_text(self.m.chat_id(), game_table)

    async def turn(self):
        try:
            data = await read_data()
            if data[self.m.chat_id()]['status']:
                if self.m.author_id() in data[self.m.chat_id()]['players'].keys():
                    if self.m.reply_to_message_id() != 'None':
                        game_table = (await bot.get_messages_info(self.m.chat_id(), [self.m.reply_to_message_id()]))['text']
                        if '├' in game_table:
                            for i in [('1', '①'),('2', '②'),('3', '③'),('4', '④'),('5', '⑤'),('6', '⑥'),('7', '⑦'),('8', '⑧'),('9', '⑨')]:
                                if self.m.text() == i[0]:
                                    if data[self.m.chat_id()]['players'][self.m.author_id()]['turn_status']:
                                        game_table = game_table.replace(i[1], data[self.m.chat_id()]['players'][self.m.author_id()]['piece'])
                                        for p in data[self.m.chat_id()]['players'].keys():
                                            turn_status = data[self.m.chat_id()]['players'][p]['turn_status']
                                            if turn_status:
                                                data[self.m.chat_id()]['players'][p]['turn_status'] = False
                                            else: 
                                                data[self.m.chat_id()]['players'][p]['turn_status'] = True
                                        await bot.reply(self.msg, game_table)
                                        break
                                    else:
                                        await bot.reply(self.msg, 'نوبت شما نیست !')
                                else:
                                    continue
                            await write_data(data)
                            await self.check_result(game_table)
                        else:
                            await bot.reply(self.msg, 'این جدول بازی نیست !')
                    else:
                        await bot.reply(self.msg, 'روی جدول بازی ریپلای کنید !')
                else:
                    await bot.reply(self.msg, 'شما جزو شرکت کنندگان بازی نیستید !')
            else:   
                await bot.reply(self.msg, 'هیچ بازی در حال اجرا نیست !')
        except KeyError:print('Error')

    async def check_result(self, game_table):
        data = await read_data()
        for p in data[self.m.chat_id()]['players'].keys():
            piece = data[self.m.chat_id()]['players'][p]['piece']
            piece = [piece, piece ,piece]
            name = data[self.m.chat_id()]['players'][p]['name']
            if piece == [game_table[3], game_table[9], game_table[15]]:
                return await self.send_result(name)
            elif piece == [game_table[24], game_table[30], game_table[36]]:
                return await self.send_result(name)
            elif piece == [game_table[45], game_table[51], game_table[57]]:
                return await self.send_result(name)
            elif piece == [game_table[3], game_table[24], game_table[45]]:
                return await self.send_result(name)
            elif piece == [game_table[9], game_table[30], game_table[51]]:
                return await self.send_result(name)
            elif piece == [game_table[15], game_table[36], game_table[57]]:
                return await self.send_result(name)
            elif piece == [game_table[3], game_table[30], game_table[57]]:
                return await self.send_result(name)
            elif piece == [game_table[15], game_table[30], game_table[45]]:
                return await self.send_result(name)
            else:
                continue
        return False

    async def send_result(self, name):
        data = await read_data()
        text = f'بازیکن {name} برنده شد !'
        data[self.m.chat_id()]['status'] = False
        data[self.m.chat_id()]['timer'] = time() + 300
        data[self.m.chat_id()]['players'] = None
        await write_data(data)
        await bot.send_text(self.m.chat_id(), text)
                    
@bot.on_message
async def update(msg):
    m = Tools.message(msg)
    d = Doz(msg)
    print(m.text())
    if m.text() in ['/doz', '/Doz', 'doz', 'Doz', 'دوز']:
        await d.start_game()
    if m.text() in ['/join', '/Join', 'join', 'Join', 'جوین']:
        await d.save_player2_info()
    for n in range(10):
        if m.text() == str(n):
            await d.turn()