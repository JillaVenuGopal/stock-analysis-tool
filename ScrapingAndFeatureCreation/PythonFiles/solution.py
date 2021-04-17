import pandas as pd
import importlib
import os
import numpy as np
import traceback
import time
equity_scrape = importlib.import_module("equity_scrape")
corporate_actions_scrape = importlib.import_module("corporate_actions_scrape")
index_scrape = importlib.import_module("index_scrape")
revenue_profit_scrape = importlib.import_module("revenue_profit_scrape")
risk_free_rate_scrape = importlib.import_module("risk_free_rate_scrape")
stock_scrape = importlib.import_module("stock_scrape")
data_cleaning = importlib.import_module("data_cleaning")
corporate_actions = importlib.import_module("corporate_actions")
feature_creation = importlib.import_module("feature_creation")

path = os.path.join(os.getcwd(), "Data")

security_id, security_code = "SBIN", "500112"

equity_scrape.download_equity()
stock_df = stock_scrape.download_stocks(security_code)
index_scrape.download_index()
corporate_actions_scrape.download_corporate_actions(security_code)
risk_free_rate_scrape.download_risk_free_rate()
revenue_profit_scrape.download_revenue_profit(security_code, security_id)
start = time.time()
try:
    index_df = pd.read_csv(os.path.join(path, "Index.csv"))
    corporate_df = pd.read_csv(os.path.join(
        path, "CorporateActions/"+security_code+".csv"))
    revenue_df = pd.read_csv(os.path.join(
        path, "Revenue/"+security_code+".csv"))
    stock_df = pd.read_csv(os.path.join(
        path, "Stock/"+security_code+".csv"))

    stock_df = data_cleaning.cleaning(stock_df, index_df)
    stock_df = corporate_actions.apply_corporate_actions(
        stock_df, corporate_df)
    stock_df = feature_creation.calculate_beta(stock_df)
    stock_df = feature_creation.add_risk_free_column(stock_df)
    stock_df = feature_creation.calculate_alpha(stock_df)

    stock_df = feature_creation.create_lower_upper_bands(stock_df)
    stock_df = feature_creation.create_eps_pe_ratio_revenue_income_expenditure_net_profit(
        revenue_df, stock_df)
    stock_df = feature_creation.add_next_day_columns(stock_df)
    stock_df.to_csv(os.path.join(path, "Stock/"+"fc" +
                    str(security_code)+".csv"), index=None)

    # stock_df[feature_creation.direct_columns] = stock_df[feature_creation.direct_columns].apply(
    #     pd.to_numeric, errors="coerce")
    stock_df[feature_creation.direct_columns] = (stock_df[feature_creation.direct_columns].astype(
        str)).apply(pd.to_numeric, errors='coerce')

    stock_df = feature_creation.find_gain_loss(stock_df)
    stock_df = feature_creation.sequential_increase(stock_df)
    stock_df = feature_creation.sequential_decrease(stock_df)
    stock_df = feature_creation.sequential_increase_percentage(stock_df)
    stock_df = feature_creation.sequential_decrease_percentage(stock_df)
    stock_df = feature_creation.sequential_increase_decrease(stock_df)

    for col in feature_creation.cols:
        try:
            stock_df = feature_creation.quarter_wise_growthrate(stock_df, col)
        except Exception as e:
            traceback.print_exc()
    stock_df = feature_creation.close_price_as_percent_of_LV_HV_BA(stock_df)
    stock_df.to_csv(os.path.join(
        path, "Stock/"+"gr" + str(security_code)+".csv"), index=None)
except:
    traceback.print_exc()
    pass

end = time.time()
print(end-start)
