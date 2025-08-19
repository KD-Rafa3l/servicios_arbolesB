import os
import time
import random
from collections import defaultdict

class Proveedor:
    def __init__(self, id_proveedor, nombre, servicio, calificacion, ubicacion=None):
        """Clase que representa un proveedor de servicios con validación de datos"""
        if not nombre or not isinstance(nombre, str):
            raise ValueError("Nombre no válido")
        if not servicio or not isinstance(servicio, str):
            raise ValueError("Servicio no válido")
        try:
            calificacion = float(calificacion)
            if not (1 <= calificacion <= 5):
                raise ValueError("Calificación debe ser entre 1 y 5")
        except (ValueError, TypeError):
            raise ValueError("Calificación debe ser un número entre 1 y 5")
        
        self.id = int(id_proveedor)
        self.nombre = nombre.strip()
        self.servicio = servicio.strip().lower()
        self.calificacion = calificacion
        self.ubicacion = ubicacion.strip() if ubicacion and isinstance(ubicacion, str) else "Sin ubicación"
    
    def __str__(self):
        return (f"ID: {self.id} | Nombre: {self.nombre} | Servicio: {self.servicio} | "
                f"Calificación: {self.calificacion:.1f} | Ubicación: {self.ubicacion}")

class NodoB:
    def __init__(self, grado_minimo, hoja=True):
        """Nodo del árbol B que puede almacenar múltiples proveedores"""
        self.grado_minimo = grado_minimo
        self.hoja = hoja
        self.claves = []
        self.hijos = []
        self.proveedores = defaultdict(dict)
        self.ids_registrados = set()
    
    def esta_lleno(self):
        return len(self.claves) >= (2 * self.grado_minimo) - 1
    
    def tiene_minimo(self):
        return len(self.claves) >= self.grado_minimo - 1
    
    def agregar_proveedor(self, proveedor):
        if proveedor.id in self.ids_registrados:
            return False
        if self.hoja and proveedor.servicio not in self.claves:
            idx = 0
            while idx < len(self.claves) and proveedor.servicio > self.claves[idx]:
                idx += 1
            self.claves.insert(idx, proveedor.servicio)
        self.proveedores[proveedor.servicio][proveedor.id] = proveedor
        self.ids_registrados.add(proveedor.id)
        return True
    
    def eliminar_proveedor(self, id_proveedor):
        for servicio in list(self.proveedores.keys()):
            if id_proveedor in self.proveedores[servicio]:
                del self.proveedores[servicio][id_proveedor]
                self.ids_registrados.discard(id_proveedor)
                if not self.proveedores[servicio]:
                    del self.proveedores[servicio]
                    if self.hoja:
                        try:
                            self.claves.remove(servicio)
                        except ValueError:
                            pass
                return True
        return False
    
    def obtener_proveedor(self, id_proveedor):
        for servicio in self.proveedores:
            if id_proveedor in self.proveedores[servicio]:
                return self.proveedores[servicio][id_proveedor]
        return None

class ArbolB:
    def __init__(self, grado_minimo=3):
        if grado_minimo < 2:
            raise ValueError("El grado mínimo debe ser al menos 2")
        self.grado_minimo = grado_minimo
        self.raiz = NodoB(grado_minimo, True)
        self._contador_id = 1
        self._total_proveedores = 0
    
    def verificar_ids(self, max_id=20):
        return [id_esperado for id_esperado in range(1, max_id + 1) 
                if not self._existe_id(id_esperado)]
    
    def insertar(self, nombre, servicio, calificacion, ubicacion=None, id_proveedor=None):
        try:
            nombre = str(nombre).strip()
            if not nombre:
                raise ValueError("El nombre no puede estar vacío")
            servicio = str(servicio).strip().lower()
            if not servicio:
                raise ValueError("El servicio no puede estar vacío")
            try:
                calificacion = float(calificacion)
                if not (1 <= calificacion <= 5):
                    raise ValueError("La calificación debe estar entre 1 y 5")
            except (ValueError, TypeError):
                raise ValueError("La calificación debe ser un número entre 1 y 5")
            ubicacion = str(ubicacion).strip() if ubicacion is not None else "Sin ubicación"
            
            if id_proveedor is None:
                id_proveedor = self._generar_id_unico()
            else:
                id_proveedor = int(id_proveedor)
                if id_proveedor <= 0:
                    raise ValueError("ID debe ser positivo")
                if self._existe_id(id_proveedor):
                    raise ValueError(f"El ID {id_proveedor} ya está en uso")
            
            proveedor = Proveedor(id_proveedor, nombre, servicio, calificacion, ubicacion)
            
            if self.raiz.esta_lleno():
                nueva_raiz = NodoB(self.grado_minimo, False)
                nueva_raiz.hijos.append(self.raiz)
                self._dividir_hijo(nueva_raiz, 0)
                self.raiz = nueva_raiz
            
            self._insertar_no_lleno(self.raiz, proveedor)
            self._total_proveedores += 1
            
            if id_proveedor >= self._contador_id:
                self._contador_id = id_proveedor + 1
                
            return proveedor.id
        except Exception as e:
            print(f"Error al insertar proveedor: {e}")
            return None
    
    def _generar_id_unico(self):
        nuevo_id = self._contador_id
        self._contador_id += 1
        return nuevo_id
    
    def _existe_id(self, id_proveedor):
        return self._buscar_id(self.raiz, id_proveedor) is not None
    
    def _buscar_id(self, nodo, id_proveedor):
        proveedor = nodo.obtener_proveedor(id_proveedor)
        if proveedor is not None:
            return proveedor
        if not nodo.hoja:
            for hijo in nodo.hijos:
                resultado = self._buscar_id(hijo, id_proveedor)
                if resultado is not None:
                    return resultado
        return None
    
    def _insertar_no_lleno(self, nodo, proveedor):
        idx = 0
        while idx < len(nodo.claves) and proveedor.servicio > nodo.claves[idx]:
            idx += 1
        if nodo.hoja:
            if not nodo.agregar_proveedor(proveedor):
                raise ValueError(f"ID {proveedor.id} ya existe en el nodo")
        else:
            if nodo.hijos[idx].esta_lleno():
                self._dividir_hijo(nodo, idx)
                if proveedor.servicio > nodo.claves[idx]:
                    idx += 1
            self._insertar_no_lleno(nodo.hijos[idx], proveedor)
    
    def _dividir_hijo(self, padre, indice_hijo):
        """Divide un nodo hijo lleno, asegurando integridad de datos"""
        hijo = padre.hijos[indice_hijo]
        nuevo_hijo = NodoB(self.grado_minimo, hijo.hoja)
        
        punto_division = self.grado_minimo - 1
        clave_media = hijo.claves[punto_division]
        
        # Mover claves al nuevo hijo
        nuevo_hijo.claves = hijo.claves[punto_division + 1:]
        hijo.claves = hijo.claves[:punto_division]
        
        # Mover proveedores correspondientes
        for clave in nuevo_hijo.claves:
            if clave in hijo.proveedores:
                nuevo_hijo.proveedores[clave] = hijo.proveedores.pop(clave)
        
        # Mover hijos si no es hoja
        if not hijo.hoja:
            nuevo_hijo.hijos = hijo.hijos[punto_division + 1:]
            hijo.hijos = hijo.hijos[:punto_division + 1]
        
        # Manejar la clave media
        if clave_media in hijo.proveedores:
            if hijo.hoja:
                # Dividir proveedores de la clave media
                todos_proveedores = list(hijo.proveedores[clave_media].values())
                mitad = len(todos_proveedores) // 2 if todos_proveedores else 0
                hijo.proveedores[clave_media] = {p.id: p for p in todos_proveedores[:mitad]}
                nuevo_hijo.proveedores[clave_media] = {p.id: p for p in todos_proveedores[mitad:]}
                if not nuevo_hijo.claves or clave_media < nuevo_hijo.claves[0]:
                    nuevo_hijo.claves.insert(0, clave_media)
            else:
                nuevo_hijo.proveedores[clave_media] = hijo.proveedores.pop(clave_media, {})
        
        # Actualizar ids_registrados
        hijo.ids_registrados = set()
        nuevo_hijo.ids_registrados = set()
        for servicio in hijo.proveedores:
            hijo.ids_registrados.update(hijo.proveedores[servicio].keys())
        for servicio in nuevo_hijo.proveedores:
            nuevo_hijo.ids_registrados.update(nuevo_hijo.proveedores[servicio].keys())
        
        # Insertar clave media en el padre
        padre.claves.insert(indice_hijo, clave_media)
        padre.hijos.insert(indice_hijo + 1, nuevo_hijo)
        
        # Depuración
        print(f"División completada. Clave media: {clave_media}, "
              f"Hijo IDs: {hijo.ids_registrados}, Nuevo hijo IDs: {nuevo_hijo.ids_registrados}")
    
    def buscar_por_servicio(self, servicio, orden='nombre'):
        try:
            servicio = str(servicio).strip().lower()
            if not servicio:
                print("Error: El servicio no puede estar vacío")
                return []
            resultados = []
            self._buscar_en_arbol(self.raiz, servicio, resultados)
            resultados_unicos = {p.id: p for p in resultados}
            resultados = list(resultados_unicos.values())
            if orden == 'nombre':
                resultados.sort(key=lambda p: p.nombre)
            elif orden == 'calificacion':
                resultados.sort(key=lambda p: (-p.calificacion, p.nombre))
            elif orden == 'id':
                resultados.sort(key=lambda p: p.id)
            return resultados
        except Exception as e:
            print(f"Error en búsqueda por servicio: {e}")
            return []
    
    def _buscar_en_arbol(self, nodo, servicio, resultados):
        try:
            idx = 0
            while idx < len(nodo.claves) and servicio > nodo.claves[idx]:
                if not nodo.hoja:
                    self._buscar_en_arbol(nodo.hijos[idx], servicio, resultados)
                idx += 1
            if idx < len(nodo.claves) and nodo.claves[idx] == servicio:
                resultados.extend(nodo.proveedores[servicio].values())
            if not nodo.hoja:
                self._buscar_en_arbol(nodo.hijos[idx], servicio, resultados)
        except Exception as e:
            print(f"Error en búsqueda recursiva: {e}")
    
    def listar_todos(self, orden='servicio'):
        try:
            todos = []
            self._recorrer_inorden(self.raiz, todos)
            unicos = {p.id: p for p in todos}
            todos = list(unicos.values())
            if orden == 'servicio':
                todos.sort(key=lambda p: (p.servicio, p.nombre))
            elif orden == 'calificacion':
                todos.sort(key=lambda p: (-p.calificacion, p.servicio, p.nombre))
            elif orden == 'nombre':
                todos.sort(key=lambda p: p.nombre)
            elif orden == 'id':
                todos.sort(key=lambda p: p.id)
            return todos
        except Exception as e:
            print(f"Error al listar proveedores: {e}")
            return []
    
    def _recorrer_inorden(self, nodo, resultados):
        try:
            if nodo.hoja:
                for servicio in nodo.claves:
                    resultados.extend(nodo.proveedores[servicio].values())
            else:
                for i in range(len(nodo.claves)):
                    self._recorrer_inorden(nodo.hijos[i], resultados)
                    resultados.extend(nodo.proveedores.get(nodo.claves[i], {}).values())
                self._recorrer_inorden(nodo.hijos[-1], resultados)
        except Exception as e:
            print(f"Error en recorrido inorden: {e}")
    
    def eliminar_proveedor(self, id_proveedor):
        try:
            id_proveedor = int(id_proveedor)
            if id_proveedor <= 0:
                print("Error: ID debe ser positivo")
                return False
            encontrado = self._eliminar_en_arbol(self.raiz, id_proveedor)
            if encontrado:
                self._total_proveedores -= 1
                if not self.raiz.hoja and len(self.raiz.claves) == 0 and len(self.raiz.hijos) == 1:
                    self.raiz = self.raiz.hijos[0]
                return True
            else:
                print(f"Proveedor con ID {id_proveedor} no encontrado")
                return False
        except (ValueError, TypeError):
            print("Error: ID debe ser un número entero positivo")
            return False
        except Exception as e:
            print(f"Error al eliminar proveedor: {e}")
            return False
    
    def _eliminar_en_arbol(self, nodo, id_proveedor):
        try:
            for servicio in list(nodo.proveedores.keys()):
                if id_proveedor in nodo.proveedores[servicio]:
                    del nodo.proveedores[servicio][id_proveedor]
                    nodo.ids_registrados.discard(id_proveedor)
                    if not nodo.proveedores[servicio]:
                        del nodo.proveedores[servicio]
                        if nodo.hoja:
                            try:
                                nodo.claves.remove(servicio)
                            except ValueError:
                                pass
                    return True
            if not nodo.hoja:
                for i, hijo in enumerate(nodo.hijos):
                    if self._eliminar_en_arbol(hijo, id_proveedor):
                        return True
            return False
        except Exception as e:
            print(f"Error en eliminación recursiva: {e}")
            return False
    
    def actualizar_proveedor(self, id_proveedor, **kwargs):
        try:
            id_proveedor = int(id_proveedor)
            if id_proveedor <= 0:
                print("Error: ID debe ser positivo")
                return False
            proveedor = self._buscar_id(self.raiz, id_proveedor)
            if proveedor is None:
                print(f"Proveedor con ID {id_proveedor} no encontrado")
                return False
            actualizaciones = 0
            if 'nombre' in kwargs:
                nuevo_nombre = str(kwargs['nombre']).strip()
                if nuevo_nombre:
                    proveedor.nombre = nuevo_nombre
                    actualizaciones += 1
            if 'servicio' in kwargs:
                nuevo_servicio = str(kwargs['servicio']).strip().lower()
                if nuevo_servicio and nuevo_servicio != proveedor.servicio:
                    self.eliminar_proveedor(id_proveedor)
                    self.insertar(
                        proveedor.nombre, 
                        nuevo_servicio, 
                        proveedor.calificacion, 
                        proveedor.ubicacion, 
                        id_proveedor
                    )
                    return True
            if 'calificacion' in kwargs:
                try:
                    nueva_calificacion = float(kwargs['calificacion'])
                    if 1 <= nueva_calificacion <= 5:
                        proveedor.calificacion = nueva_calificacion
                        actualizaciones += 1
                    else:
                        print("Error: Calificación debe estar entre 1 y 5")
                except (ValueError, TypeError):
                    print("Error: Calificación debe ser un número entre 1 y 5")
            if 'ubicacion' in kwargs:
                nueva_ubicacion = str(kwargs['ubicacion']).strip()
                proveedor.ubicacion = nueva_ubicacion if nueva_ubicacion else "Sin ubicación"
                actualizaciones += 1
            return actualizaciones > 0
        except (ValueError, TypeError):
            print("Error: ID debe ser un número entero positivo")
            return False
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
            return False
    
    def comparar_busqueda(self, servicio):
        try:
            servicio = str(servicio).strip().lower()
            if not servicio:
                return {'error': 'Servicio no válido'}
            todos = self.listar_todos()
            inicio_arbol = time.time()
            resultados_arbol = self.buscar_por_servicio(servicio)
            tiempo_arbol = time.time() - inicio_arbol
            inicio_lineal = time.time()
            resultados_lineal = [p for p in todos if p.servicio == servicio]
            tiempo_lineal = time.time() - inicio_lineal
            return {
                'servicio': servicio,
                'arbol': {
                    'cantidad': len(resultados_arbol),
                    'tiempo': tiempo_arbol,
                    'resultados': resultados_arbol
                },
                'lineal': {
                    'cantidad': len(resultados_lineal),
                    'tiempo': tiempo_lineal,
                    'resultados': resultados_lineal
                },
                'mejora': tiempo_lineal / tiempo_arbol if tiempo_arbol > 0 else float('inf')
            }
        except Exception as e:
            print(f"Error al comparar búsquedas: {e}")
            return {'error': str(e)}
    
    def estadisticas(self):
        stats = {
            'total_proveedores': self._total_proveedores,
            'proximo_id': self._contador_id,
            'servicios': defaultdict(int),
            'profundidad': self._calcular_profundidad(self.raiz),
            'ids_faltantes': self.verificar_ids(20)
        }
        todos = self.listar_todos()
        for prov in todos:
            stats['servicios'][prov.servicio] += 1
        return stats
    
    def _calcular_profundidad(self, nodo):
        if nodo.hoja:
            return 1
        if not nodo.hijos:
            return 1
        return 1 + self._calcular_profundidad(nodo.hijos[0])

def mostrar_menu():
    print("\n=== Sistema de Gestión de Proveedores con Árbol B ===")
    print("1. Registrar nuevo proveedor")
    print("2. Buscar proveedores por servicio")
    print("3. Listar todos los proveedores")
    print("4. Eliminar proveedor por ID")
    print("5. Actualizar datos de proveedor")
    print("6. Comparar métodos de búsqueda")
    print("7. Mostrar estadísticas del sistema")
    print("8. Cargar datos de prueba")
    print("9. Verificar IDs de proveedores")
    print("10. Salir")

def registrar_proveedor(arbol):
    print("\n--- Registro de Nuevo Proveedor ---")
    nombre = input("Nombre del proveedor: ")
    servicio = input("Tipo de servicio: ")
    while True:
        calificacion = input("Calificación (1-5): ")
        try:
            calificacion = float(calificacion)
            if 1 <= calificacion <= 5:
                break
            print("La calificación debe estar entre 1 y 5")
        except ValueError:
            print("Por favor ingrese un número válido")
    ubicacion = input("Ubicación (opcional): ")
    id_proveedor = arbol.insertar(nombre, servicio, calificacion, ubicacion)
    if id_proveedor:
        print(f"\n✅ Proveedor registrado con ID: {id_proveedor}")

def buscar_proveedores(arbol):
    print("\n--- Búsqueda de Proveedores por Servicio ---")
    servicio = input("Ingrese el servicio a buscar: ")
    print("\nOrdenar resultados por:")
    print("1. Nombre (A-Z)")
    print("2. Calificación (mejor primero)")
    print("3. ID")
    opcion = input("Seleccione una opción: ")
    orden = 'nombre' if opcion == '1' else 'calificacion' if opcion == '2' else 'id'
    resultados = arbol.buscar_por_servicio(servicio, orden)
    print(f"\n🔍 {len(resultados)} proveedores encontrados para '{servicio}':")
    for i, prov in enumerate(resultados, 1):
        print(f"{i}. {prov}")

def listar_proveedores(arbol):
    print("\n--- Listado Completo de Proveedores ---")
    print("\nOrdenar por:")
    print("1. Servicio y nombre")
    print("2. Calificación (mejor primero)")
    print("3. Nombre (A-Z)")
    print("4. ID")
    opcion = input("Seleccione una opción: ")
    orden = 'servicio' if opcion == '1' else 'calificacion' if opcion == '2' else 'nombre' if opcion == '3' else 'id'
    proveedores = arbol.listar_todos(orden)
    print(f"\n📋 Total de proveedores registrados: {len(proveedores)}")
    for i, prov in enumerate(proveedores, 1):
        print(f"{i}. {prov}")

def eliminar_proveedor(arbol):
    print("\n--- Eliminar Proveedor ---")
    id_proveedor = input("Ingrese el ID del proveedor a eliminar: ")
    if arbol.eliminar_proveedor(id_proveedor):
        print("\n✅ Proveedor eliminado correctamente")
    else:
        print("\n❌ No se pudo eliminar el proveedor")

def actualizar_proveedor(arbol):
    print("\n--- Actualizar Datos de Proveedor ---")
    id_proveedor = input("Ingrese el ID del proveedor a actualizar: ")
    print("\nDeje en blanco los campos que no desea cambiar")
    nombre = input("Nuevo nombre: ")
    servicio = input("Nuevo servicio: ")
    calificacion = input("Nueva calificación (1-5): ")
    ubicacion = input("Nueva ubicación: ")
    updates = {}
    if nombre: updates['nombre'] = nombre
    if servicio: updates['servicio'] = servicio
    if calificacion: updates['calificacion'] = calificacion
    if ubicacion: updates['ubicacion'] = ubicacion
    if arbol.actualizar_proveedor(id_proveedor, **updates):
        print("\n✅ Proveedor actualizado correctamente")
    else:
        print("\n❌ No se pudo actualizar el proveedor")

def comparar_busquedas(arbol):
    print("\n--- Comparación de Métodos de Búsqueda ---")
    servicio = input("Ingrese el servicio a comparar: ")
    resultado = arbol.comparar_busqueda(servicio)
    if 'error' in resultado:
        print(f"\n❌ Error: {resultado['error']}")
        return
    print(f"\n🔍 Resultados para '{servicio}':")
    print(f"Árbol B: {resultado['arbol']['cantidad']} proveedores en {resultado['arbol']['tiempo']:.6f} segundos")
    print(f"Búsqueda lineal: {resultado['lineal']['cantidad']} proveedores en {resultado['lineal']['tiempo']:.6f} segundos")
    print(f"\nEl árbol B fue {resultado['mejora']:.1f} veces más rápido")
    if resultado['arbol']['cantidad'] > 0:
        print("\nPrimeros resultados del árbol B:")
        for i, prov in enumerate(resultado['arbol']['resultados'][:5], 1):
            print(f"{i}. {prov}")

def mostrar_estadisticas(arbol):
    print("\n--- Estadísticas del Sistema ---")
    stats = arbol.estadisticas()
    print(f"Total de proveedores registrados: {stats['total_proveedores']}")
    print(f"Próximo ID disponible: {stats['proximo_id']}")
    print(f"Profundidad del árbol: {stats['profundidad']}")
    print("\n📊 Proveedores por servicio:")
    for servicio, cantidad in sorted(stats['servicios'].items()):
        print(f"- {servicio.capitalize()}: {cantidad}")
    if stats['ids_faltantes']:
        print(f"\n⚠ IDs faltantes del 1 al 20: {stats['ids_faltantes']}")
    else:
        print("\n✅ Todos los IDs del 1 al 20 están presentes")

def cargar_datos_prueba(arbol):
    """Carga datos de prueba en el sistema asegurando 20 proveedores con IDs 1-20"""
    servicios = ['electricista', 'plomero', 'albañil', 'programador', 'diseñador', 
                'carpintero', 'pintor', 'jardinero']
    nombres = ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Luis Rodríguez', 
              'Sofía Hernández', 'Pedro González', 'Laura Díaz', 'Miguel Sánchez', 'Elena Ramírez']
    ubicaciones = ['Ciudad A', 'Ciudad B', 'Ciudad C', 'Ciudad D', 'Ciudad E']
    
    for id_proveedor in range(1, 21):
        intentos = 0
        while intentos < 5:  # Aumentar intentos para mayor robustez
            nombre = random.choice(nombres)
            servicio = random.choice(servicios)
            calificacion = round(random.uniform(3, 5), 1)
            ubicacion = random.choice(ubicaciones)
            
            print(f"Intentando insertar proveedor ID {id_proveedor}: {nombre}, {servicio}")
            success = arbol.insertar(nombre, servicio, calificacion, ubicacion, id_proveedor)
            
            if success and arbol._existe_id(id_proveedor):
                print(f"✅ Proveedor {id_proveedor} registrado correctamente")
                break
            intentos += 1
            print(f"⚠ Error al cargar proveedor {id_proveedor}. Intento {intentos} de 5...")
        
        if intentos == 5:
            print(f"❌ No se pudo cargar proveedor {id_proveedor} después de 5 intents")
            nombre = f"Proveedor_{id_proveedor}"
            servicio = random.choice(servicios)
            calificacion = 4.0
            ubicacion = "Ciudad Default"
            success = arbol.insertar(nombre, servicio, calificacion, ubicacion, id_proveedor)
            if not success or not arbol._existe_id(id_proveedor):
                print(f"❌ Fallo crítico: No se pudo registrar proveedor {id_proveedor}")
            else:
                print(f"✅ Proveedor {id_proveedor} registrado con datos por defecto")
    
    arbol._contador_id = max(arbol._contador_id, 21)
    print("\n✅ Finalizó la carga de 20 proveedores de prueba con IDs del 1 al 20")
    
    faltantes = arbol.verificar_ids(20)
    if faltantes:
        print(f"❌ IDs faltantes: {faltantes}")
    else:
        print("✅ Todos los IDs del 1 al 20 están registrados")

def verificar_ids_proveedores(arbol):
    print("\n--- Verificación de IDs de Proveedores ---")
    max_id = input("Ingrese el ID máximo a verificar (deje vacío para 20): ")
    try:
        max_id = int(max_id) if max_id else 20
        faltantes = arbol.verificar_ids(max_id)
        if faltantes:
            print(f"\n❌ IDs faltantes del 1 al {max_id}: {faltantes}")
        else:
            print(f"\n✅ Todos los IDs del 1 al {max_id} están presentes")
    except ValueError:
        print("Error: Ingrese un número válido")

def main():
    try:
        os.system('cls')
        print("=== Configuración Inicial del Árbol B ===")
        while True:
            try:
                grado = int(input("Ingrese el grado mínimo del árbol B (recomendado 3): "))
                if grado >= 2:
                    break
                print("El grado mínimo debe ser al menos 2")
            except ValueError:
                print("Por favor ingrese un número válido")
        
        arbol = ArbolB(grado_minimo=grado)
        print("\n¡Bienvenido al sistema de gestión de proveedores!\n")
        
        while True:
            os.system('cls')
            mostrar_menu()
            opcion = input("\nSeleccione una opción: ").strip()
            
            try:
                if opcion == '1':
                    os.system('cls')
                    registrar_proveedor(arbol)
                elif opcion == '2':
                    os.system('cls')
                    buscar_proveedores(arbol)
                elif opcion == '3':
                    os.system('cls')
                    listar_proveedores(arbol)
                elif opcion == '4':
                    os.system('cls')
                    eliminar_proveedor(arbol)
                elif opcion == '5':
                    os.system('cls')
                    actualizar_proveedor(arbol)
                elif opcion == '6':
                    os.system('cls')
                    comparar_busquedas(arbol)
                elif opcion == '7':
                    os.system('cls')
                    mostrar_estadisticas(arbol)
                elif opcion == '8':
                    os.system('cls')
                    cargar_datos_prueba(arbol)
                elif opcion == '9':
                    os.system('cls')
                    verificar_ids_proveedores(arbol)
                elif opcion == '10':
                    os.system('cls')
                    print("\n¡Gracias por usar el sistema!")
                    break
                else:
                    os.system('cls')
                    print("\n❌ Opción no válida. Intente nuevamente.")
                
                input("\nPresione Enter para continuar...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Presione Enter para continuar...")
    except KeyboardInterrupt:
        print("\n\nPrograma terminado por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        print("Por favor, reinicie el programa.")


main()