# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
import streamlit as st
import datetime
import folium
from streamlit_folium import folium_static

from PIL import Image # aqui importamos a biblioteca para colocar imagens no streamlit


st.set_page_config(page_title='Visão Empresa', layout='wide')

# ---------------------------------------
# Funções
# ---------------------------------------
def country_maps(df1):
            
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]]
                 .groupby(['City', 'Road_traffic_density']).median().reset_index())
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    
    folium_static(map, width=1024, height=600)

def order_share_by_week(df1):
            
    df_aux01 = df1.loc[:,['week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    
    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['Delivery_person_ID']
    
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    
    return fig

def order_by_week(df1):
        
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def traffic_order_city(df1):    
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def traffic_order_share(df1):
            
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    
    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density')
    
    return fig

def order_metric(df1):
    # Oder Metric
    
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    
    # criei uma variavel fig para colocar dentro da propriedade plotly
    fig = px.bar( df_aux, x='order_date', y='qtde_entregas' )
    
    return fig



def clean_code(df):
    """ Esta função tem a responsabilibsade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

        Imput: dataframe
        Output: dataframe
    """
    # Remover spaco da string
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    
    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    # Remove as linhas da culuna multiple_deliveries que tenham o
    # conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )
    
    # Comando para remover o texto de números
    df = df.reset_index( drop=True )
    
    # Retirando os numeros da coluna Time_taken(min)
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: re.findall( r'\d+', x))
    
    # Retirando os espaços da coluna Festival
    df['Festival'] = df['Festival'].str.strip()

    return df
# -------------------------------- 
# Inicio da Estrutura 
# -------------------------------

# ---------------------------------------
# Lendo e copiando DataFrame
# ---------------------------------------

df_raw = pd. read_csv('dataset/train.csv')
df = df_raw.copy()

# --------------------------------------
# Limpando o dataframe
# --------------------------------------
df = clean_code(df)

# -------------------------------------
# Copia do df
# -------------------------------------

df1 = df.copy()

# -------------------------------------
# Barra Lateral
# -------------------------------------

st.header( "Market Place - Visão Empresa")

st.sidebar.markdown('# Cury Comapny')
st.sidebar.markdown('## Fastest delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11), #mudou o datetime, agora é necessário importar o datetime
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de Transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
#linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
#df1 = df1.loc[linhas_selecionadas, :]

# ----------------------------------------
# Layout no Streamlit
# ----------------------------------------

# Criando os menus

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])


with tab1:
    with st.container():
        fig = order_metric(df1)
        st.header('Orders By Date')
        # Plotly é uma propriedade do strealit para poder exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)
        

    with st.container():

        col1, col2 = st.columns(2)


    with col1:
        fig = traffic_order_share(df1)
        st.header('Traffic Order Share')
        st.plotly_chart(fig, use_container_width=True)


    with col2:
        fig = traffic_order_city(df1)
        st.header('Traffic Order City')
        st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.header('Order By Week')
        st.plotly_chart(fig, use_container_width=True)


    with st.container():
        fig = order_share_by_week(df1)
        st.header('Order Share By Week')
        st.plotly_chart(fig, use_container_width=True)


with tab3:
    with st.container():
        st.header('Country Maps')
        country_maps(df1)

        

        














