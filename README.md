# 🚀 Simulador Round Robin - Planificación de Procesos

Una aplicación moderna y completa para simular el algoritmo de planificación Round Robin con interfaz gráfica avanzada.

## ✨ Características

- **Interfaz Gráfica Moderna**: Diseño oscuro y profesional con PyQt5
- **Simulación Paso a Paso**: Visualiza cada entrada y salida del procesador para comprobar exclusión mutua
- **Diagrama de Gantt Interactivo**: Representación visual colorida del timeline de ejecución
- **Cálculos Precisos**: Implementación correcta de las fórmulas:
  - `Tf = tiempo_final`
  - `Tr = Tf - tiempo_llegada` 
  - `Te = Tr - tiempo_rafaga`
- **Reproducción Automática**: Modo automático para ver la simulación completa
- **Estadísticas Completas**: Promedios y métricas de rendimiento

## 🛠️ Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python main.py
```

## 📋 Uso

1. **Agregar Procesos**: Introduce tiempo de llegada y ráfaga, luego haz clic en "Agregar Proceso"
2. **Configurar Quantum**: Establece el valor del quantum para el algoritmo Round Robin
3. **Ejecutar Simulación**: Haz clic en "Ejecutar Simulación" para procesar todos los procesos
4. **Ver Paso a Paso**: Usa "Siguiente Paso" o "Reproducción Automática" para ver la ejecución detallada
5. **Analizar Resultados**: Revisa el diagrama de Gantt y la tabla de resultados finales

## 🔧 Funcionalidades Técnicas

- **Exclusión Mutua**: Cada log muestra claramente cuando el procesador entra y sale de la sección crítica
- **Gestión de Cola**: Visualización del estado de la cola en cada momento
- **Cálculos Correctos**: Algoritmo mejorado que maneja correctamente:
  - Procesos que llegan en diferentes momentos
  - División por quantum
  - Cálculo preciso de tiempos de finalización, retorno y espera
 
## 🧮 Fórmulas Implementadas

- **Tiempo Final (Tf)**: Momento en que termina la ejecución del proceso
- **Tiempo Retorno (Tr)**: `Tf - tiempo_llegada`
- **Tiempo Espera (Te)**: `Tr - tiempo_rafaga`
- **Promedios**: Cálculo automático de tiempos promedio de retorno y espera
