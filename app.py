import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 设置网页标题和图标
st.set_page_config(page_title="全球汇率实时看板", page_icon="💰")

st.title("💰 多国兑换人民币实时汇率")
st.caption(f"数据更新于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 设置侧边栏参数
st.sidebar.header("配置选项")
amount = st.sidebar.number_input("请输入人民币金额 (CNY)", min_value=1.0, value=100.0)

# 获取汇率数据 (无需 Key 的公开接口)
@st.cache_data(ttl=3600)  # 缓存1小时，避免频繁刷新被封
def get_data():
    url = "https://api.exchangerate-api.com/v4/latest/CNY"
    res = requests.get(url)
    return res.json()["rates"]

try:
    rates = get_data()
    
    # 我们关心的货币
    target_currencies = {
        "USD": "美元", "EUR": "欧元", "GBP": "英镑", "AUD": "澳元", 
    }

    # 数据转换逻辑
    display_data = []
    for code, name in target_currencies.items():
        rate = rates[code]
        display_data.append({
            "货币": f"{name} ({code})",
            "当前汇率 (1外币=X元)": round(1/rate, 4),
            f"{amount} 人民币可兑换": f"{round(amount * rate, 2)} {code}"
        })

    # 1. 核心看板展示 (最亮眼的部分)
    cols = st.columns(3)
    cols[0].metric("美元/人民币", f"{round(1/rates['USD'], 4)}")
    cols[1].metric("欧元/人民币", f"{round(1/rates['EUR'], 4)}")

    # 2. 详细数据表格
    st.subheader(f"💵 {amount} 元人民币的详细兑换清单")
    df = pd.DataFrame(display_data)
    st.table(df)

    # 3. 下载功能
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("下载数据为 Excel/CSV", csv, "exchange_rates.csv", "text/csv")

except Exception as e:
    st.error(f"数据加载失败，请刷新页面重试。错误原因: {e}")

st.info("💡 提示：本程序数据源自公共接口，仅供参考，实际请以银行柜台为准。")
