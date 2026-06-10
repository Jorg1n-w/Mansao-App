import streamlit as st
import pandas as pd
from supabase import create_client, Client
import threading

# Configuração da Página
st.set_page_config(page_title="Mansão App")

if 'grupo_aberto' not in st.session_state:
    st.session_state.grupo_aberto = None
    
if 'selecao_aberta' not in st.session_state:
    st.session_state.selecao_aberta = None

if 'grupo_aberto_repetidas' not in st.session_state:
    st.session_state.grupo_aberto_repetidas = None
    
if 'selecao_aberta_repetidas' not in st.session_state:
    st.session_state.selecao_aberta_repetidas = None

st.markdown("""
    <style>
        /* 1. Otimização do Layout do Streamlit para Celular */
        @media (max-width: 640px) {
            /* Força as colunas a ficarem lado a lado (Grid de 4) */
            div[data-testid="stColumns"],
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 2% !important; /* Espaço mínimo entre as colunas */
            }
            
            /* Define que cada coluna ocupa 23.5% (cabem 4 na tela) */
            div[data-testid="stColumn"],
            div[data-testid="column"] {
                width: 23.5% !important;
                flex: 0 0 23.5% !important;
                min-width: 23.5% !important;
                padding: 0 !important; /* Remove o padding da coluna */
                margin-bottom: 6px !important; /* Distância para a linha de baixo */
            }
        }

        /* 2. Estilização Global dos Botões (Formato Figurinha) */
        /* Alvo: Botões que estão dentro das colunas */
        div[data-testid="stColumns"] button {
            height: 45px !important; /* Força uma altura quadrada padrão */
            padding: 0 !important; /* Remove o respiro interno do botão */
            margin: 0 !important; 
            border-radius: 6px !important; /* Bordas levemente arredondadas */
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            font-size: 14px !important; /* Tamanho da fonte mais legível */
            font-weight: 600 !important; /* Texto em negrito */
            letter-spacing: 0.5px !important; /* Espaçamento entre as letras */
            transition: all 0.2s ease !important;
            width: 100% !important;
        }

        /* 3. Cores Customizadas (Opcional, para deixar mais bonito) */
        /* Botão Faltante (Secundário) */
        button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            border: 1.5px solid #444 !important; /* Borda cinza escura */
            color: #ccc !important;
        }
        
        /* Botão Obtido (Primário) */
        button[data-testid="baseButton-primary"] {
            background-color: #ff4b4b !important; /* Vermelho Streamlit / Copa */
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
            color: #ff4b4b; /* Vermelho para destacar a quantidade */
        }
    </style>
""", unsafe_allow_html=True)

# Conecta supabase
url = "https://pbgqppburbsifxikmgjy.supabase.co"
key = "sb_publishable_3wX2yAg-4iPKxnujUa_TYA_fqk0SdCN"
supabase: Client = create_client(url, key)

# ==========================================
# FUNÇÃO DE SEGUNDO PLANO (ZERO DELAY)
# ==========================================
def atualizar_banco_bg(id_fig, coluna, novo_valor):
    try:
        supabase.table('Figurinhas').update({coluna: novo_valor}).eq('IdFigurinha', id_fig).execute()
    except Exception:
        pass # Ignora erros de rede em silêncio para nunca travar o app

# Popula df com dados do supabase
@st.cache_data
def carregar_dados_iniciais():
    get = supabase.table('Figurinhas').select("*").execute()
    get_bandeiras = supabase.table('Bandeiras').select("*").execute()
    df_figurinhas = pd.DataFrame(get.data)
    df_bandeiras = pd.DataFrame(get_bandeiras.data)
    if not df_figurinhas.empty:
        df_figurinhas = df_figurinhas.sort_values(by='IdFigurinha')
    return df_figurinhas, df_bandeiras

if 'df_figurinhas' not in st.session_state or 'df_bandeiras' not in st.session_state:
    df_f, df_b = carregar_dados_iniciais()
    st.session_state.df_figurinhas = df_f.copy()
    st.session_state.df_bandeiras = df_b.copy()

df = st.session_state.df_figurinhas
df_band = st.session_state.df_bandeiras

if not df.empty:

    total_figurinhas = len(df)
    total_obtidas = df['Obtido'].sum()
    # Proteção caso o banco venha zerado para não dar erro de divisão por zero
    obtidas_pct = round((total_obtidas/total_figurinhas)*100) if total_figurinhas > 0 else 0

    st.title(f"Mansão das Figurinhas")
    st.subheader(f"Progresso: {obtidas_pct}% ({total_obtidas}/{total_figurinhas})")
    st.write("Completar o albúm é nossa única meta")

    aba_album, aba_repetidas = st.tabs(["📒 Álbum", "🔁 Repetidas"])

    def gera_texto_obtidas(df):
        texto_final = "*Figurinhas Obtidas* \n\n"

        df_obtido = df[df['Obtido'] == True]

        grupo_obtido = df_obtido['Grupo'].unique()

        for grupo in grupo_obtido:

            texto_final += f"*GRUPO {grupo.upper()}*\n"

            df_grupo = df_obtido[df_obtido['Grupo'] == grupo]
            selecoes_obtido = df_grupo['Selecao'].unique()

            for selecao in selecoes_obtido:

                df_selecao = df_grupo[df_grupo['Selecao'] == selecao]
                bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].item()

                numeros_lista = df_selecao['Cod_Figurinha'].sort_values().astype(str).tolist()
                numeros_formatados = ", ".join(numeros_lista)

                texto_final += f"{bandeira} {selecao}:\n {numeros_formatados}\n"

            texto_final += "\n"
            
        return texto_final.strip()
    
    def gera_texto_nobtidas(df):
        texto_final = "*Figurinhas Não Obtidas* \n\n"

        df_nobtido = df[df['Obtido'] == False]

        grupo_nobtido = df_nobtido['Grupo'].unique()

        for grupo in grupo_nobtido:

            texto_final += f"*GRUPO {grupo.upper()}*\n"

            df_grupo = df_nobtido[df_nobtido['Grupo'] == grupo]
            selecoes_nobtido = df_grupo['Selecao'].unique()

            for selecao in selecoes_nobtido:

                df_selecao = df_grupo[df_grupo['Selecao'] == selecao]
                bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].item()

                numeros_lista = df_selecao['Cod_Figurinha'].sort_values().astype(str).tolist()
                numeros_formatados = ", ".join(numeros_lista)

                texto_final += f"{bandeira} {selecao}:\n {numeros_formatados}\n"

            texto_final += "\n"
            
        return texto_final.strip()

    def gera_texto_repetidas(df):
        texto_final = "*Figurinhas Repetidas* \n\n"

        df_repeat = df[(df['Obtido'] == True) & (df['QTD'] > 0)]

        grupo_repeat = df_repeat['Grupo'].unique()

        for grupo in grupo_repeat:

            texto_final += f"*GRUPO {grupo.upper()}*\n"

            df_grupo = df_repeat[df_repeat['Grupo'] == grupo]
            selecoes_repeat = df_grupo['Selecao'].unique()

            for selecao in selecoes_repeat:

                df_selecao = df_grupo[df_grupo['Selecao'] == selecao]
                bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].item()
                figurinhas_repeat = df_selecao['Cod_Figurinha'].unique()

                texto_final += f"{bandeira} {selecao}:\n"

                for figurinha in figurinhas_repeat:

                    cod_figurinha = df_selecao.loc[df_selecao['Cod_Figurinha'] == figurinha, 'Cod_Figurinha'].item()
                    qtd_figurinha = df_selecao.loc[df_selecao['Cod_Figurinha'] == figurinha, 'QTD'].sum()

                    texto_final += f"- {cod_figurinha}: {qtd_figurinha}\n"

                

            texto_final += "\n"
            
        return texto_final.strip()

    with aba_album:
        
        item_pesquisa = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo: (figurinhas devem ser pesquisadas pelo código. Ex: KSA01, MEX19. Apague e aperte enter para limpar.)")
        df_filtrado = df.copy()

        if item_pesquisa:
            df_filtrado = df_filtrado[
                df_filtrado['Grupo'].str.contains(item_pesquisa, case=False, na=False) |
                df_filtrado['Selecao'].str.contains(item_pesquisa, case=False, na=False) |
                df_filtrado['Cod_Figurinha'].str.contains(item_pesquisa, case=False, na=False)
            ]

        df_album = df_filtrado

        if not df_album.empty:
            distinct_grupos = df_album['Grupo'].unique()

            # Sanfona 1 (Grupos)
            for grupo in distinct_grupos:
                manter_aberto_grupo = (st.session_state.grupo_aberto == grupo)
                obtido_grupo = df_album.loc[df_album['Grupo'] == grupo, 'Obtido'].sum()
                total_grupo = df_album.loc[df_album['Grupo'] == grupo, 'Obtido'].count()
                pct_grupo = round((obtido_grupo/total_grupo)*100) if total_grupo > 0 else 0

                with st.expander(f'⚽ Grupo {grupo} | {pct_grupo}% ({obtido_grupo}/{total_grupo})', expanded=manter_aberto_grupo):
                    selecoes_grupo = df_album[df_album['Grupo'] == grupo]['Selecao'].unique()

                    # Sanfona 2 (Seleções)
                    for selecao in selecoes_grupo:
                        manter_aberto_selecao = (st.session_state.selecao_aberta == selecao)
                        obtido_selecao = df_album.loc[df_album['Selecao'] == selecao, 'Obtido'].sum()
                        total_selecao = df_album.loc[df_album['Selecao'] == selecao, 'Obtido'].count()
                        bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].item()
                        pct_selecao = round((obtido_selecao/total_selecao)*100) if total_selecao > 0 else 0

                        with st.expander(f'{bandeira} {selecao} | {pct_selecao}% ({obtido_selecao}/{total_selecao})', expanded=manter_aberto_selecao):
                            
                            figurinhas_selecao = df_album[(df_album['Grupo'] == grupo) & (df_album['Selecao'] == selecao)]
                            figurinhas_selecao = figurinhas_selecao.sort_values(by='IdFigurinha')

                            colunas = st.columns(4)

                            # Usamos o 'enumerate' para garantir que os botões comecem sempre na primeira coluna (0)
                            for i, (index, linha) in enumerate(figurinhas_selecao.iterrows()):
                                id_fig = linha['IdFigurinha']
                                num_fig = linha['Num_Figurinha']
                                status = linha['Obtido']
                                figurinha = linha['Cod_Figurinha']

                                cor = 'primary' if status else 'secondary'
                                icone = '✅' if status else ''
                                
                                # 'i' vai ser 0, 1, 2, 3, 4... garantindo a ordem perfeita da grade
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
                                        
                                        st.session_state.df_figurinhas.loc[st.session_state.df_figurinhas['IdFigurinha'] == id_fig, 'Obtido'] = novo_status
                                        
                                        threading.Thread(target=atualizar_banco_bg, args=(id_fig, 'Obtido', novo_status)).start()

                                        st.session_state.grupo_aberto = grupo
                                        st.session_state.selecao_aberta = selecao
                                        st.rerun()
            
            with st.expander("📱 Exportar Obtidas para WhatsApp"):
                st.write("Clique no botão de copiar no canto superior direito do quadro abaixo:")
                
                
                texto_zap = gera_texto_obtidas(df)
                
                if texto_zap:
                    st.code(texto_zap, language="text")
                else:
                    st.success("-")
            
            with st.expander("📱 Exportar Não Obtidas para WhatsApp"):
                st.write("Clique no botão de copiar no canto superior direito do quadro abaixo:")
                
                texto_zap = gera_texto_nobtidas(df)
                
                if texto_zap:
                    st.code(texto_zap, language="text")
                else:
                    st.success("-")

        else:
            st.info("Nenhuma figurinha encontrada para a busca atual.")


    with aba_repetidas:
        item_pesquisa_REP = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo:  (figurinhas devem ser pesquisadas pelo código. Ex: KSA01, MEX19. Apague e aperte enter para limpar.)")
        df_filtrado_rep = df[df['Obtido'] == True]

        if item_pesquisa_REP:
            df_filtrado_rep = df_filtrado_rep[
                df_filtrado_rep['Grupo'].str.contains(item_pesquisa_REP, case=False, na=False) |
                df_filtrado_rep['Selecao'].str.contains(item_pesquisa_REP, case=False, na=False) |
                df_filtrado_rep['Cod_Figurinha'].str.contains(item_pesquisa_REP, case=False, na=False)
            ]

        if not df_filtrado_rep.empty:
            distinct_grupos = df_filtrado_rep['Grupo'].unique()

            for grupo in distinct_grupos:
                manter_aberto_grupo_repetidas = (st.session_state.grupo_aberto_repetidas == grupo)

                total_repetidas_grupo = df_filtrado_rep.loc[df_filtrado_rep['Grupo'] == grupo, 'QTD'].sum()

                with st.expander(f"⚽ Grupo {grupo} | {total_repetidas_grupo} repetidas", expanded=manter_aberto_grupo_repetidas):
                    selecoes_grupo = df_filtrado_rep[df_filtrado_rep['Grupo'] == grupo]['Selecao'].unique()

                    for selecao in selecoes_grupo:
                        manter_aberto_selecao_rep = (st.session_state.selecao_aberta_repetidas == selecao)
                        total_rep_selecao = df_filtrado_rep.loc[df_filtrado_rep['Selecao'] == selecao, 'QTD'].sum()
                        bandeira = df_band.loc[df_band['Nome'] == selecao, 'Bandeira'].item()

                        with st.expander(f'{bandeira} {selecao} | {total_rep_selecao} Repetidas', expanded=manter_aberto_selecao_rep):
                            
                            figurinhas_selecao = df_filtrado_rep[(df_filtrado_rep['Grupo'] == grupo) & (df_filtrado_rep['Selecao'] == selecao)]
                            figurinhas_selecao = figurinhas_selecao.sort_values(by='IdFigurinha')

                            for index, linha in figurinhas_selecao.iterrows():
                                id_fig = linha['IdFigurinha']
                                figurinha = linha['Cod_Figurinha']

                                qtd_repetidas = int(linha['QTD']) if pd.notna(linha['QTD']) else 0

                                #espaço das colunas na tela
                                col_texto, col_menos, col_qtd, col_mais = st.columns([4, 1, 1, 1])

                                with col_texto:
                                    st.markdown(f"<div class='texto-lista'>{figurinha}</div>", unsafe_allow_html=True)
                                
                                with col_menos:
                                    if st.button("➖", key=f"menos_{id_fig}", type="secondary", use_container_width=True):
                                        if qtd_repetidas > 0: # Impede o número de ficar negativo
                                            nova_qtd = qtd_repetidas - 1
                                            st.session_state.df_figurinhas.loc[st.session_state.df_figurinhas['IdFigurinha'] == id_fig, 'QTD'] = nova_qtd
                                            
                                            threading.Thread(target=atualizar_banco_bg, args=(id_fig, 'QTD', nova_qtd)).start()
                                            
                                            st.session_state.grupo_aberto_repetidas = grupo
                                            st.session_state.selecao_aberta_repetidas = selecao
                                            st.rerun()

                                with col_qtd:
                                    st.markdown(f"<div class='numero-lista'>{qtd_repetidas}</div>", unsafe_allow_html=True)
                                
                                with col_mais:
                                    if st.button("➕", key=f"mais_{id_fig}", type="primary", use_container_width=True):
                                        nova_qtd = qtd_repetidas + 1
                                        st.session_state.df_figurinhas.loc[st.session_state.df_figurinhas['IdFigurinha'] == id_fig, 'QTD'] = nova_qtd
                                        
                                        threading.Thread(target=atualizar_banco_bg, args=(id_fig, 'QTD', nova_qtd)).start()
                                        
                                        st.session_state.grupo_aberto_repetidas = grupo
                                        st.session_state.selecao_aberta_repetidas = selecao
                                        st.rerun()
                                        
                                # Cria uma linha divisória quase invisível entre as figurinhas
                                st.markdown("<hr style='margin: 4px 0px; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

            with st.expander("📱 Exportar Repetidas para WhatsApp"):
                st.write("Clique no botão de copiar no canto superior direito do quadro abaixo:")
                
                texto_zap = gera_texto_repetidas(df)
                
                if texto_zap:
                    st.code(texto_zap, language="text")
                else:
                    st.success("-")

else:
    st.info("Deu ruim fml! O banco de dados está vazio.")