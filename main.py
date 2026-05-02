from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class UnicornioApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        self.lbl = Label(text="UNICORNIO 360\nPROTOCOLO 5234 ACTIVO", 
                         halign="center", font_size='24sp', color=(0, 1, 1, 1))
        btn = Button(text="SINCRONIZAR RAÍZ", size_hint=(1, 0.3),
                     background_color=(0, 1, 0, 1))
        btn.bind(on_press=self.ejecutar)
        layout.add_widget(self.lbl)
        layout.add_widget(btn)
        return layout

    def ejecutar(self, instance):
        self.lbl.text = "ESTADO: IMPACTO GLOBAL\nSELLO 1991 CONFIRMADO"

if __name__ == "__main__":
    UnicornioApp().run()