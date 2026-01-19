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

def format_number(number):
    """Форматирует число с разделителями тысяч"""
    return f"{number:,}".replace(",", ".")

# ==============================
# БАЗА ДАННЫХ
# ==============================

class GameDatabase:
    def __init__(self):
        # ВНИМАНИЕ: Замените путь на свой!
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
            business_1_upgrades = row[25] if row[25] else '{}'
            business_2_upgrades = row[27] if row[27] else '{}'
            business_3_upgrades = row[29] if row[29] else '{}'
            
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
                'business_1_upgrades': json.loads(business_1_upgrades),
                'business_2_level': row[26] or 0,
                'business_2_upgrades': json.loads(business_2_upgrades),
                'business_3_level': row[28] or 0,
                'business_3_upgrades': json.loads(business_3_upgrades)
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
    
    def add_power(self, user_id, amount):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET power = power + ? WHERE user_id = ?', (amount, user_id))
        self.conn.commit()
        return True
    
    def set_power(self, user_id, new_power, admin_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET power = ? WHERE user_id = ?', (new_power, user_id))
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''', (admin_id, 'set_power', user_id, f'Установлена сила: {new_power}'))
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
    
    def update_dumbbell_level(self, user_id, new_level, dumbbell_name):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET dumbbell_level = ?, dumbbell_name = ? WHERE user_id = ?',
                     (new_level, dumbbell_name, user_id))
        self.conn.commit()
        return True
    
    def set_dumbbell_level(self, user_id, new_level, admin_id):
        cursor = self.conn.cursor()
        
        if new_level in DUMBBELL_LEVELS:
            dumbbell_info = DUMBBELL_LEVELS[new_level]
            cursor.execute('UPDATE players SET dumbbell_level = ?, dumbbell_name = ? WHERE user_id = ?',
                         (new_level, dumbbell_info['name'], user_id))
            
            cursor.execute('UPDATE players SET dumbbell_sets_given = dumbbell_sets_given + 1 WHERE user_id = ?',
                         (admin_id,))
            
            cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
                   VALUES (?, ?, ?, ?)''', (admin_id, 'set_dumbbell_level', user_id, f'Установлен уровень гантели: {new_level}'))
            
            self.conn.commit()
            return True
        return False
    
    def update_dumbbell_use_time(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET last_dumbbell_use = ? WHERE user_id = ?',
                     (datetime.now().isoformat(), user_id))
        self.conn.commit()
        return True
    
    def increment_total_lifts(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET total_lifts = total_lifts + 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()
        return True
    
    def set_total_lifts(self, user_id, new_total, admin_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET total_lifts = ? WHERE user_id = ?', (new_total, user_id))
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''', (admin_id, 'set_total_lifts', user_id, f'Установлено поднятий: {new_total}'))
        self.conn.commit()
        return True
    
    def set_custom_income(self, user_id, custom_income, admin_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET custom_income = ? WHERE user_id = ?', (custom_income, user_id))
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''', (admin_id, 'set_custom_income', user_id, f'Установлен кастомный доход: {custom_income}'))
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
    
    def make_admin(self, user_id, admin_id, admin_level=1):
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT MAX(CAST(admin_id AS INTEGER)) FROM players WHERE admin_id IS NOT NULL AND admin_id != ""')
        result = cursor.fetchone()
        
        if result[0] is None:
            new_admin_id = 1000
        else:
            new_admin_id = int(result[0]) + 1
        
        cursor.execute('''UPDATE players 
               SET admin_level = ?, admin_since = ?, admin_id = ?
               WHERE user_id = ?''',
               (admin_level, datetime.now().isoformat(), str(new_admin_id), user_id))
        
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''',
               (admin_id, 'make_admin', user_id, f'Назначение администратора уровня {admin_level} с ID {new_admin_id}'))
        
        self.conn.commit()
        return str(new_admin_id)
    
    def remove_admin(self, user_id, admin_id):
        cursor = self.conn.cursor()
        
        player_data = self.get_player(user_id)
        
        cursor.execute('''UPDATE players 
               SET admin_level = 0, admin_nickname = NULL, admin_since = NULL, admin_id = NULL,
                   bans_given = 0, permabans_given = 0, deletions_given = 0,
                   dumbbell_sets_given = 0, nickname_changes_given = 0
               WHERE user_id = ?''', (user_id,))
        
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''',
               (admin_id, 'remove_admin', user_id, f'Снятие с должности администратора: {player_data["username"]}'))
        
        self.conn.commit()
        return True
    
    def set_admin_nickname(self, user_id, nickname):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET admin_nickname = ? WHERE user_id = ?', (nickname, user_id))
        self.conn.commit()
        return True
    
    def ban_player(self, user_id, days, reason, admin_id):
        cursor = self.conn.cursor()
        
        if days == 0:
            ban_until = None
        else:
            ban_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute('UPDATE players SET is_banned = 1, ban_reason = ?, ban_until = ? WHERE user_id = ?',
                     (reason, ban_until, user_id))
        
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''',
               (admin_id, 'ban', user_id, f'Бан: {days} дней, причина: {reason}'))
        
        self.conn.commit()
        return True
    
    def unban_player(self, user_id, admin_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET is_banned = 0, ban_reason = NULL, ban_until = NULL WHERE user_id = ?',
                     (user_id,))
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''', (admin_id, 'unban', user_id, 'Разбан игрока'))
        self.conn.commit()
        return True
    
    def delete_player(self, user_id, admin_id):
        cursor = self.conn.cursor()
        
        player_data = self.get_player(user_id)
        
        cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM dumbbell_uses WHERE user_id = ?', (user_id,))
        cursor.execute('DELETE FROM players WHERE user_id = ?', (user_id,))
        
        cursor.execute('''INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) 
               VALUES (?, ?, ?, ?)''',
               (admin_id, 'delete_player', user_id, f'Удален игрок: {player_data["username"]}'))
        
        self.conn.commit()
        return True
    
    def find_player_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id FROM players WHERE username = ?', (username,))
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    
    def log_dumbbell_use(self, user_id, dumbbell_level, income, power_gained):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO dumbbell_uses (user_id, dumbbell_level, income, power_gained) 
               VALUES (?, ?, ?, ?)''', (user_id, dumbbell_level, income, power_gained))
        self.conn.commit()
        return True
    
    def increment_admin_stat(self, user_id, stat_name):
        cursor = self.conn.cursor()
        
        stats_map = {
            'bans': 'bans_given',
            'permabans': 'permabans_given',
            'deletions': 'deletions_given',
            'dumbbell_sets': 'dumbbell_sets_given',
            'nickname_changes': 'nickname_changes_given'
        }
        
        if stat_name in stats_map:
            column = stats_map[stat_name]
            cursor.execute(f'UPDATE players SET {column} = {column} + 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
        return True
    
    def get_top_balance(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, balance, dumbbell_name FROM players WHERE is_banned = 0 ORDER BY balance DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    
    def get_top_lifts(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, total_lifts, dumbbell_name FROM players WHERE is_banned = 0 ORDER BY total_lifts DESC LIMIT ?', (limit,))
        return cursor.fetchall()
    
    def get_top_earners(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, dumbbell_name, dumbbell_level, total_earned FROM players WHERE is_banned = 0 ORDER BY total_earned DESC LIMIT ?', (limit,))
        return cursor.fetchall()

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
        elif cmd == 'б' and not cmd_args:
            return self.show_all_businesses(user_id)
        
        # Обычные команды
        elif cmd in ['начать', '/начать']:
            return self.welcome_message(user_id, username)
        elif cmd in ['профиль', '/профиль']:
            return self.get_profile(user_id)
        elif cmd in ['баланс', '/баланс']:
            return self.get_balance(user_id)
        elif cmd in ['помощь', '/помощь']:
            return self.get_help()
        elif cmd in ['гантеля', '/гантеля']:
            return self.get_dumbbell_info(user_id)
        elif cmd in ['поднять', '/поднять']:
            return self.use_dumbbell(user_id)
        elif cmd in ['прокачаться', '/прокачаться']:
            return self.upgrade_dumbbell(user_id)
        elif cmd in ['магазин', '/магазин']:
            return self.get_dumbbell_shop(user_id)
        elif cmd in ['топ', '/топ']:
            return self.get_top_list(user_id)
        elif cmd in ['топ', 'монет', '/топ', 'монет'] or command == '/топ монет':
            return self.get_top_balance()
        elif cmd in ['топ', 'поднятий', '/топ', 'поднятий'] or command == '/топ поднятий':
            return self.get_top_lifts()
        elif cmd in ['топ', 'заработка', '/топ', 'заработка'] or command == '/топ заработка':
            return self.get_top_earners()
        elif cmd in ['гник', '/гник']:
            return self.change_username(user_id, ' '.join(cmd_args) if cmd_args else None)
        
        # Админ команды
        elif self.is_admin(user_id):
            if cmd in ['админпанель', '/админпанель', 'админ_панель']:
                return self.admin_panel(user_id)
            elif cmd in ['аник', '/аник']:
                return self.set_admin_nickname_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['назначить', '/назначить']:
                return self.make_admin_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['снять', '/снять']:
                return self.remove_admin_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['лгантеля', '/лгантеля']:
                return self.set_dumbbell_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['-баланс', '/-баланс']:
                return self.remove_balance_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['+баланс', '/+баланс']:
                return self.add_balance_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['бан', '/бан']:
                return self.ban_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['пермбан', '/пермбан']:
                return self.permaban_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['разбан', '/разбан']:
                return self.unban_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['удалить', '/удалить']:
                return self.delete_player_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd == '/удалить+':
                return self.confirm_delete_command(user_id)
            elif cmd == '/удалить-':
                return self.cancel_delete_command(user_id)
            elif cmd in ['сгник', '/сгник']:
                return self.change_player_username_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['поднятия', '/поднятия']:
                return self.set_lifts_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['заработок', '/заработок']:
                return self.set_custom_income_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['банки', '/банки']:
                return self.add_magnesia_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['связь', '/связь']:
                return self.send_message_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['рассылка', '/рассылка']:
                return self.broadcast_message_command(user_id, ' '.join(cmd_args) if cmd_args else None)
            elif cmd in ['админ', '/админ']:
                return self.admin_help()
        
        else:
            return jsonify({
                'success': False,
                'message': '❌ Неизвестная команда. Напишите /помощь для списка команд.'
            })
    
    # ======================
    # ОБЫЧНЫЕ КОМАНДЫ
    # ======================
    
    def welcome_message(self, user_id, username):
        player = self.db.get_player(user_id)
        
        welcome_text = (
            "🔥 <b>Привет! Ты попал в Gym Legend</b> 😩🤟\n\n"
            "💪 Здесь ты можешь стать легендой фитнес-индустрии!\n"
            f"👤 Твой ник: <b>{username}</b>\n"
            f"💰 Стартовый баланс: <b>{format_number(player['balance'])} монет</b>\n"
            f"🏋️‍♂️ Стартовая гантеля: <b>{player['dumbbell_name']}</b>\n\n"
            "🏋️‍♂️ <b>Как играть:</b>\n"
            "1. Качайся с гантелями (/поднять)\n"
            "2. Прокачивай гантели (/прокачаться)\n"
            "3. Открой бизнес (/б магазин)\n"
            "4. Соревнуйся с другими (/топ)\n\n"
            "📝 Напиши команду <b>/помощь</b>, чтобы узнать все команды"
        )
        
        return jsonify({
            'success': True,
            'type': 'welcome',
            'message': welcome_text
        })
    
    def change_username(self, user_id, new_username):
        if not new_username:
            return jsonify({
                'success': False,
                'message': '❌ Укажите новый ник!\n📝 Использование: /гник [новый_ник]'
            })
        
        if len(new_username) > 20:
            return jsonify({
                'success': False,
                'message': '❌ Ник не может быть длиннее 20 символов!'
            })
        
        if len(new_username) < 3:
            return jsonify({
                'success': False,
                'message': '❌ Ник должен быть не короче 3 символов!'
            })
        
        if re.search(r'[@#$%^&*()+=|\\<>{}[\]:;"\'?/~`]', new_username):
            return jsonify({
                'success': False,
                'message': '❌ Ник не может содержать специальные символы!\n✅ Разрешены: буквы, цифры, пробелы, дефисы, подчеркивания'
            })
        
        if new_username != new_username.strip():
            return jsonify({
                'success': False,
                'message': '❌ Ник не может начинаться или заканчиваться пробелом!'
            })
        
        if '  ' in new_username:
            return jsonify({
                'success': False,
                'message': '❌ Ник не может содержать несколько пробелов подряд!'
            })
        
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ0-9 _-]+$', new_username):
            return jsonify({
                'success': False,
                'message': '❌ Ник содержит недопустимые символы!\n✅ Разрешены: буквы, цифры, пробелы, дефисы, подчеркивания'
            })
        
        self.db.update_username(user_id, new_username)
        
        return jsonify({
            'success': True,
            'message': f'✅ Ваш ник изменен на: <b>{new_username}</b>'
        })
    
    def get_dumbbell_info(self, user_id):
        player = self.db.get_player(user_id)
        
        if player.get('custom_income') is not None:
            income_per_use = player['custom_income']
            custom_note = f"⚡ <i>Кастомный доход</i>\n"
        else:
            dumbbell_info = self.dumbbell_levels[player['dumbbell_level']]
            income_per_use = dumbbell_info['income_per_use']
            custom_note = ""
        
        next_level = player['dumbbell_level'] + 1
        
        if next_level in self.dumbbell_levels:
            next_dumbbell = self.dumbbell_levels[next_level]
            upgrade_info = f"🔜 <b>Следующий уровень:</b> {next_dumbbell['name']}\n💵 Цена: {format_number(next_dumbbell['price'])} монет\n💰 Доход за подход: {next_dumbbell['income_per_use']} монет"
        else:
            upgrade_info = "🏆 <b>Вы достигли максимального уровня гантели!</b>"
        
        info_text = (
            f"🏋️‍♂️ <b>Ваша гантеля:</b>\n\n"
            f"{custom_note}"
            f"⚖️ Вес: <b>{player['dumbbell_name']}</b>\n"
            f"⭐ Уровень: <b>{player['dumbbell_level']}</b>\n"
            f"💰 Доход за подход: <b>{income_per_use} монет</b>\n"
            f"💪 Сила за подход: <b>{dumbbell_info['power_per_use']}</b>\n\n"
            f"{upgrade_info}"
        )
        
        return jsonify({
            'success': True,
            'type': 'dumbbell_info',
            'message': info_text,
            'dumbbell_level': player['dumbbell_level'],
            'dumbbell_name': player['dumbbell_name']
        })
    
    def use_dumbbell(self, user_id):
        player = self.db.get_player(user_id)
        
        last_use_str = player['last_dumbbell_use']
        if last_use_str:
            last_use = datetime.fromisoformat(last_use_str)
            seconds_passed = (datetime.now() - last_use).total_seconds()
            
            if seconds_passed < self.dumbbell_cooldown:
                seconds_left = int(self.dumbbell_cooldown - seconds_passed)
                return jsonify({
                    'success': False,
                    'message': f'⏳ Время отдыха! Подождите {seconds_left} секунд'
                })
        
        if player.get('custom_income') is not None:
            income = player['custom_income']
        else:
            dumbbell_info = self.dumbbell_levels[player['dumbbell_level']]
            income = dumbbell_info['income_per_use']
            power_gained = dumbbell_info['power_per_use']
        
        self.db.update_player_balance(
            user_id,
            income,
            'dumbbell_income',
            f'Подъем гантели {player["dumbbell_name"]}'
        )
        
        self.db.add_power(user_id, power_gained)
        self.db.update_dumbbell_use_time(user_id)
        self.db.increment_total_lifts(user_id)
        self.db.log_dumbbell_use(user_id, player['dumbbell_level'], income, power_gained)
        
        return jsonify({
            'success': True,
            'message': f'💪 <b>Вы подняли гантелю {player["dumbbell_name"]}!</b>\n💰 Получено: <b>{income} монет</b>\n💪 Получено силы: <b>{power_gained}</b>\n📈 Баланс: <b>{format_number(player["balance"] + income)} монет</b>',
            'income': income,
            'new_balance': player['balance'] + income,
            'power_gained': power_gained,
            'dumbbell_name': player['dumbbell_name']
        })
    
    def upgrade_dumbbell(self, user_id):
        player = self.db.get_player(user_id)
        current_level = player['dumbbell_level']
        next_level = current_level + 1
        
        if next_level not in self.dumbbell_levels:
            return jsonify({
                'success': False,
                'message': '🏆 Вы уже достигли максимального уровня гантели!'
            })
        
        next_dumbbell = self.dumbbell_levels[next_level]
        
        if player['balance'] < next_dumbbell['price']:
            return jsonify({
                'success': False,
                'message': f'❌ Недостаточно монет. Нужно {format_number(next_dumbbell["price"])} 💰, у вас {format_number(player["balance"])} 💰'
            })
        
        self.db.update_player_balance(
            user_id,
            -next_dumbbell['price'],
            'dumbbell_upgrade',
            f'Прокачка гантели до уровня {next_level}'
        )
        
        self.db.update_dumbbell_level(user_id, next_level, next_dumbbell['name'])
        
        return jsonify({
            'success': True,
            'message': f'🎉 <b>Гантеля прокачана!</b>\n🏋️‍♂️ Новый уровень: <b>{next_dumbbell["name"]}</b>\n💰 Доход за подход: <b>{next_dumbbell["income_per_use"]} монет</b>\n💪 Сила за подход: <b>{next_dumbbell["power_per_use"]}</b>\n💵 Потрачено: <b>{format_number(next_dumbbell["price"])} монет</b>',
            'new_level': next_level,
            'new_dumbbell_name': next_dumbbell['name'],
            'new_balance': player['balance'] - next_dumbbell['price']
        })
    
    def get_dumbbell_shop(self, user_id):
        player = self.db.get_player(user_id)
        current_level = player['dumbbell_level']
        
        shop_items = []
        for level in range(1, 15):
            dumbbell = self.dumbbell_levels[level]
            
            if level == current_level:
                prefix = "✅ "
            elif level < current_level:
                prefix = "✔️ "
            else:
                prefix = "🔘 "
            
            if level == current_level:
                suffix = " (Ваш текущий)"
            elif player['balance'] >= dumbbell['price']:
                suffix = " 🔥"
            else:
                suffix = " ⏳"
            
            shop_items.append(
                f"{prefix}<b>Уровень {level}:</b> {dumbbell['name']}\n"
                f"   ⚖️ Вес: {dumbbell['weight']} | "
                f"💰 Доход: {dumbbell['income_per_use']} монет | "
                f"💪 Сила: {dumbbell['power_per_use']} | "
                f"💵 Цена: {format_number(dumbbell['price'])} монет{suffix}"
            )
        
        shop_text = (
            "🏪 <b>Магазин гантелей</b>\n\n"
            "💪 <b>Как прокачаться:</b>\n"
            "1. Накапливайте монеты (/поднять)\n"
            "2. Купите улучшение (/прокачаться)\n"
            "3. Получайте больше дохода!\n\n"
            "📊 <b>Доступные гантели:</b>\n" +
            "\n".join(shop_items) +
            f"\n\n💰 <b>Ваш баланс:</b> {format_number(player['balance'])} монет\n"
            f"🏋️‍♂️ <b>Текущая гантеля:</b> {player['dumbbell_name']}"
        )
        
        return jsonify({
            'success': True,
            'type': 'dumbbell_shop',
            'message': shop_text
        })
    
    def get_profile(self, user_id):
        player = self.db.get_player(user_id)
        if not player:
            return jsonify({'success': False, 'message': 'Игрок не найден'})
        
        if player.get('custom_income') is not None:
            income_per_use = player['custom_income']
            income_note = f"💰 Доход за подход: <b>{income_per_use} монет</b> ⚡\n"
        else:
            dumbbell_info = self.dumbbell_levels[player['dumbbell_level']]
            income_per_use = dumbbell_info['income_per_use']
            income_note = f"💰 Доход за подход: <b>{income_per_use} монет</b>\n"
        
        created_date = datetime.fromisoformat(player['created_at']).strftime("%d.%m.%Y")
        
        admin_level = player.get('admin_level', 0)
        if admin_level > 0:
            privileges = "💎 Админ"
        else:
            privileges = "💎 Игрок"
        
        profile_text = (
            f"👤 <b>Профиль игрока #{player['user_id']}</b>\n\n"
            f"💪 Ник: <b>{player['username']}</b>\n"
            f"💎 Привилегии: <b>{privileges}</b>\n"
            f"💰 Баланс: <b>{format_number(player['balance'])} монет</b>\n"
            f"💪 Сила: <b>{format_number(player['power'])}</b>\n"
            f"🏋️‍♂️ Гантеля: <b>{player['dumbbell_name']}</b>\n"
            f"⭐ Уровень гантели: <b>{player['dumbbell_level']}</b>\n"
            f"{income_note}"
            f"💪 Поднятий гантели: <b>{format_number(player['total_lifts'])}</b>\n"
            f"💎 Банки магнезии: <b>{format_number(player['magnesia'])} банок</b>\n"
            f"📅 Дата регистрации: <b>{created_date}</b>"
        )
        
        return jsonify({
            'success': True,
            'type': 'profile',
            'message': profile_text,
            'data': {
                'username': player['username'],
                'user_id': player['user_id'],
                'balance': player['balance'],
                'power': player['power'],
                'magnesia': player['magnesia'],
                'dumbbell_level': player['dumbbell_level'],
                'dumbbell_name': player['dumbbell_name'],
                'dumbbell_income': income_per_use,
                'total_lifts': player['total_lifts'],
                'created_at': created_date,
                'privileges': privileges
            }
        })
    
    def get_balance(self, user_id):
        player = self.db.get_player(user_id)
        return jsonify({
            'success': True,
            'message': f'💰 <b>Ваш баланс:</b> {format_number(player["balance"])} монет',
            'balance': player['balance']
        })
    
    def get_top_balance(self):
        top_players = self.db.get_top_balance(10)
        
        if not top_players:
            return jsonify({
                'success': True,
                'message': '🏆 Топ пока пуст. Будьте первым!'
            })
        
        top_text = "🏆 <b>ТОП по монетам:</b>\n\n"
        
        for i, (username, balance, dumbbell_name) in enumerate(top_players, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "🔸"))
            top_text += f"{medal} <b>{i}.</b> {username}\n"
            top_text += f"   💰 {format_number(balance)} монет | 🏋️‍♂️ {dumbbell_name}\n\n"
        
        return jsonify({
            'success': True,
            'type': 'top_balance',
            'message': top_text
        })
    
    def get_top_lifts(self):
        top_players = self.db.get_top_lifts(10)
        
        if not top_players:
            return jsonify({
                'success': True,
                'message': '🏆 Топ пока пуст. Будьте первым!'
            })
        
        top_text = "💪 <b>ТОП по поднятиям:</b>\n\n"
        
        for i, (username, total_lifts, dumbbell_name) in enumerate(top_players, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "🔸"))
            top_text += f"{medal} <b>{i}.</b> {username}\n"
            top_text += f"   💪 {format_number(total_lifts)} поднятий | 🏋️‍♂️ {dumbbell_name}\n\n"
        
        return jsonify({
            'success': True,
            'type': 'top_lifts',
            'message': top_text
        })
    
    def get_top_earners(self):
        top_players = self.db.get_top_earners(10)
        
        if not top_players:
            return jsonify({
                'success': True,
                'message': '🏆 Топ пока пуст. Будьте первым!'
            })
        
        top_text = "💰 <b>ТОП по заработку:</b>\n\n"
        
        for i, (username, dumbbell_name, dumbbell_level, total_earned) in enumerate(top_players, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "🔸"))
            dumbbell_info = self.dumbbell_levels.get(dumbbell_level, {"income_per_use": 1})
            income_per_lift = dumbbell_info['income_per_use']
            
            top_text += f"{medal} <b>{i}.</b> {username}\n"
            top_text += f"   💰 {format_number(total_earned)} монет | 🏋️‍♂️ {dumbbell_name}\n"
            top_text += f"   📈 {income_per_lift} монет/подход\n\n"
        
        return jsonify({
            'success': True,
            'type': 'top_earners',
            'message': top_text
        })
    
    def get_top_list(self, user_id):
        player = self.db.get_player(user_id)
        
        top_text = (
            "🏆 <b>Система ТОПа Gym Legend</b>\n\n"
            "📊 <b>Доступные рейтинги:</b>\n\n"
            "💰 <b>/топ монет</b> - топ игроков по балансу\n"
            "💪 <b>/топ поднятий</b> - топ по количеству поднятий\n"
            "📈 <b>/топ заработка</b> - топ по общему заработку\n\n"
            f"💪 <b>Ваши показатели:</b>\n"
            f"💰 Баланс: {format_number(player['balance'])} монет\n"
            f"💪 Поднятий: {format_number(player['total_lifts'])}\n"
            f"🏋️‍♂️ Гантеля: {player['dumbbell_name']}\n\n"
            "Выберите нужный топ из списка выше!"
        )
        
        return jsonify({
            'success': True,
            'type': 'top_list',
            'message': top_text
        })
    
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
                income = business['base_income'] + (business_level - 1) * business['income_increase']
                business_list.append(f"{business_id}. ✅ <b>{business['name']}</b>\n   ⏳ Доход: {format_number(income)} банок магнезии/час\n   📊 Уровень: {business_level}")
        
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
    
    def admin_panel(self, user_id):
        player = self.db.get_player(user_id)
        
        if not player or player.get('admin_level', 0) == 0:
            return jsonify({
                'success': False,
                'message': '❌ У вас нет прав администратора!'
            })
        
        admin_level = player['admin_level']
        if admin_level == 1:
            position = "👮 Администратор"
        elif admin_level == 2:
            position = "👑 Создатель🌟"
        else:
            position = "❓ Неизвестная должность"
        
        admin_since = "Не назначен"
        if player.get('admin_since'):
            admin_since_date = datetime.fromisoformat(player['admin_since'])
            admin_since = admin_since_date.strftime("%d.%m.%Y %H:%M")
        
        admin_nickname = player.get('admin_nickname', 'Не установлен')
        if admin_nickname != 'Не установлен':
            admin_nickname_display = f"{admin_nickname} 👑"
        else:
            admin_nickname_display = admin_nickname
        
        admin_id = player.get('admin_id', 'Не назначен')
        
        stats = [
            f"🚫 Банов выдано: {player.get('bans_given', 0)}",
            f"⛔ Пермбанов выдано: {player.get('permabans_given', 0)}",
            f"🗑️ Удалений профилей: {player.get('deletions_given', 0)}",
            f"🏋️‍♂️ Выдано уровней гантели: {player.get('dumbbell_sets_given', 0)}",
            f"📝 Изменено ников другим: {player.get('nickname_changes_given', 0)}"
        ]
        
        panel_text = (
            f"🏛️ <b>АДМИН ПАНЕЛЬ</b>\n\n"
            f"👑 <b>Администратор:</b>\n"
            f"├─ 🏢 Должность: <b>{position}</b>\n"
            f"├─ ⭐ Уровень прав: <b>{admin_level}</b>\n"
            f"├─ 📛 Админ-ник: <b>{admin_nickname_display}</b>\n"
            f"├─ 🆔 Админ ID: <b>{admin_id}</b>\n"
            f"└─ 📅 Назначен: <b>{admin_since}</b>\n\n"
            f"📊 <b>Статистика действий:</b>\n"
            f"{chr(10).join(stats)}\n\n"
            f"⚙️ <b>Доступные команды:</b>\n"
            f"• /назначить [ник] [уровень] - назначить админа\n"
            f"• /админ - список всех админ-команд"
        )
        
        if admin_level == 2:
            panel_text += f"\n\n👑 <b>Особые права создателя:</b>\n• Может назначать администраторов\n• Полный доступ ко всем командам"
        
        return jsonify({
            'success': True,
            'type': 'admin_panel',
            'message': panel_text
        })
    
    def admin_help(self):
        commands = [
            "🏛️ <b>Административные команды Gym Legend</b>\n",
            "📝 <b>Основные команды:</b>",
            "├── /админпанель - показать админ панель",
            "├── /аник [ник] - установить админ-ник",
            "├── /лгантеля [ник] [уровень] - установить уровень гантели",
            "├── /-баланс [ник] [сумма] - убрать сумму с баланса игрока",
            "├── /+баланс [ник] [сумма] - добавить сумму на баланс игрока",
            "├── /бан [ник] [дни] [причина] - заблокировать игрока",
            "├── /пермбан [ник] [причина] - перманентный бан",
            "├── /разбан [ник] - разблокировать игрока",
            "├── /удалить [ник] [причина] - удалить профиль игрока",
            "├── /удалить+ - подтвердить удаление",
            "├── /удалить- - отменить удаление",
            "├── /сгник [старый_ник] [новый_ник] - сменить ник игроку",
            "├── /поднятия [ник] [количество] - установить поднятия",
            "├── /заработок [ник] [сумма] - установить кастомный доход",
            "├── /банки [ник] [сумма] - выдать банки магнезии игроку",
            "├── /рассылка [сообщение] - массовая рассылка всем игрокам",
            "└── /связь [ник] [сообщение] - отправить сообщение\n",
            "🌟 <b>Особенные команды:</b>",
            "├── /назначить [ник] [уровень] - назначить админа",
            "└── /снять [ник] - снять с должности администратора\n",
            "⚠️ <b>Внимание:</b>",
            "• При удалении нужно указать причину",
            "• Для подтверждения/отмены используйте /удалить+ или /удалить-",
            "• Все действия логируются"
        ]
        
        return jsonify({
            'success': True,
            'message': '\n'.join(commands)
        })
    
    def set_admin_nickname_command(self, user_id, args):
        player = self.db.get_player(user_id)
        
        if not player or player.get('admin_level', 0) == 0:
            return jsonify({
                'success': False,
                'message': '❌ У вас нет прав администратора!'
            })
        
        if not args:
            current_nickname = player.get('admin_nickname', 'Не установлен')
            return jsonify({
                'success': True,
                'message': f'👑 <b>Текущий админ-ник:</b> {current_nickname}\n\n📝 Чтобы изменить: /аник [новый_ник]\n💡 После ника автоматически добавляется 👑'
            })
        
        if len(args) > 15:
            return jsonify({
                'success': False,
                'message': '❌ Админ-ник не может быть длиннее 15 символов!'
            })
        
        self.db.set_admin_nickname(user_id, args)
        
        return jsonify({
            'success': True,
            'message': f'✅ Админ-ник установлен!\n\n👑 Новый админ-ник: <b>{args} 👑</b>\n⭐ Уровень: <b>{player["admin_level"]}</b>\n📅 Дата установки: <b>{datetime.now().strftime("%d.%m.%Y %H:%M")}</b>'
        })
    
    def make_admin_command(self, user_id, args):
        player = self.db.get_player(user_id)
        
        if player.get('admin_level', 0) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только создатель может назначать администраторов!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и уровень!\n📝 Использование: /назначить [ник] [уровень]\n\nУровни:\n1 - Администратор\n2 - Создатель🌟'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и уровень!\n📝 Использование: /назначить [ник] [уровень]'
            })
        
        username = ' '.join(parts[:-1])
        try:
            admin_level = int(parts[-1])
        except:
            return jsonify({
                'success': False,
                'message': '❌ Уровень должен быть числом 1 или 2!'
            })
        
        if admin_level not in [1, 2]:
            return jsonify({
                'success': False,
                'message': '❌ Уровень должен быть 1 (Администратор) или 2 (Создатель🌟)!'
            })
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        if admin_level >= player['admin_level'] and target_id != user_id:
            return jsonify({
                'success': False,
                'message': '❌ Вы не можете назначить уровень равный или выше своего!'
            })
        
        admin_unique_id = self.db.make_admin(target_id, user_id, admin_level)
        
        position = "👮 Администратор" if admin_level == 1 else "👑 Создатель🌟"
        
        return jsonify({
            'success': True,
            'message': f'✅ Игрок назначен на должность!\n\n👤 Игрок: <b>{target_player["username"]}</b>\n🏢 Должность: <b>{position}</b>\n⭐ Уровень: <b>{admin_level}</b>\n🆔 Админ ID: <b>#{admin_unique_id}</b>\n👑 Назначил: <b>{player.get("admin_nickname", player["username"])} 👑</b>'
        })
    
    def remove_admin_command(self, user_id, args):
        player = self.db.get_player(user_id)
        
        if player.get('admin_level', 0) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только создатель может снимать с должности!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник администратора!\n📝 Использование: /снять [ник]'
            })
        
        target_ids = self.db.find_player_by_username(args)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Администратор с точным ником "{args}" не найден!\n💡 Введите точный ник администратора'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        if target_player.get('admin_level', 0) == 0:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок <b>{target_player["username"]}</b> не является администратором!'
            })
        
        if target_id == user_id:
            return jsonify({
                'success': False,
                'message': '❌ Вы не можете снять самого себя!'
            })
        
        if target_player.get('admin_level', 0) == 2 and target_id != user_id:
            return jsonify({
                'success': False,
                'message': '❌ Вы не можете снять другого создателя!'
            })
        
        old_position = "👑 Создатель🌟" if target_player['admin_level'] == 2 else "👮 Администратор"
        old_admin_id = target_player.get('admin_id', 'Не назначен')
        
        self.db.remove_admin(target_id, user_id)
        
        return jsonify({
            'success': True,
            'message': f'🚫 <b>Администратор снят с должности!</b>\n\n👤 Администратор: <b>{target_player["username"]}</b>\n🏢 Бывшая должность: <b>{old_position}</b>\n🆔 Бывший Админ ID: <b>{old_admin_id}</b>\n👑 Снял: <b>{player.get("admin_nickname", player["username"])} 👑</b>\n\n⚠️ <b>Все административные права были сняты</b>'
        })
    
    def set_dumbbell_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и уровень!\n📝 Использование: /лгантеля [ник] [уровень]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и уровень!\n📝 Использование: /лгантеля [ник] [уровень]'
            })
        
        username = ' '.join(parts[:-1])
        try:
            level = int(parts[-1])
        except:
            return jsonify({
                'success': False,
                'message': '❌ Уровень должен быть числом от 1 до 14!'
            })
        
        if level < 1 or level > 14:
            return jsonify({
                'success': False,
                'message': '❌ Уровень должен быть от 1 до 14!'
            })
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.db.set_dumbbell_level(target_id, level, user_id)
        self.db.increment_admin_stat(user_id, 'dumbbell_sets')
        
        dumbbell_info = self.dumbbell_levels[level]
        
        return jsonify({
            'success': True,
            'message': f'✅ Уровень гантели изменен!\n👤 Игрок: <b>{target_player["username"]}</b>\n🏋️‍♂️ Новая гантеля: <b>{dumbbell_info["name"]}</b>\n⭐ Уровень: <b>{level}</b>\n👮 Изменил: <b>Администратор</b>'
        })
    
    def remove_balance_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /-баланс [ник] [сумма]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /-баланс [ник] [сумма]'
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
        
        if target_player['balance'] < amount:
            return jsonify({
                'success': False,
                'message': f'❌ У игрока недостаточно монет!\n💰 Баланс игрока: {format_number(target_player["balance"])} монет'
            })
        
        new_balance = target_player['balance'] - amount
        self.db.set_player_balance(target_id, new_balance, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ Баланс изменен!\n👤 Игрок: <b>{target_player["username"]}</b>\n💰 Списано: <b>{format_number(amount)} монет</b>\n💵 Новый баланс: <b>{format_number(new_balance)} монет</b>\n👮 Изменил: <b>Администратор</b>'
        })
    
    def add_balance_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /+баланс [ник] [сумма]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /+баланс [ник] [сумма]'
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
        
        new_balance = target_player['balance'] + amount
        self.db.set_player_balance(target_id, new_balance, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ Баланс изменен!\n👤 Игрок: <b>{target_player["username"]}</b>\n💰 Добавлено: <b>{format_number(amount)} монет</b>\n💵 Новый баланс: <b>{format_number(new_balance)} монет</b>\n👮 Изменил: <b>Администратор</b>'
        })
    
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
    
    def ban_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник, дни и причину!\n📝 Использование: /бан [ник] [дни] [причина]'
            })
        
        parts = args.split()
        if len(parts) < 3:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник, дни и причину!\n📝 Использование: /бан [ник] [дни] [причина]'
            })
        
        try:
            days = int(parts[-2])
        except:
            return jsonify({
                'success': False,
                'message': '❌ Дни должны быть числом!'
            })
        
        if days <= 0:
            return jsonify({
                'success': False,
                'message': '❌ Дни должны быть положительным числом!'
            })
        
        username = ' '.join(parts[:-2])
        reason = parts[-1]
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.db.ban_player(target_id, days, reason, user_id)
        self.db.increment_admin_stat(user_id, 'bans')
        
        ban_until = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
        
        return jsonify({
            'success': True,
            'message': f'🚫 <b>Игрок заблокирован!</b>\n\n👤 Игрок: <b>{target_player["username"]}</b>\n⏳ Срок: <b>{days} дней</b>\n📝 Причина: <b>{reason}</b>\n👮 Администратор: <b>Админ</b>\n📅 Разблокировка: <b>{ban_until}</b>'
        })
    
    def permaban_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и причину!\n📝 Использование: /пермбан [ник] [причина]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и причину!\n📝 Использование: /пермбан [ник] [причина]'
            })
        
        username = ' '.join(parts[:-1])
        reason = parts[-1]
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.db.ban_player(target_id, 0, reason, user_id)
        self.db.increment_admin_stat(user_id, 'permabans')
        
        return jsonify({
            'success': True,
            'message': f'🚫 <b>Игрок заблокирован навсегда!</b>\n\n👤 Игрок: <b>{target_player["username"]}</b>\n⏳ Срок: <b>Навсегда</b>\n📝 Причина: <b>{reason}</b>\n👮 Администратор: <b>Админ</b>\n⚠️ <b>Перманентная блокировка</b>'
        })
    
    def unban_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока!\n📝 Использование: /разбан [ник]'
            })
        
        target_ids = self.db.find_player_by_username(args)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{args}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        if not target_player['is_banned']:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок <b>{target_player["username"]}</b> не заблокирован!'
            })
        
        self.db.unban_player(target_id, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Игрок разблокирован!</b>\n\n👤 Игрок: <b>{target_player["username"]}</b>\n👮 Администратор: <b>Админ</b>\n🎉 <b>Теперь игрок может снова играть!</b>'
        })
    
    def delete_player_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и причину!\n📝 Использование: /удалить [ник] [причина]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и причину!\n📝 Использование: /удалить [ник] [причина]'
            })
        
        username = ' '.join(parts[:-1])
        reason = parts[-1]
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.pending_deletions[user_id] = {
            'target_id': target_id,
            'target_username': target_player['username'],
            'reason': reason,
            'timestamp': time.time()
        }
        
        return jsonify({
            'success': True,
            'message': f'⚠️ <b>Подтверждение удаления</b>\n\nВы собираетесь удалить игрока: <b>{target_player["username"]}</b>\n📝 Причина: <b>{reason}</b>\n\n<b>Для подтверждения введите:</b>\n<code>/удалить+</code>\n\n<b>Для отмены введите:</b>\n<code>/удалить-</code>\n\n<b>Действие отменится через 60 секунд</b>'
        })
    
    def confirm_delete_command(self, user_id):
        if user_id not in self.pending_deletions:
            return jsonify({
                'success': False,
                'message': '❌ Нет ожидающих удалений!'
            })
        
        pending = self.pending_deletions[user_id]
        
        if time.time() - pending['timestamp'] > 60:
            del self.pending_deletions[user_id]
            return jsonify({
                'success': False,
                'message': '❌ Время подтверждения истекло!'
            })
        
        target_id = pending['target_id']
        reason = pending['reason']
        
        self.db.delete_player(target_id, user_id)
        self.db.increment_admin_stat(user_id, 'deletions')
        
        del self.pending_deletions[user_id]
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Профиль удален!</b>\n\n👤 Игрок: <b>{pending["target_username"]}</b>\n📝 Причина: <b>{reason}</b>\n👮 Администратор: <b>Админ</b>\n🕒 Время: <b>{datetime.now().strftime("%d.%m.%Y %H:%M")}</b>\n\n⚠️ <b>Все данные игрока были удалены</b>'
        })
    
    def cancel_delete_command(self, user_id):
        if user_id not in self.pending_deletions:
            return jsonify({
                'success': False,
                'message': '❌ Нет ожидающих удалений!'
            })
        
        pending = self.pending_deletions[user_id]
        del self.pending_deletions[user_id]
        
        return jsonify({
            'success': True,
            'message': f'❌ <b>Удаление отменено</b>\n\nПрофиль игрока <b>{pending["target_username"]}</b> не был удален.\nДействие отменено администратором.'
        })
    
    def change_player_username_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите старый и новый ник!\n📝 Использование: /сгник [старый_ник] [новый_ник]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите старый и новый ник!\n📝 Использование: /сгник [старый_ник] [новый_ник]'
            })
        
        new_username = parts[-1]
        old_username = ' '.join(parts[:-1])
        
        if len(new_username) > 20:
            return jsonify({
                'success': False,
                'message': '❌ Новый ник не может быть длиннее 20 символов!'
            })
        
        if len(new_username) < 3:
            return jsonify({
                'success': False,
                'message': '❌ Новый ник должен быть не короче 3 символов!'
            })
        
        target_ids = self.db.find_player_by_username(old_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{old_username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.db.update_username(target_id, new_username)
        self.db.increment_admin_stat(user_id, 'nickname_changes')
        
        return jsonify({
            'success': True,
            'message': f'✅ Ник игрока изменен!\n👤 Игрок: <b>{target_player["username"]}</b>\n🆕 Новый ник: <b>{new_username}</b>\n👮 Изменил: <b>Администратор</b>'
        })
    
    def set_lifts_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и количество!\n📝 Использование: /поднятия [ник] [количество]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и количество!\n📝 Использование: /поднятия [ник] [количество]'
            })
        
        username = ' '.join(parts[:-1])
        try:
            lifts = int(parts[-1])
        except:
            return jsonify({
                'success': False,
                'message': '❌ Количество должно быть числом!'
            })
        
        if lifts < 0:
            return jsonify({
                'success': False,
                'message': '❌ Количество не может быть отрицательным!'
            })
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        target_id = target_ids[0]
        target_player = self.db.get_player(target_id)
        
        self.db.set_total_lifts(target_id, lifts, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ Количество поднятий изменено!\n👤 Игрок: <b>{target_player["username"]}</b>\n💪 Новое количество: <b>{format_number(lifts)}</b>\n👮 Изменил: <b>Администратор</b>'
        })
    
    def set_custom_income_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /заработок [ник] [сумма]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сумму!\n📝 Использование: /заработок [ник] [сумма]'
            })
        
        username = ' '.join(parts[:-1])
        try:
            income = int(parts[-1])
        except:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть числом!'
            })
        
        if income <= 0:
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
        
        self.db.set_custom_income(target_id, income, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ Кастомный доход установлен!\n👤 Игрок: <b>{target_player["username"]}</b>\n💰 Новый доход за подход: <b>{income} монет</b>\n⚡ <i>Теперь игрок будет получать эту сумму при каждом поднятии</i>\n👮 Установил: <b>Администратор</b>'
        })
    
    def send_message_command(self, user_id, args):
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сообщение!\n📝 Использование: /связь [ник] [сообщение]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник и сообщение!\n📝 Использование: /связь [ник] [сообщение]'
            })
        
        username = parts[0]
        message = ' '.join(parts[1:])
        
        target_ids = self.db.find_player_by_username(username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с точным ником "{username}" не найден!\n💡 Введите точный ник игрока'
            })
        
        admin_player = self.db.get_player(user_id)
        
        return jsonify({
            'success': True,
            'message': f'📨 <b>Сообщение отправлено!</b>\n\n👤 Игроку: <b>{username}</b>\n📝 Сообщение: <b>{message}</b>\n👮 Отправил: <b>{admin_player["username"]}</b>\n\n💡 <i>В реальном боте сообщение было бы отправлено в личные сообщения ВК</i>'
        })
    
    def broadcast_message_command(self, user_id, args):
        player = self.db.get_player(user_id)
        
        if not player or player.get('admin_level', 0) == 0:
            return jsonify({
                'success': False,
                'message': '❌ У вас нет прав администратора!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите сообщение для рассылки!\n📝 Использование: /рассылка [сообщение]'
            })
        
        message = args
        
        if len(message) > 200:
            return jsonify({
                'success': False,
                'message': '❌ Сообщение слишком длинное! Максимум 200 символов.'
            })
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT user_id, username FROM players WHERE is_banned = 0')
        players = cursor.fetchall()
        
        if not players:
            return jsonify({
                'success': False,
                'message': '❌ В базе данных нет активных игроков!'
            })
        
        total_players = len(players)
        
        cursor.execute(
            'INSERT INTO admin_actions (admin_id, action_type, target_user_id, details) VALUES (?, ?, ?, ?)',
            (user_id, 'broadcast', 0, f'Массовая рассылка: "{message[:50]}..."')
        )
        
        self.db.conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'📢 <b>Рассылка успешно отправлена!</b>\n\n📝 Сообщение: <b>{message}</b>\n👥 Игроков получило: <b>{total_players}</b>\n👮 Отправил: <b>{player.get("admin_nickname", player["username"])} 👑</b>\n\n💡 <i>В реальном боте сообщение было бы отправлено в личные сообщения ВК</i>'
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

@app.route('/api/profile', methods=['GET'])
def get_profile():
    user_id = request.args.get('user_id', default=1, type=int)
    return bot.get_profile(user_id)

# Для Callback API ВК
@app.route('/api/callback', methods=['POST'])
def vk_callback():
    data = request.get_json()
    
    if data.get('type') == 'confirmation':
        return 'ваша_строка_подтверждения'
    
    elif data.get('type') == 'message_new':
        message = data.get('object', {}).get('message', {})
        user_id = message.get('from_id')
        text = message.get('text', '')
        
        username = f"Игрок_{user_id}"
        
        result = bot.handle_command(user_id, username, text)
        
        return 'ok'
    
    return 'ok'

# ==============================
# ЗАПУСК СЕРВЕРА
# ==============================

if __name__ == '__main__':
    print("Gym Legend Bot initialized!")
    app.run(debug=True)
