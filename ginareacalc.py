import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("🧮 Продвинутый калькулятор DCA-сетки")

# --- Пресеты монет ---
COIN_PRESETS = {
    "BTC": {"min_grid_step": 0.2, "min_order_size": 10.0},
    "ETH": {"min_grid_step": 0.25, "min_order_size": 10.0},
    "BNB": {"min_grid_step": 0.3, "min_order_size": 5.0},
    "SOL": {"min_grid_step": 0.5, "min_order_size": 5.0},
    "XRP": {"min_grid_step": 0.5, "min_order_size": 2.0},
    "DOGE": {"min_grid_step": 1.0, "min_order_size": 1.0}
}

with st.sidebar:
    st.header("Grid settings (Настройки сетки)")
    
    coin_selection = st.selectbox(
        "Выберите монету для автозаполнения:",
        ['Ручной'] + sorted(list(COIN_PRESETS.keys()))
    )

    if coin_selection != 'Ручной':
        preset = COIN_PRESETS[coin_selection]
        default_grid_step = preset["min_grid_step"]
        default_order_size = preset["min_order_size"]
    else:
        default_grid_step = 1.0
        default_order_size = 10.0

    initial_order_size = st.number_input("Initial order size (Начальный ордер, $)", min_value=0.1, value=default_order_size)
    safety_order_size = st.number_input("Safety order size (Страховочный ордер, $)", min_value=0.1, value=default_order_size)
    volume_multiplier = st.number_input("Volume multiplier (Множитель суммы)", min_value=1.0, value=1.0, format="%.2f")
    safety_orders_count = st.number_input("Max safety orders count (Макс. кол-во СО)", min_value=1, max_value=100, value=20)
    price_step_percent = st.number_input("Price deviation (Шаг цены, %)", min_value=0.01, value=default_grid_step, format="%.2f")
    price_step_multiplier = st.number_input("Safety order step multiplier (Множитель шага цены)", min_value=1.0, value=1.5, format="%.2f")
    
    st.divider() # Разделитель
    
    # --- ИЗМЕНЕНИЕ: Мгновенный расчет и вывод в сайдбаре ---
    st.header("Live Calculation (Живой расчет)")
    order_sizes_live = [safety_order_size * (volume_multiplier ** i) for i in range(safety_orders_count)]
    price_steps_live = [price_step_percent * (price_step_multiplier ** i) for i in range(safety_orders_count)]
    required_deposit_live = initial_order_size + sum(order_sizes_live)
    theoretical_range_live = sum(price_steps_live)
    
    st.metric("Required Deposit (Требуемый депозит)", f"${required_deposit_live:,.2f}")
    st.metric("Trading Range (Перекрытие цены)", f"{theoretical_range_live:.2f}%")


st.header("📋 Детальная таблица сетки")
grid_data = []
cumulative_volume = initial_order_size
for i in range(safety_orders_count):
    cumulative_volume += order_sizes_live[i]
    grid_data.append({
        '№ СО': i + 1,
        'Размер ордера ($)': order_sizes_live[i],
        'Отклонение цены (%)': price_steps_live[i],
        'Суммарный объем ($)': cumulative_volume
    })

initial_row = pd.DataFrame([{'№ СО': 'Начальный', 'Размер ордера ($)': initial_order_size, 'Отклонение цены (%)': 0.0, 'Суммарный объем ($)': initial_order_size}])
grid_df = pd.concat([initial_row, pd.DataFrame(grid_data)], ignore_index=True).set_index('№ СО')

st.dataframe(grid_df.style.format({
    'Размер ордера ($)': '${:,.2f}',
    'Отклонение цены (%)': '{:,.2f}%',
    'Суммарный объем ($)': '${:,.2f}'
}))
