from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from threading import Thread
import signal
import sys

class UnicornioApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audit_thread = None
        self.running = True
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Graceful shutdown handler"""
        print("\n[!] Iniciando apagado seguro...")
        self.running = False
        sys.exit(0)
    
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
        """Execute audit in background thread"""
        self.lbl.text = "ESTADO: INICIANDO\nPROCESO EN BACKGROUND"
        
        # Start audit in separate thread to avoid UI blocking
        if self.audit_thread is None or not self.audit_thread.is_alive():
            self.audit_thread = Thread(target=self.run_audit, daemon=True)
            self.audit_thread.start()
    
    def run_audit(self):
        """Run audit process"""
        try:
            from auditoria_raiz import ejecutar_auditoria
            ejecutar_auditoria(lambda: self.running)
            self.lbl.text = "ESTADO: IMPACTO GLOBAL\nSELLO 1991 CONFIRMADO"
        except Exception as e:
            print(f"[ERROR] {e}")
            self.lbl.text = f"ERROR: {str(e)}"

if __name__ == "__main__":
    UnicornioApp().run()
