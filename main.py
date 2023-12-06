import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import pandas_datareader.data as web
import capm_functions

st.set_page_config(page_title="CAPM",
                   page_icon="chart_with_upwards_trend",
                   layout="wide")

try:
    # Title and introduction
    st.title("StockRisk Pro")
    st.write("📈 Welcome to StockRisk Pro, a tool for analyzing stock risk using CAPM.")

    # Section to select index and stocks
    col1, col2 = st.columns([1, 1])
    with col1:
        # Select index (NSE or S&P 500)
        index = st.selectbox("🌐 Select the Index", ('^NSEI', '^GSPC'))
        # Explanation about selecting the index
        st.write("Choose the market index for analysis (NSE for Indian stocks, S&P 500 for U.S. stocks).")

        if index == '^NSEI':
            # NSE stock options
            stocks_list = st.multiselect("📊 Choose Stocks", (
                'BAJFINANCE.NS', 'HDFCLIFE.NS', 'APOLLOHOSP.NS', 'HINDALCO.NS', 'TATASTEEL.NS', 'LT.NS', 'MARUTI.NS',
                'ITC.NS',
                'TITAN.NS', 'KOTAKBANK.NS', 'ULTRACEMCO.NS', 'INDUSINDBK.NS', 'LTIM.NS', 'COALINDIA.NS', 'NESTLEIND.NS',
                'ADANIENT.NS', 'TATACONSUM.NS', 'TCS.NS', 'HEROMOTOCO.NS', 'BAJAJ-AUTO.NS', 'MM.NS', 'CIPLA.NS',
                'RELIANCE.NS',
                'ONGC.NS', 'NTPC.NS', 'BAJAJFINSV.NS', 'BRITANNIA.NS', 'WIPRO.NS', 'TECHM.NS', 'BHARTIARTL.NS'),
                                         ['BAJFINANCE.NS', 'HDFCLIFE.NS', 'APOLLOHOSP.NS', 'HINDALCO.NS',
                                          'TATASTEEL.NS'])
            index_name = 'nifty50'
        else:
            # S&P 500 stock options
            stocks_list = st.multiselect("📊 Choose Stocks", ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA',
                                                             'GOOGL'), ['TSLA', 'AAPL', 'AMZN', 'GOOGL'])
            index_name = 'sp500'

    with col2:
        # Input number of years for analysis
        year = st.number_input("⏳ Number of years", 1, 10)
        # Explanation about selecting the number of years
        st.write("Select the number of years for historical data analysis.")

    # Download historical stock data
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
    index_df = yf.download(index, period=f'{year}y')
    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock, period=f'{year}y')
        stocks_df[f'{stock}'] = data['Close']

    # Combine stock and index data
    stocks_df[index_name] = index_df['Close']
    stocks_df.reset_index(inplace=True)
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])

    # Display DataFrame head and tail
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### 📊 Dataframe Head')
        # Explanation about DataFrame Head
        st.write("View initial rows of stock data to understand structure and values.")
        st.dataframe(stocks_df.head(), use_container_width=True)

    with col2:
        st.markdown('### 📊 Dataframe Tail')
        # Explanation about DataFrame Tail
        st.write("View last rows of stock data to observe latest values and trends.")
        st.dataframe(stocks_df.tail(), use_container_width=True)

    # Plot stock prices and normalized prices
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### 📈 Price of all the Stocks')
        # Explanation about Price of all the Stocks
        st.write("Explore historical closing prices of selected stocks over chosen time period.")
        st.plotly_chart(capm_functions.interactive_plot(stocks_df), use_container_width=True)

    with col2:
        st.markdown('### 📈 Normalized Prices of the Stocks')
        # Explanation about Normalized Prices of the Stocks
        st.write("View normalized closing prices with initial price as baseline (1.0).")
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)),
                        use_container_width=True)

    # Calculate daily returns, beta, and alpha values
    stocks_daily_return = capm_functions.daily_return(stocks_df)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != index_name:
            b, a = capm_functions.calculate_beta(stocks_daily_return, i, index_name)

            beta[i] = b
            alpha[i] = a

    # Display calculated beta values
    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i, 2)) for i in beta.values()]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### 📈 Calculate Beta Value')
        # Explanation about Calculate Beta Value
        st.write("Understand risk level of each stock by calculating its Beta value with respect to market index.")
        st.dataframe(beta_df, use_container_width=True)

    # Calculate expected returns using CAPM
    rf = 0
    rm = stocks_daily_return[index_name].mean() * 252
    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))
    return_df['Stock'] = stocks_list
    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### 📈 Calculated Return using CAPM')
        # Explanation about Calculated Returns using CAPM
        st.write("Estimate expected returns of each stock based on calculated CAPM values.")
        st.dataframe(return_df, use_container_width=True)

    # Plot histograms for beta values and expected returns
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(capm_functions.histogram(beta_df), use_container_width=True)

    with col2:
        st.plotly_chart(capm_functions.histogram(return_df),
                        use_container_width=True)

    # Simulate stock investment
    last_day_df = stocks_df.iloc[[-1]]
    last_day_df.reset_index(inplace=True)
    st.markdown('### 💼 Look how the selected stock performs!')
    stock_selected = st.selectbox('📈 Select Stock to Invest', tuple(stocks_list))
    current = round(last_day_df._get_value(0, stock_selected), 2)
    st.markdown(f'###### 💰 Current Price is :blue[₹{current}]')
    quantity = st.number_input("📊 Number of Stocks ", 1, 1000, 10)
    principle = current * quantity
    st.markdown(f'###### 💸 Money Invested :blue[₹{round(principle, 2)}]')
    time = st.number_input("⏰ Investment Period :alarm_clock:", 1, 10)
    investment_df = return_df[(return_df['Stock'] == stock_selected)]
    investment_df.reset_index(inplace=True)
    rate = investment_df._get_value(0, 'Return Value')
    returns = capm_functions.calculate_amount(float(principle), float(time), float(rate))

    # Historical stock prices with investment period visualization
    st.markdown('### 📊 Historical Stock Prices with Investment Period')
    capm_functions.plot_investment_period(stocks_df, stock_selected, time)

    if principle > returns:
        color = 'red'
    else:
        color = 'green'
    st.write(f'After {time} year(s), This stock will be valued at: :{color}[₹{returns}]')
    st.write(f'Expected Profit in {time} year(s): :{color}[₹{round((returns - principle), 2)}]')

except:
    st.write("Try Again!")
