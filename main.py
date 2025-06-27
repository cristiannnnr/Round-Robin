import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QTextEdit, QSplitter, QGroupBox, QFrame, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from copy import deepcopy

class ProcessNode:
    """Nodo para la lista circular de procesos"""
    def __init__(self, process):
        self.process = process
        self.next = None
        self.prev = None

class CircularQueue:
    """Lista circular dinámica para el algoritmo Round Robin"""
    def __init__(self):
        self.current = None
        self.size = 0
    
    def is_empty(self):
        return self.size == 0
    
    def add_process(self, process):
        """Agregar proceso al final de la cola circular"""
        new_node = ProcessNode(process)
        
        if self.is_empty():
            self.current = new_node
            new_node.next = new_node
            new_node.prev = new_node
        else:
            # Insertar antes del nodo actual (al final de la cola)
            last_node = self.current.prev
            new_node.next = self.current
            new_node.prev = last_node
            last_node.next = new_node
            self.current.prev = new_node
        
        self.size += 1
        return new_node
    
    def get_next_process(self):
        """Obtener el siguiente proceso y mover el puntero"""
        if self.is_empty():
            return None
        
        current_process = self.current.process
        self.current = self.current.next
        return current_process
    
    def remove_current_process(self):
        """Eliminar el proceso actual de la cola"""
        if self.is_empty():
            return None
        
        if self.size == 1:
            removed_process = self.current.process
            self.current = None
            self.size = 0
            return removed_process
        
        # Más de un proceso
        removed_process = self.current.process
        prev_node = self.current.prev
        next_node = self.current.next
        
        prev_node.next = next_node
        next_node.prev = prev_node
        self.current = next_node
        self.size -= 1
        
        return removed_process
    
    def peek_current(self):
        """Ver el proceso actual sin moverlo"""
        if self.is_empty():
            return None
        return self.current.process
    
    def get_queue_status(self):
        """Obtener el estado actual de la cola como lista de IDs"""
        if self.is_empty():
            return []
        
        processes = []
        start_node = self.current
        current_node = start_node
        
        while True:
            processes.append(current_node.process.id)
            current_node = current_node.next
            if current_node == start_node:
                break
        
        return processes
    
    def get_size(self):
        return self.size

class Process:
    def __init__(self, pid, arrival, burst):
        self.id = pid
        self.arrival = arrival
        self.burst = burst
        self.original_burst = burst
        self.remaining = burst
        self.finish_time = 0
        self.turnaround = 0
        self.waiting = 0
        self.start_time = -1


def schedule_rr_step_by_step(processes, quantum):
    # Hacer copias profundas de los procesos para no modificar los originales
    proc_copies = [deepcopy(p) for p in processes]
    
    time = 0
    circular_queue = CircularQueue()  # Cola circular dinámica
    waiting_processes = sorted(proc_copies, key=lambda x: x.arrival)  # Procesos esperando llegar
    arrival_idx = 0
    events = []  # (pid, start, end, remaining_before, remaining_after)
    steps = []  # Cada paso incluye: logs, events_so_far, completed_so_far
    completed = []
    
    step_logs = []
    step_logs.append("=== INICIO DE SIMULACIÓN ROUND ROBIN CON LISTA CIRCULAR ===")
    step_logs.append(f"Quantum: {quantum}")
    step_logs.append("🔄 Usando lista circular dinámica de nodos")
    step_logs.append("")
    
    # Agregar primer paso
    steps.append({
        'logs': step_logs.copy(),
        'events': [],
        'completed': [],
        'current_time': time,
        'queue_status': []
    })
    
    while arrival_idx < len(waiting_processes) or not circular_queue.is_empty():
        step_logs = []
        
        # Agregar procesos que han llegado a la cola circular
        while arrival_idx < len(waiting_processes) and waiting_processes[arrival_idx].arrival <= time:
            arriving_process = waiting_processes[arrival_idx]
            node = circular_queue.add_process(arriving_process)
            step_logs.append(f"⏰ Tiempo {time}: Proceso {arriving_process.id} llega a la cola circular")
            step_logs.append(f"   🔗 Nodo creado y enlazado en posición {circular_queue.get_size()}")
            arrival_idx += 1
        
        # Si no hay procesos en cola, avanzar al siguiente proceso
        if circular_queue.is_empty():
            if arrival_idx < len(waiting_processes):
                next_arrival = waiting_processes[arrival_idx].arrival
                step_logs.append(f"⏸️ CPU inactiva - Cola circular vacía")
                step_logs.append(f"   ⏭️ Avanzando tiempo de {time} a {next_arrival}")
                time = next_arrival
                continue
            else:
                break
        
        # Obtener el proceso actual de la cola circular
        current = circular_queue.peek_current()
        start_time = time
        
        # Establecer tiempo de inicio si es la primera vez
        if current.start_time == -1:
            current.start_time = start_time
        
        # Calcular tiempo de ejecución
        exec_time = min(quantum, current.remaining)
        remaining_before = current.remaining
        
        step_logs.append(f"🔒 Tiempo {start_time}: Procesador ENTRA en sección crítica")
        step_logs.append(f"   🎯 Nodo actual en cola circular: {current.id}")
        step_logs.append(f"   ⏱️ Tiempo restante antes: {remaining_before}")
        step_logs.append(f"   🚀 Tiempo a ejecutar: {exec_time}")
        
        # Ejecutar el proceso
        time += exec_time
        current.remaining -= exec_time
        
        step_logs.append(f"🔓 Tiempo {time}: Procesador SALE de sección crítica")
        step_logs.append(f"   ⏱️ Tiempo restante después: {current.remaining}")
        
        # Agregar evento para el diagrama de Gantt
        current_event = (current.id, start_time, time, remaining_before, current.remaining)
        events.append(current_event)
        
        # Agregar procesos que llegaron durante la ejecución
        while arrival_idx < len(waiting_processes) and waiting_processes[arrival_idx].arrival <= time:
            arriving_process = waiting_processes[arrival_idx]
            circular_queue.add_process(arriving_process)
            step_logs.append(f"⏰ Tiempo {time}: Proceso {arriving_process.id} llega durante ejecución")
            step_logs.append(f"   🔗 Enlazado al final de la cola circular")
            arrival_idx += 1
        
        # Verificar si el proceso terminó
        if current.remaining == 0:
            current.finish_time = time
            current.turnaround = current.finish_time - current.arrival
            current.waiting = current.turnaround - current.original_burst
            completed.append(current)
            
            # Remover de la cola circular
            circular_queue.remove_current_process()
            step_logs.append(f"✅ Proceso {current.id} COMPLETADO")
            step_logs.append(f"   🗑️ Nodo eliminado de la cola circular")
            step_logs.append(f"   → Tf = {current.finish_time} (tiempo final)")
            step_logs.append(f"   → Tr = {current.turnaround} (Tf - llegada = {current.finish_time} - {current.arrival})")
            step_logs.append(f"   → Te = {current.waiting} (Tr - ráfaga = {current.turnaround} - {current.original_burst})")
        else:
            # Mover al siguiente nodo en la cola circular
            circular_queue.get_next_process()  # Esto mueve el puntero al siguiente
            step_logs.append(f"🔄 Proceso {current.id} continúa en cola circular")
            step_logs.append(f"   ➡️ Puntero movido al siguiente nodo")
        
        queue_status = circular_queue.get_queue_status()
        step_logs.append(f"� Cola circular actual: {queue_status}")
        step_logs.append(f"   📏 Tamaño: {circular_queue.get_size()} nodos")
        step_logs.append("")
        
        # Agregar paso actual
        steps.append({
            'logs': step_logs,
            'events': events.copy(),
            'completed': [deepcopy(p) for p in completed],
            'current_time': time,
            'queue_status': queue_status
        })
    
    # Agregar paso final con resumen
    final_logs = []
    final_logs.append("=== RESUMEN FINAL - LISTA CIRCULAR COMPLETADA ===")
    final_logs.append("🔄 Todos los nodos han sido procesados y eliminados")
    
    if completed:
        total_turnaround = sum(p.turnaround for p in completed)
        total_waiting = sum(p.waiting for p in completed)
        avg_turnaround = total_turnaround / len(completed)
        avg_waiting = total_waiting / len(completed)
        
        final_logs.append("")
        final_logs.append("Proceso | Llegada | Ráfaga | Tf | Tr | Te")
        final_logs.append("--------|---------|--------|----|----|----")
        for p in sorted(completed, key=lambda x: x.id):
            final_logs.append(f"{p.id:7} | {p.arrival:7} | {p.original_burst:6} | {p.finish_time:2} | {p.turnaround:2} | {p.waiting:2}")
        
        final_logs.append("")
        final_logs.append(f"⏱️ Tiempo promedio de retorno: {avg_turnaround:.2f}")
        final_logs.append(f"⏰ Tiempo promedio de espera: {avg_waiting:.2f}")
        final_logs.append(f"🔄 Total de rotaciones en cola circular: {len(events)}")
    
    steps.append({
        'logs': final_logs,
        'events': events.copy(),
        'completed': [deepcopy(p) for p in completed],
        'current_time': time,
        'queue_status': []
    })
    
    return steps
    
    steps.append({
        'logs': final_logs,
        'events': events.copy(),
        'completed': [deepcopy(p) for p in completed],
        'current_time': time
    })
    
    return steps

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🚀 Simulador Round Robin - Lista Circular Dinámica')
        self.setGeometry(100, 100, 1200, 800)
        self.processes = []
        self.simulation_steps = []
        self.current_step = 0
        self.events = []
        self.completed_processes = []
        
        # Aplicar estilo moderno
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #3c3c3c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QSpinBox {
                padding: 8px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #404040;
                color: white;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #404040;
                alternate-background-color: #4a4a4a;
                color: white;
                gridline-color: #555555;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Grupo de entrada de procesos
        input_group = QGroupBox("📝 Agregar Procesos")
        input_layout = QHBoxLayout(input_group)
        
        input_layout.addWidget(QLabel('Tiempo de Llegada:'))
        self.spin_arrival = QSpinBox()
        self.spin_arrival.setRange(0, 1000)
        self.spin_arrival.setSuffix(' ms')
        input_layout.addWidget(self.spin_arrival)
        
        input_layout.addWidget(QLabel('Tiempo de Ráfaga:'))
        self.spin_burst = QSpinBox()
        self.spin_burst.setRange(1, 1000)
        self.spin_burst.setSuffix(' ms')
        self.spin_burst.setValue(5)
        input_layout.addWidget(self.spin_burst)
        
        btn_add = QPushButton('➕ Agregar Proceso')
        btn_add.clicked.connect(self.add_process)
        input_layout.addWidget(btn_add)
        
        btn_clear = QPushButton('🗑️ Limpiar Todo')
        btn_clear.clicked.connect(self.clear_processes)
        btn_clear.setStyleSheet("QPushButton { background-color: #f44336; } QPushButton:hover { background-color: #da190b; }")
        input_layout.addWidget(btn_clear)
        
        main_layout.addWidget(input_group)
        
        # Tabla de procesos
        process_group = QGroupBox("📋 Lista de Procesos")
        process_layout = QVBoxLayout(process_group)
        
        self.process_table = QTableWidget(0, 4)
        self.process_table.setHorizontalHeaderLabels(['ID Proceso', 'Llegada (ms)', 'Ráfaga (ms)', 'Estado'])
        self.process_table.horizontalHeader().setStretchLastSection(True)
        process_layout.addWidget(self.process_table)
        
        main_layout.addWidget(process_group)
        
        # Grupo de configuración y ejecución
        exec_group = QGroupBox("⚙️ Configuración y Ejecución")
        exec_layout = QHBoxLayout(exec_group)
        
        exec_layout.addWidget(QLabel('Quantum (ms):'))
        self.spin_quantum = QSpinBox()
        self.spin_quantum.setRange(1, 100)
        self.spin_quantum.setValue(3)
        self.spin_quantum.setSuffix(' ms')
        exec_layout.addWidget(self.spin_quantum)
        
        btn_execute = QPushButton('🚀 Ejecutar Simulación')
        btn_execute.clicked.connect(self.run_simulation)
        exec_layout.addWidget(btn_execute)
        
        self.btn_step = QPushButton('▶️ Siguiente Paso')
        self.btn_step.setEnabled(False)
        self.btn_step.clicked.connect(self.show_next_log)
        exec_layout.addWidget(self.btn_step)
        
        self.btn_auto = QPushButton('⏩ Reproducción Automática')
        self.btn_auto.setEnabled(False)
        self.btn_auto.clicked.connect(self.toggle_auto_play)
        exec_layout.addWidget(self.btn_auto)
        
        main_layout.addWidget(exec_group)
        
        # Área principal dividida
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Logs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        logs_group = QGroupBox("📜 Registro de Ejecución (Lista Circular - Exclusión Mutua)")
        logs_layout = QVBoxLayout(logs_group)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        logs_layout.addWidget(self.log_display)
        
        left_layout.addWidget(logs_group)
        
        # Panel derecho - Gantt y Resultados
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Diagrama de Gantt
        gantt_group = QGroupBox("📊 Diagrama de Gantt")
        gantt_layout = QVBoxLayout(gantt_group)
        
        self.figure = Figure(figsize=(8, 4), facecolor='#2b2b2b')
        self.canvas = FigureCanvas(self.figure)
        gantt_layout.addWidget(self.canvas)
        
        right_layout.addWidget(gantt_group)
        
        # Tabla de resultados
        results_group = QGroupBox("📈 Resultados Finales")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget(0, 6)
        self.results_table.setHorizontalHeaderLabels(['Proceso', 'Llegada', 'Ráfaga', 'Tf', 'Tr', 'Te'])
        results_layout.addWidget(self.results_table)
        
        self.stats_label = QLabel("Estadísticas aparecerán aquí después de la simulación")
        self.stats_label.setStyleSheet("QLabel { color: #4CAF50; font-size: 14px; }")
        results_layout.addWidget(self.stats_label)
        
        right_layout.addWidget(results_group)
        
        # Configurar splitter
        content_splitter.addWidget(left_panel)
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([500, 700])
        
        main_layout.addWidget(content_splitter)
        
        # Timer para reproducción automática
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.show_next_log)
        self.auto_playing = False

    def add_process(self):
        pid = f'P{len(self.processes) + 1}'
        arrival = self.spin_arrival.value()
        burst = self.spin_burst.value()
        
        process = Process(pid, arrival, burst)
        self.processes.append(process)
        
        # Agregar a la tabla
        row = self.process_table.rowCount()
        self.process_table.insertRow(row)
        self.process_table.setItem(row, 0, QTableWidgetItem(pid))
        self.process_table.setItem(row, 1, QTableWidgetItem(str(arrival)))
        self.process_table.setItem(row, 2, QTableWidgetItem(str(burst)))
        self.process_table.setItem(row, 3, QTableWidgetItem("Esperando"))
        
        # Limpiar campos
        self.spin_arrival.setValue(0)
        self.spin_burst.setValue(5)

    def clear_processes(self):
        self.processes.clear()
        self.process_table.setRowCount(0)
        self.log_display.clear()
        self.results_table.setRowCount(0)
        self.stats_label.setText("Estadísticas aparecerán aquí después de la simulación")
        self.figure.clear()
        self.canvas.draw()
        self.btn_step.setEnabled(False)
        self.btn_auto.setEnabled(False)
        self.simulation_steps = []
        self.current_step = 0

    def run_simulation(self):
        if not self.processes:
            self.log_display.setText("❌ Error: No hay procesos para simular")
            return
        
        quantum = self.spin_quantum.value()
        self.simulation_steps = schedule_rr_step_by_step(self.processes, quantum)
        
        self.current_step = 0
        self.log_display.clear()
        self.results_table.setRowCount(0)
        self.figure.clear()
        self.canvas.draw()
        
        self.btn_step.setEnabled(True)
        self.btn_auto.setEnabled(True)
        
        # Mostrar primer paso
        self.show_current_step()

    def show_next_log(self):
        if self.current_step < len(self.simulation_steps) - 1:
            self.current_step += 1
            self.show_current_step()
        else:
            self.btn_step.setEnabled(False)
            if self.auto_playing:
                self.toggle_auto_play()

    def show_current_step(self):
        if self.current_step < len(self.simulation_steps):
            step = self.simulation_steps[self.current_step]
            
            # Mostrar logs del paso actual
            for log in step['logs']:
                self.log_display.append(log)
            
            # Actualizar diagrama de Gantt paso a paso
            self.draw_gantt_progressive(step['events'])
            
            # Actualizar tabla de resultados paso a paso
            self.update_results_table_progressive(step['completed'])

    def toggle_auto_play(self):
        if self.auto_playing:
            self.auto_timer.stop()
            self.btn_auto.setText('⏩ Reproducción Automática')
            self.auto_playing = False
        else:
            self.auto_timer.start(800)  # 800ms entre pasos
            self.btn_auto.setText('⏸️ Pausar')
            self.auto_playing = True

    def draw_gantt_progressive(self, events_so_far):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#2b2b2b')
        
        if not events_so_far:
            ax.set_title('Diagrama de Gantt - Round Robin (Esperando eventos...)', 
                        color='white', fontsize=14, fontweight='bold')
            self.canvas.draw()
            return
        
        # Obtener procesos únicos y asignar colores
        unique_processes = list(set([event[0] for event in events_so_far]))
        colors = plt.cm.Set3(range(len(unique_processes)))
        color_map = {proc: colors[i] for i, proc in enumerate(unique_processes)}
        
        # Dibujar barras solo hasta el punto actual
        for i, (pid, start, end, _, _) in enumerate(events_so_far):
            duration = end - start
            y_pos = unique_processes.index(pid)
            
            ax.barh(y_pos, duration, left=start, height=0.6, 
                   color=color_map[pid], alpha=0.8, edgecolor='white', linewidth=1)
            
            # Agregar etiqueta en el centro de la barra
            ax.text(start + duration/2, y_pos, f'{pid}', 
                   ha='center', va='center', fontweight='bold', fontsize=10)
        
        # Configurar ejes
        ax.set_yticks(range(len(unique_processes)))
        ax.set_yticklabels(unique_processes)
        ax.set_xlabel('Tiempo (ms)', color='white', fontsize=12)
        ax.set_ylabel('Procesos', color='white', fontsize=12)
        ax.set_title(f'Diagrama de Gantt - Round Robin (Paso {self.current_step + 1})', 
                    color='white', fontsize=14, fontweight='bold')
        
        # Configurar colores
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Agregar líneas de tiempo
        if events_so_far:
            max_time = max([event[2] for event in events_so_far])
            for t in range(0, max_time + 1, max(1, max_time // 10)):
                ax.axvline(x=t, color='gray', linestyle='--', alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def update_results_table_progressive(self, completed_so_far):
        # Limpiar tabla
        self.results_table.setRowCount(0)
        
        if not completed_so_far:
            self.stats_label.setText("📊 Procesos completados: 0 - Esperando finalización...")
            return
        
        # Agregar solo procesos completados hasta ahora
        self.results_table.setRowCount(len(completed_so_far))
        
        total_turnaround = 0
        total_waiting = 0
        
        for i, process in enumerate(sorted(completed_so_far, key=lambda x: x.id)):
            self.results_table.setItem(i, 0, QTableWidgetItem(process.id))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(process.arrival)))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(process.original_burst)))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(process.finish_time)))
            self.results_table.setItem(i, 4, QTableWidgetItem(str(process.turnaround)))
            self.results_table.setItem(i, 5, QTableWidgetItem(str(process.waiting)))
            
            total_turnaround += process.turnaround
            total_waiting += process.waiting
        
        # Actualizar estadísticas
        avg_turnaround = total_turnaround / len(completed_so_far)
        avg_waiting = total_waiting / len(completed_so_far)
        
        stats_text = f"""
        📊 ESTADÍSTICAS PARCIALES:
        • Procesos completados: {len(completed_so_far)} de {len(self.processes)}
        • Tiempo promedio de retorno: {avg_turnaround:.2f} ms
        • Tiempo promedio de espera: {avg_waiting:.2f} ms
        """
        if completed_so_far:
            stats_text += f"• Tiempo actual de simulación: {max([p.finish_time for p in completed_so_far])} ms"
        
        self.stats_label.setText(stats_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())