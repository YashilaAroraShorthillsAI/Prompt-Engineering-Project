import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV
file_path = "MW-NIFTY-50-03-Apr-2025.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

# Rename columns for easy access
df.rename(columns={"30 D   %CHNG": "30 D %CHNG", "SYMBOL \n": "SYMBOL"}, inplace=True)

# Convert relevant columns to numeric
df["%CHNG"] = pd.to_numeric(df.get("%CHNG"), errors="coerce")
df["30 D %CHNG"] = pd.to_numeric(df.get("30 D %CHNG"), errors="coerce")

# Top 5 Gainers
top_gainers = df.sort_values(by="%CHNG", ascending=False).head(5)

# Top 5 Losers
top_losers = df.sort_values(by="%CHNG", ascending=True).head(5)

# Create bar plots
fig, axs = plt.subplots(1, 2, figsize=(15, 5))

# Plot Top 5 Gainers
axs[0].bar(top_gainers["SYMBOL"], top_gainers["%CHNG"], color='green')
axs[0].set_title("Top 5 Gainers")
axs[0].set_xlabel("Stock Symbol")
axs[0].set_ylabel("% Change")
axs[0].grid(True)

# Plot Top 5 Losers
axs[1].bar(top_losers["SYMBOL"], top_losers["%CHNG"], color='red')
axs[1].set_title("Top 5 Losers")
axs[1].set_xlabel("Stock Symbol")
axs[1].set_ylabel("% Change")
axs[1].grid(True)

plt.tight_layout()
plt.show()
