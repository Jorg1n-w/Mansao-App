import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração da Página
st.set_page_config(page_title="Mansão App")

if 'grupo_aberto' not in st.session_state:
    st.session_state.grupo_aberto = None
    
if 'selecao_aberta' not in st.session_state:
    st.session_state.selecao_aberta = None

# CSS HACK PARA A GRADE NO CELULAR
st.markdown("""
    <style>
        @media (max-width: 640px) {
            div[data-testid="stColumns"],
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: wrap !important;
            }
            div[data-testid="stColumn"],
            div[data-testid="column"] {
                width: 25% !important;
                flex: 0 0 25% !important;
                min-width: 25% !important;
                padding: 0 2px !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# Conecta supabase
url = "https://pbgqppburbsifxikmgjy.supabase.co"
key = "sb_publishable_3wX2yAg-4iPKxnujUa_TYA_fqk0SdCN"
supabase: Client = create_client(url, key)

# Popula df com dados do supabase
get = supabase.table('Figurinhas').select("*").execute()
df = pd.DataFrame(get.data)

if not df.empty:
    df = df.sort_values(by='IdFigurinha')

    total_figurinhas = len(df)
    total_obtidas = df['Obtido'].sum()
    # Proteção caso o banco venha zerado para não dar erro de divisão por zero
    obtidas_pct = round((total_obtidas/total_figurinhas)*100) if total_figurinhas > 0 else 0

    st.title(f"Mansão das Figurinhas")
    st.subheader(f"Progresso: {obtidas_pct}% ({total_obtidas}/{total_figurinhas})")
    st.write("Completar o albúm é nossa única meta")

    item_pesquisa = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo: (figurinhas devem ser pesquisadas pelo código. Ex: KSA01, MEX19. Apague e aperte enter para limpar.)")
    df_filtrado = df.copy()

    if item_pesquisa:
        df_filtrado = df_filtrado[
            df_filtrado['Grupo'].str.contains(item_pesquisa, case=False, na=False) |
            df_filtrado['Selecao'].str.contains(item_pesquisa, case=False, na=False) |
            df_filtrado['Cod_Figurinha'].str.contains(item_pesquisa, case=False, na=False)
        ]

    df = df_filtrado

    if not df.empty:
        distinct_grupos = df['Grupo'].unique()

        # Sanfona 1 (Grupos)
        for grupo in distinct_grupos:
            manter_aberto_grupo = (st.session_state.grupo_aberto == grupo)
            obtido_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].sum()
            total_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].count()
            pct_grupo = round((obtido_grupo/total_grupo)*100) if total_grupo > 0 else 0

            with st.expander(f'⚽ Grupo {grupo} | {pct_grupo}% ({obtido_grupo}/{total_grupo})', expanded=manter_aberto_grupo):
                selecoes_grupo = df[df['Grupo'] == grupo]['Selecao'].unique()

                # Sanfona 2 (Seleções)
                for selecao in selecoes_grupo:
                    manter_aberto_selecao = (st.session_state.selecao_aberta == selecao)
                    obtido_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].sum()
                    total_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].count()
                    pct_selecao = round((obtido_selecao/total_selecao)*100) if total_selecao > 0 else 0

                    with st.expander(f'👕 {selecao} | {pct_selecao}% ({obtido_selecao}/{total_selecao})', expanded=manter_aberto_selecao):
                        
                        figurinhas_selecao = df[(df['Grupo'] == grupo) & (df['Selecao'] == selecao)]
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
                                    supabase.table('Figurinhas').update({'Obtido': novo_status}).eq('IdFigurinha', id_fig).execute()

                                    st.session_state.grupo_aberto = grupo
                                    st.session_state.selecao_aberta = selecao
                                    st.rerun()

    else:
        st.info("Nenhuma figurinha encontrada para a busca atual.")
else:
    st.info("Deu ruim fml! O banco de dados está vazio.")