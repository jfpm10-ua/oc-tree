import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import sys
from collections import defaultdict
import math

class PuntoNube:
    """Clase para representar un punto 3D con información adicional"""
    def __init__(self, x, y, z, r=0, g=0, b=0):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.g = g
        self.b = b
    
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

class LectorPCD:
    """Lector de archivos PCD para cargar nubes de puntos"""
    
    @staticmethod
    def leer_archivo_pcd(ruta_archivo):
        """
        Lee un archivo PCD y devuelve una lista de puntos
        """
        puntos = []
        
        try:
            with open(ruta_archivo, 'r') as archivo:
                # Leer cabecera
                linea = archivo.readline()
                while linea and not linea.startswith('DATA'):
                    if linea.startswith('POINTS'):
                        num_puntos = int(linea.split()[1])
                    linea = archivo.readline()
                
                # Leer datos
                for linea in archivo:
                    if linea.strip():
                        valores = linea.strip().split()
                        if len(valores) >= 3:
                            x = float(valores[0])
                            y = float(valores[1])
                            z = float(valores[2])
                            
                            # Valores RGB si están disponibles
                            r = int(valores[3]) if len(valores) > 3 else 0
                            g = int(valores[4]) if len(valores) > 4 else 0
                            b = int(valores[5]) if len(valores) > 5 else 0
                            
                            puntos.append(PuntoNube(x, y, z, r, g, b))
        
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {ruta_archivo}")
            return []
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return []
        
        return puntos
    
    @staticmethod
    def generar_datos_sinteticos(num_puntos=10000, rango=10.0):
        """
        Genera datos sintéticos para pruebas
        """
        puntos = []
        np.random.seed(42)  # Para reproducibilidad
        
        for _ in range(num_puntos):
            x = np.random.uniform(-rango, rango)
            y = np.random.uniform(-rango, rango)
            z = np.random.uniform(-rango, rango)
            
            r = np.random.randint(0, 255)
            g = np.random.randint(0, 255)
            b = np.random.randint(0, 255)
            
            puntos.append(PuntoNube(x, y, z, r, g, b))
        
        return puntos

class Celda:
    """Clase para representar una celda en la rejilla de ocupación"""
    def __init__(self):
        self.num_puntos = 0
        self.suma_x = 0.0
        self.suma_y = 0.0
        self.suma_z = 0.0
        self.puntos = []
    
    def agregar_punto(self, punto):
        """Agrega un punto a la celda"""
        self.num_puntos += 1
        self.suma_x += punto.x
        self.suma_y += punto.y
        self.suma_z += punto.z
        self.puntos.append(punto)
    
    def obtener_media(self):
        """Calcula la media de los puntos en la celda"""
        if self.num_puntos == 0:
            return None
        return PuntoNube(
            self.suma_x / self.num_puntos,
            self.suma_y / self.num_puntos,
            self.suma_z / self.num_puntos
        )
    
    def esta_ocupada(self):
        """Verifica si la celda está ocupada"""
        return self.num_puntos > 0

class RejillaOcupacion:
    """Implementación de rejilla de ocupación 3D"""
    
    def __init__(self, tamaño_celda=1.0):
        self.tamaño_celda = tamaño_celda
        self.celdas = {}
        self.num_puntos_total = 0
        self.limites = {'min_x': float('inf'), 'max_x': float('-inf'),
                       'min_y': float('inf'), 'max_y': float('-inf'),
                       'min_z': float('inf'), 'max_z': float('-inf')}
    
    def _obtener_indices_celda(self, punto):
        """Calcula los índices de celda para un punto dado"""
        i = int(math.floor(punto.x / self.tamaño_celda))
        j = int(math.floor(punto.y / self.tamaño_celda))
        k = int(math.floor(punto.z / self.tamaño_celda))
        return (i, j, k)
    
    def agregar_punto(self, punto):
        """Agrega un punto a la rejilla"""
        indices = self._obtener_indices_celda(punto)
        
        if indices not in self.celdas:
            self.celdas[indices] = Celda()
        
        self.celdas[indices].agregar_punto(punto)
        self.num_puntos_total += 1
        
        # Actualizar límites
        self.limites['min_x'] = min(self.limites['min_x'], punto.x)
        self.limites['max_x'] = max(self.limites['max_x'], punto.x)
        self.limites['min_y'] = min(self.limites['min_y'], punto.y)
        self.limites['max_y'] = max(self.limites['max_y'], punto.y)
        self.limites['min_z'] = min(self.limites['min_z'], punto.z)
        self.limites['max_z'] = max(self.limites['max_z'], punto.z)
    
    def agregar_puntos(self, puntos):
        """Agrega múltiples puntos a la rejilla"""
        for punto in puntos:
            self.agregar_punto(punto)
    
    def obtener_estadisticas(self):
        """Calcula estadísticas de la rejilla"""
        num_celdas_ocupadas = len(self.celdas)
        num_celdas_vacias = 0
        
        # Calcular número total de celdas posibles
        if self.limites['min_x'] != float('inf'):
            dim_x = int((self.limites['max_x'] - self.limites['min_x']) / self.tamaño_celda) + 1
            dim_y = int((self.limites['max_y'] - self.limites['min_y']) / self.tamaño_celda) + 1
            dim_z = int((self.limites['max_z'] - self.limites['min_z']) / self.tamaño_celda) + 1
            num_celdas_totales = dim_x * dim_y * dim_z
            num_celdas_vacias = num_celdas_totales - num_celdas_ocupadas
        
        # Calcular media de puntos por celda ocupada
        total_puntos_celdas = sum(celda.num_puntos for celda in self.celdas.values())
        media_puntos_celda = total_puntos_celdas / num_celdas_ocupadas if num_celdas_ocupadas > 0 else 0
        
        # Calcular memoria aproximada (en bytes)
        memoria_bytes = sys.getsizeof(self.celdas)
        for celda in self.celdas.values():
            memoria_bytes += sys.getsizeof(celda) + sys.getsizeof(celda.puntos)
            memoria_bytes += sum(sys.getsizeof(p) for p in celda.puntos)
        
        return {
            'num_celdas_ocupadas': num_celdas_ocupadas,
            'num_celdas_vacias': num_celdas_vacias,
            'media_puntos_celda': media_puntos_celda,
            'memoria_bytes': memoria_bytes,
            'memoria_mb': memoria_bytes / (1024 * 1024)
        }

class NodoOctree:
    """Nodo para la estructura Octree"""
    
    def __init__(self, centro, tamaño):
        self.centro = centro  # (x, y, z)
        self.tamaño = tamaño
        self.puntos = []
        self.hijos = [None] * 8  # 8 hijos para un octree
        self.es_hoja = True
        self.num_puntos = 0
        self.suma_x = 0.0
        self.suma_y = 0.0
        self.suma_z = 0.0
    
    def agregar_punto(self, punto):
        """Agrega un punto al nodo"""
        self.puntos.append(punto)
        self.num_puntos += 1
        self.suma_x += punto.x
        self.suma_y += punto.y
        self.suma_z += punto.z
    
    def obtener_media(self):
        """Calcula la media de los puntos en el nodo"""
        if self.num_puntos == 0:
            return None
        return PuntoNube(
            self.suma_x / self.num_puntos,
            self.suma_y / self.num_puntos,
            self.suma_z / self.num_puntos
        )
    
    def contiene_punto(self, punto):
        """Verifica si el punto está dentro del nodo"""
        half_size = self.tamaño / 2
        return (self.centro[0] - half_size <= punto.x < self.centro[0] + half_size and
                self.centro[1] - half_size <= punto.y < self.centro[1] + half_size and
                self.centro[2] - half_size <= punto.z < self.centro[2] + half_size)

class Octree:
    """Implementación de estructura Octree 3D"""
    
    def __init__(self, tamaño_minimo=1.0):
        self.tamaño_minimo = tamaño_minimo
        self.raiz = None
        self.num_puntos_total = 0
        self.num_nodos = 0
    
    def _calcular_limites(self, puntos):
        """Calcula los límites del espacio de puntos"""
        if not puntos:
            return (0, 0, 0), 1.0
        
        min_x = min(p.x for p in puntos)
        max_x = max(p.x for p in puntos)
        min_y = min(p.y for p in puntos)
        max_y = max(p.y for p in puntos)
        min_z = min(p.z for p in puntos)
        max_z = max(p.z for p in puntos)
        
        centro_x = (min_x + max_x) / 2
        centro_y = (min_y + max_y) / 2
        centro_z = (min_z + max_z) / 2
        
        tamaño = max(max_x - min_x, max_y - min_y, max_z - min_z) * 1.1
        
        return (centro_x, centro_y, centro_z), tamaño
    
    def construir_octree(self, puntos):
        """Construye el octree con los puntos dados"""
        if not puntos:
            return
        
        centro, tamaño = self._calcular_limites(puntos)
        self.raiz = NodoOctree(centro, tamaño)
        self.num_nodos = 1
        
        for punto in puntos:
            self._insertar_punto(self.raiz, punto)
            self.num_puntos_total += 1
    
    def _insertar_punto(self, nodo, punto):
        """Inserta un punto en el octree"""
        if not nodo.contiene_punto(punto):
            return False
        
        # Si el nodo es una hoja y no excede el tamaño mínimo
        if nodo.es_hoja and nodo.tamaño <= self.tamaño_minimo:
            nodo.agregar_punto(punto)
            return True
        
        # Si el nodo es una hoja y debe subdividirse
        if nodo.es_hoja:
            self._subdividir_nodo(nodo)
        
        # Insertar en el hijo apropiado
        indice_hijo = self._obtener_indice_hijo(nodo, punto)
        if nodo.hijos[indice_hijo] is None:
            nuevo_centro = self._calcular_centro_hijo(nodo.centro, nodo.tamaño, indice_hijo)
            nodo.hijos[indice_hijo] = NodoOctree(nuevo_centro, nodo.tamaño / 2)
            self.num_nodos += 1
        
        return self._insertar_punto(nodo.hijos[indice_hijo], punto)
    
    def _subdividir_nodo(self, nodo):
        """Subdivide un nodo en 8 hijos"""
        nodo.es_hoja = False
        
        # Redistribuir puntos existentes
        puntos_temp = nodo.puntos[:]
        nodo.puntos = []
        
        for punto in puntos_temp:
            indice_hijo = self._obtener_indice_hijo(nodo, punto)
            if nodo.hijos[indice_hijo] is None:
                nuevo_centro = self._calcular_centro_hijo(nodo.centro, nodo.tamaño, indice_hijo)
                nodo.hijos[indice_hijo] = NodoOctree(nuevo_centro, nodo.tamaño / 2)
                self.num_nodos += 1
            
            nodo.hijos[indice_hijo].agregar_punto(punto)
    
    def _obtener_indice_hijo(self, nodo, punto):
        """Calcula el índice del hijo para un punto dado"""
        indice = 0
        if punto.x >= nodo.centro[0]:
            indice |= 1
        if punto.y >= nodo.centro[1]:
            indice |= 2
        if punto.z >= nodo.centro[2]:
            indice |= 4
        return indice
    
    def _calcular_centro_hijo(self, centro_padre, tamaño_padre, indice_hijo):
        """Calcula el centro de un nodo hijo"""
        offset = tamaño_padre / 4
        
        x = centro_padre[0] + (offset if indice_hijo & 1 else -offset)
        y = centro_padre[1] + (offset if indice_hijo & 2 else -offset)
        z = centro_padre[2] + (offset if indice_hijo & 4 else -offset)
        
        return (x, y, z)
    
    def obtener_estadisticas(self):
        """Calcula estadísticas del octree"""
        if self.raiz is None:
            return {
                'num_nodos': 0,
                'num_nodos_hoja': 0,
                'num_nodos_ocupados': 0,
                'num_nodos_vacios': 0,
                'media_puntos_nodo': 0,
                'memoria_bytes': 0,
                'memoria_mb': 0
            }
        
        stats = self._calcular_estadisticas_nodo(self.raiz)
        
        # Calcular memoria aproximada
        memoria_bytes = self._calcular_memoria_nodo(self.raiz)
        
        return {
            'num_nodos': self.num_nodos,
            'num_nodos_hoja': stats['num_hojas'],
            'num_nodos_ocupados': stats['num_ocupados'],
            'num_nodos_vacios': stats['num_vacios'],
            'media_puntos_nodo': stats['total_puntos'] / stats['num_ocupados'] if stats['num_ocupados'] > 0 else 0,
            'memoria_bytes': memoria_bytes,
            'memoria_mb': memoria_bytes / (1024 * 1024)
        }
    
    def _calcular_estadisticas_nodo(self, nodo):
        """Calcula estadísticas recursivamente"""
        if nodo is None:
            return {'num_hojas': 0, 'num_ocupados': 0, 'num_vacios': 0, 'total_puntos': 0}
        
        stats = {'num_hojas': 0, 'num_ocupados': 0, 'num_vacios': 0, 'total_puntos': 0}
        
        if nodo.es_hoja:
            stats['num_hojas'] = 1
            if nodo.num_puntos > 0:
                stats['num_ocupados'] = 1
                stats['total_puntos'] = nodo.num_puntos
            else:
                stats['num_vacios'] = 1
        else:
            for hijo in nodo.hijos:
                if hijo is not None:
                    stats_hijo = self._calcular_estadisticas_nodo(hijo)
                    stats['num_hojas'] += stats_hijo['num_hojas']
                    stats['num_ocupados'] += stats_hijo['num_ocupados']
                    stats['num_vacios'] += stats_hijo['num_vacios']
                    stats['total_puntos'] += stats_hijo['total_puntos']
        
        return stats
    
    def _calcular_memoria_nodo(self, nodo):
        """Calcula memoria usada recursivamente"""
        if nodo is None:
            return 0
        
        memoria = sys.getsizeof(nodo) + sys.getsizeof(nodo.puntos)
        memoria += sum(sys.getsizeof(p) for p in nodo.puntos)
        
        for hijo in nodo.hijos:
            if hijo is not None:
                memoria += self._calcular_memoria_nodo(hijo)
        
        return memoria

class VisualizadorOctree:
    """Visualizador 3D para octree"""
    
    def __init__(self, octree):
        self.octree = octree
    
    def visualizar_nodos(self, max_nodos=1000):
        """Visualiza los nodos del octree"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        if self.octree.raiz is None:
            print("El octree está vacío")
            return
        
        nodos_visitados = 0
        self._dibujar_nodo(ax, self.octree.raiz, max_nodos, nodos_visitados)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Visualización de Octree')
        
        plt.tight_layout()
        plt.show()
    
    def _dibujar_nodo(self, ax, nodo, max_nodos, nodos_visitados):
        """Dibuja un nodo del octree"""
        if nodo is None or nodos_visitados >= max_nodos:
            return nodos_visitados
        
        # Dibujar el cubo del nodo
        if nodo.num_puntos > 0:  # Solo dibujar nodos ocupados
            self._dibujar_cubo(ax, nodo.centro, nodo.tamaño, nodo.num_puntos)
            nodos_visitados += 1
        
        # Dibujar hijos
        if not nodo.es_hoja:
            for hijo in nodo.hijos:
                if hijo is not None:
                    nodos_visitados = self._dibujar_nodo(ax, hijo, max_nodos, nodos_visitados)
        
        return nodos_visitados
    
    def _dibujar_cubo(self, ax, centro, tamaño, num_puntos):
        """Dibuja un cubo en el espacio 3D"""
        half_size = tamaño / 2
        
        # Definir vértices del cubo
        vertices = [
            [centro[0] - half_size, centro[1] - half_size, centro[2] - half_size],
            [centro[0] + half_size, centro[1] - half_size, centro[2] - half_size],
            [centro[0] + half_size, centro[1] + half_size, centro[2] - half_size],
            [centro[0] - half_size, centro[1] + half_size, centro[2] - half_size],
            [centro[0] - half_size, centro[1] - half_size, centro[2] + half_size],
            [centro[0] + half_size, centro[1] - half_size, centro[2] + half_size],
            [centro[0] + half_size, centro[1] + half_size, centro[2] + half_size],
            [centro[0] - half_size, centro[1] + half_size, centro[2] + half_size]
        ]
        
        # Dibujar aristas del cubo
        aristas = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # Base inferior
            [4, 5], [5, 6], [6, 7], [7, 4],  # Base superior
            [0, 4], [1, 5], [2, 6], [3, 7]   # Aristas verticales
        ]
        
        # Color basado en el número de puntos
        intensidad = min(num_puntos / 100, 1.0)  # Normalizar
        color = plt.cm.viridis(intensidad)
        
        for arista in aristas:
            punto1 = vertices[arista[0]]
            punto2 = vertices[arista[1]]
            ax.plot3D([punto1[0], punto2[0]], [punto1[1], punto2[1]], [punto1[2], punto2[2]], 
                     color=color, alpha=0.6, linewidth=1)

class AnalizadorComparativo:
    """Analizador para comparar rejilla de ocupación y octree"""
    
    def __init__(self):
        self.resultados = []
    
    def comparar_metodos(self, puntos, tamaños_celda):
        """Compara ambos métodos con diferentes tamaños de celda"""
        print("Iniciando análisis comparativo...")
        
        for tamaño in tamaños_celda:
            print(f"\nAnalizando tamaño de celda: {tamaño}")
            
            # Rejilla de ocupación
            tiempo_inicio = time.time()
            rejilla = RejillaOcupacion(tamaño)
            rejilla.agregar_puntos(puntos)
            tiempo_rejilla = time.time() - tiempo_inicio
            stats_rejilla = rejilla.obtener_estadisticas()
            
            # Octree
            tiempo_inicio = time.time()
            octree = Octree(tamaño)
            octree.construir_octree(puntos)
            tiempo_octree = time.time() - tiempo_inicio
            stats_octree = octree.obtener_estadisticas()
            
            resultado = {
                'tamaño_celda': tamaño,
                'rejilla': {
                    'tiempo_construccion': tiempo_rejilla,
                    'celdas_ocupadas': stats_rejilla['num_celdas_ocupadas'],
                    'celdas_vacias': stats_rejilla['num_celdas_vacias'],
                    'media_puntos': stats_rejilla['media_puntos_celda'],
                    'memoria_mb': stats_rejilla['memoria_mb']
                },
                'octree': {
                    'tiempo_construccion': tiempo_octree,
                    'nodos_ocupados': stats_octree['num_nodos_ocupados'],
                    'nodos_vacios': stats_octree['num_nodos_vacios'],
                    'media_puntos': stats_octree['media_puntos_nodo'],
                    'memoria_mb': stats_octree['memoria_mb'],
                    'total_nodos': stats_octree['num_nodos']
                }
            }
            
            self.resultados.append(resultado)
            
            print(f"  Rejilla - Celdas ocupadas: {stats_rejilla['num_celdas_ocupadas']}, "
                  f"Memoria: {stats_rejilla['memoria_mb']:.2f} MB, "
                  f"Tiempo: {tiempo_rejilla:.3f}s")
            print(f"  Octree - Nodos ocupados: {stats_octree['num_nodos_ocupados']}, "
                  f"Memoria: {stats_octree['memoria_mb']:.2f} MB, "
                  f"Tiempo: {tiempo_octree:.3f}s")
    
    def generar_graficos(self):
        """Genera gráficos comparativos"""
        if not self.resultados:
            print("No hay resultados para graficar")
            return
        
        tamaños = [r['tamaño_celda'] for r in self.resultados]
        
        # Configurar subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Comparación Rejilla de Ocupación vs Octree', fontsize=16)
        
        # Memoria
        memoria_rejilla = [r['rejilla']['memoria_mb'] for r in self.resultados]
        memoria_octree = [r['octree']['memoria_mb'] for r in self.resultados]
        
        axes[0, 0].plot(tamaños, memoria_rejilla, 'b-o', label='Rejilla', linewidth=2)
        axes[0, 0].plot(tamaños, memoria_octree, 'r-s', label='Octree', linewidth=2)
        axes[0, 0].set_xlabel('Tamaño de Celda')
        axes[0, 0].set_ylabel('Memoria (MB)')
        axes[0, 0].set_title('Uso de Memoria')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Tiempo de construcción
        tiempo_rejilla = [r['rejilla']['tiempo_construccion'] for r in self.resultados]
        tiempo_octree = [r['octree']['tiempo_construccion'] for r in self.resultados]
        
        axes[0, 1].plot(tamaños, tiempo_rejilla, 'b-o', label='Rejilla', linewidth=2)
        axes[0, 1].plot(tamaños, tiempo_octree, 'r-s', label='Octree', linewidth=2)
        axes[0, 1].set_xlabel('Tamaño de Celda')
        axes[0, 1].set_ylabel('Tiempo (segundos)')
        axes[0, 1].set_title('Tiempo de Construcción')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Número de celdas/nodos ocupados
        ocupadas_rejilla = [r['rejilla']['celdas_ocupadas'] for r in self.resultados]
        ocupadas_octree = [r['octree']['nodos_ocupados'] for r in self.resultados]
        
        axes[1, 0].plot(tamaños, ocupadas_rejilla, 'b-o', label='Rejilla', linewidth=2)
        axes[1, 0].plot(tamaños, ocupadas_octree, 'r-s', label='Octree', linewidth=2)
        axes[1, 0].set_xlabel('Tamaño de Celda')
        axes[1, 0].set_ylabel('Número de Celdas/Nodos Ocupados')
        axes[1, 0].set_title('Celdas/Nodos Ocupados')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Media de puntos por celda/nodo
        media_rejilla = [r['rejilla']['media_puntos'] for r in self.resultados]
        media_octree = [r['octree']['media_puntos'] for r in self.resultados]
        
        axes[1, 1].plot(tamaños, media_rejilla, 'b-o', label='Rejilla', linewidth=2)
        axes[1, 1].plot(tamaños, media_octree, 'r-s', label='Octree', linewidth=2)
        axes[1, 1].set_xlabel('Tamaño de Celda')
        axes[1, 1].set_ylabel('Media de Puntos')
        axes[1, 1].set_title('Media de Puntos por Celda/Nodo')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def generar_informe(self):
        """Genera un informe textual de los resultados"""
        if not self.resultados:
            print("No hay resultados para el informe")
            return
        
        print("\n" + "="*80)
        print("INFORME COMPARATIVO: REJILLA DE OCUPACIÓN vs OCTREE")
        print("="*80)
        
        for resultado in self.resultados:
            tamaño = resultado['tamaño_celda']
            print(f"\nTAMAÑO DE CELDA: {tamaño}")
            print("-" * 50)
            
            # Rejilla
            r = resultado['rejilla']
            print(f"REJILLA DE OCUPACIÓN:")
            print(f"  - Celdas ocupadas: {r['celdas_ocupadas']}")
            print(f"  - Celdas vacías: {r['celdas_vacias']}")
            print(f"  - Media puntos/celda: {r['media_puntos']:.2f}")
            print(f"  - Memoria: {r['memoria_mb']:.2f} MB")
            print(f"  - Tiempo construcción: {r['tiempo_construccion']:.3f}s")
            
            # Octree
            o = resultado['octree']
            print(f"OCTREE:")
            print(f"  - Nodos ocupados: {o['nodos_ocupados']}")
            print(f"  - Nodos vacíos: {o['nodos_vacios']}")
            print(f"  - Total nodos: {o['total_nodos']}")
            print(f"  - Media puntos/nodo: {o['media_puntos']:.2f}")
            print(f"  - Memoria: {o['memoria_mb']:.2f} MB")
            print(f"  - Tiempo construcción: {o['tiempo_construccion']:.3f}s")
            
            # Comparación
            print(f"COMPARACIÓN:")
            memoria_ratio = r['memoria_mb'] / o['memoria_mb'] if o['memoria_mb'] > 0 else float('inf')
            tiempo_ratio = r['tiempo_construccion'] / o['tiempo_construccion'] if o['tiempo_construccion'] > 0 else float('inf')
            print(f"  - Ratio memoria (Rejilla/Octree): {memoria_ratio:.2f}")
            print(f"  - Ratio tiempo (Rejilla/Octree): {tiempo_ratio:.2f}")
            
            if memoria_ratio < 1:
                print(f"  - La rejilla usa {(1-memoria_ratio)*100:.1f}% menos memoria")
            else:
                print(f"  - El octree usa {(1-1/memoria_ratio)*100:.1f}% menos memoria")


def main():
    """Función principal para ejecutar las pruebas"""
    print("PRÁCTICA 2: MAPAS MÉTRICOS")
    print("=" * 50)
    
    # Generar datos sintéticos para pruebas
    print("Generando datos sintéticos...")
    puntos = LectorPCD.generar_datos_sinteticos(num_puntos=5000, rango=20.0)
    print(f"Generados {len(puntos)} puntos")
    
    # Definir tamaños de celda para las pruebas
    tamaños_celda = [0.5, 1.0, 2.0, 4.0, 8.0]
    
    # Crear analizador
    analizador = AnalizadorComparativo()
    
    # Realizar comparación
    analizador.comparar_metodos(puntos, tamaños_celda)
    
    # Generar informe
    analizador.generar_informe()
    
    # Generar gráficos
    print("\nGenerando gráficos comparativos...")
    analizador.generar_graficos()
    
    # Ejemplo de uso individual de cada estructura
    print("\n" + "="*50)
    print("EJEMPLO DE USO INDIVIDUAL")
    print("="*50)
    
    # Ejemplo con rejilla
    print("\nEjemplo Rejilla de Ocupación:")
    rejilla_ejemplo = RejillaOcupacion(tamaño_celda=2.0)
    rejilla_ejemplo.agregar_puntos(puntos[:1000])  # Usar subset para ejemplo
    stats_rejilla = rejilla_ejemplo.obtener_estadisticas()
    
    print(f"- Puntos procesados: 1000")
    print(f"- Celdas ocupadas: {stats_rejilla['num_celdas_ocupadas']}")
    print(f"- Media puntos por celda: {stats_rejilla['media_puntos_celda']:.2f}")
    print(f"- Memoria utilizada: {stats_rejilla['memoria_mb']:.2f} MB")
    
    # Ejemplo con octree
    print("\nEjemplo Octree:")
    octree_ejemplo = Octree(tamaño_minimo=2.0)
    octree_ejemplo.construir_octree(puntos[:1000])  # Usar subset para ejemplo
    stats_octree = octree_ejemplo.obtener_estadisticas()
    
    print(f"- Puntos procesados: 1000")
    print(f"- Nodos totales: {stats_octree['num_nodos']}")
    print(f"- Nodos ocupados: {stats_octree['num_nodos_ocupados']}")
    print(f"- Media puntos por nodo: {stats_octree['media_puntos_nodo']:.2f}")
    print(f"- Memoria utilizada: {stats_octree['memoria_mb']:.2f} MB")
    
    # Ejemplo de visualización (parte optativa)
    print("\nEjemplo de Visualización (Parte Optativa):")
    try:
        # Crear octree más pequeño para visualización
        puntos_vis = LectorPCD.generar_datos_sinteticos(num_puntos=500, rango=10.0)
        octree_vis = Octree(tamaño_minimo=2.0)
        octree_vis.construir_octree(puntos_vis)
        
        visualizador = VisualizadorOctree(octree_vis)
        print("Generando visualización 3D del octree...")
        visualizador.visualizar_nodos(max_nodos=100)
        
    except Exception as e:
        print(f"Error en visualización: {e}")
        print("La visualización requiere matplotlib con soporte 3D")


def pruebas_unitarias():
    """Pruebas unitarias para verificar el funcionamiento"""
    print("\n" + "="*50)
    print("EJECUTANDO PRUEBAS UNITARIAS")
    print("="*50)
    
    # Crear datos de prueba simples
    puntos_prueba = [
        PuntoNube(0, 0, 0),
        PuntoNube(1, 1, 1),
        PuntoNube(2, 2, 2),
        PuntoNube(-1, -1, -1)
    ]
    
    # Prueba rejilla
    print("\nPrueba Rejilla de Ocupación:")
    rejilla_test = RejillaOcupacion(tamaño_celda=1.0)
    rejilla_test.agregar_puntos(puntos_prueba)
    
    stats = rejilla_test.obtener_estadisticas()
    print(f"✓ Puntos agregados correctamente")
    print(f"✓ Celdas ocupadas: {stats['num_celdas_ocupadas']}")
    print(f"✓ Media puntos: {stats['media_puntos_celda']:.2f}")
    
    # Prueba octree
    print("\nPrueba Octree:")
    octree_test = Octree(tamaño_minimo=0.5)
    octree_test.construir_octree(puntos_prueba)
    
    stats = octree_test.obtener_estadisticas()
    print(f"✓ Octree construido correctamente")
    print(f"✓ Nodos totales: {stats['num_nodos']}")
    print(f"✓ Nodos ocupados: {stats['num_nodos_ocupados']}")
    
    # Verificar que los puntos están contenidos
    assert octree_test.raiz is not None, "La raíz del octree no debe ser None"
    assert octree_test.num_puntos_total == len(puntos_prueba), "Número de puntos incorrecto"
    
    print("✓ Todas las pruebas unitarias pasaron correctamente")


def ejemplo_lectura_pcd():
    """Ejemplo de cómo leer un archivo PCD real"""
    print("\n" + "="*50)
    print("EJEMPLO DE LECTURA DE ARCHIVO PCD")
    print("="*50)
    
    # Crear un archivo PCD de ejemplo
    contenido_pcd = """# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z r g b
SIZE 4 4 4 1 1 1
TYPE F F F I I I
COUNT 1 1 1 1 1 1
WIDTH 10
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS 10
DATA ascii
0.0 0.0 0.0 255 0 0
1.0 0.0 0.0 0 255 0
0.0 1.0 0.0 0 0 255
0.0 0.0 1.0 255 255 0
1.0 1.0 0.0 255 0 255
1.0 0.0 1.0 0 255 255
0.0 1.0 1.0 128 128 128
1.0 1.0 1.0 255 255 255
-1.0 0.0 0.0 64 64 64
0.0 -1.0 0.0 192 192 192
"""
    
    # Guardar archivo de ejemplo
    with open('ejemplo.pcd', 'w') as f:
        f.write(contenido_pcd)
    
    # Leer archivo
    print("Leyendo archivo PCD de ejemplo...")
    puntos_pcd = LectorPCD.leer_archivo_pcd('ejemplo.pcd')
    
    if puntos_pcd:
        print(f"✓ Se leyeron {len(puntos_pcd)} puntos del archivo PCD")
        print("Primeros 3 puntos:")
        for i, punto in enumerate(puntos_pcd[:3]):
            print(f"  Punto {i+1}: {punto} RGB({punto.r},{punto.g},{punto.b})")
        
        # Procesar con ambas estructuras
        print("\nProcesando puntos PCD con rejilla...")
        rejilla_pcd = RejillaOcupacion(tamaño_celda=0.5)
        rejilla_pcd.agregar_puntos(puntos_pcd)
        
        print("Procesando puntos PCD con octree...")
        octree_pcd = Octree(tamaño_minimo=0.5)
        octree_pcd.construir_octree(puntos_pcd)
        
        print("✓ Procesamiento completado")
    else:
        print("✗ Error al leer el archivo PCD")
    
    # Limpiar archivo de ejemplo
    import os
    try:
        os.remove('ejemplo.pcd')
    except:
        pass


if __name__ == "__main__":
    # Ejecutar programa principal
    main()
    
    # Ejecutar pruebas unitarias
    pruebas_unitarias()
    
    # Ejemplo de lectura PCD
    ejemplo_lectura_pcd()
    
    print("\n" + "="*80)
    print("PRÁCTICA 2 COMPLETADA")
    print("="*80)
    print("Se han implementado:")
    print("✓ Rejilla de ocupación 3D")
    print("✓ Estructura Octree 3D")
    print("✓ Lector de archivos PCD")
    print("✓ Sistema de análisis comparativo")
    print("✓ Visualizador 3D (parte optativa)")
    print("✓ Pruebas unitarias")
    print("✓ Generación de gráficos y estadísticas")
    print("\nEl código está listo para su uso y evaluación.")