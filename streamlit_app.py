import streamlit as st

st.title("Hidrología")
st.write(
    "Let's go)."
)
import math

# =====================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y TÍTULO DE LA APP
# =====================================================================
st.set_page_config(page_title="Evaporación por Tanque Clase A", layout="centered")
st.title("Estimación de la Evaporación a partir de Tanques de Evaporación")

# Texto introductorio e histórico solicitado
st.markdown("""
La información del tanque de evaporación provee la mejor indicación de evaporación en superficie de aguas abiertas.

En el Perú se utiliza principalmente el denominado **Tanque clase 'A' del US Weather Bureau**, el cual está montado sobre un enrejado de madera de forma que su base se encuentra a 5 o 10 cm por encima del suelo, permitiendo la circulación libre del aire por debajo. Está construido de fierro galvanizado y es llenado hasta 5.1 cm bajo su borde. Las mediciones se realizan apoyando en un tubo un tornillo micrométrico cuya punta se enrasa con el nivel del agua.

En esta aplicación se calcula la evaporación mediante la ecuación de **Kohler y Parmelei (1967)**, la cual tiene en consideración que para un cuerpo de agua se debe involucrar el almacenamiento de calor y la energía por advección del agua que entra y sale de dicho cuerpo de agua. Esta ecuación toma en cuenta la presión de vapor a saturación del cuerpo de agua y del tanque evaporímetro.
""")

st.markdown("---")

# =====================================================================
# 2. MOSTRAR LA ECUACIÓN MATEMÁTICA PRINCIPAL
# =====================================================================
st.subheader("Formula Base (Kohler & Parmelei / Webb, 1966)")
st.latex(r"E = K' \cdot \frac{e_{sL} - e_Z}{e_{sp} - e_Z} \cdot E_{Tanque}")

# Desplegable informativo con el significado de los símbolos
with st.expander("📖 Ver significado de los símbolos"):
    st.markdown("""
    * **$E$**: Evaporación estimada del cuerpo de agua ($mm/día$).
    * **$K'$**: Coeficiente en función al tipo de tanque de evaporación.
    * **$e_{sL}$**: Presión de vapor a saturación para la máxima temperatura sobre el espejo de agua ($kPa$).
    * **$e_{sp}$**: Presión de vapor a saturación para la máxima temperatura en el tanque de evaporación ($kPa$).
    * **$e_Z$**: Presión de vapor media del aire a una altura $Z$ sobre el espejo de agua ($kPa$).
    * **$E_{Tanque}$**: Evaporación medida en el tanque clase A ($mm$).
    """)

st.markdown("---")

# Variable de control para validar las entradas de datos
inputs_validos = True

# =====================================================================
# 3. SELECCIÓN DEL COEFICIENTE K'
# =====================================================================
st.subheader("⚙️ Configuración del Coeficiente $K'$")
tipo_k = st.selectbox(
    "Seleccione el criterio para el coeficiente K':",
    ["Recomendado (K' = 1.5) para Tanque Clase A a altura z = 4 m", "Otros (Ingresar manualmente)"]
)

if tipo_k == "Recomendado (K' = 1.5) para Tanque Clase A a altura z = 4 m":
    K_coef = 1.5
else:
    # Espacio para insertar el valor personalizado si elige 'Otros'
    K_coef = st.number_input("Inserte el valor personalizado de $K'$:", value=1.0, step=0.1, format="%.2f")
    if K_coef <= 0:
        st.error("❌ El coeficiente K' debe ser un número mayor a cero.")
        inputs_validos = False

st.markdown("---")

# =====================================================================
# 4. CAPTURA Y VALIDACIÓN DE INPUTS (Estructura Símbolo - Input - Unidad)
# =====================================================================
st.subheader("📥 Parámetros de Entrada")

# --- Función auxiliar para generar filas ordenadas (Símbolo | Input | Unidad) ---
def crear_fila_input(simbolo, descripcion, min_val, max_val, val_defecto, unidad, step_val=1.0):
    global inputs_validos
    col_sim, col_inp, col_uni = st.columns([1.5, 5, 1.5])
    
    with col_sim:
        st.markdown(f"**{simbolo}**")
    with col_inp:
        valor = st.number_input(f"___ ({descripcion})", value=val_defecto, step=step_val)
        # Validación de rangos y valores lógicos
        if valor <= min_val or valor > max_val:
            st.error(f"❌ Valor inválido. Debe estar entre {min_val} y {max_val} {unidad}.")
            inputs_validos = False
    with col_uni:
        st.markdown(f"*{unidad}*")
    return valor

# Renderizado de cada campo solicitado
E_tanque = crear_fila_input("$E_{Tanque}$", "Evaporación registrada en el tanque", 0.0, 50.0, 5.0, "mm", 0.1)
T_max_l = crear_fila_input("$T_{max,L}$", "Máxima temperatura registrada sobre el espejo de agua", -10.0, 60.0, 22.0, "°C", 0.5)
T_max_p = crear_fila_input("$T_{max,sp}$", "Máxima temperatura en el tanque de evaporación", -10.0, 60.0, 24.0, "°C", 0.5)
T_medio_aire = crear_fila_input("$T_{aire}$", "Temperatura media del aire a la altura Z", -10.0, 50.0, 18.0, "°C", 0.5)
HR = crear_fila_input("$HR$", "Humedad relativa media del aire", 0.0, 100.0, 70.0, "%", 1.0)
W_viento = crear_fila_input("$u_Z$", "Velocidad del viento a la altura del tanque (z = 4.0 m)", -0.01, 150.0, 12.0, "km/h", 1.0)

st.markdown("---")

# =====================================================================
# 5. PROCESAMIENTO MATEMÁTICO (Ecuación de Magnus-Tetens y Kohler)
# =====================================================================
if inputs_validos:
    st.subheader("📊 Valores Intermedios Calculados (Presiones de Vapor)")
    
    # Ecuación psicrométrica para calcular es a partir de la temperatura en °C
    def calcular_es(t):
        return 0.6108 * math.exp((17.27 * t) / (t + 237.3))

    # Cálculo individual de presiones de saturación
    esL = calcular_es(T_max_l) # Presión en el espejo de agua
    esp = calcular_es(T_max_p) # Presión en el tanque
    
    # Presión de vapor real del aire (ez) afectada por la Humedad Relativa
    es_aire = calcular_es(T_medio_aire)
    ez = es_aire * (HR / 100.0)

    # Mostrar las variables tabuladas intermedias con sus unidades en kPa
    col_e1, col_e2, col_e3 = st.columns(3)
    col_e1.metric(label="$e_{sL}$ (Espejo de agua)", value=f"{esL:.3f} kPa")
    col_e2.metric(label="$e_{sp}$ (Tanque)", value=f"{esp:.3f} kPa")
    col_e3.metric(label="$e_Z$ (Presión real aire)", value=f"{ez:.3f} kPa")

    # --- CONTROL DE INDETERMINACIÓN MATEMÁTICA ---
    # Evitar la división por cero si esp es igual a ez
    if abs(esp - ez) < 1e-4:
        st.error("❌ Error de cálculo: La presión en el tanque ($e_{sp}$) y la presión del aire ($e_Z$) son idénticas, causando una división por cero.")
    else:
        # Aplicación de la fórmula final de Kohler y Parmelei
        E_final = K_coef * ((esL - ez) / (esp - ez)) * E_tanque

        # =====================================================================
        # 6. PRESENTACIÓN DE RESULTADOS FINALES
        # =====================================================================
        st.markdown("---")
        st.subheader("🏁 Resultado del Análisis")
        
        # Muestra la métrica destacada
        st.metric(label="Evaporación del Cuerpo de Agua ($E$)", value=f"{E_final:.2f} mm")
        
        # Texto de conclusión dinámico solicitado
        st.success(f"**Conclusión:** El valor calculado de la evaporación a partir de la información registrada en el tanque evaporímetro es de **{E_final:.2f}** mm.")
else:
    st.info("Por favor, corrija los valores marcados en rojo arriba para poder proceder con el modelo de estimación.")
