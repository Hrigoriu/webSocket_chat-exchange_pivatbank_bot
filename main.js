console.log('Клієнт запущено!')

// Ініціалізуємо підключення до нашого Python WebSocket сервера
const ws = new WebSocket('ws://localhost:8080')

const formChat = document.getElementById('formChat')
const textField = document.getElementById('textField')
const subscribe = document.getElementById('subscribe')

// Обробник відправки форми (Enter або клік по кнопці)
formChat.addEventListener('submit', (e) => {
    e.preventDefault() 
    
    // Не відправляємо порожні рядки
    if (textField.value.trim() !== '') {
        ws.send(textField.value)
        textField.value = ''
    }
})

// Коли успішно підключилися до сервера
ws.onopen = (e) => {
    console.log('Підключено до WebSocket!')
    
    const elMsg = document.createElement('div')
    elMsg.className = 'message'
    elMsg.style.color = 'green'
    elMsg.textContent = 'З\'єднання встановлено. Спробуйте написати "exchange 2"'
    
    subscribe.appendChild(elMsg)
}

// Коли отримали повідомлення від сервера
ws.onmessage = (e) => {
    console.log("Отримано:", e.data)
    
    const elMsg = document.createElement('div')
    elMsg.className = 'message' 
    
    // Якщо це повідомлення від нашого бота, робимо його синім і жирним
    if (e.data.includes("🤖 Бот")) {
        elMsg.style.color = 'darkblue'
        elMsg.style.fontWeight = 'bold'
    }
    
    elMsg.textContent = e.data
    subscribe.appendChild(elMsg)
    
    // Прокрутка чату в самий низ при новому повідомленні
    window.scrollTo(0, document.body.scrollHeight);
}

