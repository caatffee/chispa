from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
import random, re
from datetime import datetime

class ChispaApp(App):
    def build(self):
        self.memory = {}
        self.awaiting_teach = None
        self.layout = FloatLayout()
        Window.clearcolor = (0.06, 0.05, 0.1, 1)

        self.bubble = Label(
            text='¡Hola! Soy Chispa ✨\n¡Enséñame cosas!',
            font_size='15sp',
            size_hint=(0.9, None),
            height=70,
            pos_hint={'center_x': 0.5},
            y=Window.height * 0.75,
            halign='center',
            valign='middle',
            color=(1, 0.9, 1, 1)
        )
        self.bubble.bind(size=self.bubble.setter('text_size'))
        self.layout.add_widget(self.bubble)

        self.pet = Label(
            text='🐾',
            font_size='72sp',
            size_hint=(None, None),
            size=(100, 100),
            pos=(Window.width/2 - 50, Window.height * 0.55)
        )
        self.layout.add_widget(self.pet)

        self.chat_log = Label(
            text='',
            font_size='12sp',
            size_hint=(0.92, None),
            height=160,
            pos_hint={'center_x': 0.5},
            y=75,
            halign='left',
            valign='top',
            color=(0.85, 0.8, 1, 1)
        )
        self.chat_log.bind(width=lambda *x:
            self.chat_log.setter('text_size')(self.chat_log, (self.chat_log.width, None)))
        self.layout.add_widget(self.chat_log)

        self.chat_input = TextInput(
            hint_text='Escríbele a Chispa...',
            size_hint=(0.75, None),
            height=44,
            pos_hint={'x': 0.03},
            y=18,
            multiline=False,
            background_color=(0.13, 0.1, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.4, 0.7, 1),
            cursor_color=(0.75, 0.5, 1, 1)
        )
        self.chat_input.bind(on_text_validate=self.on_send)
        self.layout.add_widget(self.chat_input)

        btn = Button(
            text='➤',
            size_hint=(0.18, None),
            height=44,
            pos_hint={'right': 0.99},
            y=18,
            background_color=(0.75, 0.3, 1, 1),
            font_size='20sp'
        )
        btn.bind(on_press=self.on_send)
        self.layout.add_widget(btn)

        Clock.schedule_interval(self.animate_pet, 5)
        Clock.schedule_interval(self.auto_ask, 90)
        return self.layout

    def animate_pet(self, dt):
        x = random.randint(20, int(Window.width) - 120)
        y = random.randint(int(Window.height*0.42), int(Window.height*0.60))
        anim = Animation(x=x, y=y, duration=2.5, t='in_out_quad')
        anim.start(self.pet)

    def auto_ask(self, dt):
        questions = [
            '¿Qué estás haciendo? 👀',
            '¡Oye! ¿Me enseñas algo? 🌟',
            '¿Cuál es tu comida favorita? 🍕',
            '¡Estoy curiosa! ¿Hablamos? 🐾',
            '¿Qué es lo más bonito que conoces? ✨',
        ]
        self.bubble.text = random.choice(questions)

    def add_log(self, who, text):
        lines = self.chat_log.text.split('\n') if self.chat_log.text else []
        lines.append(f'{who}: {text}')
        if len(lines) > 7:
            lines = lines[-7:]
        self.chat_log.text = '\n'.join(lines)

    def on_send(self, *args):
        text = self.chat_input.text.strip()
        if not text:
            return
        self.chat_input.text = ''
        self.add_log('Tú', text)
        self.process(text)

    def respond(self, text):
        self.bubble.text = text
        self.add_log('Chispa', text)
        anim = (Animation(font_size='85sp', duration=0.15) +
                Animation(font_size='72sp', duration=0.15))
        anim.start(self.pet)

    def process(self, text):
        lower = text.lower()

        if self.awaiting_teach:
            key = self.awaiting_teach
            self.memory[key] = text
            self.awaiting_teach = None
            self.respond(f'¡Aprendí! "{key}" = {text} 🎉')
            return

        if 'hora' in lower:
            h = datetime.now().strftime('%H:%M')
            self.respond(f'¡Son las {h}! ⏰')
            return

        if any(w in lower for w in ['hola','hey','buenas']):
            self.respond('¡Hola hola! 🌟 ¿Qué me enseñas hoy?')
            return

        if 'qué sabes' in lower or 'que sabes' in lower:
            if self.memory:
                self.respond(f'¡Sé {len(self.memory)} cosas! 🧠 ' + ', '.join(self.memory.keys()))
            else:
                self.respond('No sé nada aún... ¡enséñame! 🥺')
            return

        if 'olvida' in lower:
            self.memory = {}
            self.respond('¡Olvidé todo! Empecemos de nuevo 😅')
            return

        if 'fecha' in lower or 'día' in lower or 'dia' in lower:
            d = datetime.now().strftime('%d/%m/%Y')
            self.respond(f'¡Hoy es {d}! 📅')
            return

        for k in self.memory:
            if k in lower:
                self.respond(f'"{k}" es: {self.memory[k]} 😄')
                return

        m = re.match(r'^(.+?)\s+es\s+(.+)$', text, re.IGNORECASE)
        if m and len(m.group(1)) < 30:
            key = m.group(1).lower().strip()
            val = m.group(2).strip()
            self.memory[key] = val
            self.respond(f'¡Aprendido! "{key}" = "{val}" 🎉')
            return

        self.awaiting_teach = text[:25].lower().strip('?¿ ')
        self.respond('No sé eso... ¿me explicas? 🥺')

if __name__ == '__main__':
    ChispaApp().run()
