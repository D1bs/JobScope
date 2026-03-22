async function loadStats() {
    const response = await fetch('/stats')
    const data = await response.json()
    document.getElementById('total-vacancies').textContent = data.total_vacancies
    document.getElementById('avg-salary').textContent = '$' + data.avg_salary
}

async function loadVacancies() {
    const response = await fetch('/vacancies')
    const data = await response.json()
    const tbody = document.getElementById('vacancies-table')
    tbody.innerHTML = ''
    for (const vacancy of data) {
        tbody.innerHTML += `
            <tr>
                <td>${vacancy.title}</td>
                <td>${vacancy.company}</td>
                <td>${vacancy.city}</td>
                <td>${vacancy.salary_from ?? '—'}</td>
                <td>${vacancy.salary_to ?? '—'}</td>
            </tr>
        `
    }
}

async function runParse() {
    const btn = document.getElementById('parse-btn')
    btn.textContent = 'Парсинг...'
    btn.disabled = true
    const response = await fetch('/parse?query=Python&city_id=1002', {method: 'POST'})
    const data = await response.json()
    setTimeout(async () => {
        await loadStats()
        await loadVacancies()
        btn.textContent = 'Запустить парсинг'
        btn.disabled = false
    }, 3000)
}

document.getElementById('parse-btn').addEventListener('click', runParse)

loadStats()
loadVacancies()