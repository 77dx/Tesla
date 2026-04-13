<template>
  <div class="perf-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">⚡ 性能测试</h1>
        <span class="page-sub">基于 Locust 的接口压测平台</span>
      </div>
      <button class="btn btn-primary" @click="openCreate">+ 新建压测配置</button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索配置名/套件名..." @keyup.enter="loadConfigs" />
      </div>
      <button class="btn btn-primary btn-sm" @click="loadConfigs">搜索</button>
      <button class="btn btn-sm" @click="searchText = ''; loadConfigs()">重置</button>
    </div>

    <!-- 配置列表 -->
    <div class="table-container card">
      <table class="table">
        <thead><tr>
          <th>ID</th><th>压测名称</th><th>并发/时长</th>
          <th>最新状态</th><th>最新 RPS</th><th>最新平均响应</th>
          <th class="col-fail">最新失败率</th><th>执行次数</th><th>创建时间</th><th>操作</th>
        </tr></thead>
        <tbody>
          <tr v-if="loading"><td colspan="10" class="empty-state">加载中...</td></tr>
          <tr v-else-if="!configs.length"><td colspan="10" class="empty-state">暂无压测配置，点击「新建压测配置」开始</td></tr>
          <tr v-else v-for="cfg in configs" :key="cfg.id" class="data-row" @click="openConfigDetail(cfg)">
            <td class="col-id">{{ cfg.id }}</td>
            <td class="col-name">{{ cfg.display_name }}</td>
            <td class="col-meta">
              <span class="meta-chip">👥{{ cfg.users }}</span>
              <span class="meta-chip">⏱{{ cfg.run_time }}s</span>
              <span class="meta-chip">📈{{ cfg.spawn_rate }}/s</span>
            </td>
            <td>
              <span v-if="cfg.latest_result" class="status-badge" :class="'status-' + cfg.latest_result.status">{{ statusLabel(cfg.latest_result.status) }}</span>
              <span v-else class="col-dash">—</span>
            </td>
            <td class="col-num">{{ cfg.latest_result?.summary?.rps?.toFixed(1) ?? '—' }}</td>
            <td class="col-num">{{ cfg.latest_result?.summary?.avg_response_ms ? cfg.latest_result.summary.avg_response_ms.toFixed(0) + 'ms' : '—' }}</td>
            <td class="col-fail">
              <span v-if="cfg.latest_result?.summary" class="fail-rate-badge"
                :class="cfg.latest_result.summary.failure_rate > 0.05 ? 'fail-high' : cfg.latest_result.summary.failure_rate > 0 ? 'fail-mid' : 'fail-ok'"
              >{{ (cfg.latest_result.summary.failure_rate * 100).toFixed(1) }}%</span>
              <span v-else class="col-dash">—</span>
            </td>
            <td><span class="count-badge">{{ cfg.result_count }} 次</span></td>
            <td class="col-time">{{ formatTime(cfg.created_at) }}</td>
            <td @click.stop>
              <div class="action-wrap">
                <button class="btn-action btn-info" @click="openEdit(cfg)">编辑</button>
                <button class="btn-action btn-success"
                  :disabled="cfg.latest_result?.status === 'running' || cfg.latest_result?.status === 'pending'"
                  @click="handleRun(cfg)"
                >{{ cfg.latest_result?.status === 'running' ? '压测中' : cfg.latest_result?.status === 'pending' ? '等待中' : '▶ 运行' }}</button>
                <button class="btn-action btn-danger" @click="handleDeleteConfig(cfg)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新建/编辑配置弹窗 -->
    <teleport to="body">
      <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
        <div class="modal">
          <div class="modal-header">
            <h3>{{ editingConfig ? '编辑压测配置' : '新建压测配置' }}</h3>
            <button class="btn-close" @click="showForm = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group"><label>压测名称</label>
              <input v-model="form.name" type="text" class="form-control" placeholder="留空则自动使用套件名称" />
            </div>
            <div class="form-group"><label>选择套件 <span class="required">*</span></label>
              <select v-model="form.suite" class="form-control" @change="onSuiteChange" :disabled="!!editingConfig">
                <option value="">请选择套件</option>
                <option v-for="s in suiteOptions" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <div v-if="editingConfig" class="env-tip">编辑配置时套件不可更改</div>
            </div>
            <div class="form-row">
              <div class="form-group"><label>并发用户数</label><input v-model.number="form.users" type="number" min="1" max="1000" class="form-control" /></div>
              <div class="form-group"><label>每秒启动用户数</label><input v-model.number="form.spawn_rate" type="number" min="1" class="form-control" /></div>
              <div class="form-group"><label>持续时间（秒）</label><input v-model.number="form.run_time" type="number" min="10" max="3600" class="form-control" /></div>
            </div>
            <div class="form-group"><label>运行环境</label>
              <select v-model="form.environment_id" class="form-control" :disabled="!form.suite">
                <option value="">{{ form.suite ? (envOptions.length ? '留空从套件配置读取' : '该项目无可用环境') : '请先选择套件' }}</option>
                <option v-for="e in envOptions" :key="e.id" :value="e.id">{{ e.name }}{{ e.base_url ? ' — ' + e.base_url : '' }}</option>
              </select>
              <div v-if="selectedEnvHost" class="env-hint">Host: {{ selectedEnvHost }}</div>
              <div class="env-tip">💡 此处选择的环境仅用于获取压测 Host</div>
            </div>
            <div class="spawn-preview">预计 {{ Math.ceil(form.users / form.spawn_rate) }}s 后达到 {{ form.users }} 个并发用户，持续压测 {{ form.run_time }}s</div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="showForm = false">取消</button>
            <button class="btn btn-primary" :disabled="saving || !form.suite" @click="handleSave">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </div>
      </div>
    </teleport>
    <!-- 配置详情弹窗 -->
    <teleport to="body">
      <div v-if="activeConfig" class="modal-overlay" @click.self="closeConfigDetail">
        <div class="modal modal-xl">
          <div class="modal-header">
            <div class="header-title-wrap">
              <h3>{{ activeConfig.display_name }}</h3>
              <div class="header-suite-tag">{{ activeConfig.suite_name }}</div>
            </div>
            <button class="btn-close" @click="closeConfigDetail">×</button>
          </div>
          <div class="modal-body detail-layout">
            <div class="history-panel">
              <div class="history-header"><span class="history-title">执行历史</span><span class="history-count">{{ results.length }} 次</span></div>
              <div v-if="resultsLoading" class="empty-state">加载中...</div>
              <div v-else-if="!results.length" class="empty-state">暂无执行记录</div>
              <div v-else class="history-list">
                <div v-for="r in results" :key="r.id" class="history-item" :class="{ active: activeResult?.id === r.id }" @click="selectResult(r)">
                  <div class="hi-top">
                    <span class="hi-id">#{{ r.id }}</span>
                    <span class="status-badge" :class="'status-' + r.status">{{ statusLabel(r.status) }}</span>
                    <div class="hi-actions" @click.stop>
                      <button v-if="r.status === 'running'" class="btn-xs btn-danger-xs" @click="handleStopResult(r)">停止</button>
                      <button class="btn-xs btn-gray-xs" @click="handleDeleteResult(r)">删除</button>
                    </div>
                  </div>
                  <div class="hi-meta">
                    <span class="hi-chip">👥 {{ r.users }} 并发</span>
                    <span class="hi-chip">📈 {{ r.spawn_rate }}/s</span>
                    <span class="hi-chip">⏱ {{ r.run_time }}s</span>
                    <span v-if="r.host" class="hi-chip hi-host" :title="r.host">🌐 {{ r.host }}</span>
                    <span v-if="r.summary" :class="r.summary.failure_rate > 0.05 ? 'hi-fail-high' : 'hi-fail-ok'">失败 {{ (r.summary.failure_rate*100).toFixed(1) }}%</span>
                    <span v-if="r.summary">RPS {{ r.summary.rps?.toFixed(1) }}</span>
                  </div>
                  <div class="hi-time">{{ formatTime(r.created_at) }}</div>
                </div>
              </div>
            </div>
            <div class="result-panel">
              <div v-if="!activeResult" class="empty-state" style="margin-top:80px">← 点击左侧执行记录查看详情</div>
              <div v-else>
                <div class="detail-tabs">
                  <button class="detail-tab" :class="{active:detailTab==='chart'}" @click="detailTab='chart'">📈 图表</button>
                  <button class="detail-tab" :class="{active:detailTab==='log'}" @click="detailTab='log';fetchLog()">📋 日志</button>
                </div>
                <div v-show="detailTab==='chart'">
                  <!-- 多次对比 Tab -->
                  <div class="compare-tabs">
                    <button class="compare-tab" :class="{active:compareTab==='all'}" @click="compareTab='all'">🔀 全部对比</button>
                    <button v-for="(r,i) in doneResults" :key="r.id"
                      class="compare-tab" :class="{active:compareTab===r.id}"
                      @click="compareTab=r.id; selectResult(r)"
                    >第{{ i+1 }}次<span class="ct-meta"> {{ r.users }}并发 {{ r.spawn_rate }}/s {{ r.run_time }}s</span></button>
                  </div>
                  <!-- 单次执行指标（非全部模式）-->
                  <div v-if="compareTab!=='all'&&activeResult" class="compare-single-header">
                    <div class="csh-left">
                      <span class="rd-title">执行 #{{ activeResult.id }}</span>
                      <span class="status-badge" :class="'status-'+activeResult.status">{{ statusLabel(activeResult.status) }}</span>
                    </div>
                    <button v-if="activeResult.status==='done'||activeResult.status==='stopped'" class="btn btn-sm btn-ghost" @click="openReport">查看报告</button>
                  </div>
                  <div class="metrics-grid" :class="compareTab==='all'?'metrics-compact':''">
                    <template v-if="compareTab==='all'">
                      <div class="metric-card"><div class="metric-value">{{ doneResults.length }}</div><div class="metric-label">已执行次数</div></div>
                      <div class="metric-card"><div class="metric-value">{{ doneResults.filter(r=>r.summary).length ? Math.max(...doneResults.filter(r=>r.summary).map(r=>r.summary.rps||0)).toFixed(1) : '—' }}</div><div class="metric-label">最高 RPS</div></div>
                      <div class="metric-card"><div class="metric-value">{{ doneResults.filter(r=>r.summary).length ? Math.min(...doneResults.filter(r=>r.summary).map(r=>r.summary.avg_response_ms||9999)).toFixed(0)+'ms' : '—' }}</div><div class="metric-label">最低平均响应</div></div>
                      <div class="metric-card"><div class="metric-value">{{ doneResults.filter(r=>r.summary).length ? Math.min(...doneResults.filter(r=>r.summary).map(r=>(r.summary.failure_rate||0)*100)).toFixed(1)+'%' : '—' }}</div><div class="metric-label">最低失败率</div></div>
                      <div class="metric-card"><div class="metric-value">{{ doneResults.filter(r=>r.summary).length ? Math.max(...doneResults.filter(r=>r.summary).map(r=>r.users||0)) : '—' }}</div><div class="metric-label">最大并发</div></div>
                      <div class="metric-card"><div class="metric-value">{{ doneResults.filter(r=>r.summary).reduce((s,r)=>s+(r.summary?.total_requests||0),0).toLocaleString() }}</div><div class="metric-label">累计请求数</div></div>
                    </template>
                    <template v-else>
                      <div class="metric-card"><div class="metric-value">{{ currentUsers }}</div><div class="metric-label">并发用户</div></div>
                      <div class="metric-card"><div class="metric-value">{{ currentRps }}</div><div class="metric-label">RPS</div></div>
                      <div class="metric-card"><div class="metric-value">{{ currentAvgRt }}ms</div><div class="metric-label">平均响应</div></div>
                      <div class="metric-card" :class="currentFailRate > 5 ? 'metric-err' : ''"><div class="metric-value">{{ currentFailRate }}%</div><div class="metric-label">失败率</div></div>
                      <div class="metric-card"><div class="metric-value">{{ totalRequests }}</div><div class="metric-label">总请求数</div></div>
                      <div class="metric-card"><div class="metric-value">{{ elapsedTime }}s</div><div class="metric-label">已执行</div></div>
                    </template>
                  </div>
                  <div class="chart-tabs"><button v-for="ct in chartTabs" :key="ct.key" class="chart-tab" :class="{active:activeChart===ct.key}" @click="activeChart=ct.key">{{ ct.label }}</button></div>
                  <div class="chart-wrap">
                    <svg class="line-chart" viewBox="0 0 800 220" preserveAspectRatio="none">
                      <defs><linearGradient id="pg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4f8ef7" stop-opacity=".3"/><stop offset="100%" stop-color="#4f8ef7" stop-opacity="0"/></linearGradient></defs>
                      <line x1="40" y1="0" x2="40" y2="190" stroke="#e5e7eb" stroke-width="1"/><line x1="40" y1="190" x2="800" y2="190" stroke="#e5e7eb" stroke-width="1"/>
                      <text x="5" y="12" font-size="10" fill="#9ca3af">{{ multiChartMax }}</text><text x="5" y="97" font-size="10" fill="#9ca3af">{{ Math.round(multiChartMax/2) }}</text><text x="5" y="192" font-size="10" fill="#9ca3af">0</text>
                      <g v-for="(s,i) in multiSeries" :key="s.id">
                        <path v-if="s.area&&compareTab!=='all'" :d="s.area" fill="url(#pg)" opacity="0.5"/>
                        <path v-if="s.line" :d="s.line" fill="none" :stroke="seriesColors[i%seriesColors.length]" stroke-width="2" stroke-linejoin="round"/>
                      </g>
                      <text v-if="!multiSeries.length" x="400" y="100" font-size="14" fill="#d1d5db" text-anchor="middle">暂无数据</text>
                    </svg>
                    <div v-if="compareTab==='all'&&multiSeries.length>1" class="chart-legend">
                      <span v-for="(s,i) in multiSeries" :key="s.id" class="legend-item">
                        <span class="legend-dot" :style="{background:seriesColors[i%seriesColors.length]}"></span>
                        第{{ doneResults.findIndex(r=>r.id===s.id)+1 }}次 ({{ s.users }}并发)
                      </span>
                    </div>
                  </div>
                  <!-- 对比汇总表 -->
                  <div v-if="compareRows.length" class="compare-table-wrap">
                    <div class="summary-title">📊 {{ compareTab==='all' ? '所有结果对比' : '压测结果汇总' }}</div>
                    <table class="compare-table">
                      <thead><tr>
                        <th>指标</th>
                        <th v-for="(r,i) in compareRows" :key="r.id">
                          第{{ doneResults.findIndex(x=>x.id===r.id)+1 }}次<br><span class="ct-sub">{{ r.users }}并发/{{ r.run_time }}s</span>
                        </th>
                      </tr></thead>
                      <tbody>
                        <tr v-for="metric in compareMetrics" :key="metric.key">
                          <td class="ct-label">{{ metric.label }}</td>
                          <td v-for="r in compareRows" :key="r.id" :class="getCellClass(metric,r,compareRows)">{{ formatMetric(metric,r.summary) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
                <div v-show="detailTab==='log'" class="log-panel">
                  <div class="log-toolbar"><span class="log-title">locust.log</span><span class="log-count">{{ logLines.length }} 行</span><button class="btn btn-sm" @click="fetchLog">↻ 刷新</button><label class="log-auto-wrap"><input type="checkbox" v-model="logAutoScroll" /> 自动滚动</label></div>
                  <pre ref="logContainer" class="log-pre">{{ logLines.join('\n') || '暂无日志' }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  getPerfConfigs, createPerfConfig, updatePerfConfig, deletePerfConfig, runPerfConfig,
  getPerfResults, deletePerfResult, stopPerfResult, getPerfResultStats, getPerfResultLog, getPerfResultReport
} from '@/api/performance'
import api from '@/api/request'

const configs     = ref([])
const loading     = ref(false)
const searchText  = ref('')

async function loadConfigs() {
  loading.value = true
  try {
    const params = {}
    if (searchText.value) params.search = searchText.value
    const res = await getPerfConfigs(params)
    configs.value = res.result?.list || res.list || []
  } finally { loading.value = false }
}

const suiteOptions = ref([])
const envOptions   = ref([])

async function loadSuites() {
  const res = await api.get('/suite/suite/', { params: { page_size: 200 } })
  suiteOptions.value = res.result?.list || res.list || []
}

async function onSuiteChange() {
  form.value.environment_id = ''
  envOptions.value = []
  if (!form.value.suite) return
  const suite = suiteOptions.value.find(s => s.id === form.value.suite)
  if (!suite) return
  try {
    const res = await api.get('/suite/environment/', { params: { project: suite.project, page_size: 100 } })
    envOptions.value = res.result?.list || res.list || res.results || []
  } catch(e) { console.error('[perf] 加载环境失败', e) }
}

const selectedEnvHost = computed(() => {
  if (!form.value.environment_id) return ''
  const env = envOptions.value.find(e => e.id === form.value.environment_id)
  if (!env) return ''
  if (env.urls?.length) { const u = env.urls.find(u => u.url); if (u) return u.url }
  return env.base_url || ''
})

const showForm      = ref(false)
const saving        = ref(false)
const editingConfig = ref(null)
const form = ref({ name: '', suite: '', users: 10, spawn_rate: 2, run_time: 60, environment_id: '' })

function openCreate() {
  editingConfig.value = null
  form.value = { name: '', suite: '', users: 10, spawn_rate: 2, run_time: 60, environment_id: '' }
  envOptions.value = []
  showForm.value = true
  loadSuites()
}

async function openEdit(cfg) {
  editingConfig.value = cfg
  form.value = { name: cfg.name, suite: cfg.suite, users: cfg.users, spawn_rate: cfg.spawn_rate, run_time: cfg.run_time, environment_id: '' }
  envOptions.value = []
  showForm.value = true
  await loadSuites()
  // 加载该套件对应项目的环境列表
  try {
    const res = await api.get('/suite/environment/', { params: { project: cfg.project, page_size: 100 } })
    envOptions.value = res.result?.list || res.list || res.results || []
    // 尝试根据 host 回显环境
    if (cfg.host && envOptions.value.length) {
      const matched = envOptions.value.find(e => {
        const url = e.base_url || (e.urls?.find(u => u.url)?.url) || ''
        return url === cfg.host
      })
      if (matched) form.value.environment_id = matched.id
    }
  } catch(e) { console.error('[perf] 编辑加载环境失败', e) }
}

async function handleSave() {
  if (!form.value.suite) return
  saving.value = true
  try {
    const payload = { name: form.value.name, suite: form.value.suite, users: form.value.users, spawn_rate: form.value.spawn_rate, run_time: form.value.run_time, host: selectedEnvHost.value || '' }
    if (editingConfig.value) {
      await updatePerfConfig(editingConfig.value.id, payload)
    } else {
      await createPerfConfig(payload)
    }
    showForm.value = false
    loadConfigs()
  } finally { saving.value = false }
}

async function handleDeleteConfig(cfg) {
  if (!confirm(`确定删除压测配置「${cfg.display_name}」及其所有执行记录？`)) return
  await deletePerfConfig(cfg.id)
  loadConfigs()
  if (activeConfig.value?.id === cfg.id) closeConfigDetail()
}

const runningResultId = ref(null)

async function handleRun(cfg) {
  if (runningResultId.value !== null) return
  try {
    runningResultId.value = -1
    const res = await runPerfConfig(cfg.id)
    const result = res.result || res
    runningResultId.value = result.id
    loadConfigs()
    if (activeConfig.value?.id === cfg.id) {
      await loadResults(cfg.id)
      const r = results.value.find(r => r.id === result.id)
      if (r) selectResult(r)
    }
  } catch(e) {
    console.error('[perf] run 失败', e)
    runningResultId.value = null
  }
}

const activeConfig   = ref(null)
const results        = ref([])
const resultsLoading = ref(false)

async function openConfigDetail(cfg) {
  activeConfig.value = cfg
  activeResult.value = null
  runningResultId.value = null
  compareTab.value = 'all'
  await loadResults(cfg.id)
  if (results.value.length) selectResult(results.value[0])
}

function closeConfigDetail() {
  stopPolling(); stopLogPolling()
  activeConfig.value = null
  activeResult.value = null
  results.value = []
  runningResultId.value = null
  logLines.value = []
}

async function loadResults(configId) {
  resultsLoading.value = true
  try {
    const res = await getPerfResults({ config: configId })
    results.value = res.result?.list || res.list || []
  } finally { resultsLoading.value = false }
}

const activeResult = ref(null)
const liveData     = ref({ status: '', stats_data: [], summary: null })
let   pollTimer    = null
import { alert } from '@/composables/useAlert'

function selectResult(r) {
  stopPolling(); stopLogPolling()
  detailTab.value = 'chart'
  logLines.value = []
  activeResult.value = r
  liveData.value = { status: r.status, stats_data: r.stats_data || [], summary: r.summary }
  fetchStats(r.id)
  if (r.status === 'running' || r.status === 'pending') { startPolling(r.id); startLogPolling() }
}

function startPolling(id) { stopPolling(); pollTimer = setInterval(() => fetchStats(id), 4000) }
function stopPolling()    { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }

async function fetchStats(id) {
  try {
    const res = await getPerfResultStats(id)
    const r = res.result || res
    liveData.value = { status: r.status, stats_data: r.stats_data || [], summary: r.summary || null }
    if (r.status !== 'running' && r.status !== 'pending') {
      stopPolling(); stopLogPolling()
      if (runningResultId.value === id) runningResultId.value = null
      loadConfigs()
      if (activeConfig.value) loadResults(activeConfig.value.id)
      const idx = results.value.findIndex(x => x.id === id)
      if (idx !== -1) results.value[idx] = { ...results.value[idx], status: r.status, summary: r.summary }
    }
  } catch(e) { console.error('[perf] fetchStats 失败', e) }
}

async function handleStopResult(r) {
  if (!confirm(`确定停止执行 #${r.id}？`)) return
  await stopPerfResult(r.id)
  stopPolling(); stopLogPolling()
  if (activeResult.value?.id === r.id) liveData.value.status = 'stopped'
  if (activeConfig.value) loadResults(activeConfig.value.id)
  loadConfigs()
}

async function handleDeleteResult(r) {
  if (!confirm(`确定删除执行记录 #${r.id}？`)) return
  await deletePerfResult(r.id)
  if (activeResult.value?.id === r.id) { activeResult.value = null; stopPolling(); stopLogPolling() }
  if (activeConfig.value) loadResults(activeConfig.value.id)
  loadConfigs()
}

async function openReport() {
  if (!activeResult.value) return
  try {
    const res = await getPerfResultReport(activeResult.value.id)
    const url = res.result?.report_url || res.report_url
    if (url) window.open(url, '_blank')
    else alert('报告还未生成')
  } catch { alert('获取报告地址失败') }
}

const detailTab     = ref('chart')
const logLines      = ref([])
const logAutoScroll = ref(true)
const logContainer  = ref(null)
let   logTimer      = null

async function fetchLog() {
  if (!activeResult.value) return
  try {
    const res = await getPerfResultLog(activeResult.value.id, 300)
    const r = res.result || res
    logLines.value = r.lines || []
    if (logAutoScroll.value) { await nextTick(); if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight }
  } catch(e) { console.error('[perf] fetchLog 失败', e) }
}
function startLogPolling() { stopLogPolling(); logTimer = setInterval(fetchLog, 3000) }
function stopLogPolling()  { if (logTimer) { clearInterval(logTimer); logTimer = null } }

const lastPoint = computed(() => { const d = liveData.value.stats_data; return d?.length ? d[d.length-1] : null })
const currentUsers    = computed(() => lastPoint.value?.users   ?? activeResult.value?.users ?? 0)
const currentRps      = computed(() => lastPoint.value ? lastPoint.value.rps.toFixed(1) : '0.0')
const currentAvgRt    = computed(() => lastPoint.value ? lastPoint.value.avg_rt.toFixed(0) : '0')
const currentFailRate = computed(() => { if (!lastPoint.value) return '0.0'; const req = lastPoint.value.requests || 1; return ((lastPoint.value.failures/req)*100).toFixed(1) })
const totalRequests   = computed(() => lastPoint.value?.requests ?? 0)
const elapsedTime     = computed(() => lastPoint.value?.elapsed  ?? 0)

const activeChart = ref('rps')
const chartTabs = [{ key: 'rps', label: 'RPS' }, { key: 'avg_rt', label: '响应时间(ms)' }, { key: 'failures', label: '失败数' }]
const chartData = computed(() => (liveData.value.stats_data || []).map(d => d[activeChart.value] || 0))
const chartMax  = computed(() => Math.ceil(Math.max(...chartData.value, 1) * 1.2))

const chartLine = computed(() => {
  const pts = chartData.value; if (pts.length < 2) return ''
  const W=760, H=185, pad=40, mx=chartMax.value
  return 'M ' + pts.map((v,i) => { const x=pad+(i/(pts.length-1))*W; const y=H-(v/mx)*H; return `${x.toFixed(1)},${y.toFixed(1)}` }).join(' L ')
})
const chartArea = computed(() => { if (!chartLine.value) return ''; const W=760,H=185,pad=40; return chartLine.value+` L ${pad+W},${H} L ${pad},${H} Z` })
const chartLabels = computed(() => {
  const data = liveData.value.stats_data || []; if (!data.length) return []
  const W=760, pad=40, step=Math.max(1,Math.floor(data.length/6))
  return data.filter((_,i)=>i%step===0).map((d,i,arr) => ({ x:(pad+(i/Math.max(arr.length-1,1))*W).toFixed(1), label:d.elapsed+'s' }))
})

const statusMap = { pending:'等待中', running:'执行中', done:'已完成', stopped:'已停止', error:'出错' }
const statusLabel = s => statusMap[s] || s
const formatTime  = ts => ts ? new Date(ts).toLocaleString('zh-CN',{hour12:false}) : ''

// ── 多次对比 ──────────────────────────────────────────
const compareTab = ref('all')
const seriesColors = ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#f97316','#84cc16']

// 有 stats_data 的已完成结果
const doneResults = computed(() =>
  results.value.filter(r => (r.status==='done'||r.status==='stopped') && r.stats_data?.length)
)

// 当前对比 tab 对应要渲染的结果集
const activeSeriesResults = computed(() => {
  if (compareTab.value === 'all') return doneResults.value
  const r = doneResults.value.find(r => r.id === compareTab.value)
  return r ? [r] : (activeResult.value ? [activeResult.value] : [])
})

// 多系列折线数据
const multiSeries = computed(() => {
  const W=760, H=185, pad=40
  const allVals = activeSeriesResults.value.flatMap(r => (r.stats_data||[]).map(d => d[activeChart.value]||0))
  const mx = Math.ceil(Math.max(...allVals, 1) * 1.2)
  return activeSeriesResults.value.map(r => {
    const pts = (r.stats_data||[]).map(d => d[activeChart.value]||0)
    if (pts.length < 2) return { id:r.id, users:r.users, line:'', area:'' }
    const line = 'M ' + pts.map((v,i) => {
      const x = pad+(i/(pts.length-1))*W
      const y = H-(v/mx)*H
      return `${x.toFixed(1)},${y.toFixed(1)}`
    }).join(' L ')
    const area = line + ` L ${pad+W},${H} L ${pad},${H} Z`
    return { id:r.id, users:r.users, line, area }
  })
})

const multiChartMax = computed(() => {
  const allVals = activeSeriesResults.value.flatMap(r => (r.stats_data||[]).map(d => d[activeChart.value]||0))
  return Math.ceil(Math.max(...allVals, 1) * 1.2)
})

// 对比汇总表
const compareRows = computed(() => {
  if (compareTab.value === 'all') return doneResults.value.filter(r => r.summary)
  const r = doneResults.value.find(r => r.id === compareTab.value)
  return r?.summary ? [r] : []
})

const compareMetrics = [
  { key: 'total_requests',  label: '总请求数',    fmt: v => v?.toLocaleString() ?? '—',   better: 'high' },
  { key: 'failure_rate',    label: '失败率',      fmt: v => v!=null ? (v*100).toFixed(2)+'%' : '—', better: 'low' },
  { key: 'rps',             label: 'RPS',        fmt: v => v?.toFixed(2) ?? '—',          better: 'high' },
  { key: 'avg_response_ms', label: '平均响应(ms)', fmt: v => v?.toFixed(0) ?? '—',          better: 'low' },
  { key: 'p50_response_ms', label: 'P50(ms)',     fmt: v => v?.toFixed(0) ?? '—',          better: 'low' },
  { key: 'p95_response_ms', label: 'P95(ms)',     fmt: v => v?.toFixed(0) ?? '—',          better: 'low' },
  { key: 'p99_response_ms', label: 'P99(ms)',     fmt: v => v?.toFixed(0) ?? '—',          better: 'low' },
  { key: 'max_response_ms', label: '最大响应(ms)', fmt: v => v?.toFixed(0) ?? '—',          better: 'low' },
]

function formatMetric(metric, summary) {
  if (!summary) return '—'
  return metric.fmt(summary[metric.key])
}

function getCellClass(metric, row, rows) {
  if (!row.summary || rows.length < 2) return ''
  const vals = rows.filter(r => r.summary).map(r => r.summary[metric.key] ?? null).filter(v => v !== null)
  if (vals.length < 2) return ''
  const v = row.summary[metric.key]
  if (v === null || v === undefined) return ''
  const best = metric.better === 'high' ? Math.max(...vals) : Math.min(...vals)
  const worst = metric.better === 'high' ? Math.min(...vals) : Math.max(...vals)
  if (v === best) return 'ct-best'
  if (v === worst) return 'ct-worst'
  return ''
}

onMounted(loadConfigs)
onUnmounted(() => { stopPolling(); stopLogPolling() })
</script>

<style>
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:9999;padding:20px;}
.modal{background:#fff;border-radius:12px;width:520px;max-height:90vh;overflow:hidden;display:flex;flex-direction:column;margin:auto;position:relative;}
.modal-wide{width:900px;max-width:calc(100vw - 40px);}
.modal-xl{width:1100px;max-width:calc(100vw - 40px);}
.modal-header{display:flex;justify-content:space-between;align-items:center;padding:16px 48px 12px 24px;border-bottom:1px solid #e5e7eb;flex-shrink:0;position:relative;}
.modal-header h3{margin:0;font-size:17px;font-weight:700;}
.header-right{display:flex;align-items:center;gap:10px;}
.modal-body{padding:20px 24px;flex:1;overflow-y:auto;}
.modal-footer{padding:12px 24px 18px;display:flex;justify-content:flex-end;gap:10px;border-top:1px solid #e5e7eb;flex-shrink:0;}
.btn-close{position:absolute;top:10px;right:12px;background:none;border:none;font-size:22px;line-height:1;cursor:pointer;color:#9ca3af;width:32px;height:32px;display:flex;align-items:center;justify-content:center;border-radius:6px;transition:background .15s,color .15s;}
.btn-close:hover{background:#f3f4f6;color:#374151;}
</style>

<style scoped>
.perf-page{display:flex;flex-direction:column;gap:16px;}
.page-header{display:flex;justify-content:space-between;align-items:center;}
.header-left{display:flex;align-items:baseline;gap:10px;}
.page-title{font-size:22px;font-weight:700;color:#111827;margin:0;}
.page-sub{font-size:13px;color:#6b7280;}
.filter-bar{display:flex;align-items:center;gap:8px;padding:10px 14px;}
.filter-input-wrap{display:flex;align-items:center;gap:5px;border:1px solid #e5e7eb;border-radius:6px;padding:0 8px;background:#fff;width:220px;}
.filter-icon{color:#9ca3af;font-size:13px;}
.filter-input{border:none;outline:none;padding:7px 0;font-size:13px;width:100%;background:transparent;}
.table-container{overflow-x:auto;}
.table{width:100%;border-collapse:collapse;font-size:13px;}
.table th{padding:10px 14px;text-align:left;background:#f9fafb;color:#6b7280;font-weight:600;border-bottom:1px solid #e5e7eb;white-space:nowrap;}
.table td{padding:11px 14px;border-bottom:1px solid #f3f4f6;vertical-align:middle;}
.data-row{cursor:pointer;transition:background .12s;}
.data-row:hover{background:#f9fafb;}
.col-id{color:#9ca3af;font-size:12px;width:50px;}
.col-name{font-weight:600;color:#111827;}
.col-suite{color:#6b7280;font-size:12px;}
.col-num{font-variant-numeric:tabular-nums;}
.col-time{font-size:12px;color:#9ca3af;white-space:nowrap;}
.col-dash{color:#d1d5db;}
.col-fail{text-align:center;}
.meta-chip{display:inline-block;background:#f3f4f6;border-radius:4px;padding:2px 6px;font-size:11px;color:#6b7280;margin-right:3px;}
.count-badge{display:inline-block;background:#e0e7ff;color:#3730a3;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;}
.fail-rate-badge{display:inline-block;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;}
.fail-ok{background:#d1fae5;color:#065f46;}
.fail-mid{background:#fef3c7;color:#92400e;}
.fail-high{background:#fee2e2;color:#991b1b;}
.status-badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:500;}
.status-pending{background:#fef3c7;color:#d97706;}
.status-running{background:#dbeafe;color:#2563eb;}
.status-done{background:#d1fae5;color:#059669;}
.status-stopped{background:#f3f4f6;color:#6b7280;}
.status-error{background:#fee2e2;color:#dc2626;}
.action-wrap{display:flex;gap:5px;white-space:nowrap;}
.btn-action{padding:4px 10px;border:none;border-radius:4px;cursor:pointer;font-size:12px;color:#fff;transition:opacity .15s;}
.btn-action:hover{opacity:.82;}
.btn-action:disabled{opacity:.45;cursor:not-allowed;}
.btn-info{background:#6366f1;}
.btn-success{background:#10b981;}
.btn-danger{background:#ef4444;}
.empty-state{text-align:center;padding:48px;color:#9ca3af;font-size:14px;}
.btn{padding:8px 18px;border-radius:6px;border:none;cursor:pointer;font-size:14px;font-weight:500;transition:opacity .15s;}
.btn:hover{opacity:.85;}
.btn-sm{padding:6px 14px;font-size:13px;}
.btn-primary{background:#3b82f6;color:#fff;}
.btn-success{background:#10b981;color:#fff;}
.btn-danger{background:#ef4444;color:#fff;}
.btn-ghost{background:#f3f4f6;color:#374151;}
.btn:disabled{opacity:.5;cursor:not-allowed;}
.form-group{margin-bottom:16px;}
.form-group label{display:block;font-size:13px;font-weight:500;margin-bottom:6px;color:#374151;}
.form-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;}
.form-control{width:100%;padding:8px 12px;border:1px solid #d1d5db;border-radius:6px;font-size:14px;box-sizing:border-box;}
.required{color:#ef4444;}
.spawn-preview{background:#f0f9ff;border:1px solid #bae6fd;border-radius:6px;padding:10px 14px;font-size:13px;color:#0369a1;}
.env-hint{margin-top:5px;font-size:12px;color:#6b7280;}
.env-tip{margin-top:6px;font-size:12px;color:#9ca3af;background:#f9fafb;padding:6px 10px;border-radius:4px;}
.header-title-wrap{display:flex;flex-direction:column;align-items:center;flex:1;gap:3px;}
.header-suite-tag{font-size:12px;color:#6b7280;background:#f3f4f6;padding:2px 10px;border-radius:20px;text-align:center;}
.detail-layout{display:flex;gap:16px;padding:16px 20px;overflow:hidden;height:calc(90vh - 130px);}
.history-panel{width:240px;flex-shrink:0;display:flex;flex-direction:column;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;}
.history-header{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:#f9fafb;border-bottom:1px solid #e5e7eb;flex-shrink:0;}
.history-title{font-size:13px;font-weight:600;color:#374151;}
.history-count{font-size:12px;color:#9ca3af;}
.history-list{flex:1;overflow-y:auto;}
.history-item{padding:10px 12px;border-bottom:1px solid #f3f4f6;cursor:pointer;transition:background .12s;}
.history-item:hover{background:#f9fafb;}
.history-item.active{background:#eff6ff;border-left:3px solid #3b82f6;}
.hi-top{display:flex;align-items:center;gap:6px;margin-bottom:4px;}
.hi-id{font-size:12px;font-weight:700;color:#6b7280;}
.hi-actions{margin-left:auto;display:flex;gap:4px;}
.hi-meta{display:flex;gap:6px;flex-wrap:wrap;font-size:11px;color:#6b7280;margin-bottom:2px;}
.hi-time{font-size:11px;color:#9ca3af;}
.hi-chip{display:inline-block;background:#f3f4f6;border:1px solid #e5e7eb;border-radius:4px;padding:1px 6px;font-size:11px;color:#374151;}
.hi-host{max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;vertical-align:middle;display:inline-block;}
.hi-fail-ok{color:#059669;font-weight:600;}
.hi-fail-high{color:#dc2626;font-weight:600;}
.btn-xs{padding:2px 7px;border:none;border-radius:3px;cursor:pointer;font-size:11px;color:#fff;}
.btn-danger-xs{background:#ef4444;}
.btn-gray-xs{background:#9ca3af;}
.result-panel{flex:1;min-width:0;overflow-y:auto;}
.result-detail-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #e5e7eb;}
.rd-title{font-size:15px;font-weight:700;color:#111827;}
.metrics-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:14px;}
.metric-card{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px;text-align:center;}
.metric-card.metric-err{background:#fef2f2;border-color:#fca5a5;}
.metric-value{font-size:18px;font-weight:700;color:#111827;}
.metric-label{font-size:11px;color:#6b7280;margin-top:3px;}
.detail-tabs{display:flex;gap:4px;margin-bottom:12px;border-bottom:2px solid #e5e7eb;}
.detail-tab{padding:6px 16px;border:none;background:none;font-size:13px;font-weight:500;color:#6b7280;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .15s;}
.detail-tab.active{color:#3b82f6;border-bottom-color:#3b82f6;}
.chart-tabs{display:flex;gap:6px;margin-bottom:8px;}
.chart-tab{padding:4px 12px;border:1px solid #e5e7eb;border-radius:5px;background:#fff;font-size:12px;cursor:pointer;color:#6b7280;}
.chart-tab.active{background:#3b82f6;color:#fff;border-color:#3b82f6;}
.chart-wrap{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:6px;overflow:hidden;}
.line-chart{width:100%;height:200px;}
.summary-section{margin-top:12px;}
.summary-title{font-size:14px;font-weight:700;color:#111827;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #e5e7eb;}
.summary-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px;}
.summary-card{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px;text-align:center;border-top:3px solid #3b82f6;}
.summary-card.sc-ok{border-top-color:#10b981;background:#f0fdf4;}
.summary-card.sc-warn{border-top-color:#f59e0b;background:#fffbeb;}
.summary-card.sc-danger{border-top-color:#ef4444;background:#fef2f2;}
.sc-value{font-size:20px;font-weight:800;color:#111827;}
.sc-label{font-size:11px;color:#6b7280;margin-top:3px;}
.summary-metrics{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px 14px;}
.sm-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.sm-row:last-child{margin-bottom:0;}
.sm-label{font-size:12px;color:#6b7280;width:80px;flex-shrink:0;}
.sm-bar-wrap{flex:1;background:#e5e7eb;border-radius:4px;height:7px;overflow:hidden;}
.sm-bar{display:block;height:100%;border-radius:4px;background:#3b82f6;transition:width .4s;}
.sm-bar-p50{background:#10b981;}.sm-bar-p95{background:#f59e0b;}.sm-bar-p99{background:#f97316;}.sm-bar-max{background:#ef4444;}
.sm-val{font-size:12px;font-weight:700;color:#111827;width:55px;text-align:right;flex-shrink:0;}
.compare-tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;padding:10px 12px;background:linear-gradient(135deg,#eff6ff,#f0fdf4);border:1px solid #dbeafe;border-radius:10px;}
.compare-tab{padding:6px 14px;border:1px solid #e5e7eb;border-radius:20px;background:#fff;font-size:12px;font-weight:500;cursor:pointer;color:#374151;transition:all .15s;white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.04);}
.compare-tab.active{background:#3b82f6;color:#fff;border-color:#3b82f6;box-shadow:0 2px 8px rgba(59,130,246,.3);}
.compare-tab:hover:not(.active){background:#f3f4f6;border-color:#d1d5db;}
.ct-meta{font-size:10px;opacity:.75;margin-left:3px;}
.compare-single-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding:8px 12px;background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;}
.csh-left{display:flex;align-items:center;gap:8px;}
.detail-run-btn{margin-left:auto;margin-right:44px;flex-shrink:0;}
.chart-legend{display:flex;flex-wrap:wrap;gap:10px;padding:6px 8px;background:#f9fafb;border-radius:0 0 6px 6px;border:1px solid #e5e7eb;border-top:none;}
.legend-item{display:flex;align-items:center;gap:5px;font-size:12px;color:#374151;}
.legend-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.compare-table-wrap{margin-top:14px;}
.compare-table{width:100%;border-collapse:collapse;font-size:12px;}
.compare-table th{padding:8px 12px;background:#f9fafb;font-weight:600;color:#6b7280;border:1px solid #e5e7eb;text-align:center;white-space:nowrap;}
.compare-table td{padding:7px 12px;border:1px solid #e5e7eb;text-align:center;font-variant-numeric:tabular-nums;}
.ct-label{font-weight:600;color:#374151;text-align:left !important;background:#f9fafb;white-space:nowrap;}
.ct-sub{font-size:10px;color:#9ca3af;font-weight:400;}
.ct-best{background:#d1fae5;color:#065f46;font-weight:700;}
.ct-worst{background:#fee2e2;color:#991b1b;}
.log-toolbar{display:flex;align-items:center;gap:8px;}
.log-title{font-size:13px;font-weight:600;color:#374151;}
.log-count{font-size:11px;color:#9ca3af;}
.log-auto-wrap{display:flex;align-items:center;gap:4px;font-size:12px;color:#6b7280;cursor:pointer;margin-left:auto;}
.log-pre{background:#0d1117;color:#8b949e;padding:12px 14px;border-radius:8px;font-family:'JetBrains Mono','Fira Code',monospace;font-size:12px;line-height:1.7;overflow-y:auto;max-height:340px;white-space:pre-wrap;word-break:break-all;margin:0;}
</style>
