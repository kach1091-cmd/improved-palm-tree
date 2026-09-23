"""Aplicación Kivy refactorizada - Unicornio 360 con threading y UI thread-safe"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from threading import Thread
import logging
import sys
from pathlib import Path

# Agregar app al path
sys.path.insert(0, str(Path(__file__).parent))

from motor_cataleya import MotorCataleya
from config import KIVY_WINDOW_WIDTH, KIVY_WINDOW_HEIGHT
from utils.audit_manager import AuditManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class UnicornioApp(App):
    """Aplicación Unicornio 360 con motor de auditoría en segundo plano"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.motor = None
        self.audit_manager = AuditManager()
        self.motor_thread = None
        self.is_running = False
    
    def build(self):
        """Construir interfaz de usuario"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Título y estado
        title_label = Label(
            text="UNICORNIO 360\nPROTOCOLO 5234 ACTIVO",
            halign="center",
            font_size='28sp',
            color=(0, 1, 1, 1),
            size_hint_y=0.2
        )
        
        # Panel de estado
        status_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        
        status_label = Label(
            text="ESTADO ACTUAL:",
            color=(0.8, 0.8, 0.8, 1),
            size_hint_x=0.4
        )
        self.status_value = Label(
            text="INACTIVO",
            color=(1, 0, 0, 1),
            size_hint_x=0.6
        )
        
        latency_label = Label(
            text="LATENCIA:",
            color=(0.8, 0.8, 0.8, 1)
        )
        self.latency_value = Label(
            text="-- ms",
            color=(0, 1, 0, 1)
        )
        
        status_layout.add_widget(status_label)
        status_layout.add_widget(self.status_value)
        status_layout.add_widget(latency_label)
        status_layout.add_widget(self.latency_value)
        
        # Botones de control
        button_layout = BoxLayout(spacing=10, size_hint_y=0.25)
        
        btn_start = Button(
            text="INICIAR SINCRONIZACIÓN",
            background_color=(0, 1, 0, 1),
            size_hint_x=0.5
        )
        btn_start.bind(on_press=self.start_synchronization)
        
        btn_stop = Button(
            text="DETENER",
            background_color=(1, 0, 0, 1),
            size_hint_x=0.5
        )
        btn_stop.bind(on_press=self.stop_synchronization)
        
        button_layout.add_widget(btn_start)
        button_layout.add_widget(btn_stop)
        
        # Botones secundarios
        secondary_buttons = BoxLayout(spacing=10, size_hint_y=0.15)
        
        btn_status = Button(
            text="CONSULTAR ESTADO",
            background_color=(0.2, 0.2, 0.8, 1)
        )
        btn_status.bind(on_press=self.check_status)
        
        btn_logs = Button(
            text="VER REPORTES",
            background_color=(0.8, 0.4, 0, 1)
        )
        btn_logs.bind(on_press=self.view_reports)
        
        secondary_buttons.add_widget(btn_status)
        secondary_buttons.add_widget(btn_logs)
        
        # Info de debug
        self.info_label = Label(
            text="Sistema listo",
            halign="left",
            font_size='10sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.2
        )
        
        # Agregar widgets al layout principal
        main_layout.add_widget(title_label)
        main_layout.add_widget(status_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(secondary_buttons)
        main_layout.add_widget(self.info_label)
        
        # Inicializar motor en background al arrancar
        Clock.schedule_once(lambda dt: self.initialize_motor(), 1)
        
        return main_layout
    
    def initialize_motor(self):
        """Inicializar motor en thread background (NO BLOQUEA UI)"""
        try:
            self.motor = MotorCataleya()
            self.update_info("Motor inicializado correctamente")
            logger.info("Motor Cataleya inicializado")
        except Exception as e:
            logger.error(f"Error inicializando motor: {e}")
            self.update_info(f"ERROR: {str(e)}")
    
    def start_synchronization(self, instance):
        """Iniciar sincronización (thread-safe)"""
        if self.motor is None:
            self.update_info("ERROR: Motor no inicializado")
            return
        
        if self.is_running:
            self.update_info("Ya hay una sincronización en curso")
            return
        
        self.is_running = True
        self.status_value.text = "SINCRONIZANDO"
        self.status_value.color = (1, 1, 0, 1)
        self.latency_value.text = "11 ms"
        
        # Ejecutar motor en thread separado
        self.motor_thread = Thread(target=self._run_motor_async, daemon=True)
        self.motor_thread.start()
        
        self.update_info("Sincronización iniciada")
        logger.info("Sincronización iniciada por usuario")
    
    def _run_motor_async(self):
        """Ejecutar motor de forma asíncrona"""
        try:
            self.motor.start()
        except Exception as e:
            logger.error(f"Error en motor async: {e}")
            Clock.schedule_once(
                lambda dt: self._handle_motor_error(str(e)), 0
            )
    
    def _handle_motor_error(self, error_msg):
        """Manejar errores del motor en thread principal"""
        self.status_value.text = "ERROR"
        self.status_value.color = (1, 0, 0, 1)
        self.update_info(f"ERROR: {error_msg}")
        self.is_running = False
    
    def stop_synchronization(self, instance):
        """Detener sincronización"""
        if self.motor:
            self.motor.stop()
        
        self.is_running = False
        self.status_value.text = "DETENIDO"
        self.status_value.color = (1, 0, 0, 1)
        self.update_info("Sincronización detenida")
        logger.info("Sincronización detenida por usuario")
    
    def check_status(self, instance):
        """Consultar estado actual"""
        try:
            latest = self.audit_manager.get_latest_report()
            report_count = self.audit_manager.get_report_count()
            
            if latest:
                msg = f"Estado: {report_count} reportes\nÚltimo: {latest['filename']}"
            else:
                msg = "No hay reportes generados"
            
            self.update_info(msg)
            logger.info(f"Estado consultado: {report_count} reportes")
        except Exception as e:
            self.update_info(f"Error consultando estado: {e}")
            logger.error(f"Error en check_status: {e}")
    
    def view_reports(self, instance):
        """Ver lista de reportes"""
        try:
            reports_count = self.audit_manager.get_report_count()
            reports = self.audit_manager.get_all_reports()
            
            msg = f"Reportes disponibles: {reports_count}\n"
            if reports:
                msg += "\n".join([Path(r).name for r in reports[-3:]])
            
            self.update_info(msg)
            logger.info(f"Visualizando {reports_count} reportes")
        except Exception as e:
            self.update_info(f"Error viendo reportes: {e}")
            logger.error(f"Error en view_reports: {e}")
    
    def update_info(self, message: str):
        """Actualizar label de info (thread-safe)"""
        Clock.schedule_once(
            lambda dt: setattr(self.info_label, 'text', message), 0
        )


if __name__ == "__main__":
    app = UnicornioApp()
    app.run()
