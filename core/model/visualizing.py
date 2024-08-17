import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# Plotting the closing price, EMA Crossover, Bollinger Bands, MACD, and RSI
fig, axs = plt.subplots(4, 1, figsize=(12, 18), sharex=True)
data = pd.read_csv('./Indicators.csv')

# Plot Closing Price with Bollinger Bands
axs[0].plot(data['timestamp'], data['close'], label='Close Price', color='blue')
axs[0].plot(data['timestamp'], data['Bollinger_upper'], label='Bollinger Upper', color='orange')
axs[0].plot(data['timestamp'], data['Bollinger_lower'], label='Bollinger Lower', color='green')
axs[0].fill_between(data['timestamp'], data['Bollinger_upper'], data['Bollinger_lower'], color='gray', alpha=0.3)
axs[0].set_title('Closing Price with Bollinger Bands')
axs[0].legend()

# Plot EMA Crossover
axs[1].plot(data['timestamp'], data['EMA_short'], label='12-Period EMA', color='purple')
axs[1].plot(data['timestamp'], data['EMA_long'], label='26-Period EMA', color='brown')
axs[1].set_title('EMA Crossover')
axs[1].legend()

# Plot MACD
axs[2].plot(data['timestamp'], data['MACD'], label='MACD', color='red')
axs[2].plot(data['timestamp'], data['Signal_line'], label='Signal Line', color='black')
axs[2].set_title('MACD and Signal Line')
axs[2].legend()

# Plot RSI
axs[3].plot(data['timestamp'], data['RSI'], label='RSI', color='green')
axs[3].axhline(70, color='red', linestyle='--')
axs[3].axhline(30, color='blue', linestyle='--')
axs[3].set_title('Relative Strength Index (RSI)')
axs[3].legend()

# Formatting the x-axis
plt.xticks(np.arange(0, len(data), step=int(len(data)/10)), rotation=45)
plt.tight_layout()
plt.show()
