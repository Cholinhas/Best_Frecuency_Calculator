import tkinter as tk
from tkinter import ttk, messagebox
import folium
from geopy.distance import geodesic
import math
import os
import webbrowser

class RadioCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Propagación para Radioaficionados")
        self.root.geometry("1300x800")
        self.root.configure(bg='#2b2b2b')
        
        # Bandas de radioaficionado
        self.bandas = {
            "160m (1.8 MHz)": 1.8,
            "80m (3.5 MHz)": 3.5,
            "40m (7.0 MHz)": 7.0,
            "30m (10.1 MHz)": 10.1,
            "20m (14.0 MHz)": 14.0,
            "17m (18.1 MHz)": 18.1,
            "15m (21.0 MHz)": 21.0,
            "12m (24.9 MHz)": 24.9,
            "10m (28.0 MHz)": 28.0,
            "6m (50.0 MHz)": 50.0,
            "4m (70.0 MHz)": 70.0,
            "2m (144.0 MHz)": 144.0,
            "70cm (432.0 MHz)": 432.0
        }
        
        # Variables
        self.emisor_coords = None
        self.receptor_coords = None
        self.mapa_html = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Entrada de datos
        left_panel = tk.Frame(main_frame, bg='#3c3f41', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Título
        title = tk.Label(left_panel, text="📻 Calculadora de Propagación", 
                        font=('Arial', 16, 'bold'), bg='#3c3f41', fg='white')
        title.pack(pady=10)
        
        # Frame para scroll en inputs
        canvas = tk.Canvas(left_panel, bg='#3c3f41', highlightthickness=0)
        scrollbar = tk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#3c3f41')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Entrada de datos
        input_frame = scrollable_frame
        
        # Potencia de emisión
        tk.Label(input_frame, text="Potencia de Emisión (Watts):", 
                font=('Arial', 10), bg='#3c3f41', fg='white').pack(pady=(10,0))
        self.potencia_entry = tk.Entry(input_frame, font=('Arial', 12), width=30)
        self.potencia_entry.pack(pady=5)
        self.potencia_entry.insert(0, "100")
        
        # Tipo de antena
        tk.Label(input_frame, text="Tipo de Antena:", 
                font=('Arial', 10), bg='#3c3f41', fg='white').pack(pady=(10,0))
        self.antena_var = tk.StringVar(value="dipolo")
        antena_frame = tk.Frame(input_frame, bg='#3c3f41')
        antena_frame.pack(pady=5)
        tk.Radiobutton(antena_frame, text="Dipolo", variable=self.antena_var, 
                      value="dipolo", bg='#3c3f41', fg='white', selectcolor='#3c3f41').pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(antena_frame, text="Directiva", variable=self.antena_var, 
                      value="directiva", bg='#3c3f41', fg='white', selectcolor='#3c3f41').pack(side=tk.LEFT, padx=10)
        
        # Coordenadas Emisor
        tk.Label(input_frame, text="📍 Coordenadas del Emisor:", 
                font=('Arial', 11, 'bold'), bg='#3c3f41', fg='#ffd700').pack(pady=(15,5))
        
        tk.Label(input_frame, text="Latitud:", bg='#3c3f41', fg='white').pack()
        self.emisor_lat = tk.Entry(input_frame, font=('Arial', 10), width=30)
        self.emisor_lat.pack(pady=2)
        self.emisor_lat.insert(0, "40.4168")  # Madrid
        
        tk.Label(input_frame, text="Longitud:", bg='#3c3f41', fg='white').pack()
        self.emisor_lon = tk.Entry(input_frame, font=('Arial', 10), width=30)
        self.emisor_lon.pack(pady=2)
        self.emisor_lon.insert(0, "-3.7038")  # Madrid
        
        # Coordenadas Receptor
        tk.Label(input_frame, text="📍 Coordenadas del Receptor:", 
                font=('Arial', 11, 'bold'), bg='#3c3f41', fg='#ffd700').pack(pady=(15,5))
        
        tk.Label(input_frame, text="Latitud:", bg='#3c3f41', fg='white').pack()
        self.receptor_lat = tk.Entry(input_frame, font=('Arial', 10), width=30)
        self.receptor_lat.pack(pady=2)
        self.receptor_lat.insert(0, "41.3851")  # Barcelona
        
        tk.Label(input_frame, text="Longitud:", bg='#3c3f41', fg='white').pack()
        self.receptor_lon = tk.Entry(input_frame, font=('Arial', 10), width=30)
        self.receptor_lon.pack(pady=2)
        self.receptor_lon.insert(0, "2.1734")  # Barcelona
        
        # Selección de banda
        tk.Label(input_frame, text="📡 Seleccionar Banda (Opcional):", 
                font=('Arial', 11, 'bold'), bg='#3c3f41', fg='#ffd700').pack(pady=(15,5))
        
        self.banda_var = tk.StringVar(value="")
        banda_combo = ttk.Combobox(input_frame, textvariable=self.banda_var, 
                                   values=[""] + list(self.bandas.keys()), width=27)
        banda_combo.pack(pady=5)
        
        # Botón de cálculo
        calcular_btn = tk.Button(input_frame, text="🔍 Calcular Mejor Frecuencia", 
                                command=self.calcular_mejor_frecuencia,
                                font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white',
                                activebackground='#45a049', cursor='hand2')
        calcular_btn.pack(pady=20)
        
        # Panel derecho - Resultados y mapa
        right_panel = tk.Frame(main_frame, bg='#2b2b2b')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Frame de resultados
        results_frame = tk.Frame(right_panel, bg='#3c3f41', relief=tk.RAISED, bd=2)
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.results_text = tk.Text(results_frame, height=10, width=50, 
                                   font=('Courier', 10), bg='#2b2b2b', fg='#00ff00')
        self.results_text.pack(padx=10, pady=10, fill=tk.BOTH)
        
        # Frame del mapa
        map_frame = tk.Frame(right_panel, bg='#2b2b2b')
        map_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(map_frame, text="🗺️ Visualización Geográfica", 
                font=('Arial', 12, 'bold'), bg='#2b2b2b', fg='white').pack(pady=5)
        
        self.map_label = tk.Label(map_frame, bg='#2b2b2b', 
                                 text="Haga clic en 'Calcular' para generar el mapa",
                                 font=('Arial', 10), fg='#cccccc')
        self.map_label.pack(expand=True, fill=tk.BOTH)
        
        # Botón para abrir mapa en navegador
        self.open_map_btn = tk.Button(right_panel, text="🌍 Abrir Mapa en Navegador", 
                                     command=self.abrir_mapa_navegador,
                                     font=('Arial', 10), bg='#2196F3', fg='white',
                                     activebackground='#1976D2', cursor='hand2',
                                     state='disabled')
        self.open_map_btn.pack(pady=5)
        
    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula la distancia entre dos puntos en kilómetros"""
        coords_1 = (lat1, lon1)
        coords_2 = (lat2, lon2)
        return geodesic(coords_1, coords_2).kilometers
    
    def calcular_perdida_espacio_libre(self, distancia_km, frecuencia_mhz):
        """Calcula la pérdida en espacio libre (FSL)"""
        if distancia_km < 0.01:
            distancia_km = 0.01
        fsl = 20 * math.log10(distancia_km) + 20 * math.log10(frecuencia_mhz) + 32.44
        return fsl
    
    def calcular_ganancia_antena(self, tipo_antena, frecuencia_mhz):
        """Calcula la ganancia aproximada de la antena en dBi"""
        if tipo_antena == "dipolo":
            return 2.15
        else:
            ganancia = 5 + math.log10(frecuencia_mhz / 10)
            return min(ganancia, 20)
    
    def calcular_potencia_recibida(self, potencia_tx_w, ganancia_tx_db, ganancia_rx_db, fsl_db):
        """Calcula la potencia recibida en dBm"""
        try:
            potencia_tx_dbm = 10 * math.log10(potencia_tx_w * 1000)
            potencia_rx_dbm = potencia_tx_dbm + ganancia_tx_db + ganancia_rx_db - fsl_db
            return potencia_rx_dbm
        except:
            return -200
    
    def evaluar_calidad_comunicacion(self, potencia_rx_dbm):
        """Evalúa la calidad de la comunicación basada en la potencia recibida"""
        if potencia_rx_dbm > -50:
            return "Excelente", "#00ff00"
        elif potencia_rx_dbm > -70:
            return "Buena", "#ffff00"
        elif potencia_rx_dbm > -90:
            return "Aceptable", "#ffa500"
        elif potencia_rx_dbm > -110:
            return "Marginal", "#ff6600"
        else:
            return "Mala", "#ff0000"
    
    def encontrar_mejor_frecuencia(self, distancia_km, potencia_w, tipo_antena, banda_especifica=None):
        """Encuentra la mejor frecuencia para la comunicación"""
        resultados = []
        
        for nombre_banda, frecuencia in self.bandas.items():
            try:
                fsl = self.calcular_perdida_espacio_libre(distancia_km, frecuencia)
                ganancia_tx = self.calcular_ganancia_antena(tipo_antena, frecuencia)
                ganancia_rx = self.calcular_ganancia_antena(tipo_antena, frecuencia)
                potencia_rx_dbm = self.calcular_potencia_recibida(potencia_w, ganancia_tx, ganancia_rx, fsl)
                calidad, color = self.evaluar_calidad_comunicacion(potencia_rx_dbm)
                merito = potencia_rx_dbm
                
                resultados.append({
                    'banda': nombre_banda,
                    'frecuencia': frecuencia,
                    'fsl': fsl,
                    'potencia_rx_dbm': potencia_rx_dbm,
                    'calidad': calidad,
                    'merito': merito,
                    'color': color
                })
            except:
                continue
        
        if banda_especifica and banda_especifica != "":
            resultados = [r for r in resultados if r['banda'] == banda_especifica]
            if resultados:
                mejor = max(resultados, key=lambda x: x['merito'])
                return mejor, resultados
            else:
                return None, []
        else:
            if resultados:
                mejor = max(resultados, key=lambda x: x['merito'])
                return mejor, resultados
            else:
                return None, []
    
    def crear_mapa(self, lat1, lon1, lat2, lon2, distancia, mejor_frecuencia):
        """Crea un mapa con Folium"""
        try:
            center_lat = (lat1 + lat2) / 2
            center_lon = (lon1 + lon2) / 2
            
            mapa = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles='OpenStreetMap')
            
            # Marcador Emisor
            folium.Marker(
                [lat1, lon1],
                popup=f'📡 EMISOR<br>Potencia: {self.potencia_entry.get()}W<br>Antena: {self.antena_var.get()}',
                icon=folium.Icon(color='red', icon='bullhorn', prefix='fa')
            ).add_to(mapa)
            
            # Marcador Receptor
            folium.Marker(
                [lat2, lon2],
                popup=f'📻 RECEPTOR<br>Distancia: {distancia:.2f} km<br>Mejor banda: {mejor_frecuencia["banda"]}',
                icon=folium.Icon(color='green', icon='signal', prefix='fa')
            ).add_to(mapa)
            
            # Línea de comunicación
            folium.PolyLine(
                locations=[[lat1, lon1], [lat2, lon2]],
                color='blue',
                weight=3,
                opacity=0.8,
                popup=f'📡 Comunicación<br>Distancia: {distancia:.2f} km'
            ).add_to(mapa)
            
            # Círculo de cobertura aproximada
            folium.Circle(
                radius=distancia * 1000,
                location=[lat1, lon1],
                color='red',
                fill=False,
                weight=2,
                opacity=0.3,
                popup='Área de cobertura'
            ).add_to(mapa)
            
            # Guardar mapa
            mapa_html = "mapa_radio.html"
            mapa.save(mapa_html)
            
            return mapa_html
        except Exception as e:
            print(f"Error creando mapa: {e}")
            return None
    
    def abrir_mapa_navegador(self):
        """Abre el mapa en el navegador web"""
        if os.path.exists("mapa_radio.html"):
            webbrowser.open("mapa_radio.html")
        else:
            messagebox.showwarning("Advertencia", "Primero debe calcular la comunicación para generar el mapa")
    
    def calcular_mejor_frecuencia(self):
        """Función principal de cálculo"""
        try:
            # Obtener datos
            potencia = float(self.potencia_entry.get())
            tipo_antena = self.antena_var.get()
            
            lat1 = float(self.emisor_lat.get())
            lon1 = float(self.emisor_lon.get())
            lat2 = float(self.receptor_lat.get())
            lon2 = float(self.receptor_lon.get())
            
            banda_seleccionada = self.banda_var.get()
            
            # Validar coordenadas
            if not (-90 <= lat1 <= 90) or not (-180 <= lon1 <= 180):
                messagebox.showerror("Error", "Coordenadas del emisor inválidas")
                return
            
            if not (-90 <= lat2 <= 90) or not (-180 <= lon2 <= 180):
                messagebox.showerror("Error", "Coordenadas del receptor inválidas")
                return
            
            # Calcular distancia
            distancia = self.calcular_distancia(lat1, lon1, lat2, lon2)
            
            # Encontrar mejor frecuencia
            mejor, todos_resultados = self.encontrar_mejor_frecuencia(
                distancia, potencia, tipo_antena, banda_seleccionada
            )
            
            # Mostrar resultados
            self.results_text.delete(1.0, tk.END)
            
            if mejor:
                self.results_text.insert(tk.END, "="*55 + "\n")
                self.results_text.insert(tk.END, "     📡 RESULTADOS DEL CÁLCULO 📡\n")
                self.results_text.insert(tk.END, "="*55 + "\n\n")
                
                self.results_text.insert(tk.END, f"📍 Distancia entre equipos: {distancia:.2f} km\n")
                self.results_text.insert(tk.END, f"⚡ Potencia de emisión: {potencia} W\n")
                self.results_text.insert(tk.END, f"📡 Tipo de antena: {tipo_antena.upper()}\n\n")
                
                self.results_text.insert(tk.END, "🏆 MEJOR FRECUENCIA RECOMENDADA:\n")
                self.results_text.insert(tk.END, "-"*40 + "\n")
                self.results_text.insert(tk.END, f"📻 Banda: {mejor['banda']}\n")
                self.results_text.insert(tk.END, f"📊 Frecuencia: {mejor['frecuencia']:.1f} MHz\n")
                self.results_text.insert(tk.END, f"📉 Pérdida espacio libre: {mejor['fsl']:.1f} dB\n")
                self.results_text.insert(tk.END, f"📶 Potencia recibida: {mejor['potencia_rx_dbm']:.1f} dBm\n")
                self.results_text.insert(tk.END, f"⭐ Calidad: {mejor['calidad']}\n\n")
                
                # Mostrar top 5 mejores bandas
                self.results_text.insert(tk.END, "📊 TOP 5 MEJORES BANDAS:\n")
                self.results_text.insert(tk.END, "-"*40 + "\n")
                
                sorted_resultados = sorted(todos_resultados, key=lambda x: x['merito'], reverse=True)
                for i, res in enumerate(sorted_resultados[:5], 1):
                    self.results_text.insert(tk.END, 
                        f"{i}. {res['banda']:15s} → {res['potencia_rx_dbm']:6.1f} dBm "
                        f"[{res['calidad']}]\n"
                    )
                
                # Recomendaciones
                self.results_text.insert(tk.END, "\n💡 RECOMENDACIONES:\n")
                self.results_text.insert(tk.END, "-"*40 + "\n")
                
                if mejor['potencia_rx_dbm'] < -90:
                    self.results_text.insert(tk.END, "⚠️  Señal débil. Considere:\n")
                    self.results_text.insert(tk.END, "   • Aumentar potencia de emisión\n")
                    self.results_text.insert(tk.END, "   • Usar antena directiva\n")
                    self.results_text.insert(tk.END, "   • Elevar altura de antenas\n")
                elif mejor['potencia_rx_dbm'] > -50:
                    self.results_text.insert(tk.END, "✅ Señal excelente. Comunicación asegurada\n")
                else:
                    self.results_text.insert(tk.END, "✅ Señal adecuada para comunicación\n")
                
                # Crear mapa
                self.results_text.insert(tk.END, "\n🗺️ Generando mapa...\n")
                self.root.update()
                
                mapa_html = self.crear_mapa(lat1, lon1, lat2, lon2, distancia, mejor)
                
                if mapa_html and os.path.exists(mapa_html):
                    self.map_label.config(text="✅ Mapa generado correctamente\nHaga clic en 'Abrir Mapa en Navegador'", 
                                         fg='#00ff00')
                    self.open_map_btn.config(state='normal')
                    self.results_text.insert(tk.END, "✅ Mapa generado correctamente\n")
                    
                    # Preguntar si quiere abrir el mapa
                    if messagebox.askyesno("Mapa generado", "¿Desea abrir el mapa en el navegador ahora?"):
                        self.abrir_mapa_navegador()
                else:
                    self.map_label.config(text="❌ Error al generar el mapa", fg='#ff0000')
                    self.results_text.insert(tk.END, "❌ Error al generar el mapa\n")
                
            else:
                self.results_text.insert(tk.END, "❌ No se encontraron resultados para la banda seleccionada\n")
                messagebox.showwarning("Sin resultados", "No se encontraron bandas disponibles")
                
        except ValueError as e:
            messagebox.showerror("Error de entrada", f"Por favor, verifique los datos ingresados:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Ha ocurrido un error:\n{str(e)}")

def main():
    root = tk.Tk()
    app = RadioCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()