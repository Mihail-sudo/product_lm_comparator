import streamlit as st
import api_requests
from api_requests.exceptions import ApiError
import styles
import llm_service


# ==================== ФУНКЦИЯ ДЛЯ ОТОБРАЖЕНИЯ ДИАЛОГА ====================

def show_comparison_dialog(selected_suppliers):
    """Отображение диалога сравнения с ботом-помощником"""
    
    if not selected_suppliers or len(selected_suppliers) < 2:
        st.warning("⚠️ Выберите минимум 2 поставщика для сравнения")
        return
    
    # Открываем диалоговое окно с помощью модального контейнера
    with st.container():
        # Создаем overlay эффект
        st.markdown(styles.chat_style, unsafe_allow_html=True)
        
        # Заголовок
        st.markdown(f"""
        <div class="dialog-header">
            <h2 class="dialog-title">📊 Сравнение поставщиков</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопка закрытия через Streamlit
        if st.button("✕ Закрыть", key="close_dialog"):
            st.session_state.show_comparison_dialog = False
            st.rerun()
        
        # ИНФОРМАЦИЯ О ВЫБРАННЫХ ПОСТАВЩИКАХ
        st.markdown(f"**Выбрано поставщиков:** {len(selected_suppliers)}")
        
        # Две колонки: карточки поставщиков и чат с ботом
        col_left, col_right = st.columns([1, 1.2])
        
        with col_left:
            st.markdown("### 🏢 Поставщики")
            
            for supplier in selected_suppliers:
                with st.container():
                    st.markdown(f"""
                    <div class="supplier-mini-card">
                        <h4>{supplier.get('name', 'Без названия')}</h4>
                        <p>📍 {', '.join(loc['city'] for loc in (supplier.get('locations') or []) if loc.get('city')) or 'Н/Д'}, {supplier.get('address', 'Н/Д')}</p>
                        <p>📞 {', '.join([c['contact_value'] for c in supplier.get('contacts', [])[:2]]) if supplier.get('contacts') else 'Нет контактов'}</p>
                        <p>📜 {len(supplier.get('certificates', []))} сертификатов</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Кнопка для получения рекомендации от бота
            if st.button("🤖 Получить рекомендацию", key="get_recommendation", use_container_width=True):
                with st.spinner("🧠 Бот анализирует поставщиков..."):
                    # Заглушка для рекомендации
                    recommendation = generate_recommendation(selected_suppliers)
                    st.session_state.bot_recommendation = recommendation
                    # Добавляем сообщение от бота в чат
                    st.session_state.chat_messages.append({
                        "role": "bot",
                        "content": recommendation
                    })
                st.rerun()
            
            # Кнопка сброса чата
            if st.button("🔄 Очистить чат", key="clear_chat", use_container_width=True):
                st.session_state.chat_messages = [
                    {"role": "system", "content": "👋 Я бот-помощник. Задайте мне вопрос о поставщиках!"}
                ]
                st.rerun()
        
        with col_right:
            st.markdown("### 💬 Чат с ботом-помощником")
            
            # Инициализация чата
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = [
                    {"role": "system", "content": "👋 Я бот-помощник. Задайте мне вопрос о поставщиках!"}
                ]
            
            # Отображение сообщений
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.chat_messages:
                    if msg["role"] == "system":
                        st.markdown(f"""
                        <div class="chat-message system">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    elif msg["role"] == "user":
                        st.markdown(f"""
                        <div class="chat-message user">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    elif msg["role"] == "bot":
                        st.markdown(f"""
                        <div class="chat-message bot">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Поле ввода сообщения
            st.markdown('<div class="chat-input">', unsafe_allow_html=True)
            
            # Используем форму для обработки ввода
            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_input(
                    "Ваше сообщение",
                    placeholder="Спросите у бота о поставщиках...",
                    key="chat_input"
                )
                submit_button = st.form_submit_button("📤 Отправить")
                
                if submit_button and user_input:
                    # Добавляем сообщение пользователя в чат
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Генерируем ответ от бота (заглушка)
                    bot_response = generate_bot_response(user_input, selected_suppliers)
                    st.session_state.chat_messages.append({
                        "role": "bot",
                        "content": bot_response
                    })
                    
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)


# ==================== ФУНКЦИИ БОТА (ЗАГЛУШКИ) ====================

def generate_recommendation(suppliers):
    if not suppliers:
        return "❌ Нет данных для анализа"
    model = st.session_state.get("llm_model", llm_service.DEFAULT_MODEL)
    result = llm_service.generate_recommendation_llm(suppliers, model)
    if result:
        return result
    return "⚠️ LLM недоступен. Убедитесь, что Ollama запущен (http://localhost:11434)."


def generate_bot_response(user_question, suppliers):
    model = st.session_state.get("llm_model", llm_service.DEFAULT_MODEL)
    result = llm_service.ask_bot_llm(user_question, suppliers, model)
    if result:
        return result
    return "⚠️ LLM недоступен. Убедитесь, что Ollama запущен (http://localhost:11434)."


# ==================== НАСТРОЙКА СТРАНИЦЫ ====================

st.set_page_config(
    page_title="Поиск поставщиков Food",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== ИНИЦИАЛИЗАЦИЯ ====================

if "initialize" not in st.session_state:
    try:
        cities = api_requests.get_supplier_cities()
        regions = api_requests.get_supplier_regions()
        root_categories = api_requests.get_categories()
        st.session_state.initialize = {
            "cities": cities,
            "regions": regions,
            "root_categories": root_categories
        }
    except ApiError as e:
        st.session_state.initialize = {
            "cities": [],
            "regions": [],
            "root_categories": {}
        }
        st.error(f"⚠️ {e}")

if "llm_model" not in st.session_state:
    st.session_state.llm_model = llm_service.DEFAULT_MODEL

if "show_comparison_dialog" not in st.session_state:
    st.session_state.show_comparison_dialog = False

if "selected_for_comparison" not in st.session_state:
    st.session_state.selected_for_comparison = []
    st.session_state.selected_suppliers = {}
    st.session_state.comp_suppliers = []
    st.session_state.chat_messages = []


# ==================== ЗАГОЛОВОК ====================

st.title("🍽️ Поиск поставщиков продуктов питания")
st.caption("Найдите идеального поставщика для вашего бизнеса")

st.markdown("---")


# ==================== САЙДБАР ====================

with st.sidebar:
    st.header("🔍 Фильтры поиска")
    
    # 1. Локация
    st.subheader("📍 Локация")
    location_mode = st.radio(
        "Тип поиска:",
        ["По городу", "По региону"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    city_input = None
    region_input = None

    if location_mode == "По городу":
        city_input = st.selectbox(
            "Выберите город:",
            st.session_state.initialize.get("cities", []),
            index=None,
        )
    else:
        region_input = st.selectbox(
            "Выберите регион:",
            st.session_state.initialize.get("regions", []),
            index=None,
        )
    
    st.markdown("---")
    
    # 2. Категория
    st.subheader("📂 Категория")
    
    selected_category = st.selectbox(
        "Выберите категорию",
        options=st.session_state.initialize.get("root_categories").keys(),
        format_func=lambda x: st.session_state.initialize.get("root_categories")[x]["name"],
        index=None
    )
    
    subcategory_options = st.session_state.initialize.get("root_categories").get(selected_category, {}).get("children") or []
    data_dict = {
        option.get("id", ""): option.get("name", "")
        for option in subcategory_options
    }
    selected_subcategory = st.selectbox(
        "Выберите подкатегорию",
        options=list(data_dict.keys()),
        format_func=lambda x: data_dict[x],
        index=None
    )
    
    st.markdown("---")

    # 3.5. LLM
    st.subheader("🧠 LLM")
    st.text_input(
        "Модель Ollama",
        key="llm_model",
        help="Укажите название модели, установленной в Ollama"
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
    subcategory_options = st.session_state.initialize.get("root_categories").get(selected_category, {}).get("children") or []
    data_dict = {
        option.get("id", ""): option.get("name", "")
        for option in subcategory_options
    }
    st.markdown(f"**📂 Категория:** {st.session_state.initialize.get('root_categories').get(selected_category, {}).get('name')}")
    st.markdown(f"**📂 Подкатегория:** {data_dict.get(selected_subcategory)}")

with col3:
    st.markdown(f"**⭐ Рейтинг:** ≥{min_rating}")
    st.markdown(f"**✅ Верификация:** {'Только верифицированные' if only_verified else 'Все'}")

st.markdown("---")

# Поиск поставщиков
if search_button:
    search_params = {
        "category_id": selected_subcategory,
        "min_rating": min_rating,
    }
    if city_input:
        search_params["city"] = city_input
    if region_input:
        search_params["region"] = region_input
    if only_verified:
        search_params["is_verified"] = True

    try:
        st.session_state.comp_suppliers = api_requests.get_suppliers_by_filter(**search_params)
    except ApiError as e:
        st.error(f"⚠️ {e}")
        st.session_state.comp_suppliers = []
    # Сбрасываем состояние диалога
    st.session_state.show_comparison_dialog = False

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
                        st.markdown(f"**📍 Адрес:** {supplier.get('address', 'Н/Д')}")
                        cities_str = ', '.join(loc['city'] for loc in (supplier.get('locations') or []) if loc.get('city')) or 'Н/Д'
                        st.markdown(f"**🏙️ Города:** {cities_str}")
                        
                        if supplier.get('contacts'):
                            st.markdown("**📞 Контакты:**")
                            for contact in supplier['contacts']:
                                if contact['contact_type'] == 'phone':
                                    st.markdown(f"- {contact.get('contact_person', 'Н/Д')}: {contact['contact_value']}")
                    
                    with col2:
                        if supplier.get('certificates'):
                            st.markdown("**📜 Сертификаты:**")
                            for cert in supplier['certificates'][:3]:
                                st.markdown(f"- {cert['certificate_name']} (выдан: {cert.get('issuing_authority', 'Н/Д')})")
                            if len(supplier['certificates']) > 3:
                                st.markdown(f"- ...еще {len(supplier['certificates']) - 3}")
                    
                    if supplier.get('description'):
                        st.markdown(f"**📝 Описание:**")
                        desc = supplier['description']
                        if len(desc) > 300:
                            desc = desc[:300] + "..."
                        st.markdown(f"{desc}")
                    
                    if supplier.get('notes'):
                        with st.expander("📌 Заметки"):
                            for note in supplier['notes'][:3]:
                                note_type = note.get('note_type', 'general').upper()
                                st.markdown(f"**{note_type}** ({note.get('date', '')}): {note.get('text', '')}")
                    
                    st.divider()
        
        # Кнопки внутри формы
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            compare_clicked = st.form_submit_button("🔍 Сравнить выбранных поставщиков", use_container_width=True)
        with col_btn2:
            clear_selection = st.form_submit_button("🔄 Очистить выбор", use_container_width=True)
        
        # Обработка нажатия кнопки сравнения
        if compare_clicked:
            selected_suppliers = [
                supplier for supplier in suppliers_data
                if st.session_state.get(f"supplier_{supplier['id']}", False)
            ]

            if len(selected_suppliers) >= 2:
                # Показываем диалог сравнения
                st.session_state.show_comparison_dialog = True
                st.session_state.selected_for_comparison = selected_suppliers
                # Инициализируем чат
                st.session_state.chat_messages = [
                    {"role": "system", "content": f"👋 Я бот-помощник. Вы выбрали {len(selected_suppliers)} поставщиков для сравнения. Задайте мне вопрос о них!"}
                ]
                st.rerun()
            else:
                st.warning("⚠️ Выберите минимум 2 поставщика для сравнения")
        
        if clear_selection:
            for supplier in suppliers_data:
                st.session_state[f"supplier_{supplier['id']}"] = False
            st.rerun()

else:
    if search_button:
        st.warning("🔍 Поставщики не найдены. Попробуйте изменить параметры поиска.")
    else:
        st.info("👈 Выберите фильтры в боковой панели и нажмите 'Найти поставщиков'")

st.markdown("---")

# Подсказка
with st.expander("💡 Как использовать сервис"):
    st.markdown(styles.how_2_use)


# ==================== ОТОБРАЖЕНИЕ ДИАЛОГА СРАВНЕНИЯ ====================

if st.session_state.show_comparison_dialog and st.session_state.selected_for_comparison:
    show_comparison_dialog(st.session_state.selected_for_comparison)
