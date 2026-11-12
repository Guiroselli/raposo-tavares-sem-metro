"""
modelo.py - Núcleo matemático do projeto "Raposo Tavares sem metrô" (CitizenTech / Cotia-SP)

Modelo de Greenshields (1935) para o trânsito:
    v(k) = vf * (1 - k/kj)        velocidade em função da densidade
    q(k) = k * v(k)               fluxo (veículos/hora) = densidade * velocidade
    T(k) = L / v(k)               tempo de viagem de um trajeto de L km

Cenário "e se tivesse metrô?": uma fração s dos carros do pico sai da rodovia -> k*(1-s).

Todo o cálculo de limites, derivadas e integrais está aqui (SymPy = simbólico,
SciPy/NumPy = numérico), reaproveitado por app.py e analise.py.
"""
from dataclasses import dataclass

import numpy as np
import sympy as sp

# Frota de Cotia - Senatran, setembro/2026 (planilha "Frota por UF/Município/Tipo", aba Cotia):
# automóvel 118.318 + caminhonete 13.706 + camioneta 10.987 + utilitário 5.208
FROTA_LEVES_COTIA = 118318 + 13706 + 10987 + 5208   # = 148.219
FROTA_TOTAL_COTIA = 390638                           # todos os tipos registrados em Cotia


@dataclass
class Params:
    vf: float = 80.0       # km/h  - velocidade de fluxo livre na Raposo Tavares (limite de projeto da rodovia)
    kj: float = 140.0      # veic/km/faixa - densidade de parada total (faixa da literatura: ~120-160)
    v_pico: float = 24.86  # km/h  - velocidade média no pico = 24,86 km / 60 min (OBSERVAÇÃO A CONFIRMAR: ~60 min no pico)
    k0: float = 30.0       # veic/km/faixa - densidade fora do pico (hipótese do cenário)
    t_pico: float = 7.5    # h     - centro do pico da manhã (pico de ~7h às 8h, informado por mim)
    w: float = 1.5         # h     - meia-largura do pico (o pico é uma parábola de t_pico-w a t_pico+w) (hipótese do cenário)
    L: float = 24.86       # km    - Cotia -> fim da Raposo Tavares no Butantã, altura da Rua Sapetuba (OSRM/OpenStreetMap), ver rota_cotia_butanta.json
    faixas: int = 3        # nº de faixas no sentido capital (hipótese)
    s: float = 0.15        # fração dos carros do pico que migraria para um metrô
    ocupacao: float = 1.5     # passageiros por carro (hipótese minha)
    acesso_min: float = 10.0  # min - tempo para chegar à estação + descer até a plataforma (hipótese minha)
    bloqueadas: int = 1    # faixas ocupadas pela fila do retorno no gargalo (observação minha: 1 ou 2)
    # --- meio ambiente (combustível e CO2) ---
    c_parado: float = 1.0     # L/h  - consumo de um carro leve parado/andando muito devagar. Faixa Argonne: 0,2-0,5 gal/h = 0,8-1,9 L/h; uso 1,0 (hipótese minha)
    a_km: float = 0.07        # L/km - consumo "por distância" em velocidade livre (~14 km/L) (hipótese minha)
    co2_litro: float = 2.348  # kg CO2 por litro de gasolina pura (EPA: 8.887 g CO2/galão ÷ 3,785 L)
    frac_fossil: float = 0.70 # fração fóssil da gasolina vendida no Brasil (o resto é etanol anidro) (hipótese minha, a confirmar)
    dias_uteis: float = 252.0 # dias úteis por ano (hipótese minha)


P0 = Params()


# ---------------------------------------------------------------- funções numéricas
def v(k, p=P0):
    return p.vf * (1 - np.asarray(k, dtype=float) / p.kj)


def q(k, p=P0):
    k = np.asarray(k, dtype=float)
    return k * v(k, p)


def T_min(k, p=P0):
    return 60.0 * p.L / v(k, p)


def k_do_pico(p=P0):
    """Densidade que reproduz a velocidade média observada no pico."""
    return p.kj * (1 - p.v_pico / p.vf)


def k_t(t, p=P0):
    """Cenário de densidade ao longo da manhã: base k0 + um pico em forma de parábola (polinômio de grau 2) entre
    t_pico-w e t_pico+w:  k(t) = k0 + (k_pico - k0)·(1 - ((t - t_pico)/w)²)."""
    kp = k_do_pico(p)
    t = np.asarray(t, dtype=float)
    u = (t - p.t_pico) / p.w
    return p.k0 + (kp - p.k0) * np.where(np.abs(u) <= 1, 1 - u ** 2, 0.0)


def k_metro(k, p=P0):
    """Densidade se uma fração s dos carros migrar para o metrô."""
    return np.asarray(k, dtype=float) * (1 - p.s)


def carros_na_pista(k, p=P0):
    """Veículos simultaneamente no trecho (todas as faixas)."""
    return k * p.L * p.faixas


# ---------------------------------------------------------------- Metrô: Linha 22-Marrom (projeto, em licenciamento)
# Fonte: Diário do Transporte (13/10/2026) e Estudo de Impacto Ambiental do Metrô-SP.
METRO = {
    "extensao_km": 31.32,        # Terminal Cotia -> Sumaré
    "estacoes": 19,
    "v_comercial": 40.0,         # km/h ("em torno de 40 km/h"; velocidade máxima de projeto 80 km/h)
    "headway_s": 100,            # intervalo entre trens (s)
    "estacoes_ate_destino": 15,  # Terminal Cotia ... Vital Brasil (estação mais próxima do fim da Raposo: hipótese minha)
}


def tempo_metro(p=P0):
    """
    Tempo de viagem de metrô (min). Espaçamento médio entre estações = extensão/(estações-1) (a fonte não traz as
    distâncias entre estações). A velocidade comercial de 40 km/h já inclui as paradas.
    Retorna (distância km, estação a estação, espera média, porta a porta).
    """
    esp = METRO["extensao_km"] / (METRO["estacoes"] - 1)
    d = (METRO["estacoes_ate_destino"] - 1) * esp
    t_viagem = 60 * d / METRO["v_comercial"]
    espera = METRO["headway_s"] / 2 / 60
    return d, t_viagem, espera, t_viagem + espera + p.acesso_min


def horarios_equilibrio(T_ref, t1=5.0, t2=10.0, p=P0):
    """
    Horários em que o tempo de carro iguala T_ref (min). Retorna (antes do pico, depois do pico) ou None.
    Solução exata (álgebra): T(k) = T_ref  =>  k_eq = kj·(1 - 60·L/(vf·T_ref));  k(t) = k_eq é uma equação do 2º grau em t:
    t = t_pico ± w·raiz(1 - (k_eq - k0)/(k_pico - k0)).
    """
    kp = k_do_pico(p)
    k_eq = p.kj * (1 - 60 * p.L / (p.vf * T_ref))
    if not (p.k0 < k_eq < kp):
        return None
    d = p.w * float(np.sqrt(1 - (k_eq - p.k0) / (kp - p.k0)))
    a, b = p.t_pico - d, p.t_pico + d
    return (a, b) if (t1 <= a and b <= t2) else None


def efeito_migracao(frac, p=P0):
    """
    Efeito no trânsito da Raposo se uma fração `frac` dos carros do pico migrar para o metrô.
    Retorna dict: tempo de carro (min), velocidade, minutos poupados, carros/h retirados, passageiros/h e por trem.
    """
    kp = k_do_pico(p)
    k = kp * (1 - frac)
    T = float(T_min(k, p))
    T_hoje = float(T_min(kp, p))
    carros_h = frac * p.faixas * float(q(kp, p))
    pass_h = carros_h * p.ocupacao
    trens_h = 3600 / METRO["headway_s"]
    return {"frac": frac, "k": k, "v": float(v(k, p)), "T": T, "poupa": T_hoje - T,
            "carros_h": carros_h, "pass_h": pass_h, "pass_por_trem": pass_h / trens_h}


def frac_otima(p=P0):
    """Fração de carros a retirar para a densidade cair ao ponto de fluxo máximo (k = kj/2)."""
    return max(0.0, 1 - (p.kj / 2) / k_do_pico(p))


def dT_dfrac(frac, p=P0):
    """
    Derivada do tempo de carro em relação à fração s que migra (min por unidade de fração), pela regra do quociente/cadeia:
    T(s) = 60·L / (vf·D(s)),  D(s) = 1 - k_pico·(1 - s)/kj   =>   T'(s) = -60·L·k_pico / (vf·kj·D(s)²).
    """
    kp = k_do_pico(p)
    D_ = 1 - kp * (1 - frac) / p.kj
    return -60 * p.L * kp / (p.vf * p.kj * D_ ** 2)


# ---------------------------------------------------------------- rota no mapa
def carregar_rota():
    import json, os
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rota_cotia_butanta.json")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def cor_velocidade(vel):
    """Cor estilo Waze: verde (livre), amarelo, laranja, vermelho (parado). Retorna RGB."""
    if vel >= 50:
        return [30, 170, 60]
    if vel >= 35:
        return [240, 200, 20]
    if vel >= 20:
        return [250, 130, 20]
    return [215, 30, 30]


# ---------------------------------------------------------------- gargalo (retorno depois do Shopping Granja Viana)
GARGALO_LAT, GARGALO_LON = -23.590192926793296, -46.829124789092916   # coordenadas do Google Maps (informadas por mim)


def _haversine_km(a, b):
    import math
    la1, lo1, la2, lo2 = map(math.radians, [a[1], a[0], b[1], b[0]])
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(d))


def posicao_gargalo(rota=None):
    """Projeta o retorno na rota: devolve (km desde Cotia, índice do ponto da rota)."""
    rota = rota or carregar_rota()
    c = rota["coords"]
    cum = [0.0]
    for i in range(1, len(c)):
        cum.append(cum[-1] + _haversine_km(c[i - 1], c[i]))
    j = min(range(len(c)), key=lambda i: _haversine_km(c[i], (GARGALO_LON, GARGALO_LAT)))
    return cum[j], j


def faixas_efetivas(p=P0):
    return p.faixas - p.bloqueadas


def v_fila_e_livre(f, p=P0):
    """
    Velocidades (km/h) antes (fila) e depois (livre) do gargalo quando ele deixa passar f faixas.
    Fluxo por faixa = (f/faixas)*q_max. Na curva de Greenshields há dois estados com o mesmo fluxo:
    s = sqrt(1 - f/faixas);  v_fila = (vf/2)(1 - s)  e  v_livre = (vf/2)(1 + s).
    """
    s_ = np.sqrt(max(0.0, 1 - f / p.faixas))
    return p.vf / 2 * (1 - s_), p.vf / 2 * (1 + s_)


def calibrar_gargalo(p=P0, Lu=None):
    """
    A Raposo fica parada até o Butantã (observação minha) e o retorno só PIORA o trecho antes dele.
    Calibração com o tempo observado no pico (T_obs = 60*L/v_pico):
      - antes do retorno: a fila anda na velocidade v_fila(f) imposta pela capacidade do retorno (f = faixas livres);
      - depois do retorno: velocidade v_depois = o que sobra do tempo observado (já engarrafado);
      - sem o retorno: o trecho antes dele andaria como o resto do congestionamento (v_depois).
    """
    Lu = posicao_gargalo()[0] if Lu is None else Lu
    Ld = p.L - Lu
    f_ref = p.faixas - max(p.bloqueadas, 1)
    v_fila, _ = v_fila_e_livre(f_ref, p)
    T_obs = 60 * p.L / p.v_pico
    T_antes = 60 * Lu / v_fila
    T_depois = max(T_obs - T_antes, 60 * Ld / p.vf)
    v_depois = 60 * Ld / T_depois
    return {"Lu": Lu, "Ld": Ld, "f_ref": f_ref, "v_fila": v_fila, "v_depois": v_depois, "T_obs": T_obs,
            "T_antes": T_antes, "T_depois": T_depois, "T_sem_retorno": 60 * p.L / v_depois,
            "ganho": T_obs - 60 * p.L / v_depois, "cap": T_antes > T_obs}


def T_gargalo_min(f, p=P0, Lu=None):
    """Tempo total (min) se o retorno deixar passar f faixas (depois do retorno a velocidade é a calibrada)."""
    c = calibrar_gargalo(p, Lu)
    vu, _ = v_fila_e_livre(f, p)
    vu = min(vu, c["v_depois"])
    return 60 * c["Lu"] / vu + c["T_depois"]


def derivada_gargalo():
    """Derivada simbólica do tempo antes do retorno, Lu/v_fila(f), em relação às faixas livres f."""
    f, F, vf, Lu, Td = sp.symbols("f F v_f L_u T_d", positive=True)
    s_ = sp.sqrt(1 - f / F)
    T_s = Lu / (vf / 2 * (1 - s_)) + Td
    return T_s, sp.simplify(sp.diff(T_s, f)), (f, F, vf, Lu, Td)


def dT_df_num(f, p=P0, Lu=None):
    """
    dT/df em min por faixa, pela regra da cadeia. T(f) = Lu/v_fila(f) + T_depois, com v_fila = (vf/2)·(1 - s), s = raiz(1 - f/F):
      ds/df = -1/(2·F·s)   =>   dv_fila/df = vf/(4·F·s)   =>   dT/df = -60·Lu·vf / (4·F·s·v_fila²)   (válido enquanto v_fila < v_depois).
    (O nome ficou _num por compatibilidade, mas a conta agora é exata.)
    """
    Lu = posicao_gargalo()[0] if Lu is None else Lu
    s_ = float(np.sqrt(max(1e-12, 1 - f / p.faixas)))
    v_f_ = p.vf / 2 * (1 - s_)
    return -60 * Lu * p.vf / (4 * p.faixas * s_ * v_f_ ** 2)


def phi_pico(t, p=P0):
    """Intensidade do pico: parábola phi(t) = 1 - ((t - t_pico)/w)² entre t_pico-w e t_pico+w (0 fora), igual a 1 no centro."""
    u = (np.asarray(t, dtype=float) - p.t_pico) / p.w
    return np.where(np.abs(u) <= 1, 1 - u ** 2, 0.0)


# ---------------------------------------------------------------- integrais por regra da potência (aula 14)
def _integral_poli_de_k(coefs, t1, t2, p=P0):
    """
    Integral definida de t1 a t2 de P(k(t)), onde P é um polinômio em k (coeficientes do maior grau ao menor) e k(t) é o
    cenário (k0 fora do pico, parábola dentro). Como P(k(t)) é um polinômio em t, uso a REGRA DA POTÊNCIA para achar a
    primitiva e o teorema fundamental (F(b) - F(a)); onde k = k0 é constante, a integral é (valor)·(duração).
    """
    kp = k_do_pico(p)
    a, b = p.t_pico - p.w, p.t_pico + p.w
    dk = kp - p.k0
    kpoly = np.poly1d([-dk / p.w ** 2, 2 * dk * p.t_pico / p.w ** 2, p.k0 + dk * (1 - p.t_pico ** 2 / p.w ** 2)])
    res = np.poly1d([0.0])
    for c in coefs:                       # Horner com polinômios: calcula P(k(t)) como polinômio em t
        res = res * kpoly + c
    F = res.integ()
    P_k0 = float(np.polyval(coefs, p.k0))
    total = 0.0
    lo, hi = t1, min(a, t2)               # antes do pico: k = k0
    if hi > lo:
        total += P_k0 * (hi - lo)
    lo, hi = max(t1, a), min(t2, b)       # dentro do pico: parábola
    if hi > lo:
        total += float(F(hi) - F(lo))
    lo, hi = max(t1, b), t2               # depois do pico: k = k0
    if hi > lo:
        total += P_k0 * (hi - lo)
    return total


def horas_gargalo(t1, t2, p=P0):
    """
    H_b = integral de Cb * phi(t) * [T(f_efetivas) - T(faixas)] dt  (veículo-horas perdidas por causa do retorno),
    com Cb = f_efetivas * q_max (veículos/h que o gargalo deixa passar). phi(t) = intensidade do pico.
    """
    f = faixas_efetivas(p)
    extra_h = (T_gargalo_min(f, p) - T_gargalo_min(p.faixas, p)) / 60
    Cb = f * p.vf * p.kj / 4
    a, b = max(t1, p.t_pico - p.w), min(t2, p.t_pico + p.w)
    F = np.poly1d([-1 / (3 * p.w ** 2), p.t_pico / p.w ** 2, 1 - p.t_pico ** 2 / p.w ** 2, 0.0])   # primitiva de phi(t) pela regra da potência
    val = float(F(b) - F(a)) if b > a else 0.0
    return Cb * extra_h * val


# ---------------------------------------------------------------- limites
def limites():
    k, vf, kj, L = sp.symbols("k v_f k_j L", positive=True)
    a_, c_ = sp.symbols("a c", positive=True)
    v_s = vf * (1 - k / kj)
    q_s = k * v_s
    T_s = L / v_s
    return {
        "v(k) quando k->0+": sp.limit(v_s, k, 0, "+"),
        "v(k) quando k->kj-": sp.limit(v_s, k, kj, "-"),
        "q(k) quando k->kj-": sp.limit(q_s, k, kj, "-"),
        "T(k) quando k->kj-": sp.limit(T_s, k, kj, "-"),
        "T(k) quando k->0+": sp.limit(T_s, k, 0, "+"),
        "consumo(k) quando k->kj-": sp.limit(a_ + c_ / v_s, k, kj, "-"),
        "consumo(k) quando k->0+": sp.simplify(sp.limit(a_ + c_ / v_s, k, 0, "+")),
    }


# ---------------------------------------------------------------- derivadas
def derivadas():
    k, vf, kj, L = sp.symbols("k v_f k_j L", positive=True)
    q_s = vf * k * (1 - k / kj)
    T_s = L / (vf * (1 - k / kj))
    dq = sp.diff(q_s, k)
    crit = sp.solve(sp.Eq(dq, 0), k)[0]
    return {"q": q_s, "dq": sp.simplify(dq), "d2q": sp.simplify(sp.diff(q_s, k, 2)),
            "k_critico": sp.simplify(crit), "q_max": sp.simplify(q_s.subs(k, crit)),
            "T": T_s, "dT": sp.simplify(sp.diff(T_s, k)),
            "consumo": sp.symbols("a", positive=True) + sp.symbols("c", positive=True) / (vf * (1 - k / kj)),
            "dconsumo": sp.simplify(sp.diff(sp.symbols("c", positive=True) / (vf * (1 - k / kj)), k))}


def ponto_critico(p=P0):
    kc = p.kj / 2
    return kc, float(q(kc, p)), float(v(kc, p))


def dT_dk_min(k, p=P0):
    """T'(k) em minutos por (veículo/km/faixa)."""
    return 60 * p.L * p.kj / (p.vf * (np.asarray(k, dtype=float) - p.kj) ** 2)


# ---------------------------------------------------------------- integrais
def integrais_simbolicas():
    k, vf, kj = sp.symbols("k v_f k_j", positive=True)
    q_s = vf * k * (1 - k / kj)
    L_ = sp.symbols("L", positive=True)
    atraso_s = L_ * k ** 2 / kj      # integrando do atraso: q(k)·[T(k) - T0] simplificado
    return {"indefinida": sp.integrate(q_s, k),
            "definida_0_kj": sp.simplify(sp.integrate(q_s, (k, 0, kj))),
            "atraso_integrando": sp.simplify(q_s * (L_ / (vf * (1 - k / kj)) - L_ / vf)),
            "atraso_primitiva": sp.integrate(atraso_s, k)}


def veiculos_atendidos(t1, t2, p=P0):
    """N = integral de q(k(t)) dt, todas as faixas (veículos que passam entre t1 e t2)."""
    # q(k) = vf·k - (vf/kj)·k²  (polinômio em k)  ->  integral pela regra da potência
    return _integral_poli_de_k([-p.vf / p.kj, p.vf, 0.0], t1, t2, p) * p.faixas


def atraso_total(t1, t2, p=P0):
    """
    D = integral de q(k(t)) * [T(k(t)) - T0] dt  (veículo-horas perdidas, todas as faixas).
    Simplificação algébrica: q(k)·[L/v(k) - L/vf] = vf·kj·x(1-x) · (L/vf)·x/(1-x) = L·k²/kj  (x = k/kj), um polinômio em k.
    """
    return _integral_poli_de_k([p.L / p.kj, 0.0, 0.0], t1, t2, p) * p.faixas


def horas_economizadas_metro(t1, t2, p=P0):
    """
    H = D(hoje) - D(com metrô): veículo-horas de atraso evitadas na via. Com a fração s dos carros a menos, k vira (1-s)·k e o
    atraso por unidade de tempo L·k²/kj vira (1-s)²·L·k²/kj; logo H = [1 - (1-s)²]·D  (integral de polinômio).
    """
    return atraso_total(t1, t2, p) * (1 - (1 - p.s) ** 2)


# ---------------------------------------------------------------- meio ambiente: combustível e CO2
# Ideia: um carro gasta combustível por distância (a_km) e, além disso, queima combustível a cada hora que passa
# no trânsito (c_parado). Como o tempo por km é 1/v(k), o consumo por km é  a + c/v(k)  (litros/km).
def consumo_km(k, p=P0):
    """Litros por km de um carro leve quando a densidade da via é k:  a + c / v(k)."""
    return p.a_km + p.c_parado / v(k, p)


def co2_km(k, p=P0):
    """kg de CO2 fóssil emitidos por km, por carro."""
    return consumo_km(k, p) * p.co2_litro * p.frac_fossil


def co2_viagem(k, p=P0):
    """kg de CO2 emitidos por um carro que faz o trecho de L km com densidade k."""
    return p.L * co2_km(k, p)


def dco2_dk(k, p=P0):
    """Derivada de co2_km em relação a k: c·kj / (vf·(kj-k)²) · fator (kg/km por veíc/km/faixa). Sempre > 0."""
    return p.co2_litro * p.frac_fossil * p.c_parado * p.kj / (p.vf * (p.kj - np.asarray(k, dtype=float)) ** 2)


def litros_excedentes(veic_horas, p=P0):
    """Combustível queimado só por causa do atraso: veículo-horas perdidas × consumo parado (L/h)."""
    return veic_horas * p.c_parado


def co2_excedente(veic_horas, p=P0):
    """kg de CO2 emitidos só por causa do atraso."""
    return litros_excedentes(veic_horas, p) * p.co2_litro * p.frac_fossil


def co2_excedente_dia(t1, t2, p=P0):
    """CO2 extra (kg) emitido na manhã (t1 a t2) por causa do congestionamento: integral de q·[T-T0]·c·e dt."""
    return co2_excedente(atraso_total(t1, t2, p), p)


def co2_evitado_metro_dia(t1, t2, p=P0):
    """CO2 (kg) que quem segue de carro deixa de emitir na manhã se a fração s migrar para o metrô (só o ganho de tempo)."""
    return co2_excedente(horas_economizadas_metro(t1, t2, p), p)


def horas_no_transito_ano(p=P0, k=None):
    """Horas por ano que um motorista passa a mais no trânsito (só a ida da manhã): (T-T0)/60 × dias úteis."""
    k = k_do_pico(p) if k is None else k
    return (float(T_min(k, p)) - 60 * p.L / p.vf) / 60 * p.dias_uteis


if __name__ == "__main__":
    p = P0
    kp = k_do_pico(p)
    print("k pico", kp, "carros na pista", carros_na_pista(kp, p), "=", carros_na_pista(kp, p) / FROTA_LEVES_COTIA * 100, "% da frota leve")
    print("T pico", T_min(kp, p), "T com metro", T_min(kp * (1 - p.s), p))
    print("N", veiculos_atendidos(5, 10, p), "D", atraso_total(5, 10, p), "H", horas_economizadas_metro(5, 10, p))
