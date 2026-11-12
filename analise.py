"""
analise.py - Gera os gráficos, imprime os cálculos e monta o RELATÓRIO TÉCNICO EM PDF.

Projeto: Raposo Tavares sem metrô (Cotia-SP)
Como rodar:   python analise.py
Saídas:       pasta graficos/ (PNG)  e  Relatorio_Tecnico_CitizenTech.pdf

Autor: Guilherme Damásio Roselli (RM 571922) - NOMES/MATRICULAS logo abaixo.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import modelo as m

# ------------------------- PREENCHER -------------------------
NOMES = ["Guilherme Damásio Roselli"]
MATRICULAS = ["RM 571922"]
# -------------------------------------------------------------

p = m.P0
PASTA = os.path.dirname(os.path.abspath(__file__))
GRAF = os.path.join(PASTA, "graficos")
os.makedirs(GRAF, exist_ok=True)

# ---------------------------------------------------------------- cálculos
kp = m.k_do_pico(p)
kc, qmax, vc = m.ponto_critico(p)
dq_pico = p.vf * (1 - 2 * kp / p.kj)
dT_pico = float(m.dT_dk_min(kp, p))
T0 = 60 * p.L / p.vf
Tpico = float(m.T_min(kp, p))
t1, t2 = 5.0, 10.0
N = m.veiculos_atendidos(t1, t2, p)
D = m.atraso_total(t1, t2, p)
area_q = p.vf * p.kj ** 2 / 6
carros_pico = m.carros_na_pista(kp, p)
pct_frota = carros_pico / m.FROTA_LEVES_COTIA * 100
ks = kp * (1 - p.s)
T_metro = float(m.T_min(ks, p))
H = m.horas_economizadas_metro(t1, t2, p)
dk_100 = 100 / (p.L * p.faixas)
min_100 = dT_pico * dk_100

Lu, jg = m.posicao_gargalo()
cal = m.calibrar_gargalo(p, Lu)
fe = cal["f_ref"]
v_fila, v_depois = cal["v_fila"], cal["v_depois"]
T_garg = cal["T_obs"]; T_sem_garg = cal["T_sem_retorno"]; ganho = cal["ganho"]
T_garg1 = m.T_gargalo_min(p.faixas - 2, p, Lu)
dTdf = m.dT_df_num(fe, p, Lu)
Hb = m.horas_gargalo(t1, t2, p)
d_m, t_m, esp_m, t_porta = m.tempo_metro(p)
eq_m = m.horarios_equilibrio(t_porta, t1, t2, p)
T14 = float(m.T_min(m.k_t(14.0, p), p))
cons_pico = float(m.consumo_km(kp, p)); cons_livre = float(m.consumo_km(0, p))
co2v_pico = float(m.co2_viagem(kp, p)); co2v_livre = float(m.co2_viagem(0, p))
L_exc = m.litros_excedentes(D, p)
co2_exc = m.co2_excedente_dia(t1, t2, p); co2_exc_ano = co2_exc * p.dias_uteis / 1000      # t/ano
co2_ev = m.co2_evitado_metro_dia(t1, t2, p); co2_ev_ano = co2_ev * p.dias_uteis / 1000
h_ano = m.horas_no_transito_ano(p)
dco2_pico = float(m.dco2_dk(kp, p))
print("=== RESULTADOS ===")
print(f"AMBIENTE: consumo pico={cons_pico:.3f} L/km livre={cons_livre:.3f}; CO2/viagem pico={co2v_pico:.2f} kg livre={co2v_livre:.2f}; "
      f"litros extra/dia={L_exc:.0f}; CO2 extra={co2_exc:.0f} kg/dia={co2_exc_ano:.0f} t/ano; evitado metro={co2_ev:.0f} kg/dia={co2_ev_ano:.0f} t/ano; h/ano={h_ano:.0f}")
for a, b in m.limites().items():
    print(f"limite {a} = {b}")
print(f"k_pico={kp:.1f}  ponto critico k={kc:.0f} q_max={qmax:.0f}/faixa v={vc:.0f}")
print(f"q'(k_pico)={dq_pico:.1f}  T'(k_pico)={dT_pico:.3f} min/(veic/km)")
print(f"T0={T0:.1f} min  T_pico={Tpico:.1f} min  T_metro={T_metro:.1f} min")
print(f"N={N:.0f}  D={D:.0f} veic.h  H={H:.0f} veic.h  area={area_q:.0f}")
print(f"GARGALO km={Lu:.1f} fila={v_fila:.1f} depois={v_depois:.1f} T={T_garg:.1f} sem={T_sem_garg:.1f} 2bloq={T_garg1:.1f} dT/df={dTdf:.1f} Hb={Hb:.0f}")
print(f"carros no trecho no pico={carros_pico:.0f} ({pct_frota:.1f}% da frota leve)")

# ---------------------------------------------------------------- gráficos
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .3})
k = np.linspace(0, p.kj, 400)
kk = np.linspace(0, p.kj * 0.97, 400)

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(k, m.v(k, p), lw=2)
ax.scatter([0, p.kj, kp], [p.vf, 0, p.v_pico], color="crimson", zorder=3)
ax.annotate(f"k->0: v = {p.vf:.0f} km/h", (0, p.vf), (10, p.vf - 10))
ax.annotate("k->kj: v = 0", (p.kj, 0), (100, 8))
ax.annotate(f"pico: {p.v_pico:.0f} km/h", (kp, p.v_pico), (95, 30))
ax.set(title="Velocidade em função da densidade (Greenshields)",
       xlabel="Densidade k (veículos/km/faixa)", ylabel="Velocidade v (km/h)")
fig.tight_layout(); fig.savefig(f"{GRAF}/g1_velocidade.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(k, m.q(k, p), lw=2, color="C0")
ax.fill_between(k, m.q(k, p), alpha=.15, color="C0", label="Área sob a curva = %.0f" % area_q)
ax.axvline(kc, ls="--", color="gray")
ax.scatter([kc], [qmax], color="crimson", zorder=3)
ax.scatter([kp], [float(m.q(kp, p))], color="orange", zorder=3, label="pico atual")
ax.annotate(f"máximo: k={kc:.0f}, q={qmax:.0f} veíc/h", (kc, qmax), (5, qmax * 0.55))
ax.text(10, 300, "q' > 0\n(cresce)"); ax.text(115, 300, "q' < 0\n(decresce)")
ax.set(title="Fluxo de veículos em função da densidade",
       xlabel="Densidade k (veículos/km/faixa)", ylabel="Fluxo q (veículos/hora/faixa)")
ax.legend(loc="upper right")
fig.tight_layout(); fig.savefig(f"{GRAF}/g2_fluxo.png", dpi=170); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(kk, m.T_min(kk, p), lw=2, color="C3")
ax.axvline(p.kj, ls="--", color="gray"); ax.text(p.kj - 28, 150, "assíntota k = kj")
ax.set_ylim(0, 200)
ax.set(title=f"Tempo de viagem de {p.L:.0f} km (limite infinito em k->kj)",
       xlabel="Densidade k (veículos/km/faixa)", ylabel="Tempo de viagem (min)")
fig.tight_layout(); fig.savefig(f"{GRAF}/g3_tempo.png", dpi=170); plt.close(fig)

t = np.linspace(t1, t2, 500)
kt = m.k_t(t, p)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 5.2), sharex=True)
a1.plot(t, p.faixas * m.q(kt, p), lw=2, color="C0")
a1.fill_between(t, p.faixas * m.q(kt, p), alpha=.2)
a1.set(title=f"Fluxo na rodovia - área = veículos atendidos ≈ {N:.0f}", ylabel="Fluxo (veíc/h, 3 faixas)")
a2.plot(t, m.T_min(kt, p), lw=2, color="C3", label="hoje")
a2.plot(t, m.T_min(m.k_metro(kt, p), p), lw=2, color="C2", label=f"com {p.s*100:.0f}% dos carros a menos")
a2.axhline(T0, ls=":", color="gray"); a2.text(t1 + .1, T0 + 1.5, f"sem trânsito ({T0:.0f} min)", color="gray")
a2.fill_between(t, m.T_min(m.k_metro(kt, p), p), m.T_min(kt, p), alpha=.15, color="C2")
a2.set(title=f"Tempo para percorrer {p.L:.0f} km", xlabel="Horário (h)", ylabel="Tempo (min)")
a2.legend(loc="upper left", fontsize=8)
fig.tight_layout(); fig.savefig(f"{GRAF}/g4_dia.png", dpi=170); plt.close(fig)

# G5 comparação pico x fora do pico ao longo do dia
th = np.linspace(0, 24, 600)
T_livre = float(m.T_min(m.k_t(14.0, p), p))
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(th, m.T_min(m.k_t(th, p), p), lw=2, color="C3")
ax.scatter([p.t_pico], [Tpico], color="crimson", zorder=3, s=50, label=f"pico {p.t_pico:.1f}h: {Tpico:.0f} min")
ax.scatter([14.0], [T_livre], color="green", zorder=3, s=50, label=f"14h (sem trânsito): {T_livre:.0f} min")
ax.set(title=f"Tempo para percorrer {p.L:.0f} km ao longo do dia", xlabel="Horário de saída (h)", ylabel="Tempo (min)")
ax.set_xlim(0, 24); ax.legend()
fig.tight_layout(); fig.savefig(f"{GRAF}/g5_comparacao.png", dpi=170); plt.close(fig)

# G6 trajeto com e sem trânsito (cores estilo Waze) + gargalo
rota = m.carregar_rota()
xs = [c[0] for c in rota["coords"]]; ys = [c[1] for c in rota["coords"]]
fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.0), sharex=True, sharey=True)
kk14 = float(m.k_t(14.0, p)); v14 = float(m.v(kk14, p)); t14 = float(m.T_min(kk14, p))
rgb = lambda v_: tuple(c / 255 for c in m.cor_velocidade(v_))
ax = axs[0]
ax.plot(xs[:jg + 1], ys[:jg + 1], color=rgb(v_fila), lw=5, solid_capstyle="round")
ax.plot(xs[jg:], ys[jg:], color=rgb(v_depois), lw=5, solid_capstyle="round")
ax.set_title(f"Pico hoje: {T_garg:.0f} min", fontsize=8)
ax.annotate(f"{v_fila:.0f} km/h", (xs[jg // 2], ys[jg // 2]), textcoords="offset points", xytext=(-5, 10), fontsize=7)
ax.annotate(f"{v_depois:.0f} km/h", (xs[(jg + len(xs)) // 2], ys[(jg + len(xs)) // 2]), textcoords="offset points", xytext=(-5, -14), fontsize=7)
axs[1].plot(xs, ys, color=rgb(v_depois), lw=5, solid_capstyle="round")
axs[1].set_title(f"Pico sem o retorno: {T_sem_garg:.0f} min", fontsize=8)
axs[2].plot(xs, ys, color=rgb(v14), lw=5, solid_capstyle="round")
axs[2].set_title(f"Sem trânsito (14h): {t14:.0f} min", fontsize=8)
for a_ in axs:
    a_.scatter([xs[0]], [ys[0]], color="#1e5adc", s=50, zorder=3); a_.scatter([xs[-1]], [ys[-1]], color="#7828a0", s=50, zorder=3)
    a_.scatter([m.GARGALO_LON], [m.GARGALO_LAT], facecolor="white", edgecolor="black", s=60, linewidth=2, zorder=4)
    a_.annotate("Cotia", (xs[0], ys[0]), textcoords="offset points", xytext=(-8, 8), fontsize=7)
    a_.annotate("Butantã", (xs[-1], ys[-1]), textcoords="offset points", xytext=(-14, -14), fontsize=7)
    a_.set_xlabel("Longitude (graus)", fontsize=8); a_.set_aspect("equal"); a_.tick_params(labelsize=6)
axs[0].set_ylabel("Latitude (graus)", fontsize=8)
fig.suptitle("Rota Cotia - Butantã (círculo branco = retorno; verde livre, amarelo/laranja lento, vermelho parado)", fontsize=8)
fig.tight_layout(); fig.savefig(f"{GRAF}/g6_rota.png", dpi=170); plt.close(fig)

# G7 tempo x faixas liberadas no retorno
fs = np.linspace(0.3, p.faixas, 200)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot(fs, [m.T_gargalo_min(f_, p, Lu) for f_ in fs], lw=2, color="C3")
ax.scatter([fe], [T_garg], color="crimson", zorder=3, s=50, label=f"hoje ({fe} faixas livres): {T_garg:.0f} min")
ax.scatter([p.faixas], [T_sem_garg], color="green", zorder=3, s=50, label=f"sem o problema do retorno: {T_sem_garg:.0f} min")
ax.set_ylim(0, 150)
ax.set(title="Tempo do trajeto x faixas que o retorno deixa passar", xlabel="Faixas livres no retorno (f)", ylabel="Tempo (min)")
ax.legend()
fig.tight_layout(); fig.savefig(f"{GRAF}/g7_gargalo.png", dpi=170); plt.close(fig)

# G8 carro x metrô
th = np.linspace(5, 10, 400)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot(th, m.T_min(m.k_t(th, p), p), lw=2, color="C3", label="carro")
ax.axhline(t_m, color="C2", lw=2, label=f"metrô, estação a estação: {t_m:.0f} min")
ax.axhline(t_porta, color="C2", lw=2, ls="--", label=f"metrô, porta a porta: {t_porta:.0f} min")
if eq_m:
    ax.fill_between(th, m.T_min(m.k_t(th, p), p), t_porta, where=(th >= eq_m[0]) & (th <= eq_m[1]), alpha=.2, color="C2")
ax.set(title="Cotia - Butantã: carro x metrô (Linha 22-Marrom, projeto)", xlabel="Horário de saída (h)", ylabel="Tempo (min)")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{GRAF}/g8_metro.png", dpi=170); plt.close(fig)

# G9 efeito da migração de carros para o metrô
fr_ot = m.frac_otima(p)
xs_ = np.linspace(0, 0.5, 200)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot(xs_ * 100, [m.efeito_migracao(x_, p)["T"] for x_ in xs_], lw=2, color="C3")
e15 = m.efeito_migracao(p.s, p); eot = m.efeito_migracao(fr_ot, p)
ax.scatter([p.s * 100], [e15["T"]], color="C2", zorder=3, s=50, label=f"{p.s*100:.0f}% -> {e15['T']:.0f} min")
ax.scatter([fr_ot * 100], [eot["T"]], color="crimson", zorder=3, s=50, label=f"ótimo {fr_ot*100:.0f}% -> {eot['T']:.0f} min")
ax.set(title="Quanto o metrô alivia a Raposo (tempo de carro no pico)", xlabel="% dos carros do pico que migram para o metrô", ylabel="Tempo de carro (min)")
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"{GRAF}/g9_migracao.png", dpi=170); plt.close(fig)

# G10 meio ambiente: CO2 por viagem x densidade, e CO2 extra ao longo da manhã (hoje x com metrô)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.4))
a1.plot(kk, [m.co2_viagem(x_, p) for x_ in kk], lw=2, color="C1")
a1.scatter([0, kp], [co2v_livre, co2v_pico], color="crimson", zorder=3)
a1.annotate(f"livre: {co2v_livre:.1f} kg", (0, co2v_livre), (8, co2v_livre + 1.5), fontsize=8)
a1.annotate(f"pico: {co2v_pico:.1f} kg", (kp, co2v_pico), (45, co2v_pico + 2.5), fontsize=8, arrowprops=dict(arrowstyle="->"))
a1.set(title=f"CO2 por carro no trecho de {p.L:.0f} km", xlabel="Densidade k (veíc/km/faixa)", ylabel="CO2 (kg por viagem)")
ts_ = np.linspace(t1, t2, 300)
def _co2_h(tt, kfun):
    kk_ = kfun(tt)
    return float(m.q(kk_, p)) * p.faixas * (p.L / float(m.v(kk_, p)) - p.L / p.vf) * p.c_parado * p.co2_litro * p.frac_fossil
a2.plot(ts_, [_co2_h(x_, lambda z: float(m.k_t(z, p))) for x_ in ts_], lw=2, color="C3", label="hoje")
a2.plot(ts_, [_co2_h(x_, lambda z: float(m.k_metro(m.k_t(z, p), p))) for x_ in ts_], lw=2, color="C2", label=f"com {p.s*100:.0f}% dos carros a menos")
a2.fill_between(ts_, [_co2_h(x_, lambda z: float(m.k_metro(m.k_t(z, p), p))) for x_ in ts_], [_co2_h(x_, lambda z: float(m.k_t(z, p))) for x_ in ts_], alpha=.15, color="C2")
a2.set(title=f"CO2 extra por hora: área hoje = {co2_exc/1000:.1f} t", xlabel="Horário (h)", ylabel="CO2 extra (kg/h)")
a2.legend(fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(f"{GRAF}/g10_ambiente.png", dpi=170); plt.close(fig)

# ---------------------------------------------------------------- relatório PDF
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=14, spaceBefore=10, textColor=colors.HexColor("#1f3b6f"))
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14.5, alignment=4)
EQ = ParagraphStyle("EQ", parent=B, alignment=1, fontName="Helvetica-Oblique", spaceBefore=3, spaceAfter=3)
CAP = ParagraphStyle("CAP", parent=B, fontSize=8.5, alignment=1, textColor=colors.grey)
doc = SimpleDocTemplate(os.path.join(PASTA, "Relatorio_Tecnico_CitizenTech.pdf"), pagesize=A4,
                        leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Relatório Técnico CitizenTech", author=", ".join(NOMES))
S = []
def par(x): S.append(Paragraph(x, B))
def eq(x): S.append(Paragraph(x, EQ))
def h1(x): S.append(Paragraph(x, H1))
def img(f, cap, w=13.5):
    S.append(Image(f"{GRAF}/{f}", width=w * cm, height=w * cm * (0.5625 if "g4" not in f else 0.8125)))
    S.append(Paragraph(cap, CAP))
def tab(rows, widths):
    tb = Table([[Paragraph(str(c), ParagraphStyle("c", parent=B, fontSize=8.5, leading=10.5, alignment=0)) for c in r] for r in rows],
               colWidths=[w * cm for w in widths])
    tb.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dfe7f5")),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    S.append(tb); S.append(Spacer(1, 6))

S.append(Paragraph("Global Solution - 2º Semestre 2026 | Cálculo | Desafio CitizenTech", CAP))
S.append(Paragraph("Raposo Tavares sem metrô: modelagem matemática do congestionamento Cotia-São Paulo",
                   ParagraphStyle("T", parent=ss["Title"], fontSize=19, leading=23)))
S.append(Paragraph("Relatório técnico", ParagraphStyle("st", parent=B, alignment=1, fontSize=12)))
tab([["Integrante", "Matrícula"]] + [[n, mt] for n, mt in zip(NOMES, MATRICULAS)], [10, 5])

h1("Resumo executivo")
par(f"Cotia não tem metrô e depende da rodovia Raposo Tavares para chegar à capital. Modelei o trecho Cotia-Butantã "
    f"({p.L:.0f} km) com o modelo clássico de Greenshields e a frota real de Cotia (Senatran, set/2026). "
    f"No pico da manhã o trecho leva <b>{Tpico:.0f} min</b>, contra <b>{T0:.0f} min</b> sem trânsito. A capacidade máxima é de "
    f"<b>{qmax:.0f} veíc/h por faixa</b> a {kc:.0f} veíc/km; o pico atual ({kp:.0f} veíc/km) está além desse ponto, "
    f"onde mais carros significam <i>menos</i> fluxo. Em um cenário em que {p.s*100:.0f}% dos carros migrassem para um "
    f"metrô, o tempo cairia para <b>{T_metro:.0f} min</b> (-{Tpico-T_metro:.0f} min) e o atraso total da via na manhã (5h-10h) cairia "
    f"<b>{H:.0f} veículo-horas</b>. Além do tempo, o congestionamento queima combustível: calculei cerca de <b>{co2_exc/1000:.0f} t de CO2 por manhã</b> só por causa dele. O protótipo (app Streamlit) permite testar o cenário.")

h1("1. Problema e variáveis")
par("<b>Problema real.</b> Cotia cresceu 26% em dez anos e não tem metrô; as promessas (monotrilho Linha 17 em 2016, Linha 22 "
    "em 2020) não saíram do papel e o governo declarou em 2021 que não havia estudo (Agência Mural, 2021). Hoje existe o projeto da "
    "Linha 22-Marrom, com Estudo de Impacto Ambiental e audiências previstas para dezembro de 2026, mas ainda sem obra nem data de operação (Diário do Transporte, 2026). "
    "Boletins de trânsito registram de 20 a mais de 30 km de lentidão na Raposo Tavares (Girosa). Pergunto: "
    "<i>quanto tempo isso custa e quanto um metrô poderia devolver?</i>")
tab([["Variável", "Significado", "Unidade", "Origem"],
     ["k", "densidade (veículos por km de faixa)", "veíc/km/faixa", "variável independente"],
     ["v(k)", "velocidade média", "km/h", "modelo"],
     ["q(k)", "fluxo = k · v", "veíc/h/faixa", "modelo"],
     ["T(k)", f"tempo de viagem de L = {p.L:.0f} km", "min", "modelo"],
     [f"vf = {p.vf:.0f}", "velocidade sem trânsito", "km/h", "limite de projeto da rodovia (a conferir)"],
     [f"kj = {p.kj:.0f}", "densidade de parada total", "veíc/km/faixa", "faixa típica da literatura (120-160)"],
     [f"v_pico = {p.v_pico:.0f}", f"velocidade média no pico (~{Tpico:.0f} min p/ {p.L:.0f} km)", "km/h", "<b>observação minha (morador de Cotia)</b>"],
     [f"{p.faixas} faixas", "faixas no sentido capital", "-", "hipótese minha"],
     [f"k0 = {p.k0:.0f}, w = {p.w:.1f} h", "densidade fora do pico e meia-largura do pico (parábola)", "-", "hipótese do cenário"],
     [f"{m.FROTA_LEVES_COTIA:,}".replace(",", "."), "frota de leves de Cotia (automóvel, caminhonete, camioneta, utilitário)", "veículos", "Senatran, set/2026"]],
    [2.9, 6.1, 2.4, 4.4])

h1("2. Modelo matemático e limites (Questão 1)")
par("<b>Função.</b> Greenshields (1935) propôs que a velocidade cai linearmente com a densidade de veículos:")
eq("v(k) = vf · (1 - k/kj)      q(k) = k · v(k) = vf · k · (1 - k/kj)      T(k) = L / v(k)")
par(f"<b>Calibração.</b> Impondo v = {p.v_pico:.0f} km/h no pico: k_pico = kj·(1 - {p.v_pico:.0f}/{p.vf:.0f}) = "
    f"<b>{kp:.1f} veíc/km/faixa</b>. Com {p.faixas} faixas e {p.L:.0f} km, isso equivale a {carros_pico:.0f} veículos "
    f"simultâneos no trecho, ou <b>{pct_frota:.1f}%</b> da frota de leves registrada em Cotia: valor plausível. "
    f"Obs.: a frota total registrada em Cotia (390.638, incluindo reboques e outros tipos) é bem maior que a de leves, e "
    f"parte dela pode ser de empresas; por isso uso apenas os leves como referência.")
par("<b>Limites calculados (SymPy):</b>")
tab([["Limite", "Resultado", "Interpretação"],
     ["lim v(k), k->0+", f"vf = {p.vf:.0f} km/h", "rodovia vazia: velocidade máxima"],
     ["lim v(k), k->kj-", "0", "com densidade máxima, o trânsito para"],
     ["lim q(k), k->kj-", "0", "engarrafamento total: ninguém passa"],
     ["lim T(k), k->kj-", "+infinito", "o tempo de viagem cresce sem limite"],
     ["lim T(k), k->0+", f"L/vf = {T0:.1f} min", "tempo mínimo possível no trecho"]],
    [4, 3.4, 8.4])
par("<b>Significado.</b> O limite infinito de T(k) mostra que o problema é <i>não linear</i>: perto da saturação, "
    "poucos carros a mais causam um aumento desproporcional no tempo de viagem. É por isso que uma alternativa "
    "como o metrô, que tira só uma parte dos carros, tem efeito grande.")
img("g1_velocidade.png", "Figura 1 - Velocidade x densidade e limites.")
img("g3_tempo.png", "Figura 2 - Tempo de viagem com assíntota em k = kj.")

h1("3. Derivadas (Questão 2)")
par("<b>Procedimento.</b> Derivando q(k) = vf·k - (vf/kj)·k²:")
eq("q'(k) = vf · (1 - 2k/kj)          q''(k) = -2·vf/kj < 0")
par(f"<b>Pontos críticos.</b> q'(k) = 0 implica k* = kj/2 = {kc:.0f} veíc/km. Como q'' é negativa, é um <b>máximo</b>: "
    f"q_max = vf·kj/4 = <b>{qmax:.0f} veíc/h por faixa</b>, a {vc:.0f} km/h.")
tab([["Intervalo", "Sinal de q'", "Comportamento de q"],
     [f"0 < k < {kc:.0f}", "positivo", "crescente: mais carros, mais veículos passam"],
     [f"k = {kc:.0f}", "zero", "máximo (capacidade da faixa)"],
     [f"{kc:.0f} < k < {p.kj:.0f}", "negativo", "decrescente: mais carros, <b>menos</b> veículos passam"]],
    [4, 3.4, 8.4])
par(f"<b>Taxa de variação.</b> No pico (k = {kp:.1f}), q'(k) = <b>{dq_pico:.1f}</b> veíc/h por (veíc/km): a via está "
    f"na região decrescente. Para o tempo de viagem:")
eq("T'(k) = L·kj / [ vf · (kj - k)² ]  > 0 sempre")
par(f"No pico, T'(k) = <b>{dT_pico:.2f} min</b> por (veíc/km/faixa). Em termos práticos, retirar 100 carros do trecho "
    f"reduz k em {dk_100:.2f} e economiza cerca de <b>{min_100:.1f} min</b> (estimativa linear pela derivada; para "
    f"mudanças grandes uso a função completa, pois T' cresce com k).")
img("g2_fluxo.png", "Figura 3 - Fluxo x densidade, máximo e área sob a curva.")

h1("4. Integrais (Questão 3)")
par("<b>(a) Integral indefinida e definida.</b>")
eq("Integral de q(k) dk = vf·k²/2 - vf·k³/(3·kj) + C            Integral de 0 a kj de q(k) dk = vf·kj²/6")
par(f"<b>(b) Área sob a curva.</b> Com vf = {p.vf:.0f} e kj = {p.kj:.0f}: área = <b>{area_q:.0f}</b> "
    f"(veíc/h)·(veíc/km), um índice do fluxo acumulado em todos os estados de densidade. Obras que aumentem vf ou kj "
    f"(faixa exclusiva de ônibus, por exemplo) aumentam essa área.")
par(f"<b>(c) Grandezas acumuladas no tempo.</b> Para somar ao longo da manhã preciso de k em função do horário. Uso um pico em forma de parábola, "
    f"k(t) = k0 + (k_pico - k0)·(1 - ((t - {p.t_pico:.1f})/{p.w:.1f})²) entre {p.t_pico-p.w:.1f}h e {p.t_pico+p.w:.1f}h, e k = k0 fora dele (hipótese de cenário). "
    f"Assim q(k(t)) é um <b>polinômio em t</b> e as integrais saem pela <b>regra da potência</b> (primitiva e teorema fundamental, F(b) - F(a)), "
    f"somando as partes do intervalo 5h-10h (propriedade da integral definida). Para as {p.faixas} faixas:")
eq("N = faixas · Integral de q(k(t)) dt, com q(k) = vf·k - (vf/kj)·k²  =  " + f"{N:.0f} veículos")
par("Para o atraso uso uma simplificação algébrica: q(k)·[L/v(k) - L/vf] = vf·kj·x·(1 - x) · (L/vf)·x/(1 - x) = L·k²/kj, com x = k/kj. "
    "Então o integrando é um polinômio de grau 2 em k:")
eq("D = faixas · (L/kj) · Integral de k(t)² dt  (primitiva de k² = k³/3)  =  " + f"{D:.0f} veículo-horas de atraso")
eq("H = D - D(k_s) = [1 - (1 - s)²] · D  =  " + f"{H:.0f} veículo-horas evitadas, com k_s = (1 - s)·k")
par(f"Interpretação: entre 5h e 10h passam {N:.0f} veículos, que perdem juntos {D:.0f} horas em relação ao trecho "
    f"livre (média de {D/N*60:.1f} min por veículo). Com {p.s*100:.0f}% dos carros migrando para o transporte coletivo, o atraso total da via cai {H:.0f} horas "
    f"na manhã. Conferi os três valores com uma integração numérica independente (SciPy), que coincide com as primitivas.")
par(f"<b>(d) Horário.</b> Fora do pico o tempo é T(k0) = {float(m.T_min(p.k0, p)):.1f} min (o mínimo do cenário); no centro do pico, {p.t_pico:.1f}h, "
    f"é máximo: {Tpico:.1f} min, onde k(t) = k_pico.")
img("g4_dia.png", "Figura 4 - Fluxo (área = veículos atendidos) e tempo de carro hoje e com 15% dos carros a menos.", w=12.5)

h1("5. Comparação: horário de pico x horário sem trânsito")
horas = [(6.0, "6h"), (p.t_pico, f"{p.t_pico:.1f}h (pico)"), (10.0, "10h"), (14.0, "14h"), (22.0, "22h")]
linhas = [["Horário de saída", "Velocidade média", f"Tempo para {p.L:.0f} km", "Diferença vs. 14h"]]
for hh, nome in horas:
    kk_ = float(m.k_t(hh, p)); tt = float(m.T_min(kk_, p))
    linhas.append([nome, f"{float(m.v(kk_, p)):.0f} km/h", f"{tt:.0f} min", "-" if hh == 14.0 else f"+{tt - T_livre:.0f} min (+{(tt / T_livre - 1) * 100:.0f}%)"])
tab(linhas, [4, 3.5, 4, 4.3])
par(f"Saindo no pico ({p.t_pico:.1f}h) o trajeto de {p.L:.0f} km leva <b>{Tpico:.0f} min</b>; saindo em um horário sem "
    f"trânsito (14h) leva <b>{T_livre:.0f} min</b>. São <b>{Tpico - T_livre:.0f} min a mais</b> "
    f"(+{(Tpico / T_livre - 1) * 100:.0f}%) para percorrer a mesma distância. Fora do pico o modelo usa a densidade base "
    f"k0 = {p.k0:.0f} veíc/km/faixa (hipótese do cenário).")
img("g5_comparacao.png", "Figura 5 - Tempo de viagem ao longo do dia: pico x horário sem trânsito.")
S.append(Image(f"{GRAF}/g6_rota.png", width=15.5 * cm, height=15.5 * cm * 3.0 / 7.4))
S.append(Paragraph("Figura 6 - Trajeto Cotia-Butantã (25 km, quase todo pela Rodovia Raposo Tavares até onde ela termina no Butantã; rota OpenStreetMap/OSRM) com e sem trânsito, com o retorno marcado. No app, o mesmo trajeto aparece sobre o mapa real.", CAP))

h1("6. O retorno que piora o engarrafamento (depois do Shopping Granja Viana)")
par(f"Como morador de Cotia, observo que a Raposo Tavares fica praticamente parada até o Butantã e que um retorno logo "
    f"depois do Shopping Granja Viana (coordenadas do Google Maps: {m.GARGALO_LAT:.5f}, {m.GARGALO_LON:.5f}; sentido "
    f"Cotia-capital; km {Lu:.1f} a partir de Cotia) <b>só piora</b> esse quadro: a fila de quem espera para retornar ocupa de 1 a 2 das "
    f"{p.faixas} faixas. <b>São observações minhas, não medições oficiais.</b>")
par("<b>Modelo.</b> Se o retorno deixa passar apenas f faixas, o fluxo por faixa antes dele fica limitado a (f/faixas)·q_max, e a "
    "fila anda na velocidade do estado engarrafado da curva de Greenshields. Com s = raiz(1 - f/faixas):")
eq("v_fila = (vf/2)·(1 - s)        T(f) = Lu / v_fila(f) + T_depois")
par(f"<b>Calibração.</b> O trecho <i>depois</i> do retorno também está engarrafado; sua velocidade é o que sobra do tempo observado "
    f"no pico ({T_garg:.0f} min): antes do retorno, com {fe} faixas livres, a fila anda a <b>{v_fila:.0f} km/h</b> e leva "
    f"{cal['T_antes']:.0f} min; depois do retorno restam {cal['T_depois']:.0f} min, ou seja, <b>{v_depois:.0f} km/h</b>. Sem o "
    f"problema do retorno, o trecho antes dele andaria como o resto da fila ({v_depois:.0f} km/h) e a viagem levaria "
    f"<b>{T_sem_garg:.0f} min</b>: o retorno custa cerca de <b>{ganho:.0f} min</b> por viagem.")
tab([["Faixas livres no retorno (f)", "Velocidade antes do retorno", "Tempo do trajeto"],
     [f"{p.faixas} (sem o problema)", f"{v_depois:.0f} km/h (como o resto)", f"{T_sem_garg:.0f} min"],
     [f"{p.faixas - 1} (1 faixa ocupada)", f"{m.v_fila_e_livre(p.faixas - 1, p)[0]:.0f} km/h", f"{m.T_gargalo_min(p.faixas - 1, p, Lu):.0f} min"],
     [f"{p.faixas - 2} (2 faixas ocupadas)", f"{m.v_fila_e_livre(p.faixas - 2, p)[0]:.0f} km/h", f"{T_garg1:.0f} min"]],
    [5.5, 5.5, 4])
par(f"<b>Atenção.</b> O tempo de pico de {T_garg:.0f} min é uma estimativa minha: se a Raposo está de fato parada até o Butantã, "
    f"o tempo real é maior e a velocidade depois do retorno cai (o app permite trocar esse valor). A hipótese de que, sem o retorno, o "
    f"trecho antes dele andaria como o resto da fila é uma simplificação.")
par(f"<b>Limite.</b> Quando f tende a 0, v_fila tende a 0 e T(f) tende ao infinito: se o retorno bloqueasse a rodovia, o tempo cresceria sem limite. "
    f"<b>Derivada.</b> dT/df = {dTdf:.1f} min por faixa em f = {fe}: cada faixa liberada no retorno economiza cerca de "
    f"{abs(dTdf):.0f} min. O efeito é não linear: |dT/df| é de {abs(m.dT_df_num(2.5, p, Lu)):.0f} min/faixa perto de f = 2,5 e "
    f"{abs(m.dT_df_num(1.0, p, Lu)):.0f} em f = 1. "
    f"<b>Integral.</b> Com o pico em parábola, H = integral de Cb·phi(t)·[T(f) - T(3)] dt, com phi(t) = 1 - ((t - t_pico)/w)² (primitiva pela regra da potência), resulta em <b>{Hb:.0f} veículo-horas</b> perdidas na manhã (5h-10h), "
    f"em que Cb = f·q_max é o que o retorno deixa passar e phi(t) é a intensidade do pico.")
img("g7_gargalo.png", "Figura 7 - Tempo do trajeto x faixas liberadas no retorno.")
par(f"<b>Insight.</b> Resolver o retorno (por exemplo, passagem em desnível ou reorganização do retorno) não acabaria com o "
    f"engarrafamento da Raposo, mas reduziria o trajeto de {T_garg:.0f} para cerca de {T_sem_garg:.0f} min, ganho de "
    f"<b>{ganho:.0f} min</b> por viagem, em uma intervenção pontual que pode ser avaliada sem depender de uma obra do porte de um metrô.")

h1("7. Comparação com o metrô (Linha 22-Marrom)")
par("A Linha 22-Marrom é um projeto do Metrô-SP, em licenciamento, com 31,32 km e 19 estações entre Cotia e Sumaré; sete ficam em "
    "Cotia (Terminal Cotia, Portão, Sabiá, Parque Alexandra, Cotia-km 26, São George e Granja Viana), seguidas por duas em Osasco e dez na "
    "capital. A velocidade comercial prevista é de cerca de 40 km/h (máxima de projeto: 80 km/h) e o intervalo entre trens é de 100 s. "
    "O gráfico anterior (Figura 4) <b>não</b> é o tempo do metrô: é o tempo de carro com menos carros na pista. Aqui calculo o tempo do metrô.")
eq("T_metro = d / v_comercial        d = (estações até o destino - 1) · (extensão / (estações - 1))")
par(f"A fonte não informa a distância entre estações; uso o espaçamento médio de 31,32/18 = {31.32/18:.2f} km. Considero a estação "
    f"Vital Brasil (a 15ª contando do Terminal Cotia) como a mais próxima do fim da Raposo, hipótese minha a confirmar. Resultado: "
    f"d = <b>{d_m:.1f} km</b> e T_metro = <b>{t_m:.0f} min</b> de estação a estação (a velocidade comercial já inclui as paradas). "
    f"Somando a espera média (metade do intervalo, {esp_m:.1f} min) e {p.acesso_min:.0f} min para chegar à estação (hipótese minha), "
    f"o tempo porta a porta é de <b>{t_porta:.0f} min</b>.")
tab([["Modo", "Tempo", "Observação"],
     ["Carro no pico (7h30)", f"{Tpico:.0f} min", "depende do trânsito (estimativa minha)"],
     ["Carro fora do pico (14h)", f"{T14:.0f} min", "cenário de densidade base"],
     ["Metrô, estação a estação", f"{t_m:.0f} min", "constante, não depende do trânsito"],
     ["Metrô, porta a porta", f"{t_porta:.0f} min", f"inclui espera de {esp_m:.1f} min e acesso de {p.acesso_min:.0f} min"]],
    [5, 3, 7.8])
if eq_m:
    par(f"<b>Quando o metrô ganha do carro.</b> Igualando T_carro(t) ao tempo porta a porta (equação do 2º grau em t, resolvida exatamente), o metrô "
        f"é mais rápido para quem sai entre <b>{eq_m[0]:.1f} h e {eq_m[1]:.1f} h</b>. No pico, o metrô poupa {Tpico - t_porta:.0f} min porta a porta "
        f"({Tpico - t_m:.0f} min estação a estação). Fora do pico o carro continua mais rápido, o que é coerente com o modelo.")
img("g8_metro.png", "Figura 8 - Tempo de carro ao longo da manhã x tempo de metrô (área verde = janela em que o metrô compensa).")

par("<b>Com o metrô funcionando, quanto o trânsito da Raposo diminui?</b> Se uma fração s dos carros do pico migrar para o metrô, a "
    "densidade cai para k_s = (1 - s)·k_pico e o tempo de carro passa a ser T(k_s). A tabela mostra cenários (não uma previsão: a "
    "adesão real depende de tarifa, acesso às estações e conforto).")
fr_ot = m.frac_otima(p)
fr_lista = sorted({0.05, 0.10, 0.15, 0.20, fr_ot, 0.40})
linhas_m = [["% dos carros no metrô", "Tempo de carro", "Velocidade", "Minutos poupados", "Carros a menos/h", "Passag./trem"]]
for f_ in fr_lista:
    e_ = m.efeito_migracao(f_, p)
    linhas_m.append([f"{f_*100:.0f}%" + (" (ótimo)" if abs(f_ - fr_ot) < 1e-3 else ""), f"{e_['T']:.0f} min", f"{e_['v']:.0f} km/h",
                     f"{e_['poupa']:.0f} min", f"{e_['carros_h']:.0f}", f"{e_['pass_por_trem']:.0f}"])
tab(linhas_m, [3.4, 2.5, 2.3, 2.8, 2.8, 2.7])
par(f"<b>Leitura.</b> Com {p.s*100:.0f}% dos carros no metrô ({m.efeito_migracao(p.s, p)['carros_h']:.0f} carros/h a menos), o carro que continua na "
    f"rodovia leva {m.efeito_migracao(p.s, p)['T']:.0f} min em vez de {Tpico:.0f} min, ganho de <b>{m.efeito_migracao(p.s, p)['poupa']:.0f} min</b>. "
    f"A pista atinge o fluxo máximo (k = kj/2, v = {p.vf/2:.0f} km/h) quando se retiram cerca de <b>{fr_ot*100:.0f}%</b> dos carros: "
    f"o tempo cai para {m.efeito_migracao(fr_ot, p)['T']:.0f} min. Em passageiros, isso é pouco para o metrô: com trens a cada 100 s (36 por hora) e "
    f"{p.ocupacao:.1f} pessoas por carro (hipótese minha), {p.s*100:.0f}% dos carros equivalem a "
    f"{m.efeito_migracao(p.s, p)['pass_h']:.0f} passageiros por hora, cerca de {m.efeito_migracao(p.s, p)['pass_por_trem']:.0f} por trem.")
par(f"<b>Derivada.</b> dT/ds = {m.dT_dfrac(0.001, p)/100:.1f} min por ponto percentual no início e {m.dT_dfrac(0.2, p)/100:.1f} min perto de 20%: "
    f"os primeiros carros retirados são os que mais ajudam, já que a via sai da região de congestionamento onde o tempo cresce mais rápido.")
img("g9_migracao.png", "Figura 9 - Tempo de carro no pico em função da fração de carros que migra para o metrô.")

h1("8. Meio ambiente e saúde")
par("O trânsito parado não custa só tempo: o motor continua queimando combustível sem andar. Como o modelo já calcula "
    "os <b>veículo-horas perdidos</b>, posso convertê-los em litros de gasolina e em CO2. Os gases do escapamento "
    "(CO2, que alimenta o efeito estufa, e material particulado, que o carro lança no ar da cidade) são o motivo ambiental de se preocupar com o engarrafamento.")
par(f"<b>Função.</b> Um carro gasta combustível por distância (a) e, além disso, queima combustível a cada hora que fica no trânsito (c). "
    f"Como o tempo por km é 1/v(k), o consumo por km depende da densidade:")
eq("consumo(k) = a + c / v(k)  [L/km]        CO2(k) = L · consumo(k) · e · f   [kg por viagem]")
par(f"Uso c = {p.c_parado:.1f} L/h (carro parado ou quase parado; a faixa medida pelo Argonne National Laboratory para carros de passeio é de "
    f"0,2 a 0,5 galão/h, ou 0,8 a 1,9 L/h; o valor dentro da faixa é escolha minha), a = {p.a_km:.2f} L/km (cerca de 14 km/L em velocidade livre, <b>hipótese minha</b>), "
    f"e = {p.co2_litro:.3f} kg de CO2 por litro de gasolina pura (EPA: 8.887 g de CO2 por galão) e f = {p.frac_fossil:.2f} para a fração fóssil da gasolina "
    f"vendida no Brasil, que tem etanol misturado (<b>hipótese minha, a confirmar</b>). O etanol usado como combustível só devolve ao ar o carbono que a cana tirou, por isso conto apenas a parte fóssil.")
par("<b>Limite.</b> Quando k tende a kj, v tende a 0 e o consumo por km tende a +infinito (SymPy confirma); quando k tende a 0, o consumo vai para "
    "a + c/vf, o mínimo. Em termos práticos: quanto mais parado, mais combustível se queima por quilômetro rodado.")
par(f"<b>Derivada.</b> consumo'(k) = c·kj / [vf·(kj - k)²] é sempre positiva: o consumo por km só cresce com a densidade, e cresce cada vez mais "
    f"rápido perto da saturação. No pico, a derivada de CO2(k) é {dco2_pico:.4f} kg/km por (veíc/km/faixa); cada carro a mais no trecho piora a emissão de <i>todos</i> os carros do trecho.")
tab([["Situação", "Consumo", "CO2 por carro (trecho de " + f"{p.L:.0f}" + " km)"],
     ["Sem trânsito (k->0)", f"{cons_livre:.3f} L/km ({p.L*cons_livre:.1f} L)", f"{co2v_livre:.1f} kg"],
     [f"Pico ({Tpico:.0f} min)", f"{cons_pico:.3f} L/km ({p.L*cons_pico:.1f} L)", f"{co2v_pico:.1f} kg (+{(co2v_pico/co2v_livre-1)*100:.0f}%)"]],
    [5, 5.5, 5.3])
par(f"<b>Integral.</b> Os {D:.0f} veículo-horas de atraso entre 5h e 10h (seção 4) queimam, por causa do congestionamento, "
    f"{L_exc:.0f} litros a mais por manhã. Em CO2:")
eq("E = Integral de q(k(t)) · [T(k(t)) - T0] · c · e · f dt = " + f"{co2_exc/1000:.1f} t de CO2 por manhã")
par(f"Em {p.dias_uteis:.0f} dias úteis, são cerca de <b>{co2_exc_ano:.0f} toneladas de CO2 por ano</b>, só neste trecho e só no sentido capital pela manhã. "
    f"Com {p.s*100:.0f}% dos carros no metrô, o atraso cai {H:.0f} veículo-horas e a via emite <b>{co2_ev/1000:.1f} t de CO2 a menos por manhã "
    f"(cerca de {co2_ev_ano:.0f} t por ano)</b>. Esse valor é conservador: conta só o CO2 extra do congestionamento, não o combustível dos carros que saíram da rodovia, "
    f"e também não desconta a energia do metrô.")
S.append(Image(f"{GRAF}/g10_ambiente.png", width=15.5 * cm, height=15.5 * cm * 3.4 / 7.6))
S.append(Paragraph("Figura 10 - CO2 por carro conforme a densidade (esquerda) e CO2 extra emitido ao longo da manhã, hoje e com menos carros (direita; área = toneladas).", CAP))
par(f"<b>Saúde e estresse.</b> A saúde entra por dois caminhos. (1) O ar: a Organização Mundial da Saúde estima que a poluição do ar de fora de casa, da qual "
    f"o transporte faz parte, esteja ligada a 4,2 milhões de mortes prematuras por ano no mundo (dado de 2016), por causa de partículas que chegam ao pulmão e à "
    f"corrente sanguínea. (2) O tempo: pelo modelo, um motorista que faz esse trajeto toda manhã perde cerca de <b>{h_ano:.0f} horas por ano</b> "
    f"a mais no trânsito ({Tpico - T0:.0f} min a mais por viagem × {p.dias_uteis:.0f} dias; só a ida; o valor depende do meu tempo de pico observado). "
    f"<b>Não calculei</b> o custo em saúde nem o estresse em números, porque não encontrei uma fonte que eu pudesse usar para converter horas ou gramas "
    f"de poluente em casos de doença; por isso trato esses efeitos de forma qualitativa e uso as horas perdidas e o CO2 como medidas do problema.")
par("<b>Contexto nacional.</b> O transporte responde por cerca de 10 a 11% das emissões brasileiras de gases de efeito estufa, e mais de 90% disso vem do "
    "modo rodoviário (ICCT, 2025; coalizão de entidades de transporte, 2025). Aumentar a oferta de transporte coletivo é, portanto, também uma política de clima.")

h1("9. Protótipo CitizenTech")
par("O arquivo <b>app.py</b> é um aplicativo web (Streamlit) em que o cidadão de Cotia informa o horário de saída e "
    "a fração de carros que migraria para o transporte coletivo, e vê o tempo estimado de carro, o tempo do metrô, o tempo poupado e as integrais. "
    "Serve de argumento técnico para cobrar transporte de massa.")

h1("10. Conclusões e limitações")
par(f"1) O tempo de viagem explode perto da saturação (limite infinito). 2) No pico a via opera acima da densidade ótima "
    f"({kp:.0f} contra {kc:.0f} veíc/km): <b>tirar carros aumenta o fluxo</b>. 3) Tirar {p.s*100:.0f}% dos carros reduziria o trecho "
    f"de {Tpico:.0f} para {T_metro:.0f} min (para quem segue de carro); e o metrô da Linha 22-Marrom, se existir, faria o trajeto em cerca de {t_m:.0f} min, independentemente do trânsito. "
    f"4) Meio ambiente: o congestionamento da manhã queima cerca de {L_exc:.0f} L a mais e emite cerca de {co2_exc/1000:.1f} t de CO2 por dia útil; "
    f"{p.s*100:.0f}% dos carros a menos evitariam cerca de {co2_ev_ano:.0f} t por ano (estimativa conservadora).")
par("<b>Limitações.</b> Os números de combustível e CO2 dependem de hipóteses minhas (consumo parado, consumo em velocidade livre e fração fóssil da gasolina) e cobrem só os carros leves na manhã, no sentido capital. Greenshields é simplificado e menos preciso em densidades altas. A velocidade de pico, o nº de "
    "faixas, k0 e w são hipóteses e observações minhas, a serem substituídas por contagens da concessionária ou "
    "da ARTESP. A frota registrada em Cotia não é a frota que circula na Raposo Tavares. O cenário de migração de carros é ilustrativo; o tempo do metrô usa dados de projeto, ainda sujeitos a mudança.")

h1("11. Métodos usados e as aulas")
par("Todo o cálculo deste relatório usa só o conteúdo das Aulas 12, 13 e 14 (Celso Jacubavicius):")
tab([["Aula", "Conteúdo", "Onde foi usado"],
     ["12 - Derivadas", "definição pelo limite, regra da potência, quociente, cadeia, derivada segunda",
      "q'(k) e q''(k); T'(k) = L·kj/[vf(kj - k)²] (quociente/cadeia); dT/df com raiz quadrada (cadeia); dT/ds; consumo'(k)"],
     ["13 - Aplicações", "taxa de variação instantânea; máximo e mínimo por ponto crítico",
      "k* = kj/2 onde q'(k) = 0 e q'' < 0 (máximo de fluxo); T'(k) como taxa de variação do tempo; consumo'(k) como taxa do consumo"],
     ["14 - Integral", "primitiva, integral indefinida e definida, regra da potência",
      "primitiva de q(k) e de L·k²/kj; N, D, H e horas do retorno como integrais definidas de polinômios; CO2 extra = c·e·f · D"]],
    [2.8, 5.4, 7.6])
par("Para que as integrais saiam por esses métodos, o pico do trânsito na manhã é uma parábola (um polinômio) e não uma curva em sino. "
    "As raízes dos horários em que o metrô ganha do carro saem de uma equação do 2º grau. Os limites usam as ideias da Aula 12 (a derivada é um limite).")

h1("Referências")
for r in ["GREENSHIELDS, B. D. A study of traffic capacity. Highway Research Board Proceedings, v. 14, 1935.",
          "Agência Mural. Sem metrô, Cotia acumula promessas que nunca saíram do papel na Raposo Tavares (03/09/2021). https://agenciamural.org.br/sem-metro-cotia-acumula-promessas-que-nunca-sairam-do-papel-na-raposo-tavares/",
          "Girosa. Cotia: Raposo Tavares registra mais de 30 km de lentidão. https://girosa.com.br/cotia-raposo-tavares-registra-30-lentidao-quarta-14/",
          "Diário do Transporte. Linha 22-Marrom terá audiências em dezembro; projeto prevê 19 estações entre Cotia e Sumaré (13/10/2026). https://diariodotransporte.com.br/2026/10/13/linha-22-marrom-tera-audiencias-em-dezembro-projeto-preve-19-estacoes-entre-cotia-e-sumare/",
          "Gazeta SP. Linha 22-Marrom terá 19 estações em SP, Osasco e Cotia. https://www.gazetasp.com.br/cotidiano/linha-22-marrom-tera-19-estacoes-em-sp-osasco-e-cotia/1141671",
          "OpenStreetMap / OSRM. Rota de carro Cotia-Butantã (distância 24,86 km, até o fim da Rodovia Raposo Tavares no Butantã). https://project-osrm.org",
          "Senatran. Frota de veículos por UF, município, tipo, espécie e eixos - setembro/2026 (aba Cotia).",
          "IBGE. Cotia - Panorama (Censo 2022: 274.413 habitantes). https://www.ibge.gov.br/cidades-e-estados/sp/cotia.html",
          "EPA (EUA). Greenhouse Gas Equivalencies Calculator - Calculations and References (8.887 g de CO2 por galão de gasolina). https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references",
          "Argonne National Laboratory. Idling worksheet - light duty e estudos de consumo em marcha lenta de veículos leves (0,2 a 0,5 galão/h). https://webarchive.library.unt.edu/web/20130218071111/http://www.transportation.anl.gov/pdfs/idling_worksheet_light-duty.pdf",
          "OMS. 9 em cada 10 pessoas respiram ar poluído (4,2 milhões de mortes por ano pela poluição do ar externo, dado de 2016). Resumo em https://www.ccacoalition.org/en/news/world-health-organization-releases-new-global-air-pollution-data",
          "ICCT. Mobilidade zero emissões no Brasil (transporte: 10% das emissões do país em 2023, 92% pelo modo rodoviário). https://theicct.org/wp-content/uploads/2025/11/ID-510-–-Mobilidade-zero-emissoes_research-brief_final.pdf",
          "NPTEL. Traffic Stream Characteristics (Greenshields). https://archive.nptel.ac.in/content/storage2/courses/105101008/513_TrStream/point2/point.html"]:
    S.append(Paragraph(r, ParagraphStyle("R", parent=B, fontSize=8.5, leading=11, alignment=0)))
doc.build(S)
print("PDF gerado: Relatorio_Tecnico_CitizenTech.pdf")
