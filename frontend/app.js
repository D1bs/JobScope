let skillsChart = null
let salaryChart = null
let allSkillsData = []
let currentN = 10

async function loadStats(filters = {}) {
    const params = new URLSearchParams(
        Object.entries(filters).filter(([, v]) => v)
    )
    const res = await fetch(`/stats?${params}`)
    const data = await res.json()
    document.getElementById('total-vacancies').textContent = data.total_vacancies.toLocaleString('ru')
    document.getElementById('avg-salary').textContent = data.avg_salary
        ? Math.round(data.avg_salary).toLocaleString('ru')
        : '—'
}

async function loadVacancies(filters = {}) {
    const params = new URLSearchParams(
        Object.entries(filters).filter(([, v]) => v)
    )
    const res = await fetch(`/vacancies?${params}`)
    const data = await res.json()
    const tbody = document.getElementById('vacancies-table')
    tbody.innerHTML = ''

    if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:32px">Вакансии не найдены</td></tr>`
        return
    }

    for (const v of data) {
        const scheduleBadge = getBadge(v.schedule)
        const salFrom = v.salary_from
            ? `<span class="salary">${v.salary_from.toLocaleString('ru')}</span>`
            : `<span class="salary-none">—</span>`
        const salTo = v.salary_to
            ? `<span class="salary">${v.salary_to.toLocaleString('ru')}</span>`
            : `<span class="salary-none">—</span>`
        tbody.innerHTML += `
            <tr>
                <td><a href="${v.url}" target="_blank" style="color:inherit;text-decoration:none;">${v.title}</a></td>
                <td>${v.company}</td>
                <td>${v.city}</td>
                <td>${scheduleBadge}</td>
                <td>${v.employment ?? '—'}</td>
                <td>${salFrom}</td>
                <td>${salTo}</td>
            </tr>`
    }

    buildSalaryChart(data)
}

function getBadge(schedule) {
    if (!schedule) return '<span class="salary-none">—</span>'
    if (schedule.includes('Удалён')) return `<span class="badge badge-remote">${schedule}</span>`
    if (schedule.includes('Полный')) return `<span class="badge badge-full">${schedule}</span>`
    return `<span class="badge badge-other">${schedule}</span>`
}

async function loadSkillsChart(n = 10, filters = {}) {
    const params = new URLSearchParams(
        Object.entries(filters).filter(([, v]) => v)
    )
    const res = await fetch(`/skills?${params}`)
    const data = await res.json()
    allSkillsData = data.skills

    if (allSkillsData.length) {
        document.getElementById('top-skill').textContent = allSkillsData[0].name
    }

    renderSkillsChart(n)
}

function renderSkillsChart(n) {
    const slice = allSkillsData.slice(0, n)
    const labels = slice.map(s => s.name)
    const counts = slice.map(s => s.count)
    const maxVal = Math.max(...counts)

    const colors = counts.map(c => {
        const ratio = c / maxVal
        const alpha = 0.4 + ratio * 0.6
        return `rgba(124, 108, 252, ${alpha})`
    })

    if (skillsChart) skillsChart.destroy()

    const ctx = document.getElementById('skillsChart').getContext('2d')
    skillsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data: counts,
                backgroundColor: colors,
                borderColor: 'rgba(124,108,252,0.8)',
                borderWidth: 1,
                borderRadius: 5,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1c1c22',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleColor: '#f0f0f4',
                    bodyColor: '#9999aa',
                    padding: 10,
                    callbacks: { label: ctx => ` ${ctx.parsed.y} вакансий` }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#6b6b7a', font: { size: 11, family: 'DM Sans' } },
                    border: { color: 'transparent' }
                },
                y: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#6b6b7a', font: { size: 11, family: 'DM Sans' }, precision: 0 },
                    border: { color: 'transparent' }
                }
            }
        }
    })
}

function buildSalaryChart(vacancies) {
    const buckets = { '0–50k': 0, '50–100k': 0, '100–200k': 0, '200–350k': 0, '350k+': 0 }

    for (const v of vacancies) {
        const s = v.salary_from
        if (!s) continue
        if (s < 50000) buckets['0–50k']++
        else if (s < 100000) buckets['50–100k']++
        else if (s < 200000) buckets['100–200k']++
        else if (s < 350000) buckets['200–350k']++
        else buckets['350k+']++
    }

    const labels = Object.keys(buckets)
    const counts = Object.values(buckets)

    if (salaryChart) salaryChart.destroy()

    const ctx = document.getElementById('salaryChart').getContext('2d')
    salaryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(124,108,252,0.3)',
                    'rgba(124,108,252,0.5)',
                    'rgba(124,108,252,0.7)',
                    'rgba(167,139,250,0.85)',
                    'rgba(167,139,250,1)',
                ],
                borderColor: '#141418',
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9999aa',
                        font: { size: 11, family: 'DM Sans' },
                        padding: 12,
                        usePointStyle: true,
                        pointStyleWidth: 8
                    }
                },
                tooltip: {
                    backgroundColor: '#1c1c22',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    titleColor: '#f0f0f4',
                    bodyColor: '#9999aa',
                    padding: 10,
                    callbacks: { label: ctx => ` ${ctx.parsed} вакансий` }
                }
            }
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
    const filters = getFilters()
    loadVacancies(filters)
    loadStats(filters)
    loadSkillsChart(currentN, filters)
}

function resetFilters() {
    document.getElementById('searchInput').value      = ''
    document.getElementById('salaryInput').value      = ''
    document.getElementById('scheduleSelect').value   = ''
    document.getElementById('employmentSelect').value = ''
    loadVacancies()
    loadStats()
    loadSkillsChart(currentN)
}

async function runParse() {
    const btn = document.getElementById('parse-btn')
    const svg = btn.querySelector('svg')
    btn.disabled = true
    svg.classList.add('spinning')
    btn.childNodes[1].textContent = ' Обновление...'

    await fetch('/parse?query=Python&city_id=1002', { method: 'POST' })

    setTimeout(async () => {
        await Promise.all([loadStats(), loadVacancies(), loadSkillsChart(currentN)])
        btn.disabled = false
        svg.classList.remove('spinning')
        btn.childNodes[1].textContent = ' Обновить данные'
        showToast('Данные обновлены')
    }, 5000)
}

function showToast(msg) {
    const toast = document.getElementById('toast')
    toast.textContent = msg
    toast.style.display = 'block'
    clearTimeout(toast._t)
    toast._t = setTimeout(() => { toast.style.display = 'none' }, 3500)
}

function createWebSocket() {
    const host = window.location.host
    const ws = new WebSocket(`ws://${host}/ws`)

    ws.onopen = () => {
        document.getElementById('status-dot').className = 'status-dot connected'
        document.getElementById('status-text').textContent = 'Подключено'
    }

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'new_vacancies') {
            showToast(`Добавлено вакансий: ${data.count}`)
            loadVacancies(getFilters())
            loadStats(getFilters())
            loadSkillsChart(currentN, getFilters())
        }
    }

    ws.onclose = () => {
        document.getElementById('status-dot').className = 'status-dot'
        document.getElementById('status-text').textContent = 'Переподключение...'
        setTimeout(createWebSocket, 3000)
    }
}

document.getElementById('parse-btn').addEventListener('click', runParse)

document.getElementById('searchInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') applyFilters()
})

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'))
        tab.classList.add('active')
        currentN = parseInt(tab.dataset.n)
        renderSkillsChart(currentN)
    })
})

createWebSocket()
loadStats()
loadVacancies()
loadSkillsChart()