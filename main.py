#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Mobile Money - Version Responsive & Mobile Optimisée
Compatible Android/iOS avec gestion dynamique des tailles d'écran
"""

import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import pygal
from io import BytesIO

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.utils import platform

# =============================================================================
# CONFIGURATION GLOBALE ET CONSTANTES RESPONSIVES
# =============================================================================

# Détection de la plateforme
IS_MOBILE = platform in ['android', 'ios']

# Couleurs
COLORS = {
    'PRIMARY': [0.129, 0.588, 0.953, 1],    # Bleu
    'SECONDARY': [0.961, 0.341, 0.133, 1],   # Orange
    'BACKGROUND': [0.95, 0.95, 0.95, 1],     # Gris clair
    'TEXT': [0.2, 0.2, 0.2, 1],             # Noir
    'WHITE': [1, 1, 1, 1],
    'ERROR': [0.9, 0.1, 0.1, 1],             # Rouge
    'SUCCESS': [0.2, 0.7, 0.2, 1],           # Vert
    'GRAY': [0.5, 0.5, 0.5, 1]
}

OPERATORS = ['Orange Money', 'Moov Money', 'Telecel', 'Wave', 'TNT']

# =============================================================================
# GESTION RESPONSIVE DES DIMENSIONS
# =============================================================================

class ResponsiveHelper:
    """Classe utilitaire pour gérer les dimensions adaptatives"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.screen_width = Window.width
        self.screen_height = Window.height
        self.is_small_screen = self.screen_width < dp(360)
        self.is_tablet = self.screen_width > dp(600)
        Window.bind(on_resize=self._on_resize)
    
    def _on_resize(self, window, width, height):
        self.screen_width = width
        self.screen_height = height
        self.is_small_screen = width < dp(360)
        self.is_tablet = width > dp(600)
    
    def get_padding(self):
        """Retourne le padding adaptatif"""
        if self.is_small_screen:
            return [dp(10), dp(10)]
        elif self.is_tablet:
            return [dp(40), dp(40)]
        return [dp(20), dp(20)]
    
    def get_spacing(self):
        """Retourne l'espacement adaptatif"""
        if self.is_small_screen:
            return dp(8)
        elif self.is_tablet:
            return dp(20)
        return dp(12)
    
    def get_font_size(self, base_size):
        """Retourne la taille de police adaptative"""
        if self.is_small_screen:
            return sp(base_size * 0.85)
        elif self.is_tablet:
            return sp(base_size * 1.1)
        return sp(base_size)
    
    def get_button_height(self):
        """Retourne la hauteur de bouton adaptative"""
        if self.is_small_screen:
            return dp(44)
        elif self.is_tablet:
            return dp(60)
        return dp(50)
    
    def get_input_height(self):
        """Retourne la hauteur de champ de saisie adaptative"""
        if self.is_small_screen:
            return dp(40)
        elif self.is_tablet:
            return dp(55)
        return dp(45)

# Instance globale
responsive = ResponsiveHelper()

# =============================================================================
# COMPOSANTS PERSONNALISÉS RESPONSIFS
# =============================================================================

class ResponsiveButton(Button):
    """Bouton avec style moderne et taille adaptive"""
    
    def __init__(self, **kwargs):
        # Extraire la couleur personnalisée avant l'init parent
        bg_color = kwargs.pop('bg_color', COLORS['PRIMARY'])
        super().__init__(**kwargs)
        
        self.background_color = [0, 0, 0, 0]  # Transparent pour canvas
        self.background_normal = ''
        self.background_down = ''
        self.bold = True
        self.color = COLORS['WHITE']
        
        # Taille adaptative
        self.size_hint_y = None
        self.height = responsive.get_button_height()
        self.font_size = responsive.get_font_size(16)
        
        # Canvas pour arrondi
        with self.canvas.before:
            Color(*bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[dp(12),]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class ResponsiveInput(TextInput):
    """Champ de saisie avec style moderne"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.multiline = False
        self.size_hint_y = None
        self.height = responsive.get_input_height()
        self.font_size = responsive.get_font_size(16)
        self.padding = [dp(15), (self.height - self.font_size) / 2]
        self.background_color = COLORS['WHITE']
        self.foreground_color = COLORS['TEXT']
        self.cursor_color = COLORS['PRIMARY']
        self.selection_color = [*COLORS['PRIMARY'][:3], 0.3]
        
        # Bordure
        with self.canvas.before:
            Color(0.8, 0.8, 0.8, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8),]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect, focus=self._on_focus)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def _on_focus(self, instance, value):
        # Changer la couleur de bordure selon le focus
        self.canvas.before.clear()
        with self.canvas.before:
            if value:
                Color(*COLORS['PRIMARY'])
            else:
                Color(0.8, 0.8, 0.8, 1)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8),]
            )

class Card(BoxLayout):
    """Carte avec ombre et bords arrondis"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = responsive.get_padding()
        self.spacing = responsive.get_spacing()
        
        with self.canvas.before:
            Color(*COLORS['WHITE'])
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15),]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# =============================================================================
# GESTION DE LA BASE DE DONNÉES (inchangée mais optimisée)
# =============================================================================

class DatabaseManager:
    
    DB_NAME = 'mobile_money.db'
    
    @classmethod
    def init_database(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                operator TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES users(id)
            )
        ''')
        
        # Admin par défaut
        c.execute("SELECT * FROM users WHERE username='admin'")
        if not c.fetchone():
            hashed = hashlib.sha256('admin123'.encode()).hexdigest()
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ('admin', hashed, 'admin')
            )
        
        conn.commit()
        conn.close()
    
    @classmethod
    def add_user(cls, username, password, role):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed, role)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @classmethod
    def get_user(cls, username, password):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        hashed = hashlib.sha256(password.encode()).hexdigest()
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed)
        )
        user = c.fetchone()
        conn.close()
        return user
    
    @classmethod
    def get_all_agents(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE role='agent' ORDER BY username")
        agents = c.fetchall()
        conn.close()
        return agents
    
    @classmethod
    def record_transaction(cls, agent_id, operator, trans_type, amount):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute('''
            INSERT INTO transactions (agent_id, operator, type, amount)
            VALUES (?, ?, ?, ?)
        ''', (agent_id, operator, trans_type, amount))
        conn.commit()
        conn.close()
    
    @classmethod
    def get_transactions_by_agent(cls, agent_id):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute('''
            SELECT operator, type, amount, timestamp 
            FROM transactions WHERE agent_id=?
            ORDER BY timestamp DESC
        ''', (agent_id,))
        trans = c.fetchall()
        conn.close()
        return trans
    
    @classmethod
    def get_all_transactions(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute('''
            SELECT t.operator, t.type, t.amount, t.timestamp, u.username 
            FROM transactions t 
            JOIN users u ON t.agent_id = u.id
            ORDER BY t.timestamp DESC
        ''')
        trans = c.fetchall()
        conn.close()
        return trans
    
    @classmethod
    def get_daily_summary(cls, days=7):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute('''
            SELECT 
                DATE(timestamp) AS date,
                operator,
                type,
                SUM(amount) AS total,
                COUNT(*) AS count
            FROM transactions
            WHERE timestamp >= date('now', '-{} days')
            GROUP BY date, operator, type
            ORDER BY date DESC
        '''.format(days))
        summary = c.fetchall()
        conn.close()
        return summary
    
    @classmethod
    def get_operator_summary(cls):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute('''
            SELECT
                operator,
                type,
                SUM(amount) AS total,
                COUNT(*) AS count
            FROM transactions
            GROUP BY operator, type
            ORDER BY operator, type
        ''')
        summary = c.fetchall()
        conn.close()
        return summary
    
    @classmethod
    def get_agent_balance(cls, agent_id):
        conn = sqlite3.connect(cls.DB_NAME)
        c = conn.cursor()
        c.execute('''
            SELECT 
                SUM(CASE WHEN type='Dépôt' THEN amount ELSE 0 END) as deposits,
                SUM(CASE WHEN type='Retrait' THEN amount ELSE 0 END) as withdrawals
            FROM transactions
            WHERE agent_id=?
        ''', (agent_id,))
        result = c.fetchone()
        conn.close()
        
        deposits = result[0] or 0
        withdrawals = result[1] or 0
        return {
            'deposits': deposits,
            'withdrawals': withdrawals,
            'balance': deposits - withdrawals
        }

# =============================================================================
# ÉCRANS DE L'APPLICATION
# =============================================================================

class BaseScreen(Screen):
    """Classe de base pour tous les écrans avec gestion responsive"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_background()
        Window.bind(on_resize=self._on_resize)
    
    def _setup_background(self):
        with self.canvas.before:
            Color(*COLORS['BACKGROUND'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _on_resize(self, window, width, height):
        # Rafraîchir l'affichage lors du redimensionnement
        Clock.schedule_once(self._refresh_layout, 0.1)
    
    def _refresh_layout(self, dt):
        pass  # À surcharger dans les classes filles
    
    def show_popup(self, title, message, msg_type='ERROR', auto_dismiss=True):
        """Affiche une popup moderne"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Icône ou indicateur visuel
        icon_color = COLORS['SUCCESS'] if msg_type == 'SUCCESS' else COLORS['ERROR']
        icon_text = '✓' if msg_type == 'SUCCESS' else '✕'
        
        icon_label = Label(
            text=icon_text,
            font_size=sp(40),
            color=icon_color,
            size_hint_y=None,
            height=dp(50)
        )
        content.add_widget(icon_label)
        
        # Message
        msg_label = Label(
            text=message,
            font_size=responsive.get_font_size(16),
            color=COLORS['TEXT'],
            size_hint_y=None,
            height=dp(60),
            text_size=(None, None),
            halign='center'
        )
        content.add_widget(msg_label)
        
        # Bouton
        btn = ResponsiveButton(
            text='OK',
            bg_color=COLORS['PRIMARY'],
            size_hint_y=None,
            height=responsive.get_button_height()
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, None),
            height=dp(250),
            auto_dismiss=auto_dismiss,
            title_color=COLORS['PRIMARY'],
            title_size=sp(18),
            separator_color=COLORS['PRIMARY']
        )
        
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        
        return popup

class LoginScreen(BaseScreen):
    """Écran de connexion optimisé pour mobile"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal avec défilement
        root = ScrollView(size_hint=(1, 1))
        
        # Container centré
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=max(dp(500), Window.height * 0.8),
            padding=responsive.get_padding(),
            spacing=responsive.get_spacing()
        )
        
        # Logo/Titre
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=0.35,
            spacing=dp(10)
        )
        
        title = Label(
            text='MOBILE MONEY',
            font_size=responsive.get_font_size(32),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=0.6
        )
        
        subtitle = Label(
            text='Gestion des transactions',
            font_size=responsive.get_font_size(14),
            color=COLORS['GRAY'],
            size_hint_y=0.4
        )
        
        header.add_widget(title)
        header.add_widget(subtitle)
        container.add_widget(header)
        
        # Carte de formulaire
        card = Card(size_hint_y=0.65)
        
        # Formulaire
        form_layout = BoxLayout(
            orientation='vertical',
            spacing=responsive.get_spacing(),
            padding=[dp(10), dp(20)]
        )
        
        # Champ utilisateur
        form_layout.add_widget(Label(
            text="Nom d'utilisateur",
            font_size=responsive.get_font_size(14),
            color=COLORS['TEXT'],
            size_hint_y=None,
            height=dp(30),
            halign='left',
            text_size=(None, None)
        ))
        
        self.username = ResponsiveInput(hint_text="Entrez votre nom d'utilisateur")
        form_layout.add_widget(self.username)
        
        # Champ mot de passe
        form_layout.add_widget(Label(
            text="Mot de passe",
            font_size=responsive.get_font_size(14),
            color=COLORS['TEXT'],
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        self.password = ResponsiveInput(
            hint_text="Entrez votre mot de passe",
            password=True
        )
        form_layout.add_widget(self.password)
        
        # Espace flexible
        form_layout.add_widget(Widget(size_hint_y=0.3))
        
        # Bouton connexion
        btn_login = ResponsiveButton(
            text='SE CONNECTER',
            bg_color=COLORS['PRIMARY'],
            on_press=self.authenticate
        )
        form_layout.add_widget(btn_login)
        
        # Version
        version_label = Label(
            text='v1.0.0',
            font_size=responsive.get_font_size(12),
            color=COLORS['GRAY'],
            size_hint_y=None,
            height=dp(20)
        )
        form_layout.add_widget(version_label)
        
        card.add_widget(form_layout)
        container.add_widget(card)
        root.add_widget(container)
        self.add_widget(root)
    
    def authenticate(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()
        
        if not username or not password:
            self.show_popup('Erreur', 'Veuillez remplir tous les champs')
            return
        
        user = DatabaseManager.get_user(username, password)
        
        if user:
            app = App.get_running_app()
            app.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
            
            # Transition vers le bon menu
            if user[3] == 'admin':
                self.manager.current = 'admin_menu'
            else:
                self.manager.current = 'menu'
            
            # Réinitialiser les champs
            self.username.text = ''
            self.password.text = ''
        else:
            self.show_popup('Erreur', 'Identifiants incorrects')

class MenuScreen(BaseScreen):
    """Menu principal pour les agents"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        root = ScrollView(size_hint=(1, 1))
        
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=responsive.get_padding(),
            spacing=responsive.get_spacing()
        )
        container.bind(minimum_height=container.setter('height'))
        
        # Header avec info utilisateur
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            spacing=dp(5)
        )
        
        welcome = Label(
            text='Bienvenue,',
            font_size=responsive.get_font_size(16),
            color=COLORS['GRAY'],
            size_hint_y=0.3
        )
        
        self.user_label = Label(
            text='Agent',
            font_size=responsive.get_font_size(24),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=0.4
        )
        
        role = Label(
            text='Espace Agent',
            font_size=responsive.get_font_size(14),
            color=COLORS['SECONDARY'],
            size_hint_y=0.3
        )
        
        header.add_widget(welcome)
        header.add_widget(self.user_label)
        header.add_widget(role)
        container.add_widget(header)
        
        # Grille de boutons
        grid = GridLayout(
            cols=2 if responsive.screen_width > dp(400) else 1,
            spacing=responsive.get_spacing(),
            size_hint_y=None,
            height=dp(300)
        )
        
        buttons = [
            ('💰 DÉPÔT', COLORS['PRIMARY'], self.go_deposit),
            ('💸 RETRAIT', COLORS['SECONDARY'], self.go_withdrawal),
            ('📊 STATISTIQUES', COLORS['PRIMARY'], self.go_stats),
            ('🚪 DÉCONNEXION', [0.6, 0.6, 0.6, 1], self.logout)
        ]
        
        for text, color, callback in buttons:
            btn = ResponsiveButton(
                text=text,
                bg_color=color,
                on_press=callback
            )
            grid.add_widget(btn)
        
        container.add_widget(grid)
        root.add_widget(container)
        self.add_widget(root)
    
    def on_enter(self):
        """Appelé lors de l'affichage de l'écran"""
        app = App.get_running_app()
        if app.current_user:
            self.user_label.text = app.current_user['username']
    
    def go_deposit(self, instance):
        screen = self.manager.get_screen('transaction')
        screen.transaction_type = 'Dépôt'
        self.manager.current = 'transaction'
    
    def go_withdrawal(self, instance):
        screen = self.manager.get_screen('transaction')
        screen.transaction_type = 'Retrait'
        self.manager.current = 'transaction'
    
    def go_stats(self, instance):
        self.manager.current = 'stats'
    
    def logout(self, instance):
        App.get_running_app().current_user = None
        self.manager.current = 'login'

class TransactionScreen(BaseScreen):
    """Écran de transaction (dépôt/retrait)"""
    
    transaction_type = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        root = ScrollView(size_hint=(1, 1))
        
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=responsive.get_padding(),
            spacing=responsive.get_spacing()
        )
        container.bind(minimum_height=container.setter('height'))
        
        # Header dynamique
        self.header_label = Label(
            text='',
            font_size=responsive.get_font_size(28),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=None,
            height=dp(60)
        )
        container.add_widget(self.header_label)
        
        # Carte principale
        card = Card()
        
        form = BoxLayout(
            orientation='vertical',
            spacing=responsive.get_spacing(),
            padding=[dp(10), dp(20)]
        )
        
        # Sélection opérateur
        form.add_widget(Label(
            text='Opérateur Mobile Money',
            font_size=responsive.get_font_size(14),
            color=COLORS['TEXT'],
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        self.operator_spinner = Spinner(
            text='Sélectionnez un opérateur',
            values=OPERATORS,
            size_hint_y=None,
            height=responsive.get_input_height(),
            background_color=COLORS['WHITE'],
            color=COLORS['TEXT'],
            font_size=responsive.get_font_size(14)
        )
        form.add_widget(self.operator_spinner)
        
        # Montant
        form.add_widget(Label(
            text='Montant (XOF)',
            font_size=responsive.get_font_size(14),
            color=COLORS['TEXT'],
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        self.amount_input = ResponsiveInput(
            hint_text='0',
            input_filter='float'
        )
        form.add_widget(self.amount_input)
        
        # Espace
        form.add_widget(Widget(size_hint_y=0.5))
        
        # Boutons d'action
        btn_layout = BoxLayout(
            size_hint_y=None,
            height=responsive.get_button_height(),
            spacing=dp(10)
        )
        
        btn_save = ResponsiveButton(
            text='VALIDER',
            bg_color=COLORS['PRIMARY'],
            on_press=self.save_transaction
        )
        
        btn_cancel = ResponsiveButton(
            text='ANNULER',
            bg_color=[0.6, 0.6, 0.6, 1],
            on_press=self.go_back
        )
        
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)
        form.add_widget(btn_layout)
        
        card.add_widget(form)
        container.add_widget(card)
        root.add_widget(container)
        self.add_widget(root)
    
    def on_transaction_type(self, instance, value):
        self.header_label.text = f'{value.upper()}'
        # Changer la couleur selon le type
        if value == 'Dépôt':
            self.header_label.color = COLORS['PRIMARY']
        else:
            self.header_label.color = COLORS['SECONDARY']
    
    def save_transaction(self, instance):
        operator = self.operator_spinner.text
        amount_str = self.amount_input.text.strip()
        
        # Validation
        if operator == 'Sélectionnez un opérateur':
            self.show_popup('Erreur', 'Veuillez sélectionner un opérateur')
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Montant négatif")
            if amount > 10000000:  # Limite 10 millions
                raise ValueError("Montant trop élevé")
        except ValueError:
            self.show_popup('Erreur', 'Veuillez entrer un montant valide (max 10 000 000 XOF)')
            return
        
        # Enregistrement
        app = App.get_running_app()
        DatabaseManager.record_transaction(
            app.current_user['id'],
            operator,
            self.transaction_type,
            amount
        )
        
        # Succès
        self.show_popup(
            'Succès',
            f'{self.transaction_type} de {amount:,.0f} XOF\nenregistré avec succès!',
            'SUCCESS'
        )
        
        # Réinitialiser
        self.amount_input.text = ''
        self.operator_spinner.text = 'Sélectionnez un opérateur'
    
    def go_back(self, instance):
        self.manager.current = 'menu'

class StatsScreen(BaseScreen):
    """Écran de statistiques avec graphiques"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        root = ScrollView(size_hint=(1, 1))
        
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=responsive.get_padding(),
            spacing=responsive.get_spacing()
        )
        container.bind(minimum_height=container.setter('height'))
        
        # Titre
        container.add_widget(Label(
            text='STATISTIQUES',
            font_size=responsive.get_font_size(24),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=None,
            height=dp(50)
        ))
        
        # Onglets personnalisés (plus simple que TabbedPanel pour mobile)
        self.content_area = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(400),
            spacing=dp(10)
        )
        
        # Sélecteur de vue
        selector = BoxLayout(
            size_hint_y=None,
            height=responsive.get_button_height(),
            spacing=dp(10)
        )
        
        btn_operators = ResponsiveButton(
            text='Par Opérateur',
            bg_color=COLORS['PRIMARY'],
            on_press=lambda x: self.show_operator_stats()
        )
        
        btn_daily = ResponsiveButton(
            text='Journalier',
            bg_color=COLORS['SECONDARY'],
            on_press=lambda x: self.show_daily_stats()
        )
        
        selector.add_widget(btn_operators)
        selector.add_widget(btn_daily)
        container.add_widget(selector)
        container.add_widget(self.content_area)
        
        # Bouton retour
        btn_back = ResponsiveButton(
            text='RETOUR',
            bg_color=[0.6, 0.6, 0.6, 1],
            on_press=self.go_back
        )
        container.add_widget(btn_back)
        
        root.add_widget(container)
        self.add_widget(root)
    
    def on_enter(self):
        self.show_operator_stats()
    
    def show_operator_stats(self):
        self.content_area.clear_widgets()
        
        data = DatabaseManager.get_operator_summary()
        if not data:
            self.content_area.add_widget(Label(
                text='Aucune donnée disponible',
                color=COLORS['GRAY']
            ))
            return
        
        # Créer graphique circulaire
        chart = pygal.Pie(
            print_values=True,
            inner_radius=0.4,
            legend_at_bottom=True,
            legend_font_size=10
        )
        chart.title = 'Répartition par Opérateur'
        
        df = pd.DataFrame(data, columns=['operator', 'type', 'amount', 'count'])
        totals = df.groupby('operator')['amount'].sum()
        
        for operator, total in totals.items():
            chart.add(operator, total)
        
        self.display_chart(chart)
    
    def show_daily_stats(self):
        self.content_area.clear_widgets()
        
        data = DatabaseManager.get_daily_summary(days=7)
        if not data:
            self.content_area.add_widget(Label(
                text='Aucune donnée disponible',
                color=COLORS['GRAY']
            ))
            return
        
        # Graphique barres
        chart = pygal.Bar(
            x_label_rotation=45,
            print_values=False,
            legend_at_bottom=True,
            legend_font_size=10
        )
        chart.title = '7 Derniers Jours'
        
        df = pd.DataFrame(data, columns=['date', 'operator', 'type', 'amount', 'count'])
        df['date'] = pd.to_datetime(df['date'])
        
        dates = sorted(df['date'].unique())
        chart.x_labels = [d.strftime('%d/%m') for d in dates]
        
        for trans_type in df['type'].unique():
            amounts = []
            for date in dates:
                mask = (df['date'] == date) & (df['type'] == trans_type)
                total = df[mask]['amount'].sum()
                amounts.append(total if total > 0 else 0)
            chart.add(trans_type, amounts)
        
        self.display_chart(chart)
    
    def display_chart(self, chart):
        """Affiche un graphique pygal"""
        try:
            buf = BytesIO(chart.render_to_png(dpi=72))
            img = Image()
            img.texture = CoreImage(buf, ext='png').texture
            img.allow_stretch = True
            img.size_hint_y = None
            img.height = dp(350)
            self.content_area.add_widget(img)
        except Exception as e:
            self.content_area.add_widget(Label(
                text=f'Erreur graphique: {str(e)}',
                color=COLORS['ERROR']
            ))
    
    def go_back(self, instance):
        app = App.get_running_app()
        if app.current_user['role'] == 'admin':
            self.manager.current = 'admin_menu'
        else:
            self.manager.current = 'menu'

class AdminMenuScreen(BaseScreen):
    """Menu administrateur"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        root = ScrollView(size_hint=(1, 1))
        
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=responsive.get_padding(),
            spacing=responsive.get_spacing()
        )
        container.bind(minimum_height=container.setter('height'))
        
        # Header
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(5)
        )
        
        header.add_widget(Label(
            text='ADMINISTRATION',
            font_size=responsive.get_font_size(28),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=0.6
        ))
        
        header.add_widget(Label(
            text='Espace Gestionnaire',
            font_size=responsive.get_font_size(14),
            color=COLORS['SECONDARY'],
            size_hint_y=0.4
        ))
        
        container.add_widget(header)
        
        # Grille de boutons
        grid = GridLayout(
            cols=1,
            spacing=responsive.get_spacing(),
            size_hint_y=None,
            height=dp(400)
        )
        
        buttons = [
            ('👤 NOUVEL AGENT', COLORS['PRIMARY'], self.show_register),
            ('💼 SOLDES AGENTS', COLORS['SECONDARY'], self.go_balance),
            ('📥 IMPORT EXCEL', [0.2, 0.6, 0.2, 1], self.show_import),
            ('📊 STATISTIQUES', COLORS['PRIMARY'], self.go_stats),
            ('🚪 DÉCONNEXION', [0.6, 0.6, 0.6, 1], self.logout)
        ]
        
        for text, color, callback in buttons:
            btn = ResponsiveButton(
                text=text,
                bg_color=color,
                on_press=callback
            )
            grid.add_widget(btn)
        
        container.add_widget(grid)
        root.add_widget(container)
        self.add_widget(root)
    
    def show_register(self, instance):
        """Popup d'enregistrement d'agent"""
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=responsive.get_spacing()
        )
        
        content.add_widget(Label(
            text='Nouvel Agent',
            font_size=responsive.get_font_size(20),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=None,
            height=dp(40)
        ))
        
        self.reg_username = ResponsiveInput(hint_text="Nom d'utilisateur")
        content.add_widget(self.reg_username)
        
        self.reg_password = ResponsiveInput(
            hint_text="Mot de passe",
            password=True
        )
        content.add_widget(self.reg_password)
        
        self.reg_confirm = ResponsiveInput(
            hint_text="Confirmer le mot de passe",
            password=True
        )
        content.add_widget(self.reg_confirm)
        
        self.error_label = Label(
            text='',
            color=COLORS['ERROR'],
            size_hint_y=None,
            height=dp(30),
            font_size=responsive.get_font_size(12)
        )
        content.add_widget(self.error_label)
        
        btn_layout = BoxLayout(
            size_hint_y=None,
            height=responsive.get_button_height(),
            spacing=dp(10)
        )
        
        btn_save = ResponsiveButton(
            text='ENREGISTRER',
            bg_color=COLORS['PRIMARY'],
            on_press=self.do_register
        )
        
        btn_cancel = ResponsiveButton(
            text='ANNULER',
            bg_color=[0.6, 0.6, 0.6, 1],
            on_press=lambda x: self.popup.dismiss()
        )
        
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)
        
        self.popup = Popup(
            title='',
            content=content,
            size_hint=(0.9, None),
            height=dp(400),
            auto_dismiss=False
        )
        self.popup.open()
    
    def do_register(self, instance):
        username = self.reg_username.text.strip()
        password = self.reg_password.text.strip()
        confirm = self.reg_confirm.text.strip()
        
        if not all([username, password, confirm]):
            self.error_label.text = 'Tous les champs sont requis'
            return
        
        if password != confirm:
            self.error_label.text = 'Les mots de passe ne correspondent pas'
            return
        
        if len(password) < 4:
            self.error_label.text = 'Mot de passe trop court (min 4 caractères)'
            return
        
        if DatabaseManager.add_user(username, password, 'agent'):
            self.popup.dismiss()
            self.show_popup('Succès', f'Agent {username} créé avec succès!', 'SUCCESS')
        else:
            self.error_label.text = "Ce nom d'utilisateur existe déjà"
    
    def go_balance(self, instance):
        self.manager.current = 'balance'
    
    def show_import(self, instance):
        """Popup d'importation de fichier"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        
        content.add_widget(Label(
            text='Sélectionner un fichier Excel',
            font_size=responsive.get_font_size(16),
            color=COLORS['PRIMARY'],
            size_hint_y=None,
            height=dp(40)
        ))
        
        filechooser = FileChooserIconView(
            filters=['*.xlsx', '*.xls'],
            path='/sdcard' if IS_MOBILE else '~',
            size_hint_y=0.7
        )
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(
            size_hint_y=None,
            height=responsive.get_button_height(),
            spacing=dp(10)
        )
        
        def do_import(x):
            if filechooser.selection:
                self.simulate_import(filechooser.selection[0])
        
        btn_import = ResponsiveButton(
            text='IMPORTER',
            bg_color=COLORS['PRIMARY'],
            on_press=do_import
        )
        
        btn_cancel = ResponsiveButton(
            text='ANNULER',
            bg_color=[0.6, 0.6, 0.6, 1],
            on_press=lambda x: popup.dismiss()
        )
        
        btn_layout.add_widget(btn_import)
        btn_layout.add_widget(btn_cancel)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Importation',
            content=content,
            size_hint=(0.95, 0.8)
        )
        popup.open()
    
    def simulate_import(self, filepath):
        """Simule l'importation avec barre de progression"""
        content = BoxLayout(
            orientation='vertical',
            padding=dp(30),
            spacing=dp(20)
        )
        
        content.add_widget(Label(
            text='Importation en cours...',
            font_size=responsive.get_font_size(16)
        ))
        
        progress = ProgressBar(max=100, value=0)
        content.add_widget(progress)
        
        popup = Popup(
            title='Veuillez patienter',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False
        )
        popup.open()
        
        def update_progress(dt):
            if progress.value < 100:
                progress.value += 20
                return True
            else:
                popup.dismiss()
                self.show_popup(
                    'Succès',
                    f'Fichier importé:\n{filepath.split("/")[-1]}',
                    'SUCCESS'
                )
                return False
        
        Clock.schedule_interval(update_progress, 0.3)
    
    def go_stats(self, instance):
        self.manager.current = 'stats'
    
    def logout(self, instance):
        App.get_running_app().current_user = None
        self.manager.current = 'login'

class BalanceScreen(BaseScreen):
    """Écran de consultation des soldes des agents"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        root = ScrollView(size_hint=(1, 1))
        
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=responsive.get_padding(),
            spacing=responsive.get_spacing()
        )
        container.bind(minimum_height=container.setter('height'))
        
        # Titre
        container.add_widget(Label(
            text='SOLDES DES AGENTS',
            font_size=responsive.get_font_size(24),
            bold=True,
            color=COLORS['PRIMARY'],
            size_hint_y=None,
            height=dp(50)
        ))
        
        # Carte de sélection
        card = Card()
        
        form = BoxLayout(
            orientation='vertical',
            spacing=responsive.get_spacing(),
            padding=[dp(10), dp(20)]
        )
        
        form.add_widget(Label(
            text='Sélectionner un agent',
            font_size=responsive.get_font_size(14),
            color=COLORS['TEXT'],
            size_hint_y=None,
            height=dp(30)
        ))
        
        self.agent_spinner = Spinner(
            text='Choisir un agent',
            values=[],
            size_hint_y=None,
            height=responsive.get_input_height()
        )
        self.agent_spinner.bind(text=self.on_agent_select)
        form.add_widget(self.agent_spinner)
        
        # Affichage du solde
        self.balance_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            padding=dp(20)
        )
        
        with self.balance_card.canvas.before:
            Color(*COLORS['PRIMARY'])
            self.balance_rect = RoundedRectangle(
                pos=self.balance_card.pos,
                size=self.balance_card.size,
                radius=[dp(12),]
            )
        
        self.balance_card.bind(pos=self._update_balance_rect, size=self._update_balance_rect)
        
        self.balance_label = Label(
            text='Sélectionnez un agent',
            font_size=responsive.get_font_size(24),
            bold=True,
            color=COLORS['WHITE']
        )
        
        self.details_label = Label(
            text='',
            font_size=responsive.get_font_size(14),
            color=[1, 1, 1, 0.8]
        )
        
        self.balance_card.add_widget(self.balance_label)
        self.balance_card.add_widget(self.details_label)
        
        form.add_widget(Widget(size_hint_y=0.2))
        form.add_widget(self.balance_card)
        
        card.add_widget(form)
        container.add_widget(card)
        
        # Bouton retour
        btn_back = ResponsiveButton(
            text='RETOUR',
            bg_color=[0.6, 0.6, 0.6, 1],
            on_press=lambda x: setattr(self.manager, 'current', 'admin_menu')
        )
        container.add_widget(btn_back)
        
        root.add_widget(container)
        self.add_widget(root)
    
    def _update_balance_rect(self, *args):
        self.balance_rect.pos = self.balance_card.pos
        self.balance_rect.size = self.balance_card.size
    
    def on_enter(self):
        """Chargement de la liste des agents"""
        agents = DatabaseManager.get_all_agents()
        self.agents_map = {name: id for id, name in agents}
        self.agent_spinner.values = list(self.agents_map.keys())
        self.agent_spinner.text = 'Choisir un agent'
        self.balance_label.text = 'Sélectionnez un agent'
        self.details_label.text = ''
    
    def on_agent_select(self, spinner, text):
        if text == 'Choisir un agent' or text not in self.agents_map:
            return
        
        agent_id = self.agents_map[text]
        balance_info = DatabaseManager.get_agent_balance(agent_id)
        
        balance = balance_info['balance']
        deposits = balance_info['deposits']
        withdrawals = balance_info['withdrawals']
        
        # Animation de changement de couleur selon le solde
        if balance < 0:
            color = COLORS['ERROR']
        elif balance > 1000000:
            color = COLORS['SUCCESS']
        else:
            color = COLORS['PRIMARY']
        
        self.balance_card.canvas.before.clear()
        with self.balance_card.canvas.before:
            Color(*color)
            self.balance_rect = RoundedRectangle(
                pos=self.balance_card.pos,
                size=self.balance_card.size,
                radius=[dp(12),]
            )
        
        self.balance_label.text = f'{balance:,.0f} XOF'
        self.details_label.text = f'Dépôts: {deposits:,.0f} | Retraits: {withdrawals:,.0f}'

# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================

class MobileMoneyApp(App):
    
    current_user = ObjectProperty(None, allownone=True)
    
    def build(self):
        # Configuration fenêtre
        Window.clearcolor = COLORS['BACKGROUND']
        
        # Initialisation DB
        DatabaseManager.init_database()
        
        # Gestionnaire d'écrans avec transition fluide
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        
        # Ajout des écrans
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TransactionScreen(name='transaction'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(AdminMenuScreen(name='admin_menu'))
        sm.add_widget(BalanceScreen(name='balance'))
        
        return sm
    
    def on_pause(self):
        """Gestion de la mise en pause (Android)"""
        return True
    
    def on_resume(self):
        """Gestion de la reprise"""
        pass

if __name__ == '__main__':
    MobileMoneyApp().run()
