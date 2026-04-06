async function loadStats() {
    const response = await fetch('/stats')
    const data = await response.json()
    document.getElementById('total-vacancies').textContent = data.total_vacancies
    document.getElementById('avg-salary').textContent = '$' + data.avg_salary
}

async function loadVacancies(filters = {}) {
    const params = new URLSearchParams(
        Object.entries(filters).filter(([, value]) => value)
    )
    const response = await fetch(`/vacancies?${params}`)
    const data = await response.json()
    const tbody = document.getElementById('vacancies-table')
    tbody.innerHTML = ''
    for (const vacancy of data) {
    tbody.innerHTML += `
        <tr>
            <td>${vacancy.title}</td>
            <td>${vacancy.company}</td>
            <td>${vacancy.city}</td>
            <td>${vacancy.schedule ?? '—'}</td>
            <td>${vacancy.employment ?? '—'}</td>
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

let skillsChart = null

async function loadSkillsChart() {
    const response = await fetch('/skills')
    const data = await response.json()

    const labels = data.skills.map(s => s.name)
    const counts = data.skills.map(s => s.count)

    if (skillsChart) {
        skillsChart.destroy()
    }

    skillsChart = new Chart(document.getElementById('skillsChart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Количество вакансий',
                data: counts,
                backgroundColor: '#e94560'
            }]
        },
        options: {
            indexAxis: 'y',
            plugins: { legend: { display: false } }
        }
    })
}

function getFilters() {
    return {
        search:     document.getElementById('searchInput').value.trim(),
        salary_min: document.getElementById('salaryInput').value,
        schedule:   document.getElementById('scheduleSelect').value,
        employment: document.getElementById('employmentSelect').value,
    }
}

function applyFilters() {
    loadVacancies(getFilters())
}

function resetFilters() {
    document.getElementById('searchInput').value      = ''
    document.getElementById('salaryInput').value      = ''
    document.getElementById('scheduleSelect').value   = ''
    document.getElementById('employmentSelect').value = ''
    loadVacancies()
}

function createWebSocket() {
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => console.log('[WS] connected')

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'new_vacancies') {
            showToast(`Добавлено вакансий: ${data.count}`)
            loadVacancies()
            loadStats()
            loadSkillsChart()
        }
    }

    ws.onclose = () => {
        console.log('[WS] disconnected, reconnecting in 3s...')
        setTimeout(createWebSocket, 3000)
    }
}

function showToast(message) {
    const toast = document.createElement('div')
    toast.textContent = message
    toast.className = 'toast'
    document.body.appendChild(toast)
    setTimeout(() => toast.remove(), 4000)
}

document.getElementById('searchInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') applyFilters()
})

document.getElementById('parse-btn').addEventListener('click', runParse)

createWebSocket()
loadStats()
loadVacancies()
loadSkillsChart()