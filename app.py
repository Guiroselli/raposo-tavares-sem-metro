"""
app.py - Protótipo CitizenTech: "Raposo Tavares sem metrô" (Cotia-SP)
Rodar:  streamlit run app.py
"""
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import streamlit.components.v1 as components

import modelo as m

rota = m.carregar_rota()

st.set_page_config(page_title="Raposo Tavares sem metrô - CitizenTech", layout="wide")
st.title("🚌 Raposo Tavares sem metrô (Cotia → São Paulo)")
st.caption("Protótipo CitizenTech - modelo de Greenshields + frota real de Cotia (Senatran, set/2026).")

with st.sidebar:
    st.header("Seu trajeto")
    saida = st.slider("Horário de saída (h)", 5.0, 10.0, 7.5, 0.25)
    hora_livre = st.slider("Horário de comparação sem trânsito (h)", 0.0, 24.0, 14.0, 0.5)
    s = st.slider("% de carros que migrariam para o transporte coletivo", 0, 50, 15) / 100
    ocup = st.number_input("Pessoas por carro", 1.0, 4.0, 1.5, help="Hipótese minha.")
    acesso = st.number_input("Tempo até a estação do metrô (min)", 0.0, 60.0, 10.0, help="Hipótese minha: caminhada/ônibus até a estação.")
    bloq = st.selectbox("Faixas ocupadas pela fila no retorno (Shopping Granja Viana)", [0, 1, 2], index=1)
    st.header("Parâmetros (avançado)")
    vf = st.number_input("Velocidade sem trânsito vf (km/h)", 40.0, 120.0, 80.0)
    kj = st.number_input("Densidade de parada kj (veíc/km/faixa)", 80.0, 200.0, 140.0)
    tpico_min = st.number_input("Tempo da viagem no pico (min) - observado", 20.0, 240.0, 60.0)
    faixas = st.number_input("Faixas no sentido capital", 1, 6, 3)
    k0 = st.number_input("Densidade fora do pico k0", 5.0, 80.0, 30.0)
    w_pico = st.slider("Meia-largura do pico w (h)", 0.5, 2.5, 1.5, help="O pico é uma parábola entre (centro - w) e (centro + w).")

L = rota["distancia_km"]
vpico = L * 60 / tpico_min
p = m.Params(vf=vf, kj=kj, v_pico=vpico, k0=k0, w=w_pico, L=L, faixas=int(faixas), s=s, bloqueadas=int(bloq), acesso_min=acesso, ocupacao=ocup)
kt = float(m.k_t(saida, p))
T = float(m.T_min(kt, p))
Tm = float(m.T_min(m.k_metro(kt, p), p))
T0 = 60 * L / vf

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tempo hoje", f"{T:.0f} min")
c2.metric("Sem trânsito", f"{T0:.0f} min")
c3.metric(f"Com {s*100:.0f}% dos carros a menos", f"{Tm:.0f} min", f"-{T - Tm:.0f} min", delta_color="normal")
kp = m.k_do_pico(p)
c4.metric("Carros no trecho (pico)", f"{m.carros_na_pista(kp, p):.0f}",
          f"{m.carros_na_pista(kp, p) / m.FROTA_LEVES_COTIA * 100:.1f}% da frota leve de Cotia", delta_color="off")

t = np.linspace(5, 10, 400)
tabm, tabg, tabmt, tab0, tab1, tab2, tab3, tab4, tabamb = st.tabs(["Mapa", "Gargalo", "Metrô", "Comparação", "Manhã", "Limites", "Derivadas", "Integrais", "Meio ambiente"])

GARG_KM, GARG_J = m.posicao_gargalo(rota)


def desenhar_mapa(hora, titulo, idx, modo="livre"):
    """modo: 'retorno' (pico atual), 'sem_retorno' (pico sem o retorno) ou 'livre' (horário sem trânsito)."""
    pts = rota["coords"]
    latlng = [[y, x] for x, y in pts]
    cal = m.calibrar_gargalo(p, GARG_KM)
    if modo == "retorno":
        tmin = cal["T_obs"]
        segs = [(latlng[:GARG_J + 1], m.cor_velocidade(cal["v_fila"])), (latlng[GARG_J:], m.cor_velocidade(cal["v_depois"]))]
        sub = f"{cal['v_fila']:.0f} km/h antes do retorno, {cal['v_depois']:.0f} km/h depois"
    elif modo == "sem_retorno":
        tmin = cal["T_sem_retorno"]
        segs = [(latlng, m.cor_velocidade(cal["v_depois"]))]
        sub = f"{cal['v_depois']:.0f} km/h; poupa {cal['ganho']:.0f} min"
    else:
        kk = float(m.k_t(hora, p)); vel = float(m.v(kk, p)); tmin = float(m.T_min(kk, p))
        segs = [(latlng, m.cor_velocidade(vel))]
        sub = f"{vel:.0f} km/h"
    polis = "".join(
        "L.polyline(%s, {color: 'rgb(%d,%d,%d)', weight: 8, opacity: 0.9}).addTo(map);" % (pl, *cor) for pl, cor in segs)
    html = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="map{idx}" style="height:380px;border-radius:8px"></div>
    <script>
      var map = L.map('map{idx}');
      L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 19, attribution: '&copy; OpenStreetMap'}}).addTo(map);
      var pts = {latlng};
      {polis}
      L.circleMarker(pts[0], {{radius: 9, color: '#1e5adc', fillOpacity: 1}}).bindTooltip('Cotia').addTo(map);
      L.circleMarker(pts[pts.length-1], {{radius: 9, color: '#7828a0', fillOpacity: 1}}).bindTooltip('Butantã').addTo(map);
      L.circleMarker([{m.GARGALO_LAT}, {m.GARGALO_LON}], {{radius: 10, color: '#000', fillColor: '#fff', fillOpacity: 1, weight: 3}}).bindTooltip('Retorno (gargalo)', {{permanent: false}}).addTo(map);
      map.fitBounds(L.polyline(pts).getBounds(), {{padding: [20, 20]}});
    </script>"""
    st.markdown(f"**{titulo}** — saída às {hora:.1f} h")
    components.html(html, height=395)
    st.metric("Tempo estimado", f"{tmin:.0f} min", sub, delta_color="off")

with tabm:
    st.caption("Rota de carro Cotia → Butantã (OpenStreetMap/OSRM). Cor = velocidade média estimada pelo modelo: "
               "verde ≥ 50 km/h, amarelo 35-50, laranja 20-35, vermelho < 20.")
    ca, cb, cc = st.columns(3)
    with ca:
        desenhar_mapa(p.t_pico, "Pico, como é hoje", 1, "retorno")
    with cb:
        desenhar_mapa(p.t_pico, "Pico, sem o problema do retorno", 3, "sem_retorno")
    with cc:
        desenhar_mapa(hora_livre, "Sem trânsito", 2, "livre")
    st.caption(f"Círculo branco = retorno depois do Shopping Granja Viana (km {GARG_KM:.1f} a partir de Cotia). "
               f"A Raposo fica engarrafada até o Butantã; o retorno só piora o trecho antes dele (a fila ocupa {bloq} faixa(s)). "
               f"A velocidade depois do retorno é calculada a partir do tempo de pico que eu informei.")

with tabg:
    st.subheader("O retorno que piora o engarrafamento")
    cal = m.calibrar_gargalo(p, GARG_KM)
    fs = np.linspace(0.3, p.faixas, 200)
    Ts = [m.T_gargalo_min(f, p, GARG_KM) for f in fs]
    fe = cal["f_ref"]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(fs, Ts, lw=2, color="C3")
    ax.scatter([fe], [cal["T_obs"]], color="crimson", zorder=3, s=60, label="situação atual")
    ax.scatter([p.faixas], [cal["T_sem_retorno"]], color="green", zorder=3, s=60, label="sem o problema do retorno")
    ax.set(xlabel="Faixas livres no retorno (f)", ylabel="Tempo do trajeto (min)", title="Tempo de viagem x faixas livres no retorno")
    ax.set_ylim(0, 150); ax.legend(); ax.grid(alpha=.3)
    st.pyplot(fig)
    c1, c2, c3 = st.columns(3)
    c1.metric("Hoje (pico)", f"{cal['T_obs']:.0f} min")
    c2.metric("Sem o problema do retorno", f"{cal['T_sem_retorno']:.0f} min")
    c3.metric("Piora causada pelo retorno", f"{cal['ganho']:.0f} min")
    st.write(f"**Derivada:** dT/df = **{m.dT_df_num(fe, p, GARG_KM):.1f} min por faixa** em f = {fe}: cada faixa liberada no retorno economiza esse tempo. "
             f"O efeito é não linear: ~{abs(m.dT_df_num(2.5, p, GARG_KM)):.0f} min/faixa perto de f = 2,5 e ~{abs(m.dT_df_num(1.0, p, GARG_KM)):.0f} em f = 1.")
    st.write(f"**Integral:** na manhã (5h-10h) o retorno faz perder cerca de **{m.horas_gargalo(5, 10, p):.0f} veículo-horas**.")
    st.caption("Hipótese: sem o retorno, o trecho antes dele andaria na mesma velocidade do resto da fila. "
               "Se a Raposo está praticamente parada até o Butantã, aumento o tempo de pico na lateral: a velocidade depois do retorno cai.")

with tabmt:
    st.subheader("Carro x metrô (Linha 22-Marrom, projeto)")
    d_m, t_m, espera, t_porta = m.tempo_metro(p)
    th = np.linspace(5, 10, 400)
    tc = m.T_min(m.k_t(th, p), p)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(th, tc, lw=2, color="C3", label="carro")
    ax.axhline(t_m, color="C2", lw=2, label=f"metrô (estação a estação): {t_m:.0f} min")
    ax.axhline(t_porta, color="C2", lw=2, ls="--", label=f"metrô (porta a porta): {t_porta:.0f} min")
    ax.set(xlabel="Horário de saída (h)", ylabel="Tempo de viagem (min)", title=f"Cotia → Butantã ({d_m:.0f} km de metrô)")
    ax.legend(); ax.grid(alpha=.3)
    st.pyplot(fig)
    a, b, c = st.columns(3)
    a.metric("Metrô (estação a estação)", f"{t_m:.0f} min", f"{d_m:.1f} km, {m.METRO['estacoes_ate_destino']} estações")
    b.metric("Metrô (porta a porta)", f"{t_porta:.0f} min", f"+{espera:.1f} min de espera, +{acesso:.0f} min de acesso", delta_color="off")
    c.metric("Carro no pico", f"{float(m.T_min(m.k_t(p.t_pico, p), p)):.0f} min")
    eq = m.horarios_equilibrio(t_porta, 5, 10, p)
    if eq:
        st.write(f"**Quando o metrô ganha do carro (porta a porta):** saindo entre **{eq[0]:.1f} h e {eq[1]:.1f} h** "
                 f"(equação do 2º grau em t). No pico, o metrô poupa {float(m.T_min(m.k_do_pico(p), p)) - t_porta:.0f} min.")
    else:
        st.write("Com esses parâmetros, o metrô porta a porta não ganha do carro em nenhum horário da manhã.")
    st.caption("Fonte do metrô: Diário do Transporte (13/10/2026) e EIA do Metrô-SP: 31,32 km, 19 estações, velocidade comercial ~40 km/h, "
               "trens a cada 100 s. A fonte não traz a distância entre estações; uso o espaçamento médio. Considero a estação Vital Brasil "
               "como a mais próxima do fim da Raposo. O metrô ainda é projeto: não há data de operação.")

with tab0:
    t_pk = float(p.t_pico)
    T_pk = float(m.T_min(m.k_t(t_pk, p), p))
    T_lv = float(m.T_min(m.k_t(hora_livre, p), p))
    st.subheader(f"Trajeto: Cotia → Butantã ({L:.1f} km)")
    a, b, c = st.columns(3)
    a.metric(f"Pico ({t_pk:.1f} h)", f"{T_pk:.0f} min", f"{m.v(m.k_t(t_pk, p), p):.0f} km/h", delta_color="off")
    b.metric(f"Sem trânsito ({hora_livre:.1f} h)", f"{T_lv:.0f} min", f"{m.v(m.k_t(hora_livre, p), p):.0f} km/h", delta_color="off")
    c.metric("Diferença", f"{T_pk - T_lv:.0f} min a mais no pico", f"+{(T_pk/T_lv - 1)*100:.0f}%", delta_color="inverse")
    th = np.linspace(0, 24, 600)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.plot(th, m.T_min(m.k_t(th, p), p), lw=2, color="C3")
    ax.scatter([t_pk], [T_pk], color="crimson", zorder=3, s=60, label=f"pico: {T_pk:.0f} min")
    ax.scatter([hora_livre], [T_lv], color="green", zorder=3, s=60, label=f"sem trânsito: {T_lv:.0f} min")
    ax.set(xlabel="Horário de saída (h)", ylabel="Tempo de viagem (min)", title=f"Tempo para percorrer {L:.0f} km ao longo do dia")
    ax.set_xlim(0, 24); ax.legend(); ax.grid(alpha=.3)
    st.pyplot(fig)
    st.caption("Fora do pico o modelo usa a densidade base k0 (hipótese). Em dias reais, acidentes e chuva alteram isso.")

    st.divider()
    st.subheader("E com o metrô funcionando? Quanto o trânsito da Raposo diminui")
    fr_ot = m.frac_otima(p)
    fracs = sorted({0.05, 0.10, 0.15, 0.20, fr_ot, 0.40})
    linhas = [m.efeito_migracao(f_, p) for f_ in fracs]
    import pandas as pd
    tabela = pd.DataFrame({
        "% dos carros que vão de metrô": [f"{e['frac']*100:.0f}%" + (" (ótimo)" if abs(e['frac'] - fr_ot) < 1e-3 else "") for e in linhas],
        "Tempo de carro no pico (min)": [f"{e['T']:.0f}" for e in linhas],
        "Velocidade (km/h)": [f"{e['v']:.0f}" for e in linhas],
        "Minutos poupados": [f"{e['poupa']:.0f}" for e in linhas],
        "Carros a menos por hora": [f"{e['carros_h']:.0f}" for e in linhas],
        "Passageiros por trem": [f"{e['pass_por_trem']:.0f}" for e in linhas],
    })
    st.dataframe(tabela, hide_index=True, use_container_width=True)
    xs_ = np.linspace(0, 0.5, 200)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(xs_ * 100, [m.efeito_migracao(x_, p)["T"] for x_ in xs_], lw=2, color="C3")
    ef_s = m.efeito_migracao(s, p)
    ax.scatter([s * 100], [ef_s["T"]], color="C2", zorder=3, s=60, label=f"seu cenário: {s*100:.0f}% -> {ef_s['T']:.0f} min")
    ax.scatter([fr_ot * 100], [m.efeito_migracao(fr_ot, p)["T"]], color="crimson", zorder=3, s=60, label=f"ótimo: {fr_ot*100:.0f}% -> {m.efeito_migracao(fr_ot, p)['T']:.0f} min")
    ax.set(xlabel="% dos carros do pico que migram para o metrô", ylabel="Tempo de carro no pico (min)", title="Quanto o metrô alivia a Raposo")
    ax.legend(); ax.grid(alpha=.3)
    st.pyplot(fig)
    st.write(f"**Resumo:** se **{s*100:.0f}%** dos carros do pico forem de metrô ({ef_s['carros_h']:.0f} carros/h, cerca de {ef_s['pass_h']:.0f} passageiros/h), "
             f"o carro que continua na Raposo leva **{ef_s['T']:.0f} min** em vez de {float(m.T_min(m.k_do_pico(p), p)):.0f} min: **{ef_s['poupa']:.0f} min a menos**. "
             f"Para a pista chegar ao fluxo máximo (v = {p.vf/2:.0f} km/h) bastaria tirar cerca de **{fr_ot*100:.0f}%** dos carros.")
    st.write(f"**Derivada:** dT/d(fração) = {m.dT_dfrac(0.001, p)/100:.1f} min por 1 ponto percentual no início e {m.dT_dfrac(0.2, p)/100:.1f} em 20%: "
             "os primeiros carros retirados são os que mais ajudam.")
    st.caption(f"O número de passageiros por trem considera {3600/m.METRO['headway_s']:.0f} trens/h (intervalo de 100 s) e {p.ocupacao:.1f} pessoas por carro (hipótese minha). "
               "O percentual de carros que de fato migraria depende de tarifa, acesso às estações e conforto; aqui mostro cenários, não uma previsão.")

with tab1:
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(t, m.T_min(m.k_t(t, p), p), lw=2, color="C3", label="hoje")
    ax.plot(t, m.T_min(m.k_metro(m.k_t(t, p), p), p), lw=2, color="C2", label=f"com {s*100:.0f}% dos carros a menos")
    ax.axvline(saida, ls="--", color="gray")
    ax.set(xlabel="Horário (h)", ylabel="Tempo de viagem (min)", title=f"Tempo para percorrer {L:.0f} km")
    ax.legend(); ax.grid(alpha=.3)
    st.pyplot(fig)

with tab2:
    kk = np.linspace(0, p.kj * 0.97, 300)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(kk, m.T_min(kk, p), lw=2); ax.set_ylim(0, 4 * T0 + 60)
    ax.axvline(p.kj, ls="--", color="gray")
    ax.set(xlabel="Densidade k (veíc/km/faixa)", ylabel="Tempo (min)", title="T(k) → ∞ quando k → kj")
    ax.grid(alpha=.3)
    st.pyplot(fig)
    st.write("**Limites (SymPy):**")
    for a, b in m.limites().items():
        st.write(f"- {a} = `{b}`")

with tab3:
    kc, qmax, vc = m.ponto_critico(p)
    k = np.linspace(0, p.kj, 300)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.plot(k, m.q(k, p), lw=2); ax.scatter([kc], [qmax], color="crimson", zorder=3)
    ax.scatter([kp], [float(m.q(kp, p))], color="orange", zorder=3)
    ax.set(xlabel="Densidade k (veíc/km/faixa)", ylabel="Fluxo q (veíc/h/faixa)", title="q(k): máximo (vermelho) e pico atual (laranja)")
    ax.grid(alpha=.3)
    st.pyplot(fig)
    st.latex(r"q'(k)=v_f\left(1-\frac{2k}{k_j}\right),\quad k^*=\frac{k_j}{2}")
    st.write(f"Máximo: **{qmax:.0f} veíc/h/faixa** em k = {kc:.0f}. No pico a densidade é {kp:.0f}: "
             f"q'(k) = {p.vf*(1-2*kp/p.kj):.1f} (região decrescente).")
    st.write(f"T'(k) no pico = **{float(m.dT_dk_min(kp, p)):.2f} min por (veíc/km/faixa)**.")

with tab4:
    N = m.veiculos_atendidos(5, 10, p)
    D = m.atraso_total(5, 10, p)
    H = m.horas_economizadas_metro(5, 10, p)
    st.latex(r"\int_0^{k_j} q(k)\,dk=\frac{v_f k_j^2}{6}")
    st.write(f"Área sob q(k): **{p.vf*p.kj**2/6:.0f}**")
    st.write(f"Veículos atendidos (5h-10h): **{N:.0f}**")
    st.write(f"Atraso acumulado: **{D:.0f} veículo-horas**")
    st.write(f"Atraso evitado com {s*100:.0f}% dos carros no metrô: **{H:.0f} veículo-horas**")
    st.latex(r"D=n\,\frac{L}{k_j}\int k(t)^2\,dt,\qquad H=[1-(1-s)^2]\,D")
    fig, ax = plt.subplots(figsize=(8, 3.2))
    y = p.faixas * m.q(m.k_t(t, p), p)
    ax.plot(t, y); ax.fill_between(t, y, alpha=.25)
    ax.set(xlabel="Horário (h)", ylabel="Fluxo (veíc/h)", title="Área = veículos atendidos")
    ax.grid(alpha=.3)
    st.pyplot(fig)

with tabamb:
    st.subheader("Meio ambiente: combustível e CO₂ do congestionamento")
    st.write("Parado no trânsito, o carro continua queimando combustível. Como o tempo por km é 1/v(k), o consumo por km sobe com a densidade.")
    st.latex(r"\text{consumo}(k)=a+\frac{c}{v(k)}\ \ [\text{L/km}],\qquad \lim_{k\to k_j^-}\text{consumo}(k)=+\infty,\qquad \text{consumo}'(k)=\frac{c\,k_j}{v_f\,(k_j-k)^2}>0")
    with st.expander("Parâmetros de combustível e CO₂ (hipóteses minhas, editáveis)"):
        cA, cB, cC = st.columns(3)
        c_par = cA.number_input("Consumo parado c (L/h)", 0.3, 3.0, 1.0, help="Argonne: 0,2 a 0,5 galão/h = 0,8 a 1,9 L/h.")
        a_km = cB.number_input("Consumo livre a (L/km)", 0.04, 0.20, 0.07, help="Hipótese minha (~14 km/L).")
        f_fos = cC.slider("Fração fóssil da gasolina", 0.5, 1.0, 0.70, help="Hipótese minha: o resto é etanol.")
    pa = m.Params(vf=vf, kj=kj, v_pico=vpico, k0=k0, w=w_pico, L=L, faixas=int(faixas), s=s, bloqueadas=int(bloq),
                  acesso_min=acesso, ocupacao=ocup, c_parado=c_par, a_km=a_km, frac_fossil=f_fos)
    kpa = m.k_do_pico(pa)
    La = m.litros_excedentes(m.atraso_total(5, 10, pa), pa)
    Ea = m.co2_excedente_dia(5, 10, pa)
    Eev = m.co2_evitado_metro_dia(5, 10, pa)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CO₂ por carro, sem trânsito", f"{m.co2_viagem(0, pa):.1f} kg")
    m2.metric("CO₂ por carro, no pico", f"{m.co2_viagem(kpa, pa):.1f} kg", f"+{(m.co2_viagem(kpa, pa)/m.co2_viagem(0, pa)-1)*100:.0f}%", delta_color="inverse")
    m3.metric("Combustível extra por manhã", f"{La:,.0f} L".replace(",", "."))
    m4.metric("CO₂ extra por manhã", f"{Ea/1000:.1f} t", f"{Ea*pa.dias_uteis/1000:,.0f} t/ano".replace(",", "."), delta_color="off")
    kk_ = np.linspace(0, pa.kj * 0.97, 300)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.plot(kk_, [m.co2_viagem(x_, pa) for x_ in kk_], lw=2, color="C1")
    ax.scatter([kpa], [m.co2_viagem(kpa, pa)], color="crimson", zorder=3)
    ax.set(xlabel="Densidade k (veíc/km/faixa)", ylabel="CO₂ por carro (kg/viagem)", title="CO₂ de um carro no trecho x densidade (ponto = pico)")
    ax.grid(alpha=.3)
    st.pyplot(fig)
    st.write(f"Integral do CO₂ extra na manhã (5h-10h): **{Ea/1000:.1f} t**. Com {s*100:.0f}% dos carros no transporte coletivo, "
             f"quem segue de carro emite **{Eev/1000:.1f} t a menos por manhã** (~{Eev*pa.dias_uteis/1000:,.0f} t/ano; estimativa conservadora).".replace(",", "."))
    st.write(f"Um motorista que faz o trajeto toda manhã perde cerca de **{m.horas_no_transito_ano(pa):.0f} horas por ano** a mais no trânsito (só a ida).")
    st.info("Saúde e estresse: o relatório trata esses efeitos de forma qualitativa (OMS: 4,2 milhões de mortes prematuras por ano ligadas à poluição do ar externo, dado de 2016). "
            "Não converti horas ou poluentes em casos de doença por falta de fonte.")

st.caption("Velocidade de pico, nº de faixas, k0 e w são observações e hipóteses minhas (ver README).")
