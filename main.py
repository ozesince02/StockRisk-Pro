import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pandas_datareader.data as web
import capm_functions

st.set_page_config(page_title="CAPM",
                   page_icon="chart_with_upwards_trend",
                   layout="wide")

st.title("Capital Asset Pricing Model")

col1, col2 = st.columns([1, 1])
with col1:
    index = st.selectbox("Select the Index", ('^NSEI', '^GSPC'))
    if index == '^NSEI':
        stocks_list = st.multiselect("Choose your Stocks", (
        'BAJFINANCE.NS', 'HDFCLIFE.NS', 'APOLLOHOSP.NS', 'HINDALCO.NS', 'TATASTEEL.NS', 'LT.NS', 'MARUTI.NS', 'ITC.NS',
        'TITAN.NS', 'KOTAKBANK.NS', 'ULTRACEMCO.NS', 'INDUSINDBK.NS', 'LTIM.NS', 'COALINDIA.NS', 'NESTLEIND.NS',
        'ADANIENT.NS', 'TATACONSUM.NS', 'TCS.NS', 'HEROMOTOCO.NS', 'BAJAJ-AUTO.NS', 'MM.NS', 'CIPLA.NS', 'RELIANCE.NS',
        'ONGC.NS', 'NTPC.NS', 'BAJAJFINSV.NS', 'BRITANNIA.NS', 'WIPRO.NS', 'TECHM.NS', 'BHARTIARTL.NS'),
                                     ['BAJFINANCE.NS', 'HDFCLIFE.NS', 'APOLLOHOSP.NS', 'HINDALCO.NS', 'TATASTEEL.NS'])
        index_name = 'nifty50'
    else:
        stocks_list = st.multiselect("Choose 4 Stocks", ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA',
                                                         'GOOGL'), ['TSLA', 'AAPL', 'AMZN', 'GOOGL'])
        index_name = 'sp500'

with col2:
    year = st.number_input("Number of years", 1, 10)

try:
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
    index_df = yf.download(index, period=f'{year}y')
    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock, period=f'{year}y')
        stocks_df[f'{stock}'] = data['Close']

    stocks_df[index_name] = index_df['Close']
    stocks_df.reset_index(inplace=True)
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Dataframe Head')
        st.dataframe(stocks_df.head(), use_container_width=True)

    with col2:
        st.markdown('### Dataframe Tail')
        st.dataframe(stocks_df.tail(), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Price of all the Stocks')
        st.plotly_chart(capm_functions.interactive_plot(stocks_df), use_container_width=True)

    with col2:
        st.markdown('### Normalized Prices of the Stocks')
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)),
                        use_container_width=True)

    stocks_daily_return = capm_functions.daily_return(stocks_df)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != index_name:
            b, a = capm_functions.calculate_beta(stocks_daily_return, i, index_name)

            beta[i] = b
            alpha[i] = a

    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i, 2)) for i in beta.values()]
    print(beta_df)

    with col1:
        st.markdown('### Calculate Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return[index_name].mean() * 252
    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))
    return_df['Stock'] = stocks_list
    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.dataframe(return_df, use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(capm_functions.histogram(beta_df), use_container_width=True)

    with col2:
        st.plotly_chart(capm_functions.histogram(return_df),
                        use_container_width=True)

except:
    st.write("Please Select Valid Input")
