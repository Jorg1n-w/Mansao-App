import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração da Página
st.set_page_config(page_title="Mansão App")

# Inicialização do Session State para manter as sanfonas abertas e os Toasts
if 'grupo_aberto' not in st.session_state:
    st.session_state.grupo_aberto = None
if 'selecao_aberta' not in st.session_state:
    st.session_state.selecao_aberta = None
if 'grupo_aberto_repetidas' not in st.session_state:
    st.session_state.grupo_aberto_repetidas = None
if 'selecao_aberta_repetidas' not in st.session_state:
    st.session_state.selecao_aberta_repetidas = None

# OTIMIZAÇÃO 2: Dispara o feedback visual (Toast) que foi guardado antes do rerun
if 'toast_msg' in st.session_state:
    st.toast(st.session_state.toast_msg)
    del st.session_state.toast_msg

st.markdown("""
    <style>
        /* 1. Otimização do Layout do Streamlit para Celular */
        @media (max-width: 640px) {
            div[data-testid="stColumns"],
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 2% !important; 
            }
            div[data-testid="stColumn"],
            div[data-testid="column"] {
                width: 23.5% !important;
                flex: 0 0 23.5% !important;
                min-width: 23.5% !important;
                padding: 0 !important; 
                margin-bottom: 6px !important; 
            }
        }

        /* 2. Estilização Global dos Botões (Formato Figurinha) */
        div[data-testid="stColumns"] button {
            height: 45px !important; 
            padding: 0 !important; 
            margin: 0 !important; 
            border-radius: 6px !important; 
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            font-size: 14px !important; 
            font-weight: 600 !important; 
            letter-spacing: 0.5px !important; 
            transition: all 0.2s ease !important;
            width: 100% !important;
        }

        /* 3. Cores Customizadas */
        button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            border: 1.5px solid #444 !important; 
            color: #ccc !important;
        }
        
        button[data-testid="baseButton-primary"] {
            background-color: #ff4b4b !important; 
            border: 1.5px solid #ff4b4b !important;
            color: white !important;
        }
            
        .texto-lista {
            display: flex;
            align-items: center;
            height: 45px;
            font-size: 16px;
            font-weight: bold;
        }
        .numero-lista {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 45px;
            font-size: 18px;
            font-weight: bold;
            color: #ff4b4b; 
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CACHE DA CONEXÃO E DADOS
# ==========================================
@st.cache_resource
def inicializar_conexao():
    url = "https://pbgqppburbsifxikmgjy.supabase.co"
    key = "sb_publishable_3wX2yAg-4iPKxnujUa_TYA_fqk0SdCN"
    return create_client(url, key)

supabase = inicializar_conexao()

@st.cache_data
def carregar_dados():
    get = supabase.table('Figurinhas').select("*").execute()
    get_bandeiras = supabase.table('Bandeiras').select("*").execute()
    
    df_figurinhas = pd.DataFrame(get.data)
    df_bandeiras = pd.DataFrame(get_bandeiras.data)
    
    if not df_figurinhas.empty:
        df_figurinhas = df_figurinhas.sort_values(by='IdFigurinha')
        
    return df_figurinhas, df_bandeiras

# PASSO MÁGICO: Salvamos o banco de dados na memória contínua do Streamlit (RAM)
if 'df_figurinhas' not in st.session_state or 'df_bandeiras' not in st.session_state:
    df_f, df_b = carregar_dados()
    st.session_state.df_figurinhas = df_f.copy()
    st.session_state.df_bandeiras = df_b.copy()

# A partir de agora, o app lê sempre da RAM local (Instantâneo)
df = st.session_state.df_figurinhas
df_band = st.session_state.df_bandeiras

if not df.empty:
    total_figurinhas = len(df)
    total_obtidas = df['Obtido'].sum()
    obtidas_pct = round((total_obtidas/total_figurinhas)*100) if total_figurinhas > 0 else 0

    st.title(f"Mansão das Figurinhas")
    st.subheader(f"Progresso: {obtidas_pct}% ({total_obtidas}/{total_figurinhas})")
    st.write("Completar o albúm é nossa única meta")

    aba_album, aba_repetidas = st.tabs(["📒 Álbum", "🔁 Repetidas"])

    # ==========================================
    # 2. FUNÇÕES DE TEXTO OTIMIZADAS
    # ==========================================
    def gerar_texto_lista(dataframe, tipo, df_band_ref):
        if tipo == "obtidas":
            df_filtro = dataframe[dataframe['Obtido'] == True]
            titulo = "*Figurinhas Obtidas* \n\n"
        else:
            df_filtro = dataframe[dataframe['Obtido'] == False]
            titulo = "*Figurinhas Faltantes* \n\n"

        texto_final = titulo
        grupos = df_filtro['Grupo'].unique()

        for grupo in grupos:
            texto_final += f"*{str(grupo).upper()}*\n" if "GRUPO" in str(grupo).upper() else f"*GRUPO {str(grupo).upper()}*\n"

            df_grupo = df_filtro[df_filtro['Grupo'] == grupo]
            selecoes = df_grupo['Selecao'].unique()

            for selecao in selecoes:
                df_selecao = df_grupo[df_grupo['Selecao'] == selecao]
                
                try:
                    bandeira = df_band_ref.loc[df_band_ref['Nome'] == selecao, 'Bandeira'].values[0]
                except IndexError:
                    bandeira = "🏳️"

                numeros_lista = df_selecao['Cod_Figurinha'].sort_values().astype(str).tolist()
                numeros_formatados = ", ".join(numeros_lista)

                texto_final += f"{bandeira} {selecao}: {numeros_formatados}\n"
            texto_final += "\n"
            
        return texto_final.strip()

    def gera_texto_repetidas(df_ref, df_band_ref):
        texto_final = "*Figurinhas Repetidas* \n\n"
        df_repeat = df_ref[(df_ref['Obtido'] == True) & (df_ref['QTD'] > 0)]
        grupos = df_repeat['Grupo'].unique()

        for grupo in grupos:
            texto_final += f"*{str(grupo).upper()}*\n" if "GRUPO" in str(grupo).upper() else f"*GRUPO {str(grupo).upper()}*\n"

            df_grupo = df_repeat[df_repeat['Grupo'] == grupo]
            selecoes = df_grupo['Selecao'].unique()

            for selecao in selecoes:
                df_selecao = df_grupo[df_grupo['Selecao'] == selecao]
                
                try:
                    bandeira = df_band_ref.loc[df_band_ref['Nome'] == selecao, 'Bandeira'].values[0]
                except IndexError:
                    bandeira = "🏳️"
                
                figurinhas_repeat = df_selecao['Cod_Figurinha'].unique()
                texto_final += f"{bandeira} {selecao}:\n"

                for figurinha in figurinhas_repeat:
                    cod_figurinha = df_selecao.loc[df_selecao['Cod_Figurinha'] == figurinha, 'Cod_Figurinha'].values[0]
                    qtd_figurinha = df_selecao.loc[df_selecao['Cod_Figurinha'] == figurinha, 'QTD'].sum()
                    texto_final += f"- {cod_figurinha} (x{qtd_figurinha})\n"
            texto_final += "\n"
            
        return texto_final.strip()

    # ==========================================
    # ABA 1: ÁLBUM PRINCIPAL
    # ==========================================
    with aba_album:
        # OTIMIZAÇÃO 1: Modo Foco (Ocultar Obtidas)
        mostrar_apenas_faltantes = st.toggle("👀 Ocultar figurinhas já obtidas")
        item_pesquisa = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo:", key="pesquisa_album", placeholder="Ex: KSA01, MEX19")
        
        df_filtrado_album = df.copy()

        # Aplica o filtro de foco se o botão estiver ativado
        if mostrar_apenas_faltantes:
            df_filtrado_album = df_filtrado_album[df_filtrado_album['Obtido'] == False]

        if item_pesquisa:
            df_filtrado_album = df_filtrado_album[
                df_filtrado_album['Grupo'].str.contains(item_pesquisa, case=False, na=False) |
                df_filtrado_album['Selecao'].str.contains(item_pesquisa, case=False, na=False) |
                df_filtrado_album['Cod_Figurinha'].str.contains(item_pesquisa, case=False, na=False)
            ]

        if not df_filtrado_album.empty:
            distinct_grupos = df_filtrado_album['Grupo'].unique()

            for grupo in distinct_grupos:
                manter_aberto_grupo = (st.session_state.grupo_aberto == grupo)
                obtido_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].sum()
                total_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].count()
                pct_grupo = round((obtido_grupo/total_grupo)*100) if total_grupo > 0 else 0

                with st.expander(f'⚽ Grupo {grupo} | {pct_grupo}% ({obtido_grupo}/{total_grupo})', expanded=manter_aberto_grupo):
                    selecoes_grupo = df_filtrado_album[df_filtrado_album['Grupo'] == grupo]['Selecao'].unique()

                    for selecao in selecoes_grupo:
                        manter_aberto_selecao = (st.session_state.selecao_aberta == selecao)
                        obtido_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].sum()
                        total_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].count()
                        
                        try:
                            bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].values[0]
                        except IndexError:
                            bandeira = "🏳️"
                            
                        pct_selecao = round((obtido_selecao/total_selecao)*100) if total_selecao > 0 else 0

                        with st.expander(f'{bandeira} {selecao} | {pct_selecao}% ({obtido_selecao}/{total_selecao})', expanded=manter_aberto_selecao):
                            
                            # OTIMIZAÇÃO 3: Barra de Progresso visual por seleção
                            st.progress(obtido_selecao / total_selecao if total_selecao > 0 else 0)
                            
                            figurinhas_selecao = df_filtrado_album[(df_filtrado_album['Grupo'] == grupo) & (df_filtrado_album['Selecao'] == selecao)]
                            colunas = st.columns(4)

                            for i, (index, linha) in enumerate(figurinhas_selecao.iterrows()):
                                id_fig = linha['IdFigurinha']
                                status = linha['Obtido']
                                figurinha = linha['Cod_Figurinha']

                                cor = 'primary' if status else 'secondary'
                                icone = '✅' if status else ''
                                col_atual = i % 4

                                with colunas[col_atual]:
                                    clicou = st.button(
                                        label=f"{figurinha}{icone}",
                                        key=f"btn_{id_fig}",
                                        type=cor,
                                        use_container_width=True
                                    )

                                    if clicou:
                                        novo_status = not status
                                        
                                        # 1. Atualização Otimista na Memória RAM
                                        st.session_state.df_figurinhas.loc[st.session_state.df_figurinhas['IdFigurinha'] == id_fig, 'Obtido'] = novo_status
                                        
                                        # 2. Envio rápido para o Supabase sem baixar de novo
                                        supabase.table('Figurinhas').update({'Obtido': novo_status}).eq('IdFigurinha', id_fig).execute()
                                        
                                        if novo_status:
                                            st.session_state.toast_msg = f"🎉 {figurinha} adicionada ao álbum!"
                                        else:
                                            st.session_state.toast_msg = f"🗑️ {figurinha} removida do álbum."
                                        
                                        st.session_state.grupo_aberto = grupo
                                        st.session_state.selecao_aberta = selecao
                                        st.rerun()
            
            with st.expander("📱 Exportar Obtidas para WhatsApp"):
                texto_zap_obtidas = gerar_texto_lista(df, "obtidas", df_band)
                if texto_zap_obtidas:
                    st.text_area("Copie o texto abaixo:", value=texto_zap_obtidas, height=200, key="txt_obtidas")
            
            with st.expander("📱 Exportar Faltantes para WhatsApp"):
                texto_zap_nobtidas = gerar_texto_lista(df, "faltantes", df_band)
                if texto_zap_nobtidas:
                    st.text_area("Copie o texto abaixo:", value=texto_zap_nobtidas, height=200, key="txt_faltantes")
        else:
            st.info("Nenhuma figurinha encontrada.")

    # ==========================================
    # ABA 2: REPETIDAS
    # ==========================================
    with aba_repetidas:
        item_pesquisa_REP = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo:", key="pesquisa_rep", placeholder="Ex: KSA01, MEX19")
        df_filtrado_rep = df[df['Obtido'] == True]

        if item_pesquisa_REP:
            df_filtrado_rep = df_filtrado_rep[
                df_filtrado_rep['Grupo'].str.contains(item_pesquisa_REP, case=False, na=False) |
                df_filtrado_rep['Selecao'].str.contains(item_pesquisa_REP, case=False, na=False) |
                df_filtrado_rep['Cod_Figurinha'].str.contains(item_pesquisa_REP, case=False, na=False)
            ]

        if not df_filtrado_rep.empty:
            distinct_grupos_rep = df_filtrado_rep['Grupo'].unique()

            for grupo in distinct_grupos_rep:
                manter_aberto_grupo_repetidas = (st.session_state.grupo_aberto_repetidas == grupo)
                total_repetidas_grupo = df.loc[df['Grupo'] == grupo, 'QTD'].sum()

                with st.expander(f"⚽ Grupo {grupo} | {total_repetidas_grupo} repetidas", expanded=manter_aberto_grupo_repetidas):
                    selecoes_grupo_rep = df_filtrado_rep[df_filtrado_rep['Grupo'] == grupo]['Selecao'].unique()

                    for selecao in selecoes_grupo_rep:
                        manter_aberto_selecao_rep = (st.session_state.selecao_aberta_repetidas == selecao)
                        total_rep_selecao = df.loc[df['Selecao'] == selecao, 'QTD'].sum()
                        
                        try:
                            bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].values[0]
                        except IndexError:
                            bandeira = "🏳️"

                        with st.expander(f'{bandeira} {selecao} | {total_rep_selecao} Repetidas', expanded=manter_aberto_selecao_rep):
                            
                            figurinhas_selecao = df_filtrado_rep[(df_filtrado_rep['Grupo'] == grupo) & (df_filtrado_rep['Selecao'] == selecao)]

                            for index, linha in figurinhas_selecao.iterrows():
                                id_fig = linha['IdFigurinha']
                                figurinha = linha['Cod_Figurinha']
                                qtd_repetidas = int(linha['QTD']) if pd.notna(linha['QTD']) else 0

                                col_texto, col_menos, col_qtd, col_mais = st.columns([4, 1, 1, 1])

                                with col_texto:
                                    st.markdown(f"<div class='texto-lista'>{figurinha}</div>", unsafe_allow_html=True)
                                
                                with col_menos:
                                    if st.button("➖", key=f"menos_{id_fig}", type="secondary", use_container_width=True):
                                        if qtd_repetidas > 0: 
                                            nova_qtd = qtd_repetidas - 1
                                            
                                            # Atualização Otimista local
                                            st.session_state.df_figurinhas.loc[st.session_state.df_figurinhas['IdFigurinha'] == id_fig, 'QTD'] = nova_qtd
                                            
                                            # Envia para o Supabase
                                            supabase.table('Figurinhas').update({'QTD': nova_qtd}).eq('IdFigurinha', id_fig).execute()
                                            
                                            st.session_state.toast_msg = f"➖ Uma repetida de {figurinha} removida."
                                            st.session_state.grupo_aberto_repetidas = grupo
                                            st.session_state.selecao_aberta_repetidas = selecao
                                            st.rerun()

                                with col_qtd:
                                    st.markdown(f"<div class='numero-lista'>{qtd_repetidas}</div>", unsafe_allow_html=True)
                                
                                with col_mais:
                                    if st.button("➕", key=f"mais_{id_fig}", type="primary", use_container_width=True):
                                        nova_qtd = qtd_repetidas + 1
                                        
                                        # Atualização Otimista local
                                        st.session_state.df_figurinhas.loc[st.session_state.df_figurinhas['IdFigurinha'] == id_fig, 'QTD'] = nova_qtd
                                        
                                        # Envia para o Supabase
                                        supabase.table('Figurinhas').update({'QTD': nova_qtd}).eq('IdFigurinha', id_fig).execute()
                                        
                                        st.session_state.toast_msg = f"➕ Uma repetida de {figurinha} adicionada!"
                                        st.session_state.grupo_aberto_repetidas = grupo
                                        st.session_state.selecao_aberta_repetidas = selecao
                                        st.rerun()
                                        
                                st.markdown("<hr style='margin: 4px 0px; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

            with st.expander("📱 Exportar Repetidas para WhatsApp"):
                texto_zap_rep = gera_texto_repetidas(df, df_band)
                if texto_zap_rep:
                    st.text_area("Copie o texto abaixo:", value=texto_zap_rep, height=200, key="txt_repetidas")
        else:
            st.info("Nenhuma figurinha obtida encontrada para gerir as repetidas.")
else:
    st.info("Deu ruim fml! O banco de dados está vazio.")