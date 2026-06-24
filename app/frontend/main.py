import streamlit as st

# ==================== НАСТРОЙКА СТРАНИЦЫ ====================

st.set_page_config(
    page_title="Поиск поставщиков Food",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ЗАГОЛОВОК ====================

st.title("🍽️ Поиск поставщиков продуктов питания")
st.caption("Найдите идеального поставщика для вашего бизнеса")

st.markdown("---")

# ==================== САЙДБАР ====================

with st.sidebar:
    st.header("🔍 Фильтры поиска")
    
    # 1. Локация
    st.subheader("📍 Локация")
    city_input = st.text_input(
        "Город",
        placeholder="Например: Москва, Санкт-Петербург"
    )
    region_input = st.text_input(
        "Регион (опционально)",
        placeholder="Например: Центральный, Южный"
    )
    
    st.markdown("---")
    
    # 2. Категория
    st.subheader("📂 Категория")
    
    # Временные данные для теста
    categories = ["Все категории", "Сырье", "Упаковка", "Готовая продукция"]
    selected_category = st.selectbox(
        "Выберите категорию",
        options=categories
    )
    
    # 3. Подкатегория (зависит от выбранной категории)
    subcategories_map = {
        "Сырье": ["Все подкатегории", "Мука", "Сахар", "Масло", "Молочные продукты"],
        "Упаковка": ["Все подкатегории", "Пластиковая", "Стеклянная", "Картонная"],
        "Готовая продукция": ["Все подкатегории", "Хлебобулочные", "Кондитерские"],
        "Все категории": ["Все подкатегории"]
    }
    
    subcategory_options = subcategories_map.get(selected_category, ["Все подкатегории"])
    selected_subcategory = st.selectbox(
        "Выберите подкатегорию",
        options=subcategory_options,
        disabled=len(subcategory_options) <= 1
    )
    
    st.markdown("---")
    
    # 4. Дополнительные фильтры
    st.subheader("⚙️ Дополнительно")
    min_rating = st.slider(
        "⭐ Минимальный рейтинг",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.5
    )
    only_verified = st.checkbox("✅ Только верифицированные")
    
    st.markdown("---")
    
    # 5. Кнопки
    search_button = st.button("🔍 Найти поставщиков", use_container_width=True, type="primary")
    
    if st.button("🔄 Сбросить все", use_container_width=True):
        st.rerun()

# ==================== ОСНОВНАЯ ОБЛАСТЬ ====================

# Показываем информацию о выбранных фильтрах
st.markdown("### 📋 Выбранные фильтры")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**📍 Город:** {city_input if city_input else 'Не указан'}")
    st.markdown(f"**🗺️ Регион:** {region_input if region_input else 'Не указан'}")

with col2:
    st.markdown(f"**📂 Категория:** {selected_category}")
    st.markdown(f"**📂 Подкатегория:** {selected_subcategory}")

with col3:
    st.markdown(f"**⭐ Рейтинг:** ≥{min_rating}")
    st.markdown(f"**✅ Верификация:** {'Только верифицированные' if only_verified else 'Все'}")

st.markdown("---")

# Информация о поиске
if search_button:
    st.success("🔍 Поиск выполнен! Здесь будут отображаться результаты.")
    st.info("Пока что это заглушка. Скоро здесь появятся карточки поставщиков.")
else:
    st.info("👈 Выберите фильтры в боковой панели и нажмите 'Найти поставщиков'")

st.markdown("---")

# Подсказка
with st.expander("💡 Как использовать сервис"):
    st.markdown("""
    1. Выберите **город** или **регион**
    2. Выберите **категорию** и **подкатегорию**
    3. Настройте **дополнительные фильтры** (рейтинг, верификация)
    4. Нажмите **"Найти поставщиков"**
    5. Из результатов выберите понравившихся поставщиков
    6. Сравните их в специальном окне
    """)