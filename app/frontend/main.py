import streamlit as st
import api_requests
import asyncio
# import pprint


def show_comparison(suppliers):
    """Отображение сравнения поставщиков в табличном виде"""
    
    st.markdown("## 📊 Сравнение поставщиков")
    
    # Получаем имена поставщиков для заголовков
    supplier_names = [s['name'] for s in suppliers]
    
    # Создаем таблицу сравнения в виде списка словарей
    comparison_data = []
    
    # Город
    row = {"Критерий": "🏙️ Город"}
    for supplier in suppliers:
        row[supplier['name']] = supplier.get('city', 'Н/Д')
    comparison_data.append(row)
    
    # Адрес
    row = {"Критерий": "📍 Адрес"}
    for supplier in suppliers:
        row[supplier['name']] = supplier.get('address', 'Н/Д')
    comparison_data.append(row)
    
    # Сертификаты
    row = {"Критерий": "📜 Сертификаты"}
    for supplier in suppliers:
        if supplier.get('certificates'):
            certs = ", ".join([c['certificate_name'] for c in supplier['certificates']])
            row[supplier['name']] = certs
        else:
            row[supplier['name']] = "Нет"
    comparison_data.append(row)
    
    # Контакты
    row = {"Критерий": "📞 Контакты"}
    for supplier in suppliers:
        if supplier.get('contact'):
            contacts = ", ".join([f"{c['contact_person']} ({c['contact_value']})" 
                                 for c in supplier['contact']])
            row[supplier['name']] = contacts
        else:
            row[supplier['name']] = "Нет"
    comparison_data.append(row)
    
    # Количество заметок
    row = {"Критерий": "📌 Заметки"}
    for supplier in suppliers:
        notes_count = len(supplier.get('notes', []))
        row[supplier['name']] = f"{notes_count} заметок"
    comparison_data.append(row)
    
    # Описание
    row = {"Критерий": "📝 Описание"}
    for supplier in suppliers:
        desc = supplier.get('description', '')
        if len(desc) > 100:
            desc = desc[:100] + "..."
        row[supplier['name']] = desc
    comparison_data.append(row)
    
    # Отображаем таблицу с помощью st.write
    st.write("### Сравнительная таблица")
    
    # Создаем HTML таблицу для красивого отображения
    html_table = "<table style='width:100%; border-collapse: collapse;'>"
    
    # Заголовок
    html_table += "<tr><th style='border:1px solid #ddd; padding:8px; background-color:#f2f2f2;'>Критерий</th>"
    for name in supplier_names:
        html_table += f"<th style='border:1px solid #ddd; padding:8px; background-color:#f2f2f2;'>{name}</th>"
    html_table += "</tr>"
    
    # Данные
    for row in comparison_data:
        html_table += "<tr>"
        html_table += f"<td style='border:1px solid #ddd; padding:8px;'><b>{row['Критерий']}</b></td>"
        for name in supplier_names:
            html_table += f"<td style='border:1px solid #ddd; padding:8px;'>{row[name]}</td>"
        html_table += "</tr>"
    
    html_table += "</table>"
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Анализ
    st.markdown("### 📈 Анализ")
    
    # Находим поставщика с наибольшим количеством сертификатов
    max_cert_supplier = max(suppliers, key=lambda x: len(x.get('certificates', [])))
    st.success(f"🏆 Поставщик с наибольшим количеством сертификатов: **{max_cert_supplier['name']}**")
    
    # Находим поставщика с наибольшим количеством заметок
    max_notes_supplier = max(suppliers, key=lambda x: len(x.get('notes', [])))
    st.info(f"📊 Поставщик с наибольшим количеством заметок: **{max_notes_supplier['name']}**")
    
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


if 'selected_for_comparison' not in st.session_state:
    st.session_state.selected_for_comparison = []
    st.session_state.selected_suppliers = {}
    st.session_state.comp_suppliers = []

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
    st.session_state.comp_suppliers = asyncio.run(
        api_requests.get_suppliers_by_filter(
            city = city_input,
            region = region_input,
            category_id = selected_subcategory,
            min_rating = min_rating,
            has_certificates = only_verified
        )
    )

else:
    st.info("👈 Выберите фильтры в боковой панели и нажмите 'Найти поставщиков'")

suppliers_data = st.session_state.comp_suppliers
if suppliers_data:
    st.success(f"🔍 Найдено {len(suppliers_data)} поставщиков")
    
    # Создаем форму для группировки чекбоксов
    with st.form(key="comparison_form"):
        st.markdown("### 🎯 Выберите поставщиков для сравнения")

        for idx, supplier in enumerate(suppliers_data):

            with st.container():
                col_check, col_content = st.columns([0.1, 0.9])
                
                with col_check:
                    checkbox_key = f"supplier_{supplier['id']}"
                    if checkbox_key not in st.session_state:
                        st.session_state[checkbox_key] = False

                    st.checkbox(
                        "Выбрать",
                        key=checkbox_key
                    )
                
                with col_content:
                    st.markdown(f"### 🏢 {supplier['name']}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**📍 Адрес:** {supplier['address']}")
                        st.markdown(f"**🏙️ Город:** {supplier['city']}")
                        
                        if supplier.get('contact'):
                            st.markdown("**📞 Контакты:**")
                            for contact in supplier['contact']:
                                if contact['contact_type'] == 'phone':
                                    st.markdown(f"- {contact['contact_person']}: {contact['contact_value']}")
                    
                    with col2:
                        if supplier.get('certificates'):
                            st.markdown("**📜 Сертификаты:**")
                            for cert in supplier['certificates']:
                                st.markdown(f"- {cert['certificate_name']} (выдан: {cert['issuing_authority']})")
                    
                    if supplier.get('description'):
                        st.markdown(f"**📝 Описание:**")
                        st.markdown(f"{supplier['description']}")
                    
                    if supplier.get('notes'):
                        with st.expander("📌 Заметки"):
                            for note in supplier['notes']:
                                note_type = note['note_type'].upper()
                                st.markdown(f"**{note_type}** ({note['date']}): {note['text']}")
                    
                    st.divider()
        
        # Кнопка сравнения внутри формы
        compare_clicked = st.form_submit_button("🔍 Сравнить выбранных поставщиков")
        # Обработка нажатия кнопки сравнени
        if compare_clicked:
            selected_suppliers = [
                supplier
                for supplier in suppliers_data
                if st.session_state.get(
                    f"supplier_{supplier['id']}",
                    False
                )
            ]

            if len(selected_suppliers) >= 2:
                show_comparison(selected_suppliers)
            else:
                st.warning(
                    "⚠️ Выберите минимум 2 поставщика для сравнения"
                )
else:
    st.warning("🔍 Поставщики не найдены")
    


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
