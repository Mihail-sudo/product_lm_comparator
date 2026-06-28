chat_style = """
<style>
.dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #f0f2f6;
    padding-bottom: 15px;
    margin-bottom: 20px;
}
.dialog-title {
    font-size: 1.8rem;
    font-weight: bold;
    color: #1f77b4;
    margin: 0;
}
.close-button {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}
.close-button:hover {
    background: #c0392b;
}
.comparison-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 20px;
    margin-top: 20px;
}
.supplier-cards {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}
.supplier-mini-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 10px;
    border-left: 4px solid #1f77b4;
}
.supplier-mini-card h4 {
    margin: 0 0 5px 0;
    color: #1f77b4;
}
.supplier-mini-card p {
    margin: 3px 0;
    font-size: 0.9rem;
    color: #2c3e50;
}
.chat-section {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    max-height: 500px;
    display: flex;
    flex-direction: column;
}
.chat-messages {
    flex: 1;
    overflow-y: auto;
    max-height: 350px;
    margin-bottom: 10px;
    padding: 10px;
    background: white;
    border-radius: 10px;
}
.chat-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
    max-width: 85%;
}
.chat-message.user {
    background: #1f77b4;
    color: white;
    margin-left: auto;
}
.chat-message.bot {
    background: #e8f4f8;
    color: #2c3e50;
    margin-right: auto;
}
.chat-message.system {
    background: #f1c40f;
    color: #2c3e50;
    text-align: center;
    max-width: 100%;
    font-style: italic;
}
.chat-input {
    display: flex;
    gap: 10px;
    padding-top: 10px;
    border-top: 1px solid #dee2e6;
    
}
.chat-input input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 8px;
    font-size: 14px;
}
.chat-input button {
    padding: 10px 20px;
    background: #1f77b4;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
}
.chat-input button:hover {
    background: #155a8a;
}
</style>
"""

how_2_use = """
1. Выберите **город** или **регион**
2. Выберите **категорию** и **подкатегорию**
3. Настройте **дополнительные фильтры** (рейтинг, верификация)
4. Нажмите **"Найти поставщиков"**
5. Из результатов выберите понравившихся поставщиков (минимум 2)
6. Нажмите **"Сравнить выбранных поставщиков"**
7. В диалоговом окне вы можете:
    - Посмотреть краткую информацию о поставщиках
    - Получить рекомендацию от бота
    - Задать вопросы боту в чате
"""