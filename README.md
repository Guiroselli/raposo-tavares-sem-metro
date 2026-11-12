# Raposo Tavares sem metrô — CitizenTech (Global Solution, Cálculo)

Guilherme Damásio Roselli — RM 571922

Uso Cálculo (limites, derivadas e integrais) para mostrar quanto tempo os moradores de **Cotia (SP)** perdem na rodovia Raposo Tavares por não terem metrô, quanto **combustível e CO₂** o congestionamento gasta, e quanto um transporte de massa poderia devolver.

---

## 1. O que o enunciado pede e onde está cada item

| Item do enunciado | Pontos | O que foi feito | Onde ver |
|---|---|---|---|
| **01** Modelo matemático + limite | 2,5 | Função do trânsito (modelo de Greenshields) calibrada com a realidade de Cotia; limites calculados e interpretados | PDF seções 1 e 2; `modelo.py` (função `limites`) |
| **02** Derivadas | 2,5 | Derivada do fluxo, intervalos de crescimento/decrescimento, ponto máximo, taxa de variação | PDF seção 3; `modelo.py` (função `derivadas`) |
| **03** Integrais + gráficos | 2,5 | Integral definida e indefinida, área sob a curva, veículos atendidos, atraso acumulado e horas poupadas com metrô; gráficos com título, eixos e unidades | PDF seção 4; `modelo.py`, `analise.py` |
| **04** Relatório técnico | 2,5 | Relatório em PDF para um cliente, com problema, modelo, análises, gráficos e conclusões | `Relatorio_Tecnico_CitizenTech.pdf` |
| **05** Entrega | — | Códigos em `.py` e relatório em `.pdf` | Arquivos desta pasta |

## 1.1 Ligação com as aulas (só estes métodos foram usados)

| Aula | Conteúdo | Onde aparece no projeto |
|---|---|---|
| **12 – Derivadas** | definição pelo limite, regra da potência, quociente, cadeia, derivada segunda | `q'(k)` e `q''(k)`; `T'(k) = L·kj/[vf(kj−k)²]` (quociente/cadeia); `dT/df` com raiz quadrada (cadeia); `consumo'(k)` |
| **13 – Aplicações** | taxa de variação instantânea; máximo e mínimo por ponto crítico | máximo do fluxo em `k* = kj/2` (`q' = 0`, `q'' < 0`); `T'(k)` e `consumo'(k)` como taxas de variação |
| **14 – Integral** | primitiva, integral indefinida e definida, regra da potência | primitiva de `q(k)` e de `L·k²/kj`; veículos atendidos `N`, atraso `D`, atraso evitado `H`, horas do retorno e CO₂ extra como integrais definidas de polinômios |

Para as integrais saírem por esses métodos, o pico da manhã é uma **parábola** (polinômio de grau 2) e os horários em que o metrô ganha do carro vêm de uma **equação do 2º grau**. Nada de método numérico entra nas contas do relatório (conferi os resultados com uma integração numérica à parte, só para testar).

## 2. O problema escolhido

Cotia cresceu 26% em dez anos e **não tem metrô**: as promessas antigas (monotrilho Linha 17 em 2016, Linha 22 em 2020) não saíram do papel. Hoje existe o projeto da **Linha 22-Marrom** (19 estações, Cotia–Sumaré), em licenciamento ambiental, sem obra nem data de operação. Os moradores dependem da Raposo Tavares, com lentidões de 20 a mais de 30 km. A pergunta do projeto: **quanto tempo isso custa e quanto um metrô poderia devolver?**

## 3. A ideia matemática (sem jargão)

- **Densidade (k):** quantos carros há em cada km de pista.
- **Velocidade v(k):** quanto mais carros, mais devagar. Modelo de Greenshields (1935): `v(k) = vf · (1 − k/kj)`.
- **Fluxo q(k):** quantos carros passam por hora = densidade × velocidade.
- **Limite:** quando a pista lota (k → kj), a velocidade vai a 0 e o **tempo de viagem tende ao infinito**.
- **Derivada:** o fluxo é máximo em **70 veíc/km** (2.800 veíc/h por faixa). Acima disso, mais carros fazem **menos** carros passarem. No pico, a Raposo está acima desse ponto.
- **Integral:** soma ao longo da manhã (5h–10h). Calculo quantos veículos passam (~34.400), quanto atraso acumulam (~10.400 veículo-horas) e quantas horas de atraso um metrô evitaria (~2.900), tudo por integrais de polinômios (regra da potência). O app e o relatório também comparam o **pico (60 min)** com um **horário sem trânsito (~23 min)** e mostram o trajeto no mapa com as cores de velocidade.
- **Cenário "15% dos carros a menos":** 15% dos carros do pico migram para o transporte coletivo e quem segue de carro faz o trajeto de 25 km em **~45 min** (antes 60 min). Esse gráfico **não** é o tempo do metrô.
- **Tempo do metrô (Linha 22-Marrom):** 31,32 km, 19 estações, velocidade comercial ~40 km/h, trens a cada 100 s. De Cotia até a estação Vital Brasil (15ª, a mais próxima do fim da Raposo, hipótese minha) são ~24 km e **~37 min** de estação a estação (**~47 min porta a porta** com espera e 10 min de acesso). O metrô é mais rápido que o carro para quem sai entre ~6,9h e ~8,1h; fora do pico o carro ganha.
- **Efeito do metrô no trânsito:** se 5%, 10%, 15% ou 20% dos carros do pico forem de metrô, o carro que continua na Raposo leva de ~42 a ~54 min (em vez de 60). Tirando ~27% dos carros a pista atinge o fluxo máximo (~37 min). A tabela está na aba **Comparação** do app e na seção 7 do relatório. São cenários, não previsão; a adesão real depende de tarifa, acesso e conforto.
- **Meio ambiente (seção 8 do relatório, aba "Meio ambiente" do app):** carro parado continua queimando combustível. O consumo por km é `a + c/v(k)`; quando a pista lota (k → kj) ele tende ao **infinito** (limite), e sua **derivada** é sempre positiva (mais carros, mais consumo para todos). A **integral** do atraso vira combustível e CO₂: no cenário, o congestionamento da manhã (5h–10h, só o sentido capital) queima **~10.400 L a mais** e emite **~17 t de CO₂ por dia útil (~4.300 t/ano)**; com 15% dos carros no metrô, a via emite ~4,8 t a menos por manhã (~1.200 t/ano, estimativa conservadora). Um carro emite ~4,5 kg de CO₂ no trecho no pico contra ~3,4 kg sem trânsito (+34%). Um motorista perde ~174 h/ano a mais no trânsito (só a ida).
- **Saúde e estresse:** tratados de forma **qualitativa** (a OMS associa a poluição do ar externo a 4,2 milhões de mortes prematuras por ano, dado de 2016). Não converti horas ou poluentes em casos de doença nem em estresse, porque não tenho fonte para isso; o relatório diz isso expressamente.

## 4. Dados reais e o que é suposição

| Dado | Valor | Origem |
|---|---|---|
| Frota de leves de Cotia | 148.219 (automóvel + caminhonete + camioneta + utilitário) | Planilha da Senatran, set/2026, aba Cotia (a frota total registrada é 390.638, mas inclui reboques e outros tipos, possivelmente de empresas; por isso usamos só leves) |
| População | 274.413 (Censo 2022) | [IBGE](https://www.ibge.gov.br/cidades-e-estados/sp/cotia.html) |
| Crescimento e promessas de metrô | 26% em 10 anos; Linhas 17 e 22 não saíram do papel | [Agência Mural, 2021](https://agenciamural.org.br/sem-metro-cotia-acumula-promessas-que-nunca-sairam-do-papel-na-raposo-tavares/) |
| Lentidão na rodovia | 20 a 30+ km | [Girosa](https://girosa.com.br/cotia-raposo-tavares-registra-30-lentidao-quarta-14/) |
| Metrô | Linha 22-Marrom: 31,32 km, 19 estações, ~40 km/h | [Diário do Transporte, 13/10/2026](https://diariodotransporte.com.br/2026/10/13/linha-22-marrom-tera-audiencias-em-dezembro-projeto-preve-19-estacoes-entre-cotia-e-sumare/) e [Gazeta SP](https://www.gazetasp.com.br/cotidiano/linha-22-marrom-tera-19-estacoes-em-sp-osasco-e-cotia/1141671) |
| CO₂ da gasolina | 8.887 g de CO₂ por galão (2,348 kg/L) | [EPA, Equivalencies Calculator](https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references) |
| Consumo de carro parado | 0,2 a 0,5 galão/h (0,8 a 1,9 L/h) | [Argonne National Laboratory](https://webarchive.library.unt.edu/web/20130218071111/http://www.transportation.anl.gov/pdfs/idling_worksheet_light-duty.pdf) (números confirmados em fontes secundárias; não achei uma tabela única do Argonne) |
| Poluição do ar e saúde | 4,2 milhões de mortes/ano (2016) | [OMS, resumo CCAC](https://www.ccacoalition.org/en/news/world-health-organization-releases-new-global-air-pollution-data) |
| Transporte nas emissões do Brasil | ~10% do total; ~92% é rodoviário | [ICCT, 2025](https://theicct.org/wp-content/uploads/2025/11/ID-510-–-Mobilidade-zero-emissoes_research-brief_final.pdf) |
| Modelo | Greenshields (1935) | [NPTEL](https://archive.nptel.ac.in/content/storage2/courses/105101008/513_TrStream/point2/point.html) |

**Minhas suposições (devem ser confirmadas ou substituídas):**
- Tempo da viagem no pico: **60 min** para os 25 km Cotia–Butantã (≈ 25 km/h). É uma observação de morador, não uma medição oficial; no app dá para trocar.
- Trajeto: rota de carro Cotia (centro) → o fim da Rodovia Raposo Tavares no Butantã (altura da Rua Sapetuba, -23.5738, -46.7102), **24,86 km, praticamente todo pela Raposo** (sem desvio por outras avenidas), calculada com OpenStreetMap/OSRM (arquivo `rota_cotia_butanta.json`). Cada cor do mapa é a velocidade média estimada pelo modelo para o trecho inteiro; o gargalo do retorno é tratado à parte (seção 6 do relatório e aba "Gargalo" do app), com o trecho antes dele mais lento (vermelho) e o resto da rota também engarrafado, já que a Raposo fica parada até o Butantã.
- Velocidade sem trânsito: 80 km/h; 3 faixas por sentido; densidade de parada 140 veíc/km/faixa; pico das 7h às 8h (centro 7,5h) com largura de 1h; densidade fora do pico 30 veíc/km/faixa.
- A forma do pico ao longo da manhã é uma parábola (polinômio de grau 2) entre 6h e 9h, hipótese de cenário: assim as integrais saem pela regra da potência.
- **Retorno que piora o trânsito:** observo, como morador de Cotia, que a Raposo fica parada até o Butantã e que um retorno depois do Shopping Granja Viana (coordenadas -23.59019, -46.82912; sentido Cotia → capital; km 11,7 da rota) só piora o quadro, porque a fila ocupa 1 ou 2 das 3 faixas. São observações minhas. O modelo calibra o trecho antes do retorno (~17 km/h) e o depois (~43 km/h) com o tempo de pico (60 min, suposição a confirmar); sem o problema do retorno a viagem levaria ~35 min, ou seja, o retorno custa ~25 min.
- **Combustível e CO₂:** consumo de carro parado **1,0 L/h** (dentro da faixa do Argonne, valor escolhido por mim), consumo em velocidade livre **0,07 L/km** (~14 km/L), **70% de gasolina fóssil** (o resto é etanol; a confirmar) e **252 dias úteis** por ano. São hipóteses minhas, editáveis na aba "Meio ambiente"; contam só carros leves na manhã, sentido capital.
- A frota **registrada** em Cotia não é a frota que **circula** na Raposo Tavares.

## 5. Arquivos

| Arquivo | Para que serve |
|---|---|
| `Relatorio_Tecnico_CitizenTech.pdf` | **O relatório técnico (item 04).** Comece por ele. |
| `modelo.py` | Todas as fórmulas: limites, derivadas e integrais. |
| `analise.py` | Gera os gráficos (pasta `graficos/`), imprime os resultados e cria o PDF. |
| `app.py` | Protótipo interativo (aplicativo web) com mapa, comparação pico x sem trânsito, limites, derivadas e integrais. |
| `rota_cotia_butanta.json` | Coordenadas do trajeto usado no mapa. |
| `requirements.txt` | Lista de bibliotecas Python necessárias. |
| `graficos/` | Imagens usadas no relatório. |

## 6. Como executar (opcional)

Requer Python 3.10+. No terminal, dentro desta pasta:

```bash
pip install -r requirements.txt
```

Gerar gráficos, resultados e o PDF:

```bash
python analise.py
```

Abrir o aplicativo interativo (abre no navegador):

```bash
streamlit run app.py
```

No app, mova os controles laterais (horário de saída, horário de comparação sem trânsito, % de carros que iriam de metrô, tempo observado no pico) e veja os tempos mudarem. A aba **Metrô** compara o tempo de carro com o do metrô. A aba **Mapa** mostra o trajeto com e sem trânsito; a aba **Meio ambiente** mostra combustível e CO₂; as demais mostram comparação, limites, derivadas e integrais. O mapa precisa de internet para carregar.

## 7. Antes de entregar

1. Nome e RM já estão em `analise.py` e no PDF.
2. Envie: `modelo.py`, `analise.py`, `app.py` e o PDF.
