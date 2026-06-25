import streamlit as st
import api_requests
import asyncio
import pprint


# ==================== НАСТРОЙКА СТРАНИЦЫ ====================

st.set_page_config(
    page_title="Поиск поставщиков Food",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ИИЦИАЛИЗАЦИЯ ====================

async def load_data():
    cities = await api_requests.get_supplier_cities()
    regions = await api_requests.get_supplier_regions()
    root_categories = await api_requests.get_categories()
    return cities, regions, root_categories


if "initialize" not in st.session_state:
    cities, regions, root_categories = asyncio.run(load_data())
    st.session_state.initialize = {
        "cities": cities,
        "regions": regions,
        "root_categories": root_categories
    }

if "city_input" not in st.session_state:
    st.session_state.city_input = None

if "region_input" not in st.session_state:
    st.session_state.region_input = None

# ==================== ЗАГОЛОВОК ====================

st.title("🍽️ Поиск поставщиков продуктов питания")
st.caption("Найдите идеального поставщика для вашего бизнеса")

st.markdown("---")

# ==================== САЙДБАР ====================

with st.sidebar:
    st.header("🔍 Фильтры поиска")
    
    # 1. Локация
    st.subheader("📍 Локация")
    city_input = st.selectbox(
        "Выберите город:",
        st.session_state.initialize.get("cities", []),
        index=None,
    )

    region_input = st.selectbox(
        "Выберите регион:",
        st.session_state.initialize.get("regions", []),
        index=None
    )

    if city_input and region_input:
    # Если оба выбраны, сбрасываем регион (или наоборот)
        st.warning("Выберите только один параметр!")
    
    st.markdown("---")
    
    # 2. Категория
    st.subheader("📂 Категория")
    
    # Временные данные для теста
    selected_category = st.selectbox(
        "Выберите категорию",
        options=st.session_state.initialize.get("root_categories").keys(),
        format_func=lambda x: st.session_state.initialize.get("root_categories")[x]["name"],
        index=None
    )
    
    subcategory_options = st.session_state.initialize.get("root_categories").get(selected_category, {}).get("children", [])
    data_dict = {
        option.get("id", ""): option.get("name", "")
        for option in subcategory_options
    }
    selected_subcategory = st.selectbox(
        "Выберите подкатегорию",
        options=list(data_dict.keys()),
        format_func=lambda x: data_dict[x],
        index=None
        # disabled=len(subcategory_options) <= 1
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
    if search_button:
        st.session_state.comp_suppliers = asyncio.run(
            api_requests.get_suppliers_by_filter(
                city = city_input,
                region = region_input,
                category_id = selected_subcategory,
                min_rating = min_rating,
                has_certificates = only_verified
            )
        )
        pprint.pprint(st.session_state.comp_suppliers)

# ==================== ОСНОВНАЯ ОБЛАСТЬ ====================

# Показываем информацию о выбранных фильтрах
st.markdown("### 📋 Выбранные фильтры")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**📍 Город:** {city_input if city_input else 'Не указан'}")
    st.markdown(f"**🗺️ Регион:** {region_input if region_input else 'Не указан'}")

with col2:
    subcategory_options = st.session_state.initialize.get("root_categories").get(selected_category, {}).get("children", [])
    data_dict = {
        option.get("id", ""): option.get("name", "")
        for option in subcategory_options
    }
    st.markdown(f"**📂 Категория:** {st.session_state.initialize.get("root_categories").get(selected_category, {}).get("name")}")
    st.markdown(f"**📂 Подкатегория:** {data_dict.get(selected_subcategory)}")

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
