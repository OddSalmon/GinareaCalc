import streamlit as st
import pandas as pd
import numpy as np

# --- Настройка страницы ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title("🧮 Продвинутый калькулятор DCA-сетки")

# --- Боковая панель для ввода параметров ---
with st.sidebar:
    st.header("Grid settings (Настройки сетки)")
    
    # --- Блок для ручного ввода ---
    initial_order_size = st.number_input("Initial order size (Начальный ордер, $)", min_value=0.1, value=10.0)
    safety_order_size = st.number_input("Safety order size (Страховочный ордер, $)", min_value=0.1, value=10.0)
    volume_multiplier = st.number_input("Volume multiplier (Множитель суммы)", min_value=1.0, value=1.0, format="%.2f")
    safety_orders_count = st.number_input("Max safety orders count (Макс. кол-во СО)", min_value=1, max_value=100, value=20)
    price_step_percent = st.number_input("Price deviation (Шаг цены, %)", min_value=0.01, value=2.0, format="%.2f")
    price_step_multiplier = st.number_input("Safety order step multiplier (Множитель шага цены)", min_value=1.0, value=1.5, format="%.2f")
    take_profit_percent = st.number_input("Take profit (% от общего объема)", min_value=0.01, value=2.0, format="%.2f")
    
    # --- Кнопка для запуска расчетов ---
    run_calculation = st.button("🚀 Рассчитать сетку")

# --- Основная часть: Отображение результатов после нажатия кнопки ---
if run_calculation:
    # Расчеты
    order_sizes = [safety_order_size * (volume_multiplier ** i) for i in range(safety_orders_count)]
    price_steps = [price_step_percent * (price_step_multiplier ** i) for i in range(safety_orders_count)]
    required_deposit = initial_order_size + sum(order_sizes)
    theoretical_range = sum(price_steps)

    # Вывод результатов
    st.header("📊 Рассчитанные показатели")
    col1, col2 = st.columns(2)
    col1.metric("Required Deposit (Требуемый депозит)", f"${required_deposit:,.2f}")
    col2.metric("Trading Range (Перекрытие цены)", f"{theoretical_range:.2f}%")

    st.header("📋 Детальная таблица сетки")
    grid_data = []
    cumulative_volume = initial_order_size
    for i in range(safety_orders_count):
        cumulative_volume += order_sizes[i]
        grid_data.append({
            '№ СО': i + 1,
            'Размер ордера ($)': order_sizes[i],
            'Отклонение цены (%)': price_steps[i],
            'Суммарный объем ($)': cumulative_volume
        })

    initial_row = pd.DataFrame([{'№ СО': 'Начальный', 'Размер ордера ($)': initial_order_size, 'Отклонение цены (%)': 0.0, 'Суммарный объем ($)': initial_order_size}])
    grid_df = pd.concat([initial_row, pd.DataFrame(grid_data)], ignore_index=True).set_index('№ СО')

    st.dataframe(grid_df.style.format({
        'Размер ордера ($)': '${:,.2f}',
        'Отклонение цены (%)': '{:,.2f}%',
        'Суммарный объем ($)': '${:,.2f}'
    }))
else:
    st.info("Задайте параметры в боковой панели и нажмите 'Рассчитать сетку', чтобы увидеть результаты.")
