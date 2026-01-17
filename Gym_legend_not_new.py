```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gym Legend - Игровой бот для ВК
Полная версия с административной системой, системой силы и бизнесами
"""

import json
import time
import re
import sqlite3
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==============================
# КОНСТАНТЫ ГАНТЕЛЕЙ (20 УРОВНЕЙ)
# ==============================

DUMBBELL_LEVELS = {
    1: {"name": "Гантеля 1кг", "price": 0, "weight": "1кг", "income_per_use": 1, "power_per_use": 1},
    2: {"name": "Гантеля 2кг", "price": 10, "weight": "2кг", "income_per_use": 2, "power_per_use": 2},
    3: {"name": "Гантеля 3кг", "price": 25, "weight": "3кг", "income_per_use": 3, "power_per_use": 3},
    4: {"name": "Гантеля 4кг", "price": 50, "weight": "4кг", "income_per_use": 4, "power_per_use": 4},
    5: {"name": "Гантеля 5кг", "price": 100, "weight": "5кг", "income_per_use": 5, "power_per_use": 5},
    6: {"name": "Гантеля 6кг", "price": 150, "weight": "6кг", "income_per_use": 6, "power_per_use": 6},
    7: {"name": "Гантеля 7кг", "price": 175, "weight": "7кг", "income_per_use": 7, "power_per_use": 7},
    8: {"name": "Гантеля 8кг", "price": 200, "weight": "8кг", "income_per_use": 8, "power_per_use": 8},
    9: {"name": "Гантеля 9кг", "price": 215, "weight": "9кг", "income_per_use": 9, "power_per_use": 9},
    10: {"name": "Гантеля 10кг", "price": 250, "weight": "10кг", "income_per_use": 10, "power_per_use": 10},
    11: {"name": "Гантеля 11кг", "price": 275, "weight": "11кг", "income_per_use": 11, "power_per_use": 11},
    12: {"name": "Гантеля 12.5кг", "price": 325, "weight": "12.5кг", "income_per_use": 15, "power_per_use": 12},
    13: {"name": "Гантеля 15кг", "price": 400, "weight": "15кг", "income_per_use": 20, "power_per_use": 15},
    14: {"name": "Гантеля 17.5кг", "price": 475, "weight": "17.5кг", "income_per_use": 25, "power_per_use": 17},
    15: {"name": "Гантеля 20кг", "price": 550, "weight": "20кг", "income_per_use": 30, "power_per_use": 20},
    16: {"name": "Гантеля 22,5кг", "price": 650, "weight": "22,5кг", "income_per_use": 35, "power_per_use": 22},
    17: {"name": "Гантеля 25кг", "price": 750, "weight": "25кг", "income_per_use": 40, "power_per_use": 25},
    18: {"name": "Гантеля 27,5кг", "price": 850, "weight": "27,5кг", "income_per_use": 45, "power_per_use": 27},
    19: {"name": "Гантеля 30кг", "price": 1000, "weight": "30кг", "income_per_use": 50, "power_per_use": 30},
    20: {"name": "Гантеля 35кг", "price": 1100, "weight": "35кг", "income_per_use": 55, "power_per_use": 35}
}

# ==============================
# БИЗНЕС КОНСТАНТЫ
# ==============================

BUSINESSES = {
    1: {
        "name": "Fitness зал",
        "base_price": 150,
        "base_income": 5,
        "upgrade_price": 50,
        "income_increase": 5,
        "currency": "монет",
        "upgrade_currency": "монет",
        "upgrades": {
            1: {"name": "Улучшить освещение", "emoji": "🏢"},
            2: {"name": "Улучшить интерьер", "emoji": "🎨"},
            3: {"name": "Улучшить тренажёры", "emoji": "🏋️‍♂️"},
            4: {"name": "Улучшить грифы", "emoji": "⚙️"},
            5: {"name": "Улучшить персонал", "emoji": "👥"}
        }
    },
    2: {
        "name": "🏰 Элитный fitness клуб",
        "base_price": 35000,
        "base_income": 100,
        "upgrade_price": 500,
        "income_increase": 50,
        "currency": "монет",
        "upgrade_currency": "монет",
        "upgrades": {
            1: {"name": "Улучшить системы климат-контроля", "emoji": "🏢"},
            2: {"name": "Улучшить VIP зоны отдыха", "emoji": "🎨"},
            3: {"name": "Улучшить элитные тренажёры", "emoji": "🏋️‍♂️"},
            4: {"name": "Улучшить профессиональные штанги", "emoji": "⚙️"},
            5: {"name": "Улучшить тренерский состав", "emoji": "👥"}
        }
    },
    3: {
        "name": "👑 Сеть элитных fitness клубов",
        "base_price": 55000,
        "base_income": 500,
        "upgrade_price": 400,
        "income_increase": 50,
        "currency": "банок магнезии",
        "upgrade_currency": "банок магнезии",
        "upgrades": {
            1: {"name": "Улучшить международное управление", "emoji": "🏢"},
            2: {"name": "Улучшить архитектуру клубов", "emoji": "🎨"},
            3: {"name": "Улучшить эксклюзивное оборудование", "emoji": "🏋️‍♂️"},
            4: {"name": "Улучшить систему аналитики", "emoji": "⚙️"},
            5: {"name": "Улучшить менеджмент сети", "emoji": "👥"}
        }
    }
}

# ==============================
# АДМИН КОНСТАНТЫ
# ==============================

ADMIN_USERS = [1]
PENDING_DELETIONS = {}

# ==============================
# БАЗА ДАННЫХ
# ==============================

class GameDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('/home/ВАШ_ЛОГИН/mysite/gym_legend.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 1,
                power INTEGER DEFAULT 0,
                magnesia INTEGER DEFAULT 0,
                last_dumbbell_use TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_new INTEGER DEFAULT 1,
                dumbbell_level INTEGER DEFAULT 1,
                dumbbell_name TEXT DEFAULT 'Гантеля 1кг',
                total_lifts INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                custom_income INTEGER DEFAULT NULL,
                admin_level INTEGER DEFAULT 0,
                admin_nickname TEXT DEFAULT NULL,
                admin_since TIMESTAMP DEFAULT NULL,
                admin_id TEXT DEFAULT NULL,
                bans_given INTEGER DEFAULT 0,
                permabans_given INTEGER DEFAULT 0,
                deletions_given INTEGER DEFAULT 0,
                dumbbell_sets_given INTEGER DEFAULT 0,
                nickname_changes_given INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                ban_reason TEXT,
                ban_until TIMESTAMP DEFAULT NULL,
                business_1_level INTEGER DEFAULT 0,
                business_1_upgrades TEXT DEFAULT '{}',
                business_2_level INTEGER DEFAULT 0,
                business_2_upgrades TEXT DEFAULT '{}',
                business_3_level INTEGER DEFAULT 0,
                business_3_upgrades TEXT DEFAULT '{}'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                description TEXT,
                admin_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dumbbell_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                dumbbell_level INTEGER,
                income INTEGER,
                power_gained INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                action_type TEXT,
                target_user_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self.initialize_admin_ids()
    
    def initialize_admin_ids(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, admin_since FROM players WHERE admin_level > 0 AND (admin_id IS NULL OR admin_id = "") ORDER BY admin_since ASC')
        admins = cursor.fetchall()
        
        current_id = 1000
        for admin in admins:
            user_id = admin[0]
            cursor.execute('UPDATE players SET admin_id = ? WHERE user_id = ?', (str(current_id), user_id))
            current_id += 1
        
        self.conn.commit()
        return True
    
    def get_player(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_id, username, balance, power, magnesia, last_dumbbell_use, is_new,
                   dumbbell_level, dumbbell_name, total_lifts, total_earned,
                   custom_income, admin_level, admin_nickname, admin_since,
                   admin_id, bans_given, permabans_given, deletions_given,
                   dumbbell_sets_given, nickname_changes_given,
                   is_banned, ban_reason, ban_until, created_at,
                   business_1_level, business_1_upgrades,
                   business_2_level, business_2_upgrades,
                   business_3_level, business_3_upgrades
            FROM players WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'user_id': row[0], 'username': row[1], 'balance': row[2], 'power': row[3],
                'magnesia': row[4], 'last_dumbbell_use': row[5], 'is_new': row[6],
                'dumbbell_level': row[7], 'dumbbell_name': row[8], 'total_lifts': row[9],
                'total_earned': row[10], 'custom_income': row[11], 'admin_level': row[12],
                'admin_nickname': row[13], 'admin_since': row[14], 'admin_id': row[15],
                'bans_given': row[16], 'permabans_given': row[17], 'deletions_given': row[18],
                'dumbbell_sets_given': row[19], 'nickname_changes_given': row[20],
                'is_banned': row[21], 'ban_reason': row[22], 'ban_until': row[23],
                'created_at': row[24], 'business_1_level': row[25] or 0,
                'business_1_upgrades': json.loads(row[26] if row[26] else '{}'),
                'business_2_level': row[27] or 0,
                'business_2_upgrades': json.loads(row[28] if row[28] else '{}'),
                'business_3_level': row[29] or 0,
                'business_3_upgrades': json.loads(row[30] if row[30] else '{}')
            }
        return None
    
    def create_player(self, user_id, username):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO players 
               (user_id, username, dumbbell_level, dumbbell_name) 
               VALUES (?, ?, 1, 'Гантеля 1кг')''', (user_id, username))
        self.conn.commit()
        return self.get_player(user_id)
    
    def update_username(self, user_id, new_username):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET username = ? WHERE user_id = ?', (new_username, user_id))
        self.conn.commit()
        return True
    
    def update_player_balance(self, user_id, amount, transaction_type, description, admin_id=None):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        cursor.execute('''INSERT INTO transactions (user_id, type, amount, description, admin_id) 
               VALUES (?, ?, ?, ?, ?)''', (user_id, transaction_type, amount, description, admin_id))
        
        if amount > 0:
            cursor.execute('UPDATE players SET total_earned = total_earned + ? WHERE user_id = ?', (amount, user_id))
        
        self.conn.commit()
        return True
    
    def set_player_balance(self, user_id, new_balance, admin_id):
        cursor = self.conn.cursor()
        old_balance = self.get_player(user_id)['balance']
        cursor.execute('UPDATE players SET balance = ? WHERE user_id = ?', (new_balance, user_id))
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''', (admin_id, 'set_balance', user_id, f'Изменение баланса: {old_balance} -> {new_balance}'))
        self.conn.commit()
        return True
    
    def add_magnesia(self, user_id, amount, admin_id=None):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET magnesia = magnesia + ? WHERE user_id = ?', (amount, user_id))
        
        if admin_id:
            cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
                   VALUES (?, ?, ?, ?)''', (admin_id, 'add_magnesia', user_id, f'Добавлено банок магнезии: {amount}'))
        
        self.conn.commit()
        return True
    
    def buy_business(self, user_id, business_id, business_info):
        cursor = self.conn.cursor()
        
        if business_info['currency'] == 'монет':
            cursor.execute('UPDATE players SET balance = balance - ? WHERE user_id = ?', 
                         (business_info['base_price'], user_id))
        else:
            cursor.execute('UPDATE players SET magnesia = magnesia - ? WHERE user_id = ?', 
                         (business_info['base_price'], user_id))
        
        column = f'business_{business_id}_level'
        cursor.execute(f'UPDATE players SET {column} = 1 WHERE user_id = ?', (user_id,))
        
        self.conn.commit()
        return True
    
    def upgrade_business(self, user_id, business_id, upgrade_num, price):
        cursor = self.conn.cursor()
        player = self.get_player(user_id)
        
        upgrades_column = f'business_{business_id}_upgrades'
        current_upgrades = player[upgrades_column]
        
        if str(upgrade_num) not in current_upgrades:
            current_upgrades[str(upgrade_num)] = 1
        else:
            current_upgrades[str(upgrade_num)] += 1
        
        cursor.execute(f'UPDATE players SET {upgrades_column} = ? WHERE user_id = ?', 
                     (json.dumps(current_upgrades), user_id))
        
        business_info = BUSINESSES[business_id]
        if business_info['upgrade_currency'] == 'монет':
            cursor.execute('UPDATE players SET balance = balance - ? WHERE user_id = ?', (price, user_id))
        else:
            cursor.execute('UPDATE players SET magnesia = magnesia - ? WHERE user_id = ?', (price, user_id))
        
        level_column = f'business_{business_id}_level'
        completed_upgrades = sum(1 for v in current_upgrades.values() if v > 0)
        
        if completed_upgrades >= 5:
            cursor.execute(f'UPDATE players SET {level_column} = {level_column} + 1 WHERE user_id = ?', (user_id,))
            for key in current_upgrades:
                current_upgrades[key] = 0
            cursor.execute(f'UPDATE players SET {upgrades_column} = ? WHERE user_id = ?', 
                         (json.dumps(current_upgrades), user_id))
        
        self.conn.commit()
        return True
    
    # Остальные методы остаются без изменений...
    
    def find_player_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id FROM players WHERE username = ?', (username,))
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    
    def get_top_balance(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, balance, dumbbell_name FROM players WHERE is_banned = 0 ORDER BY balance DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    
    def get_top_lifts(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, total_lifts, dumbbell_name FROM players WHERE is_banned = 0 ORDER BY total_lifts DESC LIMIT ?', (limit,))
        return cursor.fetchall()

def format_number(number):
    """Форматирует число с разделителями тысяч"""
    return f"{number:,}".replace(",", ".")

# ==============================
# ИГРОВАЯ ЛОГИКА
# ==============================

class GymLegendBot:
    def __init__(self):
        self.db = GameDatabase()
        self.starting_balance = 1
        self.dumbbell_levels = DUMBBELL_LEVELS
        self.businesses = BUSINESSES
        self.dumbbell_cooldown = 60
        self.admin_users = ADMIN_USERS
        self.pending_deletions = PENDING_DELETIONS
    
    def is_admin(self, user_id):
        player = self.db.get_player(user_id)
        return player and player.get('admin_level', 0) > 0
    
    def get_admin_level(self, user_id):
        player = self.db.get_player(user_id)
        return player.get('admin_level', 0) if player else 0
    
    def handle_command(self, user_id, username, command):
        player = self.db.get_player(user_id)
        if player and player.get('is_banned', 0) == 1:
            ban_reason = player.get('ban_reason', 'Не указана')
            ban_until = player.get('ban_until')
            
            if ban_until:
                try:
                    ban_until_date = datetime.fromisoformat(ban_until)
                    if datetime.now() > ban_until_date:
                        self.db.unban_player(user_id, 0)
                    else:
                        days_left = (ban_until_date - datetime.now()).days
                        return jsonify({
                            'success': False,
                            'message': f'🚫 Вы заблокированы!\n📝 Причина: {ban_reason}\n⏳ Срок: {days_left} дней\n📅 До: {ban_until_date.strftime("%d.%m.%Y")}'
                        })
                except:
                    pass
            else:
                return jsonify({
                    'success': False,
                    'message': f'🚫 Вы заблокированы навсегда!\n📝 Причина: {ban_reason}'
                })
        
        if not player:
            player = self.db.create_player(user_id, username)
        
        command = command.lower().strip()
        parts = command.split()
        cmd = parts[0] if parts else ""
        cmd_args = parts[1:] if len(parts) > 1 else []
        
        # Бизнес команды
        if cmd == 'б' and cmd_args:
            if len(cmd_args) == 1 and cmd_args[0].isdigit():
                business_id = int(cmd_args[0])
                return self.get_business_info(user_id, business_id)
            elif len(cmd_args) == 2 and cmd_args[1] == 'купить':
                business_id = int(cmd_args[0])
                return self.buy_business_command(user_id, business_id)
            elif len(cmd_args) == 3 and cmd_args[1].isdigit() and cmd_args[2] == 'улучшить':
                business_id = int(cmd_args[0])
                upgrade_num = int(cmd_args[1])
                return self.upgrade_business_command(user_id, business_id, upgrade_num)
            elif cmd_args[0] == 'купить':
                if len(cmd_args) == 2 and cmd_args[1].isdigit():
                    business_id = int(cmd_args[1])
                    return self.buy_business_command(user_id, business_id)
                else:
                    return self.show_business_shop(user_id)
            elif cmd_args[0] == 'магазин':
                return self.show_business_shop(user_id)
        
        # Обычные команды (остаются без изменений)...
        
        # Админ команды
        elif self.is_admin(user_id):
            if cmd in ['банки', '/банки']:
                return self.add_magnesia_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            # Остальные админ команды...
        
        else:
            return jsonify({
                'success': False,
                'message': '❌ Неизвестная команда. Напишите /помощь для списка команд.'
            })
    
    # ======================
    # БИЗНЕС КОМАНДЫ
    # ======================
    
    def get_business_info(self, user_id, business_id):
        if business_id not in self.businesses:
            return jsonify({'success': False, 'message': '❌ Бизнес не найден!'})
        
        player = self.db.get_player(user_id)
        business = self.businesses[business_id]
        
        business_level = player.get(f'business_{business_id}_level', 0)
        upgrades = player.get(f'business_{business_id}_upgrades', {})
        
        if business_level == 0:
            return jsonify({
                'success': False,
                'message': f'❌ Вы не владеете бизнесом #{business_id}!\n💡 Купите его: /б {business_id} купить'
            })
        
        income = business['base_income'] + (business_level - 1) * business['income_increase']
        completed_upgrades = sum(1 for v in upgrades.values() if v > 0)
        
        upgrade_text = ""
        for i in range(1, 6):
            level = upgrades.get(str(i), 0)
            upgrade_info = business['upgrades'][i]
            upgrade_text += f"\n{upgrade_info['emoji']} <b>{i}. {upgrade_info['name']}</b> (Уровень {level})"
        
        next_upgrade_price = business['upgrade_price'] + completed_upgrades * 50
        
        info_text = (
            f"📊 <b>БИЗНЕС #{business_id}</b>\n\n"
            f"✅ <b>{business['name']}</b>\n\n"
            f"⏳ <b>Доход:</b> {format_number(income)} банок магнезии/час\n"
            f"📊 <b>Уровень бизнеса:</b> {business_level}\n"
            f"🏗️ <b>Улучшено этапов:</b> {completed_upgrades}/5\n\n"
            f"{upgrade_text}\n\n"
            f"🕐 <b>Накоплено магнезии:</b> {format_number(player['magnesia'])} банок\n"
            f"💰 <b>Следующее улучшение:</b> {format_number(next_upgrade_price)} {business['upgrade_currency']}\n\n"
            f"💡 <i>Для улучшения: /б {business_id} [1-5] улучшить</i>"
        )
        
        return jsonify({'success': True, 'message': info_text})
    
    def show_all_businesses(self, user_id):
        player = self.db.get_player(user_id)
        
        business_list = []
        for business_id, business in self.businesses.items():
            business_level = player.get(f'business_{business_id}_level', 0)
            if business_level > 0:
                business_list.append(f"{business_id}. ✅ <b>{business['name']}</b>\n   ⏳ Доход: {business['base_income'] + (business_level - 1) * business['income_increase']} банок магнезии/час\n   📊 Уровень: {business_level}")
        
        if not business_list:
            return jsonify({
                'success': False,
                'message': '📊 <b>ВАШИ БИЗНЕСЫ</b>\n\nУ вас пока нет бизнесов! 🏢\n\n💡 <i>Посмотреть доступные бизнесы: /б магазин</i>'
            })
        
        info_text = (
            f"📊 <b>ВАШИ БИЗНЕСЫ</b>\n\n"
            f"🏢 <b>Купленные бизнесы:</b>\n\n" +
            "\n\n".join(business_list) +
            f"\n\n💎 <b>Общий баланс магнезии:</b> {format_number(player['magnesia'])} банок\n"
            f"💰 <b>Общий баланс монет:</b> {format_number(player['balance'])} монет\n\n"
            f"📝 <i>Для просмотра бизнеса: /б [номер]</i>"
        )
        
        return jsonify({'success': True, 'message': info_text})
    
    def show_business_shop(self, user_id):
        player = self.db.get_player(user_id)
        
        shop_items = []
        for business_id, business in self.businesses.items():
            business_level = player.get(f'business_{business_id}_level', 0)
            
            if business_level > 0:
                status = "✅ Куплен"
            else:
                status = "❌ Не куплен"
            
            shop_items.append(
                f"<b>{business_id}. {business['name']}</b>\n"
                f"   💰 Цена: {format_number(business['base_price'])} {business['currency']}\n"
                f"   ⏳ Доход: {business['base_income']} банок магнезии/час\n"
                f"   📈 Улучшение: {format_number(business['upgrade_price'])} {business['upgrade_currency']}/уровень\n"
                f"   {status}"
            )
        
        info_text = (
            f"📊 <b>СИСТЕМА БИЗНЕСОВ GYM LEGEND</b>\n\n"
            f"🏢 <b>Доступные бизнесы:</b>\n\n" +
            "\n\n".join(shop_items) +
            f"\n\n💰 <b>Ваш баланс:</b> {format_number(player['balance'])} монет\n"
            f"💎 <b>Накоплено магнезии:</b> {format_number(player['magnesia'])} банок\n\n"
            f"📝 <b>Команды:</b>\n"
            f"• /б [номер] - посмотреть бизнес\n"
            f"• /б [номер] купить - купить бизнес\n"
            f"• /б магазин - магазин бизнесов"
        )
        
        return jsonify({'success': True, 'message': info_text})
    
    def buy_business_command(self, user_id, business_id):
        if business_id not in self.businesses:
            return jsonify({'success': False, 'message': '❌ Бизнес не найден!'})
        
        player = self.db.get_player(user_id)
        business = self.businesses[business_id]
        
        business_level = player.get(f'business_{business_id}_level', 0)
        if business_level > 0:
            return jsonify({'success': False, 'message': '❌ Вы уже владеете этим бизнесом!'})
        
        if business['currency'] == 'монет':
            if player['balance'] < business['base_price']:
                return jsonify({
                    'success': False,
                    'message': f'❌ Недостаточно монет! Нужно {format_number(business["base_price"])} 💰'
                })
        else:
            if player['magnesia'] < business['base_price']:
                return jsonify({
                    'success': False,
                    'message': f'❌ Недостаточно банок магнезии! Нужно {format_number(business["base_price"])} 💎'
                })
        
        self.db.buy_business(user_id, business_id, business)
        
        return jsonify({
            'success': True,
            'message': f'{business["name"].split()[0]} <b>Бизнес куплен!</b>\n\n{business["name"]}\n💵 Стоимость: {format_number(business["base_price"])} {business["currency"]}\n🏋️‍♂️ Доход: {business["base_income"]} банок магнезии в час'
        })
    
    def upgrade_business_command(self, user_id, business_id, upgrade_num):
        if business_id not in self.businesses:
            return jsonify({'success': False, 'message': '❌ Бизнес не найден!'})
        
        if upgrade_num < 1 or upgrade_num > 5:
            return jsonify({'success': False, 'message': '❌ Номер улучшения должен быть от 1 до 5!'})
        
        player = self.db.get_player(user_id)
        business = self.businesses[business_id]
        
        business_level = player.get(f'business_{business_id}_level', 0)
        if business_level == 0:
            return jsonify({'success': False, 'message': '❌ Вы не владеете этим бизнесом!'})
        
        upgrades = player.get(f'business_{business_id}_upgrades', {})
        completed_upgrades = sum(1 for v in upgrades.values() if v > 0)
        
        upgrade_price = business['upgrade_price'] + completed_upgrades * 50
        
        if business['upgrade_currency'] == 'монет':
            if player['balance'] < upgrade_price:
                return jsonify({
                    'success': False,
                    'message': f'❌ Недостаточно монет! Нужно {format_number(upgrade_price)} 💰'
                })
        else:
            if player['magnesia'] < upgrade_price:
                return jsonify({
                    'success': False,
                    'message': f'❌ Недостаточно банок магнезии! Нужно {format_number(upgrade_price)} 💎'
                })
        
        self.db.upgrade_business(user_id, business_id, upgrade_num, upgrade_price)
        
        upgrade_info = business['upgrades'][upgrade_num]
        new_level = upgrades.get(str(upgrade_num), 0) + 1
        
        message = (
            f'{upgrade_info["emoji"]} <b>Улучшение #{upgrade_num} завершено!</b>\n\n'
            f'✅ {upgrade_info["name"]}\n'
            f'📈 Новый уровень: {new_level}\n'
            f'💰 Потрачено: {format_number(upgrade_price)} {business["upgrade_currency"]}\n'
            f'🏗️ Улучшено этапов: {completed_upgrades + 1}/5\n'
            f'🏢 Уровень бизнеса: {business_level}'
        )
        
        if completed_upgrades + 1 >= 5:
            message += f'\n\n🎉 <b>ВСЕ 5 УЛУЧШЕНИЙ ЗАВЕРШЕНЫ!</b>\n🏢 <b>Уровень бизнеса повышен до {business_level + 1}</b>\n💎 <b>Доход увеличен до {business["base_income"] + business_level * business["income_increase"]} банок магнезии в час!</b>'
        
        return jsonify({'success': True, 'message': message})
    
    # ======================
    # АДМИН КОМАНДЫ
    # ======================
    
    def add_magnesia_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /банки [ник] [сумма]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /банки [ник] [сумма]'
            })
        
        username = ' '.join(parts[:-1])
        try:
            amount = int(parts[-1])
        except:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть числом!'
            })
        
        if amount <= 0:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть положительной!'
            })
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.db.add_magnesia(target_id, amount, user_id)
        
        new_magnesia = target_player['magnesia'] + amount
        
        return jsonify({
            'success': True,
            'message': f'✅ Банки магнезии выданы!\n👤 Игрок: <b>{target_player["username"]}</b>\n💎 Выдано: <b>{format_number(amount)} банок магнезии</b>\n🏦 Новый баланс магнезии: <b>{format_number(new_magnesia)} банок</b>\n👮 Выдал: <b>Администратор</b>'
        })
    
    # ======================
    # СПРАВОЧНЫЕ КОМАНДЫ
    # ======================
    
    def get_help(self):
        commands = [
            "🏋️‍♂️ <b>Gym Legend - Доступные команды:</b>\n",
            "📊 <b>Профиль и информация:</b>",
            "├── /профиль - ваш профиль",
            "├── /баланс - текущий баланс\n",
            "💪 <b>Гантели:</b>",
            "├── /гантеля - информация о гантеле",
            "├── /поднять - поднять гантелю",
            "├── /прокачаться - улучшить гантелю",
            "└── /магазин - магазин гантелей\n",
            "🏢 <b>Бизнес системы:</b>",
            "├── /б - список ваших бизнесов",
            "├── /б [номер] - информация о бизнесе",
            "├── /б магазин - магазин бизнесов",
            "├── /б [номер] купить - купить бизнес",
            "└── /б [номер] [1-5] улучшить - улучшить бизнес\n",
            "🏆 <b>Рейтинги:</b>",
            "├── /топ - общий список рейтингов",
            "├── /топ монет - топ по балансу",
            "├── /топ поднятий - топ по поднятиям",
            "└── /топ заработка - топ по заработку\n",
            "💡 <b>Особенности:</b>",
            "• Гантеля 1кг дается при регистрации",
            "• Кулдаун между подходами: 1 минута",
            "• Прокачка увеличивает доход",
            "• Бизнесы приносят пассивный доход",
            "• Соревнуйтесь с другими игроками!"
        ]
        
        return jsonify({
            'success': True,
            'message': '\n'.join(commands)
        })

# ==============================
# СОЗДАНИЕ И НАСТРОЙКА БОТА
# ==============================

bot = GymLegendBot()

# ==============================
# FLASK РОУТЫ
# ==============================

@app.route('/')
def index():
    return "Gym Legend Bot is running! 🏋️‍♂️"

@app.route('/api/command', methods=['GET', 'POST'])
def handle_command():
    if request.method == 'GET':
        user_id = request.args.get('user_id', default=1, type=int)
        username = request.args.get('username', default='Игрок', type=str)
        command = request.args.get('command', default='', type=str)
    else:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        username = data.get('username', 'Игрок')
        command = data.get('command', '')
    
    if not command:
        return jsonify({'success': False, 'message': 'Команда не указана'})
    
    return bot.handle_command(user_id, username, command)

# ==============================
# ЗАПУСК СЕРВЕРА
# ==============================

if __name__ == '__main__':
    print("Gym Legend Bot initialized!")
    app.run(debug=True)
```
