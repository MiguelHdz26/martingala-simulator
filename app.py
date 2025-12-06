import streamlit as st
import random
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE PÁGINA (MOBILE FRIENDLY) ---
# Usamos layout="centered" porque se ve mejor en pantallas verticales de celular
st.set_page_config(page_title="Simulador Martingala", layout="centered")

st.title("🎲 Simulador Martingala")
st.markdown("Compara la **Teoría** vs. **Realidad** en tu celular.")

# --- FUNCIONES DE SIMULACIÓN (ACTUALIZADAS) ---

def simular_dados(capital_inicial, apuesta_base, max_intentos, limite_mesa):
    saldo = capital_inicial
    apuesta_actual = apuesta_base
    historial_saldo = [saldo]
    msg_estado = ""
    veces_limite = 0  # NUEVO CONTADOR

    for i in range(max_intentos):
        # 1. Aplicar límite de mesa
        if apuesta_actual > limite_mesa:
            apuesta_actual = limite_mesa
            veces_limite += 1  # CONTAMOS QUE TOCÓ EL TECHO

        # 2. Verificar fondos
        if saldo < apuesta_actual:
            msg_estado = f"Quiebra en intento {i+1}"
            historial_saldo.append(0)
            break

        # 3. Simulación (1-6). Gana Pares.
        dado = random.randint(1, 6)
        es_par = (dado % 2 == 0)

        if es_par:
            saldo += apuesta_actual
            apuesta_actual = apuesta_base
        else:
            saldo -= apuesta_actual
            apuesta_actual *= 2

        historial_saldo.append(saldo)

        if saldo <= 0:
            msg_estado = f"Quiebra total en intento {i+1}"
            break
            
    return historial_saldo, msg_estado, veces_limite

def simular_ruleta(capital_inicial, apuesta_base, max_giros, limite_mesa):
    saldo = capital_inicial
    apuesta_actual = apuesta_base
    historial_saldo = [saldo]
    veces_cero = 0
    veces_limite = 0 # NUEVO CONTADOR
    msg_estado = ""

    for i in range(max_giros):
        # 1. Verificar fondos antes de apostar
        if saldo < apuesta_actual:
            msg_estado = f"Quiebra en giro {i+1}"
            historial_saldo.append(0)
            break

        # 2. Aplicar límite de mesa
        if apuesta_actual > limite_mesa:
            apuesta_actual = limite_mesa
            veces_limite += 1 # CONTAMOS QUE TOCÓ EL TECHO

        # 3. Simulación Ruleta
        casilla = random.randint(1, 38)

        if casilla <= 18: # GANA
            saldo += apuesta_actual
            apuesta_actual = apuesta_base
        else: # PIERDE
            saldo -= apuesta_actual
            if casilla >= 37:
                veces_cero += 1
            apuesta_actual *= 2

        historial_saldo.append(saldo)

        if saldo <= 0:
            msg_estado = f"Quiebra total en giro {i+1}"
            break
            
    return historial_saldo, msg_estado, veces_cero, veces_limite

# --- INTERFAZ DE USUARIO (UX MÓVIL) ---

# Usamos un expander para que los controles no ocupen toda la pantalla del celular
with st.expander("⚙️ CONFIGURACIÓN DEL JUEGO (Toca para abrir)", expanded=True):
    
    # Usamos st.form para evitar recargas constantes en el celular
    with st.form("config_form"):
        tipo_juego = st.selectbox("Elegir Juego", ["Dados Justos (50%)", "Ruleta Americana (47.3%)"])
        
        c1, c2 = st.columns(2)
        with c1:
            cap_inicial = st.number_input("Capital Inicial ($)", value=1000, step=100)
            ap_base = st.number_input("Apuesta Base ($)", value=10, step=5)
        with c2:
            n_rondas = st.number_input("Rondas", value=200, step=50)
            # Checkbox para activar límite
            usa_limite = st.checkbox("Activar Límite de Mesa", value=True)
            
        # Logica visual del limite (si no se usa, es infinito)
        limite_mesa_input = st.number_input("Tope de Apuesta ($)", value=2000, step=100)
        
        # Botón grande para ejecutar
        submitted = st.form_submit_button("🚀 SIMULAR RESULTADO", use_container_width=True)

# Lógica del límite real
if usa_limite:
    limite_real = limite_mesa_input
else:
    limite_real = float('inf')

# --- EJECUCIÓN ---
if submitted:
    
    # Correr simulación
    if tipo_juego == "Dados Justos (50%)":
        historia, mensaje, n_limite = simular_dados(cap_inicial, ap_base, n_rondas, limite_real)
        color = 'blue'
        n_ceros = 0
    else:
        historia, mensaje, n_ceros, n_limite = simular_ruleta(cap_inicial, ap_base, n_rondas, limite_real)
        color = 'orange'

    saldo_final = historia[-1]
    ganancia = saldo_final - cap_inicial

    # --- RESULTADOS (Diseño limpio) ---
    st.divider()
    
    # Métricas principales
    m1, m2 = st.columns(2)
    m1.metric("Saldo Final", f"${saldo_final:,.0f}", delta=f"{ganancia:,.0f}")
    m2.metric("Rondas Jugadas", len(historia)-1)

    # Métricas secundarias (Límite y Ceros)
    if usa_limite or n_ceros > 0:
        st.caption("Detalles de la partida:")
        d1, d2 = st.columns(2)
        
        if usa_limite:
            d1.error(f"Topes de mesa: {n_limite} veces")
        else:
            d1.info("Sin límite de mesa")
            
        if n_ceros > 0:
            d2.warning(f"Salió el 0/00: {n_ceros} veces")

    # Mensaje de estado (Quiebra o Éxito)
    if mensaje:
        st.error(f"💀 {mensaje}")
    elif ganancia > 0:
        st.success(f"🎉 ¡Ganaste ${ganancia:,.0f}!")
    else:
        st.warning("Terminaste con el capital intacto (o con pérdidas leves).")

    # --- GRÁFICA ---
    st.subheader("Evolución del Dinero")
    fig, ax = plt.subplots(figsize=(6, 4)) # Tamaño más pequeño para celular
    
    ax.plot(historia, color=color, linewidth=2)
    ax.axhline(y=cap_inicial, color='green', linestyle='--', alpha=0.5, label='Inicio')
    ax.axhline(y=0, color='red', linestyle='-', label='Quiebra')
    
    ax.set_ylabel("Saldo ($)")
    ax.set_xlabel("Rondas")
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize='small')
    
    # Fondo transparente para que se vea mejor en streamlit
    fig.patch.set_alpha(0) 
    st.pyplot(fig)