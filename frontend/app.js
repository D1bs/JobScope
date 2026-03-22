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

async function loadSkillsChart() {
    const response = await fetch('/skills')
    const data = await response.json()

    const labels = data.skills.map(s => s.name)
    const counts = data.skills.map(s => s.count)

    new Chart(document.getElementById('skillsChart'), {
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

document.getElementById('parse-btn').addEventListener('click', runParse)

loadStats()
loadVacancies()
loadSkillsChart()

