'''
Arquivo que contém todas as ferramentas comuns a todos os domínios. 
Ou seja, são funções base para o correto funcionamento de ambos os scripts.

'''

from datetime import timedelta
import requests
import base64
import streamlit as st
from io import StringIO
import plotly.express as px
import pydeck as pdk
import pandas as pd
import pytz
import hmac 
import os
import numpy as np

# Função para configurar a autenticação por senha (para tidesat-barroso e tidesat-metsul)
def checar_senha(lang, chave):
    senha_certa = st.secrets["passwords"][chave]

    if st.session_state.get("senha_correta", False):
        return True

    def senha():
        if "senha" not in st.session_state:
            return

        if hmac.compare_digest(st.session_state["senha"], senha_certa):
            st.session_state["senha_correta"] = True
            del st.session_state["senha"]
        else:
            st.session_state["senha_correta"] = False

    _, col_senha, _ = st.columns([1, 1, 1])

    with col_senha:
        st.text_input("Senha de acesso", type="password", on_change=senha, key="senha")

        if "senha_correta" in st.session_state and not st.session_state["senha_correta"]:
            st.error(f"{lang['incorrect_password']}")

        return False
    
# Função para restaurar o estado (estação e período)
def restaurar_estado():
    if st.session_state.get("atualizar_tema", False):
        st.session_state["atualizar_tema"] = False  # Resetamos o flag para evitar loop infinito

        # Restaura a estação e o período salvos temporariamente
        if "estacao_selecionada_temp" in st.session_state:
            st.session_state["estacao_selecionada"] = st.session_state.pop("estacao_selecionada_temp")

        if "ultimo_periodo_temp" in st.session_state:
            st.session_state["ultimo_periodo"] = st.session_state.pop("ultimo_periodo_temp")     

# Função que configura o layout principal
def configurar_layout():

    ms = st.session_state

    if "temas" not in ms:
        ms.temas = {
            "tema_atual": "claro",  # força claro como inicial
            "atualizado": False,
            "claro": {
                "theme.base": "light",
                "theme.backgroundColor": "#ffffff",
                "theme.primaryColor": "#0065cc", 
                "theme.secondaryBackgroundColor": "#e1e4e8",
                "theme.textColor": "black",
                "icone_botoes": "Claro",
                "cor_linha": "#0065cc",
                "cor_texto": "#0061c3",
                "cor_mapa": "#0065cc"
            },
            "escuro": {
                "theme.base": "dark",
                "theme.backgroundColor": "#121212",
                "theme.primaryColor": "#87CEEB",
                "theme.secondaryBackgroundColor": "#262B36",
                "theme.textColor": "white",
                "icone_botoes": "Escuro",
                "cor_linha": "#87CEEB",
                "cor_texto": "#87CEEB",
                "cor_mapa": "#87CEEB"
            }
        }

    # Aplica o tema atual — claro ou escuro
    tema_atual = ms.temas["tema_atual"]
    for chave, valor in ms.temas[tema_atual].items():
        if chave.startswith("theme"):
            st._config.set_option(chave, valor)

    st.set_page_config(layout="wide", page_icon="logo_simbolo_aba.png",page_title="TideSat", initial_sidebar_state="collapsed")

    # CSS's para personalizar a fonte dos seletores
    st.markdown(
        """
        <style>
        /* Diminuir tamanho da fonte do seletor de estação */
        .stSelectbox > div[data-baseweb="select"] {
            font-size: 13px !important;
        }

        /* Diminuir tamanho da fonte do seletor de fuso horário */
        .stSelectbox > label {
            font-size: 13px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # CSS para personalizar e evitar a quebra de linhas nos botões
    st.markdown("""
        <style>
        /* Estilo para truncar texto no botão */
        button {
            white-space: nowrap;    /* Impede quebra de linha */
            overflow: hidden;       /* Oculta o texto que ultrapassa */
            text-overflow: ellipsis; /* Adiciona reticências (...) */
        }
        </style>
    """, unsafe_allow_html=True)

    # CSS para reduzir o espaçamento superior da página
    st.markdown("""
        <style>
        .block-container {
            padding-top: 0rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Ocultando menu e rodapé (via CSS)
    esconder = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stActionButton {display: none;}
        </style>
        """
    st.markdown(esconder, unsafe_allow_html=True)

# Função que coordena o seguinte: Se NÃO for o logo da TideSat, mostramos o "Powered by TideSat"
def configurar_poweredby(logotipo):

    if "portosrs" in logotipo.lower() or "metsul" in logotipo.lower() or "estrela" in logotipo.lower():

        tema = st.session_state["temas"]["tema_atual"]
        logo_tidesat = "TideSat_logo.png" if tema == "claro" else "TideSat_logo_escuro.png"

        imagem_base64 = converter_base64(logo_tidesat)
        extensao = logo_tidesat.split('.')[-1]

        _, col_cabecalho, _ = st.columns([1, 4, 1])

        with col_cabecalho:
            html = f"""
                <div style='display: flex; justify-content: center; align-items: center; gap: 8px;'>
                    <span style='font-size: 10px; font-style: italic; font-weight: bold; color: gray;'>POWERED BY</span>
                    <a href="https://www.tidesatglobal.com/" target="_blank">
                        <img src='data:image/{extensao};base64,{imagem_base64}' width='60'>
                    </a>
                </div>
            """
            st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

# Função para carregar os dados dos links
def carregar_dados(url):
        
        # Fazendo a requisição dos dados
        resposta = requests.get(url, verify=False, timeout=100)

        # Verifica se a requisição foi bem-sucedida
        if resposta.status_code != 200:
            st.markdown("<br>" * 2, unsafe_allow_html=True)
            st.warning("Erro ao acessar os dados da estação selecionada.")
            st.stop()

        # Carregando os dados no DataFrame
        dados_nivel = StringIO(resposta.text)
        df = pd.read_csv(dados_nivel, sep=',')

        # Verifica se o DataFrame está vazio
        if df.empty:
            st.markdown("<br>" * 2, unsafe_allow_html=True)
            st.warning("Erro ao carregar os dados da estação selecionada.")
            st.stop()

        # Renomeia as colunas conforme necessário
        df.rename(columns={
            '% year': 'year', ' month': 'month', ' day': 'day',
            ' hour': 'hour', ' minute': 'minute', ' second (GMT/UTC)': 'second',
            ' water level (meters)': 'water_level(m)'}, inplace=True)

        # Converte a data para o formato datetime
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

        # Adiciona a coluna de data UTC
        df['datetime_utc'] = df['datetime'].dt.tz_localize('UTC')

        return df

# Retorna uma cópia do DataFrame sem a última hora de dados (evitar o chicoteamento)
def corte_ultima_1h(df):

    limite = df['datetime_utc'].max() - pd.Timedelta(hours=1)
    return df[df['datetime_utc'] <= limite]

# Função do seletor de fuso
def fuso_horario(lang):

    # Lista de todos os fusos horários disponíveis
    fusos = pytz.all_timezones

    fuso_atual = st.session_state["fuso_selecionado"]

    _, col_fuso, _ = st.columns([0.3, 1, 0.3])

    with col_fuso:
        # Usando expander para esconder ou mostrar o seletor com fuso atual
        with st.expander(f"{lang['timezone']}: {fuso_atual}", expanded=False):
            
            # Seletor de fuso horário dentro do expander
            fuso_selecionado = st.selectbox(
                " ", 
                fusos, 
                index=fusos.index(fuso_atual),  # Mantém o índice correto
                label_visibility='collapsed', 
                key="fuso_selecionado"  # Vincula ao session_state
            )

    return fuso_selecionado

# Função para filtrar os dados pelo período selecionado
def filtrar_dados(df, dados_inicio, dados_fim, fuso_selecionado):

    # Convertendo dados_inicio e dados_fim para datetime no fuso selecionado
    dados_inicio_dt = pd.to_datetime(dados_inicio).tz_localize(fuso_selecionado)
    dados_fim_dt = pd.to_datetime(dados_fim).tz_localize(fuso_selecionado)

    # Obtendo o intervalo completo dos dados
    dados_inicio_total = df['datetime_ajustado'].min()
    dados_fim_total = df['datetime_ajustado'].max()

    # Verifica se o período solicitado é o mesmo que o intervalo completo
    if dados_inicio_dt == dados_inicio_total and dados_fim_dt == dados_fim_total:
        
        # Retorna o DataFrame original sem filtrar
        return df

    # Aplica o filtro nos dados
    filtro = (df['datetime_ajustado'] >= dados_inicio_dt) & (df['datetime_ajustado'] < dados_fim_dt + timedelta(days=1))

    return df.loc[filtro]

# Função para formatar o nível recente via mediana
def nivel_recente(df, fuso_selecionado, lang):

    # Limite de tempo para as últimas 4 horas
    limite_4h = df["datetime_utc"].max() - timedelta(hours=4)
    df_filtrado = df[df["datetime_utc"] >= limite_4h]

    if df_filtrado.empty or len(df_filtrado) < 2:
        st.stop()

    # Novo tempo zero: última observação real
    ultimo_registro = df_filtrado["datetime_utc"].max()

    # Delta em horas a partir do último dado observado
    df_filtrado["delta_horas"] = (df_filtrado["datetime_utc"] - ultimo_registro).dt.total_seconds() / 3600

    # Regressão
    x = df_filtrado["delta_horas"].values
    y = df_filtrado["water_level(m)"].values
    coef = np.polyfit(x, y, deg=1)

    # Estimar nível para o instante da última medição (x = 0)

    x0 = 0  # centrado na última observação
    nivel_recente_estimado = np.polyval(coef, x0)

    # Formata data/hora da última medição
    dh_ultima = ultimo_registro.tz_convert(fuso_selecionado)

    if lang["lang_code"] == "pt":

        nivel_formatado = f"{nivel_recente_estimado:.2f}&nbsp;m".replace('.', ',')
    else:
        nivel_formatado = f"{nivel_recente_estimado:.2f}&nbsp;m"


    if fuso_selecionado == "Canada/Atlantic":
        dh_ultima_formatada = dh_ultima.strftime('%Y-%m-%d | %I:%M %p')

    elif lang["lang_code"] == "en":
        dh_ultima_formatada = dh_ultima.strftime('%m/%d/%Y - %I:%M %p')
        
    else:
        dh_ultima_formatada = dh_ultima.strftime('%d/%m/%Y - %H:%M')

    return nivel_formatado, dh_ultima_formatada

# Função que calcula a velocidade de variação recente
def calcular_velocidade(df, lang):

    agora_utc = pd.Timestamp.utcnow()
    limite_12h = agora_utc - pd.Timedelta(hours=12)
    df_filtrado = df[df["datetime_utc"] >= limite_12h]

    if df_filtrado.empty or len(df_filtrado) < 2:
        return 0.0, "Indisp."

    df_filtrado["delta_horas"] = (df_filtrado["datetime_utc"] - agora_utc).dt.total_seconds() / 3600
    x = df_filtrado["delta_horas"].values
    y = df_filtrado["water_level(m)"].values
    coef = np.polyfit(x, y, deg=1)
    
    inclinacao = coef[0] * 100  # m/h para cm/h
    inclinacao_1casa = round(inclinacao, 1)

    if lang["lang_code"] == "pt":
        formatacao = f"{inclinacao_1casa:+.1f}&nbsp;cm/h".replace('.', ',')

    else:
        formatacao = f"{inclinacao_1casa:+.1f}&nbsp;cm/h"

    return inclinacao_1casa, formatacao

# Verifica o status de funcionamento da estação com base na última medição
def verificar_status_estacao(ultimo_registro_utc):

    limite_inatividade = pd.Timestamp.utcnow() - pd.Timedelta(hours=12)

    return "Ativa" if ultimo_registro_utc > limite_inatividade else "Inativa"

# Função para exibir as cotas notáveis nos filtros
def cotas_notaveis(estacao_nome, estacoes_info):

    # Recupera as cotas notáveis para a estação selecionada
    cotas = estacoes_info.get(estacao_nome, {})
    cota_alerta = cotas.get("cota_alerta")
    cota_inundacao = cotas.get("cota_inundacao")

    return cota_alerta, cota_inundacao

# Função para determinar a situação atual do nível da estação com base nas cotas
def situacao_nivel(nivel, cota_alerta, cota_inundacao):

    if cota_alerta in ("", " ", None) or cota_inundacao in ("", " ", None):

        return "—", "gray"
    
    elif nivel < cota_alerta:
        return "Normal", "green"
    
    elif cota_alerta <= nivel < cota_inundacao:
        return "Alerta", "orange"
    
    else:
        return "Inundação", "red"

# Função para converter a imagem para base64
def converter_base64(caminho_imagem):

    try:
        
        with open(caminho_imagem, "rb") as file:
            link = base64.b64encode(file.read()).decode()

        return link
        
    except Exception as e:

        print(f"Erro ao converter imagem: {e}")

        return None

# Função que configura a exibição do gráfico
def plotar_grafico(dados_finais, estacao_selecionada, cota_alerta, cota_inundacao, dados_inicio, dados_fim, lang):
    
    cor_linha, _, _, _, _ = obter_tema()

    if dados_finais is None or dados_finais.empty:
        st.write(f"Nenhum dado encontrado para o período selecionado na estação {estacao_selecionada}.")
        st.stop()

    # Criação do gráfico interativo
    fig = px.line(
        dados_finais,
        render_mode='svg',
        x='datetime_ajustado',
        y='water_level(m)',
        labels={'datetime_ajustado': "Data" if lang["lang_code"] == "pt" else "Date", 'water_level(m)': "Nível (m)" if lang["lang_code"] == "pt" else "Water level (m)"}
    )
    # Configurações dos eixos
    fig.update_xaxes(fixedrange=False)

    # Ajuste automático do eixo Y com base no período selecionado
    max_nivel = dados_finais['water_level(m)'].max()
    min_nivel = dados_finais['water_level(m)'].min()

    # Margem de segurança (melhora a visualização)
    margem = (max_nivel - min_nivel) * 0.1

    fig.update_yaxes(range=[min_nivel - margem, max_nivel + margem], fixedrange=True)

    # Define cor neutra para labels dos eixos com base no tema
    cor_labels = "white" if cor_linha == "#87CEEB" else "#1a1a1a"
    
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=dict(text=lang["yaxis_label"], font=dict(size=20, color=cor_labels)),
        font=dict(size=18, color=cor_labels),  # define cor padrão dos textos gerais (legenda, etc)
        height=430,
        margin=dict(l=40, r=0.1, t=40, b=40),
        legend=dict(
            orientation='v',
            yanchor='bottom',
            y=1.01,
            xanchor='left',
            x=0.04,
            font=dict(size=11, color=cor_labels),  # opcional: legenda também escura
        ),
        autosize=True,
    )

    fig.update_xaxes(
    color="#1a1a1a",
    linecolor="dimgray",
    gridcolor="lightgray",
    tickfont=dict(color=cor_labels)
    )
    fig.update_yaxes(
        color="#1a1a1a",
        linecolor="dimgray",
        gridcolor="lightgray",
        tickfont=dict(color=cor_labels)
    )
    
    duracao = dados_fim - dados_inicio

    fig.update_xaxes(
        ticks="outside",
        ticklabelmode="period",
        showgrid=True
    )

    # Define dtick baseado na duração
    if duracao <= pd.Timedelta(days=2):
        dtick_minor = 6 * 60 * 60 * 1000   # 6 horas

    elif duracao <= pd.Timedelta(days=7):
        dtick_minor = 12 * 60 * 60 * 1000  # 12 horas

    elif duracao <= pd.Timedelta(days=30):
        dtick_minor = 24 * 60 * 60 * 1000  # 1 dia
        
    elif duracao <= pd.Timedelta(days=180):
        dtick_minor = "M1"  # 1 mês

    else:
        dtick_minor = "M3"  # 3 meses

    # Aplica se definido
    fig.update_xaxes(minor=dict(
        dtick=dtick_minor,
        ticklen=4,
        tickcolor="gray"
    ))

    # Ajuste da cor da linha principal
    fig.update_traces(line=dict(color=cor_linha))

    # Adiciona a cota de inundação, se disponível
    if cota_inundacao not in (None, "", " "):
        fig.add_shape(
            type="line",
            xref="paper",  
            yref="y",
            x0=0,
            x1=1,
            y0=cota_inundacao,
            y1=cota_inundacao,
            line=dict(color="#FF0000", dash="dash"),
            name = "Cota de inundação" if lang["lang_code"] == "pt" else "Flood level",
            legendgroup="cota_inundacao", 
            showlegend=True  
        )

    # Adiciona a cota de alerta, se disponível
    if cota_alerta not in (None, "", " "):
        fig.add_shape(
            type="line",
            xref="paper",  
            yref="y",
            x0=0,
            x1=1,
            y0=cota_alerta,
            y1=cota_alerta,
            line=dict(color="#FFA500", dash="dash"),
            name="Cota de alerta" if lang["lang_code"] == "pt" else "Alert level",
            legendgroup="cota_alerta",  
            showlegend=True  
        )

    config = {
        "scrollZoom": True,
        "responsive": True,
        "displaylogo": False
    }
    
    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True, config=config)

# Função para obter as configurações do tema
def obter_tema():
    ms = st.session_state

    if "temas" not in ms:
        ms.temas = {
            "tema_atual": "claro",
            "atualizado": True,
            "claro": {
                "theme.base": "light",
                "theme.backgroundColor": "#ffffff",
                "theme.primaryColor": "#0065cc", 
                "theme.secondaryBackgroundColor": "#e1e4e8",
                "theme.textColor": "black",
                "icone_botoes": "Claro",
                "cor_linha": "#0065cc",
                "cor_texto": "#0061c3",
                "cor_mapa": "#0065cc"
            },
            "escuro": {
                "theme.base": "dark",
                "theme.backgroundColor": "#121212",
                "theme.primaryColor": "#87CEEB",
                "theme.secondaryBackgroundColor": "#262B36",
                "theme.textColor": "white",
                "icone_botoes": "Escuro",
                "cor_linha": "#87CEEB",
                "cor_texto": "#87CEEB",
                "cor_mapa": "#87CEEB"
            }
        }

        # Aplica visualmente o tema claro logo de cara
        for chave, valor in ms.temas["claro"].items():
            if chave.startswith("theme"):
                st._config.set_option(chave, valor)

    # Determina o tema atual
    tema_atual = ms.temas["tema_atual"]
    tema_cfg = ms.temas[tema_atual]

    cor_linha = tema_cfg["cor_linha"]
    cor_texto = tema_cfg["cor_texto"]
    cor_mapa = tema_cfg["cor_mapa"]

    cor_localizacao = "[0, 101, 204, 255]" if cor_mapa == ms.temas["claro"]["cor_mapa"] else "[135, 206, 235, 200]"

    return cor_linha, cor_texto, cor_mapa, cor_localizacao, ms

# Função para construir o layout
def main(estacoes_info, estacao_padrao, logotipo_claro, logotipo_escuro, html_logo, lang, timezone_padrao, tamanho_logo): 

    configurar_layout()

    # Define o fuso de acordo com o domínio acessado
    tz_padrao = timezone_padrao

    if "fuso_selecionado" not in st.session_state:
        st.session_state["fuso_selecionado"] = tz_padrao

    with st.container(border=True):

        _, col_filtros, _, col_grafico, _ = st.columns([0.1, 1.1, 0.1, 3, 0.1], gap="small", vertical_alignment="top")

        _, cor_texto, _, _, _ = obter_tema()

        with col_filtros:

            with st.container():

                col_img = st.columns([1])[0]

                with col_img:

                    tema_atual = st.session_state["temas"]["tema_atual"]

                    caminho_imagem = logotipo_claro if tema_atual == "claro" else logotipo_escuro

                    imagem_base64 = converter_base64(caminho_imagem)

                    html = f"""
                        <div style='text-align: center;'>
                            <a href={html_logo} target='_blank'>
                                <img src='data:image/webp;base64,{imagem_base64}' width= {tamanho_logo}>
                            </a>
                        </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                col_estacao = st.columns([1])[0]

                with col_estacao:

                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 14px; margin: 0;'>{lang['station']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    estacao_selecionada = st.selectbox(" ", list(estacoes_info.keys()), 
                                                    format_func=lambda code :estacoes_info[code]["descricao"],
                                                    index=list(estacoes_info.keys()).index(estacao_padrao),
                                                    label_visibility='collapsed')
                    
                    st.session_state["estacao_selecionada"] = estacao_selecionada

                    estacao_info = estacoes_info[estacao_selecionada]

                    url_estacao = estacao_info["url"]

                    dados = carregar_dados(url_estacao)
                    dados['datetime_ajustado'] = dados['datetime_utc'].dt.tz_convert(st.session_state["fuso_selecionado"])
                    
                    st.session_state["dados_estacao"] = dados
                    
                    dados_inicio = dados['datetime_ajustado'].min().date()
                    dados_fim = dados['datetime_ajustado'].max().date()

                    if pd.isna(dados_inicio) or pd.isna(dados_fim):
                        st.warning("A estação selecionada ainda não possui dados suficientes para exibição.")
                        st.stop()


                col_inicio, col_fim = st.columns(2, gap="small")
 
                if tz_padrao == "Canada/Atlantic":
                    formato_data = "YYYY/MM/DD"

                elif lang["lang_code"] == "pt":
                    formato_data = "DD/MM/YYYY"

                elif lang["lang_code"] == "en":
                    formato_data = "MM/DD/YYYY"

                else:
                    formato_data = "MM/DD/YYYY"

                with col_inicio:

                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 14px; margin: 0;'>{lang['initial_date']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.session_state["dados_inicio"] = st.date_input(" ", value=dados_inicio, format=formato_data, label_visibility='collapsed')

                with col_fim:

                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 14px; margin: 0;'>{lang['final_date']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.session_state["dados_fim"] = st.date_input(" ", value=dados_fim, format=formato_data, label_visibility='collapsed')

                with st.expander(f"{lang['quick_select']}", expanded=True):

                    col_inteiro, col_quinze = st.columns(2, gap="small")

                    with col_inteiro:
                        if st.button(f"{lang['full_period']}", use_container_width=True):
                            st.session_state["dados_inicio"] = dados['datetime_ajustado'].min().date()
                            st.session_state["dados_fim"] = dados['datetime_ajustado'].max().date()
                            st.session_state["ultimo_periodo"] = "inteiro"

                    with col_quinze:
                        if st.button(f"{lang['last_15_days']}", use_container_width=True):
                            st.session_state["dados_inicio"] = (dados['datetime_ajustado'].max() - timedelta(days=15)).date()
                            st.session_state["dados_fim"] = dados['datetime_ajustado'].max().date()
                            st.session_state["ultimo_periodo"] = "15d"                
                    
                    col_sete, col_24h = st.columns(2, gap="small")

                    with col_sete:
                        if st.button(f"{lang['last_7_days']}", use_container_width=True):
                            st.session_state["dados_inicio"] = (dados['datetime_ajustado'].max() - timedelta(days=7)).date()
                            st.session_state["dados_fim"] = dados['datetime_ajustado'].max().date()
                            st.session_state["ultimo_periodo"] = "7d"        

                    with col_24h:
                        if st.button(f"{lang['last_24_hours']}", use_container_width=True):
                            st.session_state["dados_inicio"] = (dados['datetime_ajustado'].max() - timedelta(hours=24)).date()
                            st.session_state["dados_fim"] = dados['datetime_ajustado'].max().date()
                            st.session_state["ultimo_periodo"] = "24h"
                            
                st.markdown("<br>", unsafe_allow_html=True)             

        with col_grafico:

            with st.container(border=False):
                    
                dados_filtrados = filtrar_dados(st.session_state["dados_estacao"], 
                                                    st.session_state["dados_inicio"],
                                                    st.session_state["dados_fim"], st.session_state["fuso_selecionado"])

                # Aplica o corte de 1h apenas para fins gráficos
                dados_finais = corte_ultima_1h(dados_filtrados)

                # Ajuste de cotas
                cota_alerta, cota_inundacao = cotas_notaveis(estacao_selecionada, estacoes_info)

                # Chamada do gráfico
                plotar_grafico(dados_finais, estacao_selecionada, cota_alerta, cota_inundacao, 
                                st.session_state["dados_inicio"], st.session_state["dados_fim"], lang)

                        
               
            st.markdown("<br>", unsafe_allow_html=True)

           # Seção com Situação do nível | Nível recente + atualização | Velocidade (em breve)
            col_operacao, col_situacao, col_nivel, col_velocidade = st.columns([1, 1, 1, 1])

            # Situação do nível
            cota_alerta, cota_inundacao = cotas_notaveis(estacao_selecionada, estacoes_info)

            df_nivel = carregar_dados(url_estacao)

            nivel_formatado, dh_ultima_formatada = nivel_recente(df_nivel, st.session_state["fuso_selecionado"], lang)

            velocidade_valor, velocidade_formatada = calcular_velocidade(df_nivel, lang)

            nivel_valor = float(nivel_formatado.replace(",", ".").replace("&nbsp;m", ""))

            situacao, cor_situacao = situacao_nivel(nivel_valor, cota_alerta, cota_inundacao)

            rotulo_situacao = {
                    "Normal": {"pt": "Normal", "en": "Normal level"},
                    "Alerta": {"pt": "Alerta", "en": "Alert"},
                    "Inundação": {"pt": "Inundação", "en": "Flood"},
                    "—": {"pt": "—", "en": "Unavailable"}
                }
            mensagem_situacao = rotulo_situacao[situacao][lang["lang_code"]]

            with col_operacao:

                    # Obtém o último dado da estação selecionada
                    ultimo_dado = dados["datetime_utc"].max()
                    status_estacao = verificar_status_estacao(ultimo_dado)

                    # Define cor visual do status
                    cor_status = "green" if status_estacao == "Ativa" else "red"

                    # Tradução para multilíngue
                    texto_status = "Operação:" if lang["lang_code"] == "pt" else "Station status:"
                    valor_status = status_estacao if lang["lang_code"] == "pt" else ("Active" if status_estacao == "Ativa" else "Inactive")

                    # Exibe o status
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 18px; margin: 0;'>
                                {texto_status}
                            <span style='font-weight: bold; color: {cor_status};'>{valor_status}</p>
                        </div>
                        """, unsafe_allow_html=True)

            with col_situacao:
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 18px; margin: 0;'>
                                Condição:
                                <span style='font-weight: bold; color: {cor_situacao};'>{mensagem_situacao}</p>
                        </div>
                    """, unsafe_allow_html=True)

            # Nível recente
            with col_nivel:

                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 18px; margin: 0;'>
                                {lang['recent_level']}:
                                <span style='font-weight: bold; color: {cor_texto};'>{nivel_formatado}</span>
                            </p>
                            <p style='font-size: 12px; margin: 0;'>Em {dh_ultima_formatada}</p>
                        </div>
                    """, unsafe_allow_html=True)

            # Velocidade futura
            cor_velocidade = "orange" if velocidade_valor > 0 else "green" if velocidade_valor < 0 else "grey"

            with col_velocidade:
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <p style='font-size: 18px; margin: 0;'>
                                Variação:
                                <span style='font-weight: bold; color: {cor_velocidade};'>{velocidade_formatada}</span>
                            </p>
                            <p style='font-size: 12px; margin: 0;'>Últimas 24h</p>
                        </div>
                    """, unsafe_allow_html=True)    
        
        st.markdown("<br>", unsafe_allow_html=True)  

    _, _, col_fuso, _, col_pow = st.columns([1, 0.1, 2, 0.1, 1], gap="small", vertical_alignment="top")

    
    with st.container():

        with col_fuso:

            fuso_horario(lang)

        with col_pow:

            # Mostra o "Powered by TideSat" só se for uma dashboard personalizada
            configurar_poweredby(caminho_imagem)



# ============================================================ FUNÇÕES DESATIVADAS (POR HORA) ============================================================

'''

# [TEMPORARIAMENTE DESATIVADA] Função para configurar a imagem da estação selecionada
def exibir_imagem_estacao(estacao):

    imagem = estacao.get("caminho_imagem")
    descricao_imagem = estacao.get("descricao_imagem")

    # Converte a imagem para base64
    img_estac_base64 = converter_base64(imagem)

    if img_estac_base64:
        expansivel_code = f"""
        <style>
            .img-expansivel {{
                transition: transform 0.2s ease-in-out;
                cursor: zoom-in;
                object-fit: contain;
                max-width: 100%;
                height: auto;
            }}
            .img-expansivel:active {{
                transform: scale(1.6);
                cursor: zoom-out;
            }}
        </style>
        <div style="display: flex; justify-content: center; align-items: center;">
            <img src='data:image/jpeg;base64,{img_estac_base64}' alt="{descricao_imagem}" 
                 title="{descricao_imagem}" class="img-expansivel">
        </div>
        """
        st.markdown(expansivel_code, unsafe_allow_html=True)
    else:
        st.warning("Imagem não disponível.")

# [TEMPORARIAMENTE DESATIVADA] Função para configurar o mapa da estação selecionada
def exibir_mapa_estacao(estacao):
    _, _, cor_mapa, cor_localizacao, _ = obter_tema()

    if estacao and "coord" in estacao:
        latitude = estacao["coord"][0]
        longitude = estacao["coord"][1]

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame([{"latitude": latitude, "longitude": longitude}]),
            get_position="[longitude, latitude]",
            get_radius=90,
            get_fill_color=cor_localizacao,
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=latitude,
            longitude=longitude,
            zoom=13.8,
            pitch=0
        )

        tooltip = {"html": f"<b>{estacao.get('descricao')}</b>", "style": {"color": cor_mapa}}

        deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)

        st.pydeck_chart(deck, use_container_width=True)   

# [TEMPORARIAMENTE DESATIVADA] Função para mudar o tema
def MudarTema():

    _, _, _, _, ms = obter_tema()

    # 1. Determina o novo tema
    tema_anterior = ms.temas["tema_atual"]
    novo_tema = "claro" if tema_anterior == "escuro" else "escuro"

    # 2. Atualiza o estado
    ms.temas["tema_atual"] = novo_tema
    ms.temas["atualizado"] = True

    # 3. Aplica o novo tema visualmente
    for chave, valor in ms.temas[novo_tema].items():
        if chave.startswith("theme"):
            st._config.set_option(chave, valor)

# [TEMPORARIAMENTE DESATIVADA] Função para o seletor de modo de visualização
def modo_visualizacao(lang):

    _, _, _, _, ms = obter_tema()

    # Determina o ícone do botão baseado no tema atual
    icone_id = (
        ms.temas["claro"]["icone_botoes"]
        if ms.temas["tema_atual"] == "claro"
        else ms.temas["escuro"]["icone_botoes"]
    )

    # Tradução dinâmica baseada no idioma
    if lang["lang_code"] == "pt":
        icone_botoes = icone_id  
    
    elif lang["lang_code"] == "en":
        icone_botoes = "Light" if icone_id == "Claro" else "Dark"
    
    else:
        icone_botoes = icone_id  # fallback

    _, col_visual, _ = st.columns([0.5, 1, 0.5])

    with col_visual:

        # Usando um expander para o seletor de modo de visualização

        with st.expander(f"{lang['theme']}: {icone_botoes}", expanded=False):

            # Botão para alternar o tema
            st.button(icone_botoes, on_click=MudarTema)

'''            