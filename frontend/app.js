let skillsChart = null
let salaryChart = null
let allSkillsData = []
let currentN = 10
let currentFilters = {}
let currentOffset = 0
let isLoading = false
let hasMore = true

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

async function loadVacancies(filters = {}, reset = true) {
    if (isLoading) return
    if (!reset && !hasMore) return

    isLoading = true

    if (reset) {
        currentOffset = 0
        hasMore = true
        currentFilters = filters
        document.getElementById('vacancies-table').innerHTML = ''
    }

    const params = new URLSearchParams(
        Object.entries(currentFilters).filter(([, v]) => v)
    )
    params.set('offset', currentOffset)

    const res = await fetch(`/vacancies?${params}`)
    const data = await res.json()

    hasMore = data.has_more
    currentOffset += data.items.length

    const tbody = document.getElementById('vacancies-table')

    if (reset && !data.items.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:32px">Вакансии не найдены</td></tr>`
        isLoading = false
        return
    }

    for (const v of data.items) {
        const scheduleBadge = getBadge(v.schedule)
        const salFrom = v.salary_from_byn
            ? `<span class="salary">${v.salary_from_byn.toLocaleString('ru')} BYN</span>`
            : `<span class="salary-none">—</span>`
        const salTo = v.salary_to_byn
            ? `<span class="salary">${v.salary_to_byn.toLocaleString('ru')} BYN</span>`
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

    isLoading = false
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

async function buildSalaryChart(filters = {}) {
    const params = new URLSearchParams(
        Object.entries(filters).filter(([, v]) => v)
    )
    const res = await fetch(`/stats/salary-distribution?${params}`)
    const data = await res.json()

    const labels = Object.keys(data.distribution)
    const counts = Object.values(data.distribution)

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
    loadVacancies(filters, true)
    loadStats(filters)
    loadSkillsChart(currentN, filters)
    buildSalaryChart(filters)
}

function resetFilters() {
    document.getElementById('searchInput').value      = ''
    document.getElementById('salaryInput').value      = ''
    document.getElementById('scheduleSelect').value   = ''
    document.getElementById('employmentSelect').value = ''
    loadVacancies({}, true)
    loadStats()
    loadSkillsChart(currentN)
    buildSalaryChart()
}

async function runParse() {
    const btn = document.getElementById('parse-btn')
    const svg = btn.querySelector('svg')
    btn.disabled = true
    svg.classList.add('spinning')
    btn.childNodes[1].textContent = ' Обновление...'

    await fetch('/parse?query=Python&city_id=1002', { method: 'POST' })

    setTimeout(async () => {
        await Promise.all([loadStats(), loadVacancies({}, true), loadSkillsChart(currentN)])
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
            loadVacancies(currentFilters, true)
            loadStats(currentFilters)
            loadSkillsChart(currentN, currentFilters)
        }
    }

    ws.onclose = () => {
        document.getElementById('status-dot').className = 'status-dot'
        document.getElementById('status-text').textContent = 'Переподключение...'
        setTimeout(createWebSocket, 3000)
    }
}

window.addEventListener('scroll', () => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement
    if (scrollHeight - scrollTop - clientHeight < 200) {
        loadVacancies({}, false)
    }
})

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
loadVacancies({}, true)
loadSkillsChart()
buildSalaryChart()