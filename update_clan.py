# ==============================
# ОБНОВЛЕННАЯ СИСТЕМА КЛАНОВ
# ==============================

def get_clan_bonuses(self, clan_level):
    """Получение бонусов клана по уровню"""
    # Базовые бонусы: 5% к бизнесам и +1 монета за поднятие на 1 уровне
    business_bonus_percent = 5 + (clan_level - 1)  # 5% + (уровень-1)%
    lift_bonus_coins = 1 + (clan_level - 1)        # 1 + (уровень-1)
    
    return {
        'business_bonus_percent': business_bonus_percent,
        'lift_bonus_coins': lift_bonus_coins,
        'business_bonus_multiplier': 1 + (business_bonus_percent / 100)  # Множитель для расчетов
    }

def calculate_business_income_with_clan(self, player, business_id, base_income):
    """Расчет дохода от бизнеса с учетом клана (НОВАЯ СИСТЕМА)"""
    clan = self.db.get_player_clan(player['user_id'])
    
    if not clan:
        # Без клана - обычный доход
        return {
            'player_income': base_income,
            'clan_income': 0,
            'total_income': base_income
        }
    
    # Получаем бонусы клана
    clan_bonuses = self.get_clan_bonuses(clan['level'])
    
    # НОВАЯ СИСТЕМА: процент идет в казну клана
    clan_bonus_amount = base_income * clan_bonuses['business_bonus_percent'] / 100
    
    # Игрок получает только базовый доход
    player_income = base_income
    
    # Клан получает процент в казну
    clan_income = clan_bonus_amount
    
    return {
        'player_income': player_income,
        'clan_income': clan_income,
        'total_income': player_income + clan_income,
        'business_bonus_percent': clan_bonuses['business_bonus_percent'],
        'clan_bonus_amount': clan_bonus_amount
    }

def calculate_dumbbell_income_with_clan(self, player, base_income, power_gained):
    """Расчет дохода от поднятия гантели с учетом клана (НОВАЯ СИСТЕМА)"""
    clan = self.db.get_player_clan(player['user_id'])
    
    if not clan:
        # Без клана - обычный доход
        return {
            'player_income': base_income,
            'clan_income': 0,
            'total_income': base_income,
            'power_gained': power_gained,
            'clan_bonus': 0
        }
    
    # Получаем бонусы клана
    clan_bonuses = self.get_clan_bonuses(clan['level'])
    
    # Определяем дополнительный бонус в казну клана (зависит от уровня гантели)
    additional_clan_bonus = 0
    if player['dumbbell_level'] <= 4:
        additional_clan_bonus = 1
    elif player['dumbbell_level'] <= 9:
        additional_clan_bonus = 2
    elif player['dumbbell_level'] <= 14:
        additional_clan_bonus = 3
    else:
        additional_clan_bonus = 4
    
    # НОВАЯ СИСТЕМА:
    # 1. Игрок получает: базовый доход + бонус клана
    player_income = base_income + clan_bonuses['lift_bonus_coins']
    
    # 2. Клан получает в казну: бонус клана + дополнительный бонус
    clan_income = clan_bonuses['lift_bonus_coins'] + additional_clan_bonus
    
    return {
        'player_income': player_income,
        'clan_income': clan_income,
        'total_income': player_income + clan_income,
        'power_gained': power_gained,
        'clan_bonus_coins': clan_bonuses['lift_bonus_coins'],
        'additional_clan_bonus': additional_clan_bonus
    }

def collect_clan_income_hourly(self):
    """Ежечасный сбор доходов с бизнесов в казну кланов (НОВАЯ СИСТЕМА)"""
    cursor = self.db.conn.cursor()
    
    # Получаем всех игроков с бизнесами
    cursor.execute('''
        SELECT user_id, 
               COALESCE(business_1_level, 0) as b1_level,
               COALESCE(business_2_level, 0) as b2_level,
               COALESCE(business_3_level, 0) as b3_level,
               clan_id
        FROM players 
        WHERE (business_1_level > 0 OR business_2_level > 0 OR business_3_level > 0)
          AND clan_id IS NOT NULL
    ''')
    
    players = cursor.fetchall()
    
    total_collected = 0
    clan_collections = {}
    
    for player in players:
        user_id = player[0]
        clan_id = player[4]
        
        if not clan_id:
            continue
        
        # Рассчитываем общий доход от всех бизнесов игрока
        total_business_income = 0
        
        # Бизнес 1
        if player[1] > 0:
            business_income = self.businesses[1]['base_income'] + (player[1] - 1) * self.businesses[1]['income_increase']
            total_business_income += business_income
        
        # Бизнес 2
        if player[2] > 0:
            business_income = self.businesses[2]['base_income'] + (player[2] - 1) * self.businesses[2]['income_increase']
            total_business_income += business_income
        
        # Бизнес 3
        if player[3] > 0:
            business_income = self.businesses[3]['base_income'] + (player[3] - 1) * self.businesses[3]['income_increase']
            total_business_income += business_income
        
        if total_business_income > 0:
            # Получаем клан игрока
            clan = self.db.get_clan_by_id(clan_id)
            if clan:
                clan_bonuses = self.get_clan_bonuses(clan['level'])
                
                # Процент от дохода идет в казну клана
                clan_income = total_business_income * clan_bonuses['business_bonus_percent'] / 100
                
                # Добавляем в сборы клана
                if clan_id not in clan_collections:
                    clan_collections[clan_id] = 0
                clan_collections[clan_id] += clan_income
                
                total_collected += clan_income
    
    # Зачисляем собранные средства в казну кланов
    for clan_id, amount in clan_collections.items():
        if amount > 0:
            cursor.execute('UPDATE clans SET treasury = treasury + ? WHERE id = ?', 
                         (int(amount), clan_id))
            
            # Логируем сбор
            cursor.execute('''
                INSERT INTO clan_treasury_log (clan_id, action_type, amount, description)
                VALUES (?, ?, ?, ?)
            ''', (clan_id, 'business_income', int(amount), f'Ежечасный сбор с бизнесов участников'))
    
    self.db.conn.commit()
    return total_collected

def process_dumbbell_lift_with_clan(self, user_id):
    """Обработка поднятия гантели с учетом клана (НОВАЯ СИСТЕМА)"""
    player = self.db.get_player(user_id)
    clan = self.db.get_player_clan(user_id)
    
    if player.get('custom_income') is not None:
        base_income = player['custom_income']
        dumbbell_info = {'power_per_use': 1}  # Минимальная сила для кастомного дохода
    else:
        dumbbell_info = self.dumbbell_levels[player['dumbbell_level']]
        base_income = dumbbell_info['income_per_use']
    
    power_gained = dumbbell_info['power_per_use']
    
    # Рассчитываем доход с учетом клана
    income_calculation = self.calculate_dumbbell_income_with_clan(player, base_income, power_gained)
    
    # Зачисляем доход игроку
    self.db.update_player_balance(
        user_id,
        income_calculation['player_income'],
        'dumbbell_income',
        f'Подъем гантели {player["dumbbell_name"]} с бонусом клана'
    )
    
    # Зачисляем бонус в казну клана
    if clan and income_calculation['clan_income'] > 0:
        cursor = self.db.conn.cursor()
        cursor.execute('UPDATE clans SET treasury = treasury + ?, total_lifts = total_lifts + 1 WHERE id = ?',
                     (income_calculation['clan_income'], clan['id']))
        
        # Логируем вклад в казну
        cursor.execute('''
            INSERT INTO clan_treasury_log (clan_id, user_id, action_type, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (clan['id'], user_id, 'lift_income', income_calculation['clan_income'],
              f'Бонус от поднятия гантели игроком {player["username"]}'))
        
        self.db.conn.commit()
    
    # Обновляем время последнего поднятия и статистику
    self.db.add_power(user_id, power_gained)
    self.db.update_dumbbell_use_time(user_id)
    self.db.increment_total_lifts(user_id)
    self.db.log_dumbbell_use(user_id, player['dumbbell_level'], 
                           income_calculation['player_income'], power_gained)
    
    return income_calculation

# ==============================
# ОБНОВЛЕННЫЕ МЕТОДЫ ДЛЯ КОМАНД
# ==============================

def use_dumbbell(self, user_id):
    """Поднятие гантели (обновлено для новой системы)"""
    player = self.db.get_player(user_id)
    
    # Проверка кулдауна
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
    
    # Обрабатываем поднятие с новой системой кланов
    income_calculation = self.process_dumbbell_lift_with_clan(user_id)
    
    # Формируем сообщение
    clan = self.db.get_player_clan(user_id)
    message_parts = [
        f'💪 <b>Вы подняли гантелю {player["dumbbell_name"]}!</b>',
        f'💰 Получено: <b>{income_calculation["player_income"]} монет</b>',
        f'💪 Получено силы: <b>{income_calculation["power_gained"]}</b>',
        f'📈 Баланс: <b>{format_number(player["balance"] + income_calculation["player_income"])} монет</b>'
    ]
    
    if clan:
        message_parts.append(f'🏦 В казну клана: <b>+{income_calculation["clan_income"]} монет</b>')
        message_parts.append(f'⭐ Бонус клана: <b>+{income_calculation["clan_bonus_coins"]} монет</b>')
    
    return jsonify({
        'success': True,
        'message': '\n'.join(message_parts),
        'income': income_calculation['player_income'],
        'new_balance': player['balance'] + income_calculation['player_income'],
        'power_gained': income_calculation['power_gained'],
        'clan_bonus': income_calculation.get('clan_bonus_coins', 0),
        'clan_contribution': income_calculation.get('clan_income', 0)
    })

def get_business_info(self, user_id, business_id):
    """Информация о бизнесе (обновлено для новой системы)"""
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
    
    # Базовый доход бизнеса
    base_income = business['base_income'] + (business_level - 1) * business['income_increase']
    
    # Рассчитываем доход с учетом клана
    clan = self.db.get_player_clan(user_id)
    income_calculation = self.calculate_business_income_with_clan(player, business_id, base_income)
    
    completed_upgrades = sum(1 for v in upgrades.values() if v > 0)
    
    upgrade_text = ""
    for i in range(1, 6):
        level = upgrades.get(str(i), 0)
        upgrade_info = business['upgrades'][i]
        upgrade_text += f"\n{upgrade_info['emoji']} <b>{i}. {upgrade_info['name']}</b> (Уровень {level})"
    
    next_upgrade_price = business['upgrade_price'] + completed_upgrades * 50
    
    # Формируем информационное сообщение
    info_parts = [
        f"📊 <b>БИЗНЕС #{business_id}</b>",
        f"",
        f"✅ <b>{business['name']}</b>",
        f"",
        f"⏳ <b>Базовый доход:</b> {format_number(base_income)} банок магнезии/час"
    ]
    
    if clan:
        clan_bonuses = self.get_clan_bonuses(clan['level'])
        info_parts.extend([
            f"🏰 <b>Ваш клан:</b> [{clan['tag']}] {clan['name']}",
            f"⭐ <b>Бонус клана:</b> +{clan_bonuses['business_bonus_percent']}% к доходу",
            f"",
            f"📊 <b>Распределение дохода:</b>",
            f"├─ 👤 Вам: {format_number(income_calculation['player_income'])} магнезии/час",
            f"└─ 🏦 В казну клана: {format_number(income_calculation['clan_income'])} магнезии/час"
        ])
    else:
        info_parts.append(f"👤 <b>Ваш доход:</b> {format_number(income_calculation['player_income'])} магнезии/час")
    
    info_parts.extend([
        f"",
        f"📊 <b>Уровень бизнеса:</b> {business_level}",
        f"🏗️ <b>Улучшено этапов:</b> {completed_upgrades}/5",
        f"",
        f"{upgrade_text}",
        f"",
        f"🕐 <b>Накоплено магнезии:</b> {format_number(player['magnesia'])} банок",
        f"💰 <b>Следующее улучшение:</b> {format_number(next_upgrade_price)} {business['upgrade_currency']}",
        f"",
        f"💡 <i>Для улучшения: /б {business_id} [1-5] улучшить</i>"
    ])
    
    return jsonify({'success': True, 'message': '\n'.join(info_parts)})

def clan_profile_command(self, user_id):
    """Профиль клана (обновлено для новой системы)"""
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
    
    # Получаем бонусы клана
    clan_bonuses = self.get_clan_bonuses(clan['level'])
    
    # Форматируем дату создания
    created_date = datetime.fromisoformat(clan['created_at']).strftime("%d.%m.%Y")
    
    # Формируем сообщение
    response_parts = [
        f"🏰 <b>ПРОФИЛЬ КЛАНА [{clan['tag']}]</b>",
        f"",
        f"🏷️ Название: <b>{clan['name']}</b>",
        f"👑 Владелец: <b>{owner_name}</b>",
        f"⭐ Уровень: <b>{clan['level']}</b>",
        f"👥 Участников: <b>{member_count}</b>",
        f"💰 Казна: <b>{format_number(clan['treasury'])} монет</b>",
        f"📈 Доход/час с бизнесов: <b>~{format_number(clan['total_income_per_hour'])} магнезии</b>",
        f"💪 Всего поднятий участников: <b>{format_number(clan['total_lifts'])}</b>",
        f"📅 Основан: <b>{created_date}</b>",
        f"",
        f"🎯 <b>СИСТЕМА БОНУСОВ (НОВАЯ):</b>",
        f"",
        f"📊 <b>Для участников:</b>",
        f"├─ 🏋️ +{clan_bonuses['lift_bonus_coins']} монет за каждое поднятие",
        f"└─ 💼 Базовый доход от бизнесов (без бонуса)",
        f"",
        f"🏦 <b>Для казны клана:</b>",
        f"├─ 💼 +{clan_bonuses['business_bonus_percent']}% от доходов всех бизнесов",
        f"└─ 🏋️ +{clan_bonuses['lift_bonus_coins']} монет от каждого поднятия",
        f"",
        f"💡 <i>Команды клана: /к помощь</i>"
    ]
    
    return jsonify({
        'success': True,
        'message': '\n'.join(response_parts)
    })

# ==============================
# НОВЫЕ КОМАНДЫ ДЛЯ РАСПРЕДЕЛЕНИЯ КАЗНЫ
# ==============================

def clan_distribute_command(self, user_id, args):
    """Распределение казны клана между участниками"""
    clan = self.db.get_player_clan(user_id)
    if not clan:
        return jsonify({
            'success': False,
            'message': '❌ Вы не состоите в клане!'
        })
    
    # Проверяем права
    cursor = self.db.conn.cursor()
    cursor.execute('SELECT role FROM clan_members WHERE user_id = ? AND clan_id = ?', 
                   (user_id, clan['id']))
    member_role = cursor.fetchone()
    
    if not member_role or member_role[0] not in ['owner', 'officer']:
        return jsonify({
            'success': False,
            'message': '❌ Только владелец и офицеры могут распределять казну!'
        })
    
    if not args:
        return jsonify({
            'success': False,
            'message': '❌ Укажите тип распределения!\n📝 Использование: /к распределить [тип] [параметры]\n\nТипы:\n• всем [сумма] - выдать всем поровну\n• топ [сумма] [кол-во] - выдать топ-игрокам\n• процент [%] - выдать процент от казны'
        })
    
    parts = args.split()
    distribution_type = parts[0].lower()
    
    if distribution_type == 'всем' and len(parts) >= 2:
        # Распределение всем поровну
        try:
            amount_per_member = int(parts[1])
            if amount_per_member <= 0:
                return jsonify({
                    'success': False,
                    'message': '❌ Сумма должна быть положительной!'
                })
        except:
            return jsonify({
                'success': False,
                'message': '❌ Сумма должна быть числом!'
            })
        
        # Получаем всех участников
        members = self.db.get_clan_members(clan['id'])
        total_amount = amount_per_member * len(members)
        
        if clan['treasury'] < total_amount:
            return jsonify({
                'success': False,
                'message': f'❌ Недостаточно средств в казне!\n💰 Нужно: {format_number(total_amount)} монет\n🏦 В казне: {format_number(clan["treasury"])} монет'
            })
        
        # Распределяем деньги
        distributed = []
        for member in members:
            self.db.update_player_balance(
                member['user_id'],
                amount_per_member,
                'clan_distribution',
                f'Распределение из казны клана [{clan["tag"]}]',
                None
            )
            distributed.append(f"{member['username']}: {format_number(amount_per_member)} монет")
        
        # Снимаем деньги с казны
        cursor.execute('UPDATE clans SET treasury = treasury - ? WHERE id = ?',
                     (total_amount, clan['id']))
        
        # Логируем операцию
        cursor.execute('''
            INSERT INTO clan_treasury_log (clan_id, user_id, action_type, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (clan['id'], user_id, 'distribution', total_amount,
              f'Распределение {format_number(amount_per_member)} монет каждому участнику'))
        
        self.db.conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'💰 <b>Казна распределена!</b>\n\n'
                      f'🏰 Клан: <b>[{clan["tag"]}] {clan["name"]}</b>\n'
                      f'👥 Участников: <b>{len(members)}</b>\n'
                      f'💸 Каждому: <b>{format_number(amount_per_member)} монет</b>\n'
                      f'💰 Всего выдано: <b>{format_number(total_amount)} монет</b>\n'
                      f'🏦 Остаток в казне: <b>{format_number(clan["treasury"] - total_amount)} монет</b>\n\n'
                      f'📋 <b>Получили:</b>\n' + '\n'.join(distributed)
        })
    
    # Другие типы распределения можно добавить позже
    
    return jsonify({
        'success': False,
        'message': '❌ Неизвестный тип распределения!\n📝 Доступные типы:\n• всем [сумма] - выдать всем поровну'
    })
