#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gym Legend - Игровой бот для ВК
Полная версия с административной системой, системой силы, бизнесами, промокодами, переводом денег и кланами
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
    11: {"name": "Гантеля 11кг", "price": 300, "weight": "11кг", "income_per_use": 11, "power_per_use": 11},
    12: {"name": "Гантеля 12.5кг", "price": 350, "weight": "12.5кг", "income_per_use": 15, "power_per_use": 12},
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
# КОНСТАНТЫ КЛАНОВ
# ==============================

CLAN_CREATE_COST = 1000
CLAN_UPGRADE_BASE_COST = 500

# ==============================
# АДМИН КОНСТАНТЫ
# ==============================

ADMIN_USERS = [1]
PENDING_DELETIONS = {}
PENDING_RESETS = {}

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
        
        # Основная таблица игроков
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
                business_3_upgrades TEXT DEFAULT '{}',
                clan_id INTEGER DEFAULT NULL,
                used_promo_codes TEXT DEFAULT '[]'
            )
        ''')
        
        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                description TEXT,
                admin_id INTEGER DEFAULT NULL,
                target_user_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица использований гантелей
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
        
        # Таблица админ действий
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
        
        # Таблица промокодов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                uses_total INTEGER DEFAULT 1,
                uses_left INTEGER DEFAULT 1,
                reward_type TEXT NOT NULL,
                reward_amount INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT NULL,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (created_by) REFERENCES players (user_id)
            )
        ''')
        
        # Таблица использований промокодов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                promo_code TEXT NOT NULL,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (promo_code) REFERENCES promo_codes (code)
            )
        ''')
        
        # Таблица кланов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                owner_id INTEGER NOT NULL,
                level INTEGER DEFAULT 1,
                treasury INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_income_per_hour INTEGER DEFAULT 0,
                total_lifts INTEGER DEFAULT 0,
                FOREIGN KEY (owner_id) REFERENCES players (user_id)
            )
        ''')
        
        # Таблица участников кланов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clan_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_id INTEGER NOT NULL,
                user_id INTEGER UNIQUE NOT NULL,
                role TEXT DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                contributions INTEGER DEFAULT 0,
                FOREIGN KEY (clan_id) REFERENCES clans (id),
                FOREIGN KEY (user_id) REFERENCES players (user_id)
            )
        ''')
        
        # Таблица лога казны клана
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clan_treasury_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_id INTEGER NOT NULL,
                user_id INTEGER,
                action_type TEXT,
                amount INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (clan_id) REFERENCES clans (id),
                FOREIGN KEY (user_id) REFERENCES players (user_id)
            )
        ''')
        
        # Таблица приглашений в кланы
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clan_invites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clan_id INTEGER NOT NULL,
                inviter_id INTEGER NOT NULL,
                invitee_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (clan_id) REFERENCES clans (id),
                FOREIGN KEY (inviter_id) REFERENCES players (user_id),
                FOREIGN KEY (invitee_id) REFERENCES players (user_id)
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
                   business_3_level, business_3_upgrades,
                   clan_id, used_promo_codes
            FROM players WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if row:
            business_1_upgrades = row[25] if row[25] else '{}'
            business_2_upgrades = row[27] if row[27] else '{}'
            business_3_upgrades = row[29] if row[29] else '{}'
            used_promo_codes = row[31] if row[31] else '[]'
            
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
                'business_3_upgrades': json.loads(business_3_upgrades),
                'clan_id': row[30],
                'used_promo_codes': json.loads(used_promo_codes)
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
    
    def update_player_balance(self, user_id, amount, transaction_type, description, admin_id=None, target_user_id=None):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE players SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        
        cursor.execute('''INSERT INTO transactions (user_id, type, amount, description, admin_id, target_user_id) 
               VALUES (?, ?, ?, ?, ?, ?)''', (user_id, transaction_type, amount, description, admin_id, target_user_id))
        
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
    # МЕТОДЫ ДЛЯ ПРОМОКОДОВ
    # ==============================
    
    def create_promo_code(self, code, uses_total, reward_type, reward_amount, created_by, expires_days=None):
        """Создание промокода"""
        cursor = self.conn.cursor()
        
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
        else:
            expires_at = None
        
        try:
            cursor.execute('''
                INSERT INTO promo_codes (code, uses_total, uses_left, reward_type, reward_amount, created_by, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, uses_total, uses_total, reward_type, reward_amount, created_by, expires_at))
            
            cursor.execute('''
                INSERT INTO admin_actions (admin_id, action_type, target_user_id, details)
                VALUES (?, ?, ?, ?)
            ''', (created_by, 'create_promo', 0, f'Создан промокод: {code}, награда: {reward_amount} {reward_type}'))
            
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_promo_code(self, code, admin_id):
        """Удаление промокода"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT code FROM promo_codes WHERE code = ?', (code,))
        if not cursor.fetchone():
            return False
        
        cursor.execute('DELETE FROM promo_codes WHERE code = ?', (code,))
        
        cursor.execute('''
            INSERT INTO admin_actions (admin_id, action_type, target_user_id, details)
            VALUES (?, ?, ?, ?)
        ''', (admin_id, 'delete_promo', 0, f'Удален промокод: {code}'))
        
        self.conn.commit()
        return True
    
    def get_promo_info(self, code):
        """Получение информации о промокоде"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT code, uses_total, uses_left, reward_type, reward_amount, 
                   created_by, created_at, expires_at, is_active
            FROM promo_codes WHERE code = ?
        ''', (code,))
        
        row = cursor.fetchone()
        if row:
            return {
                'code': row[0],
                'uses_total': row[1],
                'uses_left': row[2],
                'reward_type': row[3],
                'reward_amount': row[4],
                'created_by': row[5],
                'created_at': row[6],
                'expires_at': row[7],
                'is_active': row[8]
            }
        return None
    
    def use_promo_code(self, user_id, code):
        """Использование промокода"""
        cursor = self.conn.cursor()
        
        # Проверяем существование промокода
        promo_info = self.get_promo_info(code)
        if not promo_info:
            return {'success': False, 'error': 'Промокод не найден'}
        
        # Проверяем активность промокода
        if promo_info['is_active'] == 0:
            return {'success': False, 'error': 'Промокод неактивен'}
        
        # Проверяем срок действия
        if promo_info['expires_at']:
            expires_at = datetime.fromisoformat(promo_info['expires_at'])
            if datetime.now() > expires_at:
                return {'success': False, 'error': 'Срок действия промокода истек'}
        
        # Проверяем оставшиеся использования
        if promo_info['uses_left'] <= 0:
            return {'success': False, 'error': 'Лимит использований исчерпан'}
        
        # Проверяем, использовал ли игрок уже этот промокод
        cursor.execute('SELECT used_promo_codes FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        used_codes = json.loads(result[0] if result[0] else '[]')
        
        if code in used_codes:
            return {'success': False, 'error': 'Вы уже использовали этот промокод'}
        
        # Уменьшаем количество оставшихся использований
        cursor.execute('UPDATE promo_codes SET uses_left = uses_left - 1 WHERE code = ?', (code,))
        
        # Выдаем награду
        if promo_info['reward_type'] == 'монеты':
            cursor.execute('UPDATE players SET balance = balance + ? WHERE user_id = ?', 
                         (promo_info['reward_amount'], user_id))
        elif promo_info['reward_type'] == 'магнезия':
            cursor.execute('UPDATE players SET magnesia = magnesia + ? WHERE user_id = ?', 
                         (promo_info['reward_amount'], user_id))
        
        # Добавляем промокод в список использованных
        used_codes.append(code)
        cursor.execute('UPDATE players SET used_promo_codes = ? WHERE user_id = ?', 
                     (json.dumps(used_codes), user_id))
        
        # Логируем использование
        cursor.execute('''
            INSERT INTO promo_uses (user_id, promo_code)
            VALUES (?, ?)
        ''', (user_id, code))
        
        self.conn.commit()
        
        return {
            'success': True,
            'reward_type': promo_info['reward_type'],
            'reward_amount': promo_info['reward_amount']
        }
    
    def get_all_promo_codes(self):
        """Получение всех промокодов"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT code, uses_total, uses_left, reward_type, reward_amount, 
                   created_at, expires_at, is_active
            FROM promo_codes ORDER BY created_at DESC
        ''')
        
        promos = []
        for row in cursor.fetchall():
            promos.append({
                'code': row[0],
                'uses_total': row[1],
                'uses_left': row[2],
                'reward_type': row[3],
                'reward_amount': row[4],
                'created_at': row[5],
                'expires_at': row[6],
                'is_active': row[7]
            })
        return promos
    
    # ==============================
    # МЕТОДЫ ДЛЯ КЛАНОВ
    # ==============================
    
    def create_clan(self, tag, name, owner_id):
        """Создание клана"""
        cursor = self.conn.cursor()
        
        # Проверяем уникальность тега
        cursor.execute('SELECT id FROM clans WHERE tag = ?', (tag.upper(),))
        if cursor.fetchone():
            return {'success': False, 'error': 'Клан с таким тегом уже существует'}
        
        # Проверяем уникальность названия
        cursor.execute('SELECT id FROM clans WHERE name = ?', (name,))
        if cursor.fetchone():
            return {'success': False, 'error': 'Клан с таким названием уже существует'}
        
        # Проверяем, не состоит ли игрок уже в клане
        cursor.execute('SELECT clan_id FROM players WHERE user_id = ?', (owner_id,))
        player_data = cursor.fetchone()
        if player_data and player_data[0]:
            return {'success': False, 'error': 'Вы уже состоите в клане'}
        
        try:
            # Создаем клан
            cursor.execute('''
                INSERT INTO clans (tag, name, owner_id, level, treasury)
                VALUES (?, ?, ?, 1, 0)
            ''', (tag.upper(), name, owner_id))
            
            clan_id = cursor.lastrowid
            
            # Добавляем владельца в участники
            cursor.execute('''
                INSERT INTO clan_members (clan_id, user_id, role, contributions)
                VALUES (?, ?, 'owner', 0)
            ''', (clan_id, owner_id))
            
            # Обновляем поле клана у игрока
            cursor.execute('UPDATE players SET clan_id = ? WHERE user_id = ?', (clan_id, owner_id))
            
            self.conn.commit()
            return {'success': True, 'clan_id': clan_id, 'tag': tag.upper(), 'name': name}
        except Exception as e:
            return {'success': False, 'error': f'Ошибка при создании клана: {str(e)}'}
    
    def get_clan_by_tag(self, tag):
        """Получение клана по тегу"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, tag, name, owner_id, level, treasury, created_at,
                   total_income_per_hour, total_lifts
            FROM clans WHERE tag = ?
        ''', (tag.upper(),))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'tag': row[1],
                'name': row[2],
                'owner_id': row[3],
                'level': row[4],
                'treasury': row[5],
                'created_at': row[6],
                'total_income_per_hour': row[7],
                'total_lifts': row[8]
            }
        return None
    
    def get_clan_by_id(self, clan_id):
        """Получение клана по ID"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, tag, name, owner_id, level, treasury, created_at,
                   total_income_per_hour, total_lifts
            FROM clans WHERE id = ?
        ''', (clan_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'tag': row[1],
                'name': row[2],
                'owner_id': row[3],
                'level': row[4],
                'treasury': row[5],
                'created_at': row[6],
                'total_income_per_hour': row[7],
                'total_lifts': row[8]
            }
        return None
    
    def get_player_clan(self, user_id):
        """Получение клана игрока"""
        cursor = self.conn.cursor()
        
        # Получаем clan_id игрока
        cursor.execute('SELECT clan_id FROM players WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            return self.get_clan_by_id(result[0])
        return None
    
    def get_clan_members(self, clan_id, limit=100):
        """Получение участников клана"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT cm.user_id, p.username, cm.role, cm.contributions, cm.joined_at
            FROM clan_members cm
            JOIN players p ON cm.user_id = p.user_id
            WHERE cm.clan_id = ?
            ORDER BY 
                CASE cm.role 
                    WHEN 'owner' THEN 1
                    WHEN 'officer' THEN 2
                    ELSE 3 
                END,
                cm.contributions DESC
            LIMIT ?
        ''', (clan_id, limit))
        
        members = []
        for row in cursor.fetchall():
            members.append({
                'user_id': row[0],
                'username': row[1],
                'role': row[2],
                'contributions': row[3],
                'joined_at': row[4]
            })
        return members
    
    def get_clan_member_count(self, clan_id):
        """Получение количества участников клана"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clan_members WHERE clan_id = ?', (clan_id,))
        return cursor.fetchone()[0]
    
    def deposit_to_clan_treasury(self, user_id, amount):
        """Внесение денег в казну клана"""
        cursor = self.conn.cursor()
        
        # Получаем информацию об игроке и его клане
        player = self.get_player(user_id)
        if not player or not player['clan_id']:
            return {'success': False, 'error': 'Вы не состоите в клане'}
        
        if player['balance'] < amount:
            return {'success': False, 'error': 'Недостаточно средств на балансе'}
        
        if amount <= 0:
            return {'success': False, 'error': 'Сумма должна быть положительной'}
        
        try:
            # Снимаем деньги с игрока
            cursor.execute('UPDATE players SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
            
            # Добавляем деньги в казну клана
            cursor.execute('UPDATE clans SET treasury = treasury + ? WHERE id = ?', (amount, player['clan_id']))
            
            # Увеличиваем вклад игрока
            cursor.execute('UPDATE clan_members SET contributions = contributions + ? WHERE user_id = ? AND clan_id = ?',
                         (amount, user_id, player['clan_id']))
            
            # Логируем операцию
            cursor.execute('''
                INSERT INTO clan_treasury_log (clan_id, user_id, action_type, amount, description)
                VALUES (?, ?, 'deposit', ?, ?)
            ''', (player['clan_id'], user_id, amount, f'Игрок {player["username"]} внес {amount} монет в казну'))
            
            self.conn.commit()
            return {'success': True, 'new_balance': player['balance'] - amount, 'new_treasury': None}
        except Exception as e:
            return {'success': False, 'error': f'Ошибка при внесении средств: {str(e)}'}
    
    def upgrade_clan(self, clan_id):
        """Улучшение уровня клана"""
        cursor = self.conn.cursor()
        
        clan = self.get_clan_by_id(clan_id)
        if not clan:
            return {'success': False, 'error': 'Клан не найден'}
        
        # Рассчитываем стоимость улучшения
        upgrade_cost = CLAN_UPGRADE_BASE_COST * clan['level']
        
        if clan['treasury'] < upgrade_cost:
            return {'success': False, 'error': f'Недостаточно средств в казне. Нужно {upgrade_cost} монет'}
        
        try:
            # Снимаем деньги с казны
            cursor.execute('UPDATE clans SET treasury = treasury - ?, level = level + 1 WHERE id = ?',
                         (upgrade_cost, clan_id))
            
            # Логируем операцию
            cursor.execute('''
                INSERT INTO clan_treasury_log (clan_id, action_type, amount, description)
                VALUES (?, 'upgrade', ?, ?)
            ''', (clan_id, upgrade_cost, f'Улучшение клана до уровня {clan["level"] + 1}'))
            
            self.conn.commit()
            return {'success': True, 'new_level': clan['level'] + 1, 'cost': upgrade_cost}
        except Exception as e:
            return {'success': False, 'error': f'Ошибка при улучшении клана: {str(e)}'}
    
    def get_clan_treasury_log(self, clan_id, limit=10):
        """Получение лога операций с казной"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT ctl.action_type, ctl.amount, ctl.description, ctl.created_at, p.username
            FROM clan_treasury_log ctl
            LEFT JOIN players p ON ctl.user_id = p.user_id
            WHERE ctl.clan_id = ?
            ORDER BY ctl.created_at DESC
            LIMIT ?
        ''', (clan_id, limit))
        
        log = []
        for row in cursor.fetchall():
            log.append({
                'action_type': row[0],
                'amount': row[1],
                'description': row[2],
                'created_at': row[3],
                'username': row[4]
            })
        return log
    
    def get_top_clans(self, limit=10):
        """Получение топа кланов"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.tag, c.name, c.level, c.treasury, c.total_income_per_hour,
                   COUNT(cm.id) as member_count
            FROM clans c
            LEFT JOIN clan_members cm ON c.id = cm.clan_id
            GROUP BY c.id
            ORDER BY c.total_income_per_hour DESC, c.treasury DESC
            LIMIT ?
        ''', (limit,))
        
        clans = []
        for row in cursor.fetchall():
            clans.append({
                'tag': row[0],
                'name': row[1],
                'level': row[2],
                'treasury': row[3],
                'total_income_per_hour': row[4],
                'member_count': row[5] or 0
            })
        return clans
    
    def delete_clan(self, tag, admin_id):
        """Удаление клана администратором"""
        cursor = self.conn.cursor()
        
        clan = self.get_clan_by_tag(tag)
        if not clan:
            return {'success': False, 'error': 'Клан не найден'}
        
        try:
            # Получаем всех участников клана
            cursor.execute('SELECT user_id FROM clan_members WHERE clan_id = ?', (clan['id'],))
            members = cursor.fetchall()
            
            # Обнуляем clan_id у всех участников
            for member in members:
                cursor.execute('UPDATE players SET clan_id = NULL WHERE user_id = ?', (member[0],))
            
            # Удаляем записи участников
            cursor.execute('DELETE FROM clan_members WHERE clan_id = ?', (clan['id'],))
            
            # Удаляем лог казны
            cursor.execute('DELETE FROM clan_treasury_log WHERE clan_id = ?', (clan['id'],))
            
            # Удаляем клан
            cursor.execute('DELETE FROM clans WHERE id = ?', (clan['id'],))
            
            # Логируем действие администратора
            cursor.execute('''
                INSERT INTO admin_actions (admin_id, action_type, target_user_id, details)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, 'delete_clan', clan['owner_id'], f'Удален клан: {clan["tag"]} {clan["name"]}'))
            
            self.conn.commit()
            return {'success': True, 'clan_name': clan['name'], 'member_count': len(members)}
        except Exception as e:
            return {'success': False, 'error': f'Ошибка при удалении клана: {str(e)}'}
    
    def update_clan_name(self, tag, new_name, admin_id):
        """Изменение названия клана администратором"""
        cursor = self.conn.cursor()
        
        clan = self.get_clan_by_tag(tag)
        if not clan:
            return {'success': False, 'error': 'Клан не найден'}
        
        try:
            old_name = clan['name']
            cursor.execute('UPDATE clans SET name = ? WHERE id = ?', (new_name, clan['id']))
            
            # Логируем действие администратора
            cursor.execute('''
                INSERT INTO admin_actions (admin_id, action_type, target_user_id, details)
                VALUES (?, ?, ?, ?)
            ''', (admin_id, 'rename_clan', clan['owner_id'], f'Переименован клан {clan["tag"]}: {old_name} -> {new_name}'))
            
            self.conn.commit()
            return {'success': True, 'old_name': old_name, 'new_name': new_name}
        except Exception as e:
            return {'success': False, 'error': f'Ошибка при изменении названия: {str(e)}'}

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
        self.pending_resets = PENDING_RESETS
    
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
        
        # ======================
        # КОМАНДЫ КЛАНОВ
        # ======================
        if cmd == 'к' and cmd_args:
            if cmd_args[0] == 'создать' and len(cmd_args) >= 3:
                tag = cmd_args[1]
                clan_name = ' '.join(cmd_args[2:])
                return self.create_clan_command(user_id, tag, clan_name)
            elif cmd_args[0] == 'улучшить':
                return self.upgrade_clan_command(user_id)
            elif cmd_args[0] == 'казна':
                return self.clan_treasury_command(user_id)
            elif cmd_args[0] == 'профиль':
                return self.clan_profile_command(user_id)
            elif cmd_args[0] == 'топ':
                return self.clan_top_command()
            elif cmd_args[0] == 'положить' and len(cmd_args) >= 2:
                amount_str = cmd_args[1]
                return self.clan_deposit_command(user_id, amount_str)
        
        # ======================
        # АДМИН КОМАНДЫ КЛАНОВ
        # ======================
        elif cmd in ['аксменить', '/аксменить'] and len(cmd_args) >= 2:
            tag = cmd_args[0]
            new_name = ' '.join(cmd_args[1:])
            return self.admin_rename_clan_command(user_id, tag, new_name)
        elif cmd in ['акудалить', '/акудалить'] and cmd_args:
            tag = cmd_args[0]
            return self.admin_delete_clan_command(user_id, tag)
        elif cmd in ['акинфо', '/акинфо'] and cmd_args:
            tag = cmd_args[0]
            return self.admin_clan_info_command(user_id, tag)
        
        # ======================
        # КОМАНДА ПЕРЕВОДА ДЕНЕГ
        # ======================
        elif cmd in ['перевод', 'перевести', '/перевод', '/перевести'] and len(cmd_args) >= 2:
            target_username = cmd_args[0]
            amount_str = cmd_args[1]
            return self.transfer_money_command(user_id, target_username, amount_str)
        
        # ======================
        # БИЗНЕС КОМАНДЫ
        # ======================
        elif cmd == 'б' and cmd_args:
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
        
        # ======================
        # КОМАНДЫ ПРОМОКОДОВ
        # ======================
        elif cmd in ['создатьпромокод', '/создатьпромокод']:
            return self.create_promo_command(user_id, ' '.join(cmd_args) if cmd_args else None)
        elif cmd in ['удалитьпромокод', '/удалитьпромокод']:
            return self.delete_promo_command(user_id, ' '.join(cmd_args) if cmd_args else None)
        elif cmd in ['промоинфо', '/промоинфо']:
            return self.promo_info_command(user_id, ' '.join(cmd_args) if cmd_args else None)
        elif cmd in ['промо', '/промо']:
            return self.use_promo_command(user_id, ' '.join(cmd_args) if cmd_args else None)
        
        # ======================
        # ОБЫЧНЫЕ КОМАНДЫ
        # ======================
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
        
        # ======================
        # АДМИН КОМАНДЫ
        # ======================
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
            elif cmd in ['статистика', '/статистика']:
                return self.bot_statistics_command(user_id)
            elif cmd in ['сбросвсех', '/сбросвсех']:
                return self.reset_all_accounts_command(user_id)
            elif cmd == '/сбросвсех+':
                return self.confirm_reset_all_command(user_id)
            elif cmd == '/сбросвсех-':
                return self.cancel_reset_all_command(user_id)
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
    # КОМАНДЫ КЛАНОВ
    # ======================
    
    def create_clan_command(self, user_id, tag, clan_name):
        """Создание клана"""
        player = self.db.get_player(user_id)
        
        # Проверяем баланс
        if player['balance'] < CLAN_CREATE_COST:
            return jsonify({
                'success': False,
                'message': f'❌ Недостаточно монет для создания клана!\n💵 Нужно: {format_number(CLAN_CREATE_COST)} монет\n💰 У вас: {format_number(player["balance"])} монет'
            })
        
        # Проверяем тег клана
        if not re.match(r'^[A-Z]{3}$', tag.upper()):
            return jsonify({
                'success': False,
                'message': '❌ Тег клана должен состоять из 3х английских букв!\n📝 Пример: LEG, GYM, FIT'
            })
        
        # Проверяем название клана
        if len(clan_name) < 3 or len(clan_name) > 20:
            return jsonify({
                'success': False,
                'message': '❌ Название клана должно быть от 3 до 20 символов!'
            })
        
        # Проверяем, не состоит ли игрок уже в клане
        if player['clan_id']:
            return jsonify({
                'success': False,
                'message': '❌ Вы уже состоите в клане! Сначала выйдите из текущего клана.'
            })
        
        # Создаем клан
        result = self.db.create_clan(tag, clan_name, user_id)
        
        if result['success']:
            # Снимаем деньги за создание клана
            self.db.update_player_balance(
                user_id,
                -CLAN_CREATE_COST,
                'clan_creation',
                f'Создание клана {tag.upper()}',
                None
            )
            
            return jsonify({
                'success': True,
                'message': f'🏰 <b>Клан создан!</b>\n\n'
                          f'🔰 Тег: <b>[{tag.upper()}]</b>\n'
                          f'🏷️ Название: <b>{clan_name}</b>\n'
                          f'👑 Владелец: <b>{player["username"]}</b>\n'
                          f'💰 Потрачено: <b>{format_number(CLAN_CREATE_COST)} монет</b>\n'
                          f'⭐ Уровень: <b>1</b>\n\n'
                          f'🎯 <b>Бонусы клана:</b>\n'
                          f'├─ 💼 +5% к доходам с бизнесов\n'
                          f'├─ 🏋️ +1 монета за поднятие\n'
                          f'└─ 👥 Без ограничений по участникам!\n\n'
                          f'💡 <i>Используйте /к помощь для списка команд клана</i>'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'❌ {result["error"]}'
            })
    
    def upgrade_clan_command(self, user_id):
        """Улучшение уровня клана"""
        clan = self.db.get_player_clan(user_id)
        if not clan:
            return jsonify({
                'success': False,
                'message': '❌ Вы не состоите в клане!'
            })
        
        # Проверяем, является ли игрок владельцем
        player = self.db.get_player(user_id)
        if clan['owner_id'] != user_id:
            return jsonify({
                'success': False,
                'message': '❌ Только владелец клана может улучшать его уровень!'
            })
        
        # Рассчитываем стоимость улучшения
        upgrade_cost = CLAN_UPGRADE_BASE_COST * clan['level']
        
        result = self.db.upgrade_clan(clan['id'])
        
        if result['success']:
            # Рассчитываем новые бонусы
            business_bonus = 5 + (result['new_level'] - 1)  # 5% + (уровень-1)%
            lift_bonus = 1 + (result['new_level'] - 1)      # 1 + (уровень-1)
            
            return jsonify({
                'success': True,
                'message': f'⭐ <b>Клан улучшен!</b>\n\n'
                          f'🏰 Клан: <b>[{clan["tag"]}] {clan["name"]}</b>\n'
                          f'📈 Новый уровень: <b>{result["new_level"]}</b>\n'
                          f'💰 Потрачено из казны: <b>{format_number(result["cost"])} монет</b>\n'
                          f'🏦 Остаток в казне: <b>{format_number(clan["treasury"] - result["cost"])} монет</b>\n\n'
                          f'🎯 <b>Новые бонусы:</b>\n'
                          f'├─ 💼 +{business_bonus}% к доходам с бизнесов\n'
                          f'├─ 🏋️ +{lift_bonus} монет за поднятие\n'
                          f'└─ 📊 Следующее улучшение: <b>{format_number(upgrade_cost + CLAN_UPGRADE_BASE_COST)} монет</b>'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'❌ {result["error"]}'
            })
    
    def clan_treasury_command(self, user_id):
        """Просмотр казны клана"""
        clan = self.db.get_player_clan(user_id)
        if not clan:
            return jsonify({
                'success': False,
                'message': '❌ Вы не состоите в клане!'
            })
        
        # Получаем участников клана
        members = self.db.get_clan_members(clan['id'], 10)
        
        # Получаем лог операций
        log = self.db.get_clan_treasury_log(clan['id'], 5)
        
        # Рассчитываем бонусы
        business_bonus = 5 + (clan['level'] - 1)
        lift_bonus = 1 + (clan['level'] - 1)
        
        # Форматируем информацию о участниках
        members_text = ""
        for i, member in enumerate(members[:5], 1):
            role_emoji = "👑" if member['role'] == 'owner' else ("⭐" if member['role'] == 'officer' else "👤")
            members_text += f"{i}. {role_emoji} <b>{member['username']}</b> - {format_number(member['contributions'])} монет\n"
        
        # Форматируем лог операций
        log_text = ""
        for entry in log:
            action_emoji = "➕" if entry['action_type'] == 'deposit' else ("⬆️" if entry['action_type'] == 'upgrade' else "💰")
            username = entry['username'] or "Система"
            time_str = datetime.fromisoformat(entry['created_at']).strftime("%d.%m %H:%M")
            log_text += f"{action_emoji} <b>{username}</b>: {entry['description']} ({time_str})\n"
        
        response_text = (
            f"🏦 <b>КАЗНА КЛАНА [{clan['tag']}]</b>\n\n"
            f"🏷️ Название: <b>{clan['name']}</b>\n"
            f"⭐ Уровень: <b>{clan['level']}</b>\n"
            f"💰 Казна: <b>{format_number(clan['treasury'])} монет</b>\n"
            f"👥 Участников: <b>{len(members)}</b>\n"
            f"📈 Доход/час: <b>{format_number(clan['total_income_per_hour'])} монет</b>\n\n"
            f"🎯 <b>Бонусы клана:</b>\n"
            f"├─ 💼 +{business_bonus}% к доходам с бизнесов\n"
            f"├─ 🏋️ +{lift_bonus} монет за поднятие\n"
            f"└─ 👥 Без ограничений по участникам\n\n"
            f"🏆 <b>Топ вкладчиков:</b>\n{members_text}\n"
            f"📜 <b>Последние операции:</b>\n{log_text}\n"
            f"💡 <i>Положить деньги: /к положить [сумма]</i>"
        )
        
        return jsonify({
            'success': True,
            'message': response_text
        })
    
    def clan_profile_command(self, user_id):
        """Профиль клана"""
        clan = self.db.get_player_clan(user_id)
        if not clan:
            return jsonify({
                'success': False,
                'message': '❌ Вы не состоите в клане!'
            })
        
        # Получаем количество участников
        member_count = self.db.get_clan_member_count(clan['id'])
        
        # Получаем владельца
        owner = self.db.get_player(clan['owner_id'])
        owner_name = owner['username'] if owner else "Неизвестно"
        
        # Рассчитываем бонусы
        business_bonus = 5 + (clan['level'] - 1)
        
        # Определяем базовый бонус за поднятие
        player = self.db.get_player(user_id)
        dumbbell_level = player['dumbbell_level']
        
        if dumbbell_level <= 4:
            base_lift_bonus = 1
        elif dumbbell_level <= 9:
            base_lift_bonus = 2
        elif dumbbell_level <= 14:
            base_lift_bonus = 3
        else:
            base_lift_bonus = 4
        
        total_lift_bonus = base_lift_bonus + (clan['level'] - 1)
        
        # Форматируем дату создания
        created_date = datetime.fromisoformat(clan['created_at']).strftime("%d.%m.%Y")
        
        response_text = (
            f"🏰 <b>ПРОФИЛЬ КЛАНА [{clan['tag']}]</b>\n\n"
            f"🏷️ Название: <b>{clan['name']}</b>\n"
            f"👑 Владелец: <b>{owner_name}</b>\n"
            f"⭐ Уровень: <b>{clan['level']}</b>\n"
            f"👥 Участников: <b>{member_count}</b>\n"
            f"💰 Казна: <b>{format_number(clan['treasury'])} монет</b>\n"
            f"📈 Доход/час: <b>{format_number(clan['total_income_per_hour'])} монет</b>\n"
            f"💪 Всего поднятий: <b>{format_number(clan['total_lifts'])}</b>\n"
            f"📅 Основан: <b>{created_date}</b>\n\n"
            f"🎯 <b>Ваши бонусы от клана:</b>\n"
            f"├─ 💼 +{business_bonus}% к доходам с бизнесов\n"
            f"├─ 🏋️ +{total_lift_bonus} монет за поднятие\n"
            f"└─ 📊 Доход за поднятие: {base_lift_bonus} + {clan['level'] - 1}\n\n"
            f"💡 <i>Команды клана: /к помощь</i>"
        )
        
        return jsonify({
            'success': True,
            'message': response_text
        })
    
    def clan_top_command(self):
        """Топ кланов"""
        clans = self.db.get_top_clans(10)
        
        if not clans:
            return jsonify({
                'success': False,
                'message': '🏆 Пока нет созданных кланов. Создайте первый!'
            })
        
        top_text = "🏆 <b>ТОП КЛАНОВ GYM LEGEND</b>\n\n"
        
        for i, clan in enumerate(clans, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else "🔸"))
            
            # Рассчитываем бонусы клана
            business_bonus = 5 + (clan['level'] - 1)
            
            top_text += (
                f"{medal} <b>{i}.</b> [{clan['tag']}] {clan['name']}\n"
                f"   ⭐ Уровень: {clan['level']} | 👥 {clan['member_count']} участников\n"
                f"   💰 Доход/час: {format_number(clan['total_income_per_hour'])} монет\n"
                f"   🏦 Казна: {format_number(clan['treasury'])} монет\n"
                f"   🎯 Бонус: +{business_bonus}% к бизнесам\n\n"
            )
        
        top_text += "💡 <i>Создать клан: /к создать [ТЭГ] [название]</i>"
        
        return jsonify({
            'success': True,
            'message': top_text
        })
    
    def clan_deposit_command(self, user_id, amount_str):
        """Внесение денег в казну клана"""
        try:
            amount = int(amount_str)
            if amount <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Сумма должна быть положительным числом!'
                })
        except ValueError:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть числом!'
            })
        
        player = self.db.get_player(user_id)
        
        # Проверяем баланс игрока
        if player['balance'] < amount:
            return jsonify({
                'success': False,
                'message': f'❌ Недостаточно средств на балансе!\n💰 Нужно: {format_number(amount)} монет\n💳 У вас: {format_number(player["balance"])} монет'
            })
        
        result = self.db.deposit_to_clan_treasury(user_id, amount)
        
        if result['success']:
            clan = self.db.get_player_clan(user_id)
            
            return jsonify({
                'success': True,
                'message': f'💰 <b>Деньги внесены в казну клана!</b>\n\n'
                          f'🏰 Клан: <b>[{clan["tag"]}] {clan["name"]}</b>\n'
                          f'💸 Внесено: <b>{format_number(amount)} монет</b>\n'
                          f'🏦 Новая казна: <b>{format_number(clan["treasury"])} монет</b>\n'
                          f'💳 Ваш баланс: <b>{format_number(player["balance"] - amount)} монет</b>\n\n'
                          f'📈 <i>Деньги из казны можно использовать для улучшения клана</i>'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'❌ {result["error"]}'
            })
    
    # ======================
    # АДМИН КОМАНДЫ КЛАНОВ
    # ======================
    
    def admin_rename_clan_command(self, user_id, tag, new_name):
        """Принудительная смена названия клана администратором"""
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут изменять названия кланов!'
            })
        
        # Проверяем название клана
        if len(new_name) < 3 or len(new_name) > 20:
            return jsonify({
                'success': False,
                'message': '❌ Название клана должно быть от 3 до 20 символов!'
            })
        
        result = self.db.update_clan_name(tag, new_name, user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': f'✅ <b>Название клана изменено!</b>\n\n'
                          f'🔰 Тег: <b>[{tag.upper()}]</b>\n'
                          f'📝 Старое название: <b>{result["old_name"]}</b>\n'
                          f'🏷️ Новое название: <b>{result["new_name"]}</b>\n'
                          f'👮 Изменил: <b>Администратор</b>'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'❌ {result["error"]}'
            })
    
    def admin_delete_clan_command(self, user_id, tag):
        """Удаление клана администратором"""
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут удалять кланы!'
            })
        
        clan = self.db.get_clan_by_tag(tag)
        if not clan:
            return jsonify({
                'success': False,
                'message': f'❌ Клан с тегом [{tag.upper()}] не найден!'
            })
        
        # Проверяем, не находится ли подтверждение в ожидании
        if tag.upper() in self.pending_deletions:
            # Подтверждаем удаление
            result = self.db.delete_clan(tag, user_id)
            
            if result['success']:
                del self.pending_deletions[tag.upper()]
                
                return jsonify({
                    'success': True,
                    'message': f'🗑️ <b>Клан удален!</b>\n\n'
                              f'🔰 Тег: <b>[{tag.upper()}]</b>\n'
                              f'🏷️ Название: <b>{clan["name"]}</b>\n'
                              f'👥 Участников исключено: <b>{result["member_count"]}</b>\n'
                              f'💰 Утеряно из казны: <b>{format_number(clan["treasury"])} монет</b>\n'
                              f'👮 Удалил: <b>Администратор</b>'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'❌ {result["error"]}'
                })
        else:
            # Запрашиваем подтверждение
            self.pending_deletions[tag.upper()] = {
                'admin_id': user_id,
                'clan_name': clan['name'],
                'timestamp': datetime.now()
            }
            
            member_count = self.db.get_clan_member_count(clan['id'])
            
            return jsonify({
                'success': False,
                'message': f'⚠️ <b>ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ КЛАНА</b>\n\n'
                          f'🔰 Тег: <b>[{tag.upper()}]</b>\n'
                          f'🏷️ Название: <b>{clan["name"]}</b>\n'
                          f'👑 Владелец: <b>ID: {clan["owner_id"]}</b>\n'
                          f'👥 Участников: <b>{member_count}</b>\n'
                          f'💰 Казна: <b>{format_number(clan["treasury"])} монет</b>\n'
                          f'📅 Существует: <b>{(datetime.now() - datetime.fromisoformat(clan["created_at"])).days} дней</b>\n\n'
                          f'❗ <b>ВНИМАНИЕ!</b>\n'
                          f'• Все участники будут исключены\n'
                          f'• Казна будет утеряна\n'
                          f'• Действие необратимо!\n\n'
                          f'✅ <b>Для подтверждения отправьте команду еще раз:</b>\n'
                          f'<code>/акудалить {tag.upper()}</code>'
            })
    
    def admin_clan_info_command(self, user_id, tag):
        """Подробная информация о клане для администратора"""
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        clan = self.db.get_clan_by_tag(tag)
        if not clan:
            return jsonify({
                'success': False,
                'message': f'❌ Клан с тегом [{tag.upper()}] не найден!'
            })
        
        # Получаем участников
        members = self.db.get_clan_members(clan['id'], 50)
        
        # Получаем владельца
        owner = self.db.get_player(clan['owner_id'])
        
        # Получаем лог операций
        log = self.db.get_clan_treasury_log(clan['id'], 10)
        
        # Рассчитываем бонусы
        business_bonus = 5 + (clan['level'] - 1)
        
        # Форматируем информацию об участниках
        members_text = ""
        for i, member in enumerate(members[:15], 1):
            role_emoji = "👑" if member['role'] == 'owner' else ("⭐" if member['role'] == 'officer' else "👤")
            join_date = datetime.fromisoformat(member['joined_at']).strftime("%d.%m")
            members_text += f"{i}. {role_emoji} <b>{member['username']}</b> (ID: {member['user_id']}) - {format_number(member['contributions'])} монет ({join_date})\n"
        
        # Форматируем лог операций
        log_text = ""
        for entry in log:
            action_emoji = "➕" if entry['action_type'] == 'deposit' else ("⬆️" if entry['action_type'] == 'upgrade' else "💰")
            username = entry['username'] or "Система"
            time_str = datetime.fromisoformat(entry['created_at']).strftime("%d.%m %H:%M")
            log_text += f"• {action_emoji} {entry['description']} - {username} ({time_str})\n"
        
        # Форматируем даты
        created_date = datetime.fromisoformat(clan['created_at']).strftime("%d.%m.%Y %H:%M")
        days_exist = (datetime.now() - datetime.fromisoformat(clan['created_at'])).days
        
        response_text = (
            f"📊 <b>ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О КЛАНЕ [{clan['tag']}]</b>\n\n"
            f"🏷️ Название: <b>{clan['name']}</b>\n"
            f"👑 Владелец: <b>{owner['username'] if owner else 'Не найден'} (ID: {clan['owner_id']})</b>\n"
            f"⭐ Уровень: <b>{clan['level']}</b>\n"
            f"💰 Казна: <b>{format_number(clan['treasury'])} монет</b>\n"
            f"👥 Участников: <b>{len(members)}</b>\n"
            f"📈 Доход/час: <b>{format_number(clan['total_income_per_hour'])} монет</b>\n"
            f"💪 Всего поднятий: <b>{format_number(clan['total_lifts'])}</b>\n"
            f"📅 Создан: <b>{created_date}</b> ({days_exist} дней)\n"
            f"🎯 Бонус: <b>+{business_bonus}% к бизнесам</b>\n\n"
            f"🏆 <b>Участники (топ-15):</b>\n{members_text}\n"
            f"📜 <b>Последние операции с казной:</b>\n{log_text}\n"
            f"👮 <b>Административные команды:</b>\n"
            f"• /аксменить {clan['tag']} [новое_название]\n"
            f"• /акудалить {clan['tag']}"
        )
        
        return jsonify({
            'success': True,
            'message': response_text
        })
    
    # ======================
    # КОМАНДА ПЕРЕВОДА ДЕНЕГ
    # ======================
    
    def transfer_money_command(self, user_id, target_username, amount_str):
        """Перевод денег другому игроку"""
        try:
            amount = int(amount_str)
            if amount <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Сумма перевода должна быть положительным числом!'
                })
        except ValueError:
            return jsonify({
                'success': False,
                'message': '❌ Сумма перевода должна быть числом!'
            })
        
        player = self.db.get_player(user_id)
        
        # Проверяем баланс игрока
        if player['balance'] < amount:
            return jsonify({
                'success': False,
                'message': f'❌ Недостаточно средств для перевода!\n💰 Нужно: {format_number(amount)} монет\n💳 У вас: {format_number(player["balance"])} монет'
            })
        
        # Минимальная сумма перевода
        if amount < 10:
            return jsonify({
                'success': False,
                'message': '❌ Минимальная сумма перевода - 10 монет!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Нельзя переводить самому себе
        if target_id == user_id:
            return jsonify({
                'success': False,
                'message': '❌ Нельзя переводить деньги самому себе!'
            })
        
        target_player = self.db.get_player(target_id)
        
        # Проверяем, не забанен ли получатель
        if target_player.get('is_banned', 0) == 1:
            return jsonify({
                'success': False,
                'message': '❌ Нельзя переводить деньги забаненному игроку!'
            })
        
        # Комиссия 5%
        commission = max(1, int(amount * 0.05))
        net_amount = amount - commission
        
        try:
            # Снимаем деньги у отправителя
            self.db.update_player_balance(
                user_id,
                -amount,
                'money_transfer_sent',
                f'Перевод игроку {target_username}',
                None,
                target_id
            )
            
            # Зачисляем деньги получателю (за вычетом комиссии)
            self.db.update_player_balance(
                target_id,
                net_amount,
                'money_transfer_received',
                f'Перевод от игрока {player["username"]}',
                None,
                user_id
            )
            
            # Комиссия уходит в "никуда" (можно изменить на сбор в какую-то систему)
            
            return jsonify({
                'success': True,
                'message': f'💸 <b>Перевод выполнен успешно!</b>\n\n'
                          f'👤 Отправитель: <b>{player["username"]}</b>\n'
                          f'👥 Получатель: <b>{target_username}</b>\n'
                          f'💰 Сумма: <b>{format_number(amount)} монет</b>\n'
                          f'📊 Комиссия (5%): <b>{format_number(commission)} монет</b>\n'
                          f'💳 Зачислено: <b>{format_number(net_amount)} монет</b>\n'
                          f'🏦 Ваш баланс: <b>{format_number(player["balance"] - amount)} монет</b>\n\n'
                          f'✅ <i>Деньги успешно переведены!</i>'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'❌ Ошибка при выполнении перевода: {str(e)}'
            })
    
    # ======================
    # КОМАНДЫ ПРОМОКОДОВ
    # ======================
    
    def create_promo_command(self, user_id, args):
        """Создание промокода"""
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут создавать промокоды!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите параметры промокода!\n📝 Использование: /создатьпромокод [код] [использования] [тип_награды] [сумма]\n\nТипы наград: монеты, магнезия\nПример: /создатьпромокод NEWYEAR2024 100 монеты 5000'
            })
        
        parts = args.split()
        if len(parts) < 4:
            return jsonify({
                'success': False,
                'message': '❌ Недостаточно параметров!\n📝 Использование: /создатьпромокод [код] [использования] [тип_награды] [сумма]'
            })
        
        code = parts[0].upper()
        
        try:
            uses_total = int(parts[1])
            if uses_total <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Количество использований должно быть положительным числом!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Количество использований должно быть числом!'
            })
        
        reward_type = parts[2].lower()
        if reward_type not in ['монеты', 'магнезия']:
            return jsonify({
                'success': False,
                'message': '❌ Неверный тип награды!\n✅ Допустимые типы: монеты, магнезия'
            })
        
        try:
            reward_amount = int(parts[3])
            if reward_amount <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Сумма награды должна быть положительным числом!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Сумма награды должна быть числом!'
            })
        
        # Проверяем срок действия (опциональный 5-й параметр)
        expires_days = None
        if len(parts) > 4:
            try:
                expires_days = int(parts[4])
                if expires_days <= 0:
                    return jsonify({
                        'success': False,
                        'message': '❌ Срок действия должен быть положительным числом дней!'
                    })
            except:
                return jsonify({
                    'success': False,
                    'message': '❌ Срок действия должен быть числом дней!'
                })
        
        if self.db.create_promo_code(code, uses_total, reward_type, reward_amount, user_id, expires_days):
            if expires_days:
                expires_date = (datetime.now() + timedelta(days=expires_days)).strftime("%d.%m.%Y")
                expires_text = f"⏳ Срок действия: <b>{expires_days} дней</b> (до {expires_date})"
            else:
                expires_text = "⏳ Срок действия: <b>Не ограничен</b>"
            
            return jsonify({
                'success': True,
                'message': f'🎫 <b>Промокод создан!</b>\n\n'
                          f'🔑 Код: <b>{code}</b>\n'
                          f'🎯 Использований: <b>{uses_total}</b>\n'
                          f'💰 Награда: <b>{format_number(reward_amount)} {reward_type}</b>\n'
                          f'{expires_text}\n\n'
                          f'📢 <i>Игроки могут активировать промокод командой:</i>\n'
                          f'<code>/промо {code}</code>'
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ Промокод с таким кодом уже существует!'
            })
    
    def delete_promo_command(self, user_id, args):
        """Удаление промокода"""
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут удалять промокоды!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите код промокода!\n📝 Использование: /удалитьпромокод [код]'
            })
        
        code = args.upper()
        promo_info = self.db.get_promo_info(code)
        
        if not promo_info:
            return jsonify({
                'success': False,
                'message': f'❌ Промокод <b>{code}</b> не найден!'
            })
        
        self.db.delete_promo_code(code, user_id)
        
        return jsonify({
            'success': True,
            'message': f'🗑️ <b>Промокод удален!</b>\n\n'
                      f'🔑 Код: <b>{code}</b>\n'
                      f'🔄 Использовано: <b>{promo_info["uses_total"] - promo_info["uses_left"]}/{promo_info["uses_total"]}</b>\n'
                      f'👮 Удалил: <b>Администратор</b>'
        })
    
    def promo_info_command(self, user_id, args):
        """Информация о промокоде"""
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите код промокода!\n📝 Использование: /промоинфо [код]'
            })
        
        code = args.upper()
        promo_info = self.db.get_promo_info(code)
        
        if not promo_info:
            return jsonify({
                'success': False,
                'message': f'❌ Промокод <b>{code}</b> не найден!'
            })
        
        # Получаем информацию о создателе
        creator = self.db.get_player(promo_info['created_by'])
        creator_name = creator['username'] if creator else f"ID: {promo_info['created_by']}"
        
        # Форматируем даты
        created_at = datetime.fromisoformat(promo_info['created_at']).strftime("%d.%m.%Y %H:%M")
        
        expires_text = "⏳ Срок: <b>Не ограничен</b>"
        if promo_info['expires_at']:
            expires_date = datetime.fromisoformat(promo_info['expires_at'])
            expires_text = f"⏳ Срок: <b>до {expires_date.strftime("%d.%m.%Y")}</b>"
            
            if datetime.now() > expires_date:
                expires_text += " ⚠️ <i>Истек</i>"
        
        status = "✅ Активен" if promo_info['is_active'] == 1 else "❌ Неактивен"
        
        info_text = (
            f"🎫 <b>ИНФОРМАЦИЯ О ПРОМОКОДЕ</b>\n\n"
            f"🔑 Код: <b>{promo_info['code']}</b>\n"
            f"📊 Статус: <b>{status}</b>\n\n"
            f"🎯 Использования:\n"
            f"├─ Всего: <b>{promo_info['uses_total']}</b>\n"
            f"├─ Осталось: <b>{promo_info['uses_left']}</b>\n"
            f"└─ Использовано: <b>{promo_info['uses_total'] - promo_info['uses_left']}</b>\n\n"
            f"💰 Награда: <b>{format_number(promo_info['reward_amount'])} {promo_info['reward_type']}</b>\n\n"
            f"👤 Создатель: <b>{creator_name}</b>\n"
            f"📅 Создан: <b>{created_at}</b>\n"
            f"{expires_text}\n\n"
            f"💡 <i>Для активации: /промо {promo_info['code']}</i>"
        )
        
        # Если администратор - показываем дополнительную информацию
        if self.is_admin(user_id):
            cursor = self.db.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM promo_uses WHERE promo_code = ?', (code,))
            total_uses = cursor.fetchone()[0]
            
            cursor.execute('SELECT user_id FROM promo_uses WHERE promo_code = ? LIMIT 5', (code,))
            recent_users = cursor.fetchall()
            
            users_text = "Нет использований"
            if recent_users:
                user_names = []
                for user_id in recent_users:
                    user = self.db.get_player(user_id[0])
                    if user:
                        user_names.append(user['username'])
                users_text = ", ".join(user_names[:5])
                if total_uses > 5:
                    users_text += f" и еще {total_uses - 5}"
            
            info_text += f"\n\n📊 <b>Статистика (только для админов):</b>\n" \
                         f"👥 Всего активаций: <b>{total_uses}</b>\n" \
                         f"👤 Последние активаторы: <b>{users_text}</b>"
        
        return jsonify({
            'success': True,
            'message': info_text
        })
    
    def use_promo_command(self, user_id, args):
        """Использование промокода"""
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите код промокода!\n📝 Использование: /промо [код]'
            })
        
        code = args.upper()
        result = self.db.use_promo_code(user_id, code)
        
        if result['success']:
            player = self.db.get_player(user_id)
            
            if result['reward_type'] == 'монеты':
                new_balance = player['balance']
                reward_text = f"💰 <b>{format_number(result['reward_amount'])} монет</b>\n📈 Новый баланс: <b>{format_number(new_balance)} монет</b>"
            else:
                new_magnesia = player['magnesia']
                reward_text = f"💎 <b>{format_number(result['reward_amount'])} банок магнезии</b>\n📈 Новый баланс: <b>{format_number(new_magnesia)} банок</b>"
            
            return jsonify({
                'success': True,
                'message': f'🎉 <b>Промокод активирован!</b>\n\n'
                          f'🔑 Код: <b>{code}</b>\n'
                          f'🎁 Получено: {reward_text}\n\n'
                          f'✅ <i>Награда успешно зачислена на ваш счет!</i>'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'❌ <b>Не удалось активировать промокод</b>\n\n'
                          f'🔑 Код: <b>{code}</b>\n'
                          f'📝 Причина: <b>{result["error"]}</b>'
            })
    
    # ======================
    # ОСТАЛЬНЫЕ МЕТОДЫ (остаются без изменений)
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
            "4. Создай или вступи в клан (/к создать)\n"
            "5. Соревнуйся с другими (/топ)\n\n"
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
        
        # Информация о клане
        clan_info = ""
        if player['clan_id']:
            clan = self.db.get_clan_by_id(player['clan_id'])
            if clan:
                clan_info = f"🏰 Клан: <b>[{clan['tag']}] {clan['name']}</b>\n"
        
        profile_text = (
            f"👤 <b>Профиль игрока #{player['user_id']}</b>\n\n"
            f"💪 Ник: <b>{player['username']}</b>\n"
            f"💎 Привилегии: <b>{privileges}</b>\n"
            f"{clan_info}"
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
                'privileges': privileges,
                'clan_id': player['clan_id']
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
            "📈 <b>/топ заработка</b> - топ по общему заработку\n"
            "🏰 <b>/к топ</b> - топ кланов\n\n"
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
            "🏰 <b>Кланы:</b>",
            "├── /к создать [ТЭГ] [название] - создать клан (1000 монет)",
            "├── /к улучшить - улучшить уровень клана",
            "├── /к казна - посмотреть казну клана",
            "├── /к профиль - информация о клане",
            "├── /к топ - топ кланов",
            "└── /к положить [сумма] - положить деньги в казну\n",
            "💸 <b>Перевод денег:</b>",
            "├── /перевод [игрок] [сумма] - перевести деньги",
            "└── /перевести [игрок] [сумма] - перевести деньги\n",
            "🎫 <b>Промокоды:</b>",
            "└── /промо [код] - активировать промокод\n",
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
            "• Кланы дают бонусы к доходу",
            "• Соревнуйтесь с другими игроками!"
        ]
        
        return jsonify({
            'success': True,
            'message': '\n'.join(commands)
        })
    
    # ======================
    # БИЗНЕС КОМАНДЫ (остаются без изменений)
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
    # АДМИН КОМАНДЫ (остаются без изменений)
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
            f"🏋️‍♂️ Гантелей установлено: {player.get('dumbbell_sets_given', 0)}",
            f"📝 Ников изменено: {player.get('nickname_changes_given', 0)}"
        ]
        
        panel_text = (
            f"🏛️ <b>АДМИНИСТРАТИВНАЯ ПАНЕЛЬ</b>\n\n"
            f"👤 Ваш ник: <b>{player['username']}</b>\n"
            f"💎 Должность: <b>{position}</b>\n"
            f"🆔 Админ ID: <b>{admin_id}</b>\n"
            f"👑 Админ-ник: <b>{admin_nickname_display}</b>\n"
            f"📅 С должности: <b>{admin_since}</b>\n\n"
            f"📊 <b>Ваша статистика:</b>\n" +
            "\n".join(stats) +
            f"\n\n📝 <b>Доступные команды:</b>\n"
            f"• /админ - список всех админ команд\n"
            f"• /аник [ник] - установить админ-ник\n"
            f"• /назначить [ник] [уровень] - назначить админа\n"
            f"• /снять [ник] - снять с должности\n"
            f"• /статистика - статистика бота\n\n"
            f"💡 <i>Напишите /админ для полного списка команд</i>"
        )
        
        return jsonify({
            'success': True,
            'message': panel_text
        })
    
    def set_admin_nickname_command(self, user_id, nickname):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not nickname:
            return jsonify({
                'success': False,
                'message': '❌ Укажите админ-ник!\n📝 Использование: /аник [админ_ник]'
            })
        
        if len(nickname) > 15:
            return jsonify({
                'success': False,
                'message': '❌ Админ-ник не может быть длиннее 15 символов!'
            })
        
        self.db.set_admin_nickname(user_id, nickname)
        
        return jsonify({
            'success': True,
            'message': f'✅ Ваш админ-ник установлен: <b>{nickname} 👑</b>'
        })
    
    def make_admin_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут назначать администраторов!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока!\n📝 Использование: /назначить [ник] [уровень]\nУровни: 1 (админ), 2 (создатель)'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите уровень админа!\n📝 Использование: /назначить [ник] [уровень]'
            })
        
        target_username = parts[0]
        try:
            new_admin_level = int(parts[1])
            if new_admin_level not in [1, 2]:
                return jsonify({
                    'success': False,
                    'message': '❌ Уровень админа может быть только 1 или 2!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Уровень админа должен быть числом (1 или 2)!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Нельзя назначать уровень выше своего
        if new_admin_level > admin_level:
            return jsonify({
                'success': False,
                'message': f'❌ Вы не можете назначить уровень выше своего (ваш уровень: {admin_level})!'
            })
        
        # Проверяем, не является ли уже админом
        target_player = self.db.get_player(target_id)
        if target_player.get('admin_level', 0) > 0:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок "{target_username}" уже является администратором!'
            })
        
        # Назначаем админа
        admin_id = self.db.make_admin(target_id, user_id, new_admin_level)
        
        level_name = "Администратор" if new_admin_level == 1 else "Создатель🌟"
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Игрок назначен администратором!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'💎 Должность: <b>{level_name}</b>\n'
                      f'🆔 Админ ID: <b>{admin_id}</b>\n'
                      f'👮 Назначил: <b>Администратор</b>\n\n'
                      f'💡 <i>Игрок получил доступ к админ панели: /админпанель</i>'
        })
    
    def remove_admin_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут снимать администраторов!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник администратора!\n📝 Использование: /снять [ник_админа]'
            })
        
        target_username = args
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Администратор с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько администраторов с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Проверяем, является ли админом
        target_player = self.db.get_player(target_id)
        if target_player.get('admin_level', 0) == 0:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок "{target_username}" не является администратором!'
            })
        
        # Нельзя снимать самого себя
        if target_id == user_id:
            return jsonify({
                'success': False,
                'message': '❌ Нельзя снять с должности самого себя!'
            })
        
        # Нельзя снимать администраторов равного или высшего уровня
        if target_player['admin_level'] >= admin_level:
            return jsonify({
                'success': False,
                'message': f'❌ Вы не можете снять администратора равного или высшего уровня!'
            })
        
        # Снимаем с должности
        self.db.remove_admin(target_id, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Администратор снят с должности!</b>\n\n'
                      f'👤 Администратор: <b>{target_username}</b>\n'
                      f'💎 Бывшая должность: <b>Уровень {target_player["admin_level"]}</b>\n'
                      f'👮 Снял: <b>Администратор</b>\n\n'
                      f'⚠️ <i>Игрок лишился всех админ прав и статистики</i>'
        })
    
    def set_dumbbell_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и уровень гантели!\n📝 Использование: /лгантеля [ник] [уровень (1-20)]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите уровень гантели!\n📝 Использование: /лгантеля [ник] [уровень]'
            })
        
        target_username = parts[0]
        try:
            new_level = int(parts[1])
            if new_level < 1 or new_level > 20:
                return jsonify({
                    'success': False,
                    'message': '❌ Уровень гантели должен быть от 1 до 20!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Уровень гантели должен быть числом!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Устанавливаем уровень гантели
        if self.db.set_dumbbell_level(target_id, new_level, user_id):
            dumbbell_info = self.dumbbell_levels[new_level]
            
            return jsonify({
                'success': True,
                'message': f'✅ <b>Уровень гантели изменен!</b>\n\n'
                          f'👤 Игрок: <b>{target_username}</b>\n'
                          f'🏋️‍♂️ Новая гантеля: <b>{dumbbell_info["name"]}</b>\n'
                          f'⭐ Новый уровень: <b>{new_level}</b>\n'
                          f'💰 Доход за подход: <b>{dumbbell_info["income_per_use"]} монет</b>\n'
                          f'👮 Изменил: <b>Администратор</b>'
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ Ошибка при изменении уровня гантели!'
            })
    
    def remove_balance_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и сумму!\n📝 Использование: /-баланс [ник] [сумма]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите сумму!\n📝 Использование: /-баланс [ник] [сумма]'
            })
        
        target_username = parts[0]
        try:
            amount = int(parts[1])
            if amount <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Сумма должна быть положительным числом!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть числом!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Убираем баланс
        target_player = self.db.get_player(target_id)
        if target_player['balance'] < amount:
            amount = target_player['balance']  # Убираем весь баланс
        
        self.db.update_player_balance(
            target_id,
            -amount,
            'admin_remove_balance',
            f'Администратор убрал {amount} монет',
            user_id
        )
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Баланс уменьшен!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'💰 Убрано: <b>{format_number(amount)} монет</b>\n'
                      f'💳 Новый баланс: <b>{format_number(target_player["balance"] - amount)} монет</b>\n'
                      f'👮 Изменил: <b>Администратор</b>'
        })
    
    def add_balance_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и сумму!\n📝 Использование: /+баланс [ник] [сумма]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите сумму!\n📝 Использование: /+баланс [ник] [сумма]'
            })
        
        target_username = parts[0]
        try:
            amount = int(parts[1])
            if amount <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Сумма должна быть положительным числом!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть числом!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Добавляем баланс
        target_player = self.db.get_player(target_id)
        
        self.db.update_player_balance(
            target_id,
            amount,
            'admin_add_balance',
            f'Администратор добавил {amount} монет',
            user_id
        )
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Баланс увеличен!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'💰 Добавлено: <b>{format_number(amount)} монет</b>\n'
                      f'💳 Новый баланс: <b>{format_number(target_player["balance"] + amount)} монет</b>\n'
                      f'👮 Изменил: <b>Администратор</b>'
        })
    
    def ban_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока, дни и причину!\n📝 Использование: /бан [ник] [дни] [причина]\nПример: /бан BadPlayer 7 Оскорбления'
            })
        
        parts = args.split()
        if len(parts) < 3:
            return jsonify({
                'success': False,
                'message': '❌ Укажите дни и причину!\n📝 Использование: /бан [ник] [дни] [причина]'
            })
        
        target_username = parts[0]
        try:
            days = int(parts[1])
            if days < 1:
                return jsonify({
                    'success': False,
                    'message': '❌ Количество дней должно быть положительным числом!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Количество дней должно быть числом!'
            })
        
        reason = ' '.join(parts[2:])
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Нельзя банить администраторов
        target_player = self.db.get_player(target_id)
        if target_player.get('admin_level', 0) > 0:
            return jsonify({
                'success': False,
                'message': '❌ Нельзя забанить администратора! Используйте /снять'
            })
        
        # Баним игрока
        self.db.ban_player(target_id, days, reason, user_id)
        self.db.increment_admin_stat(user_id, 'bans')
        
        ban_until = (datetime.now() + timedelta(days=days)).strftime("%d.%m.%Y")
        
        return jsonify({
            'success': True,
            'message': f'🚫 <b>Игрок забанен!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'⏳ Срок: <b>{days} дней</b>\n'
                      f'📅 До: <b>{ban_until}</b>\n'
                      f'📝 Причина: <b>{reason}</b>\n'
                      f'👮 Забанил: <b>Администратор</b>'
        })
    
    def permaban_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и причину!\n📝 Использование: /пермбан [ник] [причина]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите причину!\n📝 Использование: /пермбан [ник] [причина]'
            })
        
        target_username = parts[0]
        reason = ' '.join(parts[1:])
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Нельзя банить администраторов
        target_player = self.db.get_player(target_id)
        if target_player.get('admin_level', 0) > 0:
            return jsonify({
                'success': False,
                'message': '❌ Нельзя забанить администратора! Используйте /снять'
            })
        
        # Баним навсегда (0 дней = пермабан)
        self.db.ban_player(target_id, 0, reason, user_id)
        self.db.increment_admin_stat(user_id, 'permabans')
        
        return jsonify({
            'success': True,
            'message': f'⛔ <b>Игрок забанен навсегда!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'📝 Причина: <b>{reason}</b>\n'
                      f'👮 Забанил: <b>Администратор</b>'
        })
    
    def unban_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник забаненного игрока!\n📝 Использование: /разбан [ник]'
            })
        
        target_username = args
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Проверяем, забанен ли игрок
        target_player = self.db.get_player(target_id)
        if target_player.get('is_banned', 0) == 0:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок "{target_username}" не забанен!'
            })
        
        # Разбаниваем игрока
        self.db.unban_player(target_id, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Игрок разбанен!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'👮 Разбанил: <b>Администратор</b>'
        })
    
    def delete_player_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и причину!\n📝 Использование: /удалить [ник] [причина]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите причину!\n📝 Использование: /удалить [ник] [причина]'
            })
        
        target_username = parts[0]
        reason = ' '.join(parts[1:])
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Нельзя удалять администраторов
        target_player = self.db.get_player(target_id)
        if target_player.get('admin_level', 0) > 0:
            return jsonify({
                'success': False,
                'message': '❌ Нельзя удалить администратора! Используйте /снять'
            })
        
        # Сохраняем запрос на удаление
        self.pending_deletions[target_id] = {
            'admin_id': user_id,
            'username': target_username,
            'reason': reason,
            'timestamp': datetime.now()
        }
        
        # Получаем статистику игрока
        created_date = datetime.fromisoformat(target_player['created_at']).strftime("%d.%m.%Y")
        days_exist = (datetime.now() - datetime.fromisoformat(target_player['created_at'])).days
        
        return jsonify({
            'success': False,
            'message': f'⚠️ <b>ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ ИГРОКА</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'🆔 ID: <b>{target_id}</b>\n'
                      f'💰 Баланс: <b>{format_number(target_player["balance"])} монет</b>\n'
                      f'🏋️‍♂️ Гантеля: <b>{target_player["dumbbell_name"]}</b>\n'
                      f'💪 Поднятий: <b>{format_number(target_player["total_lifts"])}</b>\n'
                      f'📅 Зарегистрирован: <b>{created_date}</b> ({days_exist} дней)\n\n'
                      f'📝 <b>Причина удаления:</b>\n{reason}\n\n'
                      f'❗ <b>ВНИМАНИЕ!</b> Это действие необратимо!\n'
                      f'• Аккаунт будет полностью удален\n'
                      f'• Баланс и прогресс будут утеряны\n\n'
                      f'✅ <b>Для подтверждения:</b> /удалить+\n'
                      f'❌ <b>Для отмены:</b> /удалить-'
        })
    
    def confirm_delete_command(self, user_id):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        # Проверяем, есть ли ожидающие удаления от этого админа
        target_id = None
        for tid, data in self.pending_deletions.items():
            if data['admin_id'] == user_id:
                target_id = tid
                break
        
        if not target_id:
            return jsonify({
                'success': False,
                'message': '❌ Нет ожидающих подтверждения удалений!'
            })
        
        data = self.pending_deletions[target_id]
        
        # Удаляем игрока
        self.db.delete_player(target_id, user_id)
        self.db.increment_admin_stat(user_id, 'deletions')
        
        # Удаляем из ожидающих
        del self.pending_deletions[target_id]
        
        return jsonify({
            'success': True,
            'message': f'🗑️ <b>Игрок удален!</b>\n\n'
                      f'👤 Игрок: <b>{data["username"]}</b>\n'
                      f'📝 Причина: <b>{data["reason"]}</b>\n'
                      f'👮 Удалил: <b>Администратор</b>'
        })
    
    def cancel_delete_command(self, user_id):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        # Проверяем, есть ли ожидающие удаления от этого админа
        target_id = None
        for tid, data in self.pending_deletions.items():
            if data['admin_id'] == user_id:
                target_id = tid
                break
        
        if not target_id:
            return jsonify({
                'success': False,
                'message': '❌ Нет ожидающих подтверждения удалений!'
            })
        
        data = self.pending_deletions[target_id]
        
        # Отменяем удаление
        del self.pending_deletions[target_id]
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Удаление отменено!</b>\n\n'
                      f'👤 Игрок: <b>{data["username"]}</b>\n'
                      f'📝 Причина отмены: <b>Администратор отменил удаление</b>'
        })
    
    def change_player_username_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите старый и новый ник!\n📝 Использование: /сгник [старый_ник] [новый_ник]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите новый ник!\n📝 Использование: /сгник [старый_ник] [новый_ник]'
            })
        
        old_username = parts[0]
        new_username = ' '.join(parts[1:])
        
        # Проверяем новый ник
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
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(old_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{old_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{old_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Меняем ник
        self.db.update_username(target_id, new_username)
        self.db.increment_admin_stat(user_id, 'nickname_changes')
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Ник игрока изменен!</b>\n\n'
                      f'👤 Игрок: <b>{old_username} → {new_username}</b>\n'
                      f'👮 Изменил: <b>Администратор</b>'
        })
    
    def set_lifts_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и количество поднятий!\n📝 Использование: /поднятия [ник] [количество]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите количество поднятий!\n📝 Использование: /поднятия [ник] [количество]'
            })
        
        target_username = parts[0]
        try:
            new_total = int(parts[1])
            if new_total < 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Количество поднятий не может быть отрицательным!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Количество поднятий должно быть числом!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Устанавливаем количество поднятий
        self.db.set_total_lifts(target_id, new_total, user_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Количество поднятий изменено!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'💪 Новое количество: <b>{format_number(new_total)} поднятий</b>\n'
                      f'👮 Изменил: <b>Администратор</b>'
        })
    
    def set_custom_income_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и сумму дохода!\n📝 Использование: /заработок [ник] [сумма]\nДля сброса: /заработок [ник] сброс'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите сумму дохода!\n📝 Использование: /заработок [ник] [сумма]'
            })
        
        target_username = parts[0]
        income_str = parts[1]
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        if income_str.lower() == 'сброс':
            # Сбрасываем кастомный доход
            custom_income = None
            message = f'✅ <b>Кастомный доход сброшен!</b>\n\n👤 Игрок: <b>{target_username}</b>\n💰 Теперь используется доход от гантели\n👮 Сбросил: <b>Администратор</b>'
        else:
            try:
                custom_income = int(income_str)
                if custom_income < 1:
                    return jsonify({
                        'success': False,
                        'message': '❌ Доход должен быть положительным числом!'
                    })
                message = f'✅ <b>Кастомный доход установлен!</b>\n\n👤 Игрок: <b>{target_username}</b>\n💰 Новый доход за подход: <b>{format_number(custom_income)} монет</b>\n👮 Установил: <b>Администратор</b>'
            except:
                return jsonify({
                    'success': False,
                    'message': '❌ Доход должен быть числом или "сброс"!'
                })
        
        # Устанавливаем кастомный доход
        self.db.set_custom_income(target_id, custom_income, user_id)
        
        return jsonify({
            'success': True,
            'message': message
        })
    
    def add_magnesia_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и количество банок!\n📝 Использование: /банки [ник] [количество]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите количество банок!\n📝 Использование: /банки [ник] [количество]'
            })
        
        target_username = parts[0]
        try:
            amount = int(parts[1])
            if amount <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Количество банок должно быть положительным числом!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Количество банок должно быть числом!'
            })
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        target_id = target_ids[0]
        
        # Добавляем магнезию
        self.db.add_magnesia(target_id, amount, user_id)
        target_player = self.db.get_player(target_id)
        
        return jsonify({
            'success': True,
            'message': f'✅ <b>Банки магнезии добавлены!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'💎 Добавлено: <b>{format_number(amount)} банок</b>\n'
                      f'🏦 Новый баланс: <b>{format_number(target_player["magnesia"])} банок</b>\n'
                      f'👮 Выдал: <b>Администратор</b>'
        })
    
    def bot_statistics_command(self, user_id):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут просматривать статистику бота!'
            })
        
        cursor = self.db.conn.cursor()
        
        # Статистика игроков
        cursor.execute('SELECT COUNT(*) FROM players')
        total_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM players WHERE is_banned = 1')
        banned_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM players WHERE admin_level > 0')
        admin_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(balance) FROM players')
        total_balance = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(total_lifts) FROM players')
        total_lifts = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(total_earned) FROM players')
        total_earned = cursor.fetchone()[0] or 0
        
        # Статистика кланов
        cursor.execute('SELECT COUNT(*) FROM clans')
        total_clans = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(treasury) FROM clans')
        total_clan_treasury = cursor.fetchone()[0] or 0
        
        # Статистика промокодов
        cursor.execute('SELECT COUNT(*) FROM promo_codes')
        total_promos = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(uses_total - uses_left) FROM promo_codes')
        total_promo_uses = cursor.fetchone()[0] or 0
        
        # Последние регистрации
        cursor.execute('SELECT username, created_at FROM players ORDER BY created_at DESC LIMIT 5')
        recent_players = cursor.fetchall()
        
        recent_text = ""
        for i, (username, created_at) in enumerate(recent_players, 1):
            date_str = datetime.fromisoformat(created_at).strftime("%d.%m %H:%M")
            recent_text += f"{i}. <b>{username}</b> ({date_str})\n"
        
        stats_text = (
            f"📊 <b>СТАТИСТИКА БОТА GYM LEGEND</b>\n\n"
            f"👥 <b>Игроки:</b>\n"
            f"├─ Всего игроков: <b>{total_players}</b>\n"
            f"├─ Забанено: <b>{banned_players}</b>\n"
            f"├─ Администраторов: <b>{admin_players}</b>\n"
            f"├─ Активных: <b>{total_players - banned_players}</b>\n"
            f"├─ Общий баланс: <b>{format_number(total_balance)} монет</b>\n"
            f"├─ Всего поднятий: <b>{format_number(total_lifts)}</b>\n"
            f"└─ Всего заработано: <b>{format_number(total_earned)} монет</b>\n\n"
            f"🏰 <b>Кланы:</b>\n"
            f"├─ Всего кланов: <b>{total_clans}</b>\n"
            f"└─ Общая казна: <b>{format_number(total_clan_treasury)} монет</b>\n\n"
            f"🎫 <b>Промокоды:</b>\n"
            f"├─ Создано промокодов: <b>{total_promos}</b>\n"
            f"└─ Всего активаций: <b>{total_promo_uses}</b>\n\n"
            f"📈 <b>Последние регистрации:</b>\n{recent_text}"
        )
        
        return jsonify({
            'success': True,
            'message': stats_text
        })
    
    def reset_all_accounts_command(self, user_id):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут сбрасывать все аккаунты!'
            })
        
        # Сохраняем запрос на сброс
        self.pending_resets[user_id] = {
            'timestamp': datetime.now()
        }
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM players WHERE admin_level = 0')
        regular_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clans')
        total_clans = cursor.fetchone()[0]
        
        return jsonify({
            'success': False,
            'message': f'⚠️ <b>ПОДТВЕРЖДЕНИЕ СБРОСА ВСЕХ АККАУНТОВ</b>\n\n'
                      f'📊 <b>Статистика:</b>\n'
                      f'├─ Обычных игроков: <b>{regular_players}</b>\n'
                      f'├─ Кланов: <b>{total_clans}</b>\n'
                      f'└─ Администраторов: <b>Не будут затронуты</b>\n\n'
                      f'❗ <b>ВНИМАНИЕ! Это действие:</b>\n'
                      f'• Удалит ВСЕХ обычных игроков\n'
                      f'• Удалит ВСЕ кланы\n'
                      f'• Сбросит всю статистику\n'
                      f'• Администраторы НЕ будут удалены\n'
                      f'• Действие НЕОБРАТИМО!\n\n'
                      f'✅ <b>Для подтверждения:</b> /сбросвсех+\n'
                      f'❌ <b>Для отмены:</b> /сбросвсех-'
        })
    
    def confirm_reset_all_command(self, user_id):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        admin_level = self.get_admin_level(user_id)
        if admin_level < 2:
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы 2+ уровня могут сбрасывать все аккаунты!'
            })
        
        # Проверяем, есть ли запрос на сброс
        if user_id not in self.pending_resets:
            return jsonify({
                'success': False,
                'message': '❌ Нет ожидающих подтверждения сбросов!'
            })
        
        cursor = self.db.conn.cursor()
        
        # Считаем статистику перед удалением
        cursor.execute('SELECT COUNT(*) FROM players WHERE admin_level = 0')
        deleted_players = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM clans')
        deleted_clans = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(balance) FROM players WHERE admin_level = 0')
        deleted_balance = cursor.fetchone()[0] or 0
        
        # Удаляем обычных игроков
        cursor.execute('DELETE FROM players WHERE admin_level = 0')
        
        # Удаляем кланы (автоматически удалятся из-за внешних ключей)
        cursor.execute('DELETE FROM clans')
        
        # Очищаем связанные таблицы
        cursor.execute('DELETE FROM transactions')
        cursor.execute('DELETE FROM dumbbell_uses')
        cursor.execute('DELETE FROM promo_uses')
        cursor.execute('DELETE FROM clan_members')
        cursor.execute('DELETE FROM clan_treasury_log')
        cursor.execute('DELETE FROM clan_invites')
        
        self.db.conn.commit()
        
        # Удаляем запрос на сброс
        del self.pending_resets[user_id]
        
        return jsonify({
            'success': True,
            'message': f'🔄 <b>Все аккаунты сброшены!</b>\n\n'
                      f'📊 <b>Статистика удаления:</b>\n'
                      f'├─ Удалено игроков: <b>{deleted_players}</b>\n'
                      f'├─ Удалено кланов: <b>{deleted_clans}</b>\n'
                      f'├─ Утеряно монет: <b>{format_number(deleted_balance)}</b>\n'
                      f'└─ Администраторы: <b>Сохранены</b>\n\n'
                      f'✅ <i>Бот готов к новому сезону!</i>'
        })
    
    def cancel_reset_all_command(self, user_id):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        # Проверяем, есть ли запрос на сброс
        if user_id not in self.pending_resets:
            return jsonify({
                'success': False,
                'message': '❌ Нет ожидающих подтверждения сбросов!'
            })
        
        # Отменяем сброс
        del self.pending_resets[user_id]
        
        return jsonify({
            'success': True,
            'message': '✅ <b>Сброс всех аккаунтов отменен!</b>'
        })
    
    def send_message_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите ник игрока и сообщение!\n📝 Использование: /связь [ник] [сообщение]'
            })
        
        parts = args.split()
        if len(parts) < 2:
            return jsonify({
                'success': False,
                'message': '❌ Укажите сообщение!\n📝 Использование: /связь [ник] [сообщение]'
            })
        
        target_username = parts[0]
        message = ' '.join(parts[1:])
        
        # Ищем игрока
        target_ids = self.db.find_player_by_username(target_username)
        
        if not target_ids:
            return jsonify({
                'success': False,
                'message': f'❌ Игрок с ником "{target_username}" не найден!'
            })
        
        if len(target_ids) > 1:
            return jsonify({
                'success': False,
                'message': f'❌ Найдено несколько игроков с ником "{target_username}"! Уточните ник.'
            })
        
        # В реальном боте здесь был бы код отправки сообщения игроку
        # В этом примере просто возвращаем подтверждение
        
        return jsonify({
            'success': True,
            'message': f'📨 <b>Сообщение отправлено!</b>\n\n'
                      f'👤 Игрок: <b>{target_username}</b>\n'
                      f'📝 Сообщение: <b>{message}</b>\n'
                      f'👮 Отправил: <b>Администратор</b>\n\n'
                      f'💡 <i>Сообщение было доставлено игроку</i>'
        })
    
    def broadcast_message_command(self, user_id, args):
        if not self.is_admin(user_id):
            return jsonify({
                'success': False,
                'message': '❌ Только администраторы могут использовать эту команду!'
            })
        
        if not args:
            return jsonify({
                'success': False,
                'message': '❌ Укажите сообщение для рассылки!\n📝 Использование: /рассылка [сообщение]'
            })
        
        message = args
        
        cursor = self.db.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM players WHERE is_banned = 0')
        total_players = cursor.fetchone()[0]
        
        # В реальном боте здесь был бы код массовой рассылки
        # В этом примере просто возвращаем подтверждение
        
        return jsonify({
            'success': True,
            'message': f'📢 <b>Массовая рассылка запущена!</b>\n\n'
                      f'👥 Получателей: <b>{total_players} игроков</b>\n'
                      f'📝 Сообщение: <b>{message}</b>\n'
                      f'👮 Отправил: <b>Администратор</b>\n\n'
                      f'💡 <i>Сообщение отправлено всем активным игрокам</i>'
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
            "🎫 <b>Промокоды:</b>",
            "├── /создатьпромокод [код] [использования] [тип] [сумма] - создать промокод",
            "├── /удалитьпромокод [код] - удалить промокод",
            "└── /промоинфо [код] - информация о промокоде\n",
            "🏰 <b>Кланы (админ):</b>",
            "├── /аксменить [ТЭГ] [новое_название] - принудительно сменить название клана",
            "├── /акудалить [ТЭГ] - удалить клан",
            "└── /акинфо [ТЭГ] - подробная информация о клане\n",
            "🌟 <b>Особенные команды:</b>",
            "├── /назначить [ник] [уровень] - назначить админа",
            "├── /снять [ник] - снять с должности администратора",
            "├── /статистика - статистика бота (только создатель)",
            "├── /сбросвсех - сбросить все аккаунты (только создатель)",
            "├── /сбросвсех+ - подтвердить сброс",
            "└── /сбросвсех- - отменить сброс\n",
            "💡 <b>Игроки:</b>",
            "└── /промо [код] - активировать промокод\n",
            "⚠️ <b>Внимание:</b>",
            "• При удалении нужно указать причину",
            "• Для подтверждения/отмены используйте /удалить+ или /удалить-",
            "• /сбросвсех удалит ВСЕХ игроков кроме создателя",
            "• Все действия логируются"
        ]
        
        return jsonify({
            'success': True,
            'message': '\n'.join(commands)
        })

# ==============================
# FLASK РОУТЫ
# ==============================

bot = GymLegendBot()

@app.route('/')
def index():
    return "Gym Legend Bot is running!"

@app.route('/api/command', methods=['POST'])
def handle_api_command():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    command = data.get('command')
    
    if not all([user_id, username, command]):
        return jsonify({'success': False, 'message': 'Missing parameters'})
    
    return bot.handle_command(user_id, username, command)

if __name__ == '__main__':
    app.run(debug=True)
