<template>
  <div class="result-detail">
    <div class="detail-header">
      <button @click="$router.back()" class="btn btn-back">← 返回</button>
      <div class="header-actions">
        <button v-if="result?.report_url" @click="viewReport" class="btn btn-primary">📊 查看报告</button>
        <button @click="refreshResult" class="btn btn-refresh" :disabled="refreshing">
          {{ refreshing ? '刷新中...' : '↻ 刷新状态' }}
        </button>
        <button @click="deleteResult" class="btn btn-danger">删除</button>
      </div>
    </div>

    <div v-if="result" class="info-card card">
      <div class="card-title-row">
        <h2>执行记录 #{{ result.id }}</h2>
        <span class="status-badge" :class="getStatusClass(result.status)">
          {{ getStatusText(result.status) }}
        </span>
      </div>

      <div class="info-grid">
        <div class="info-item">
          <label>测试套件</label>
          <span>{{ result.suite_name || `套件 #${result.suite}` }}</span>
        </div>
        <div class="info-item">
          <label>所属项目</label>
          <span>{{ result.project_name || `项目 #${result.project}` }}</span>
        </div>
        <div class="info-item">
          <label>执行结果</label>
          <span v-if="result.status === 4" :class="result.is_pass ? 'pass-badge' : 'fail-badge'">
            {{ result.is_pass ? '✓ 通过' : '✗ 失败' }}
          </span>
          <span v-else>-</span>
        </div>
        <div class="info-item">
          <label>创建时间</label>
          <span>{{ formatDate(result.created_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="result" class="log-card card">
      <div class="log-card-header">
        <h3>执行日志</h3>
        <div class="log-controls">
          <span class="log-status-text">
            <span v-if="polling" class="live-dot"></span>
            {{ polling ? '实时更新中...' : '已完成' }}
          </span>
          <label class="auto-scroll-label">
            <input type="checkbox" v-model="autoScroll" /> 自动滚动
          </label>
        </div>
      </div>
      <div class="log-body" ref="logContainer">
        <pre class="log-content">{{ logContent || '暂无日志，请稍候...' }}</pre>
      </div>
    </div>

    <div v-if="!result && !loading" class="empty-state card">
      未找到执行记录
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRunResult, deleteRunResult } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const result = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const logContent = ref('')
const autoScroll = ref(true)
const polling = ref(false)
const logContainer = ref(null)
let logTimer = null

const loadResult = async () => {
  loading.value = true
  try {
    const res = await getRunResult(route.params.id)
    result.value = res.result || res
  } catch (e) {
    console.error('加载执行结果失败:', e)
  } finally {
    loading.value = false
  }
}

const fetchLog = async () => {
  if (!result.value?.log_url) return
  try {
    const res = await axios.get(result.value.log_url, {
      responseType: 'text',
      params: { _t: Date.now() },
    })
    const text = typeof res.data === 'string' ? res.data : String(res.data)
    if (text !== logContent.value) {
      logContent.value = text
      if (autoScroll.value) {
        await nextTick()
        if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    }
  } catch { /* 日志文件可能还未生成 */ }
}

const startPolling = () => {
  stopPolling()
  polling.value = true
  fetchLog()
  logTimer = setInterval(async () => {
    try {
      const res = await getRunResult(result.value.id)
      result.value = { ...result.value, ...(res.result || res) }
      await fetchLog()
      if (result.value.status === 4 || result.value.status === -1) {
        stopPolling()
      }
    } catch { /* ignore */ }
  }, 3000)
}

const stopPolling = () => {
  polling.value = false
  if (logTimer) { clearInterval(logTimer); logTimer = null }
}

const refreshResult = async () => {
  refreshing.value = true
  try {
    const res = await getRunResult(result.value.id)
    result.value = { ...result.value, ...(res.result || res) }
    await fetchLog()
  } catch (e) {
    console.error('刷新失败:', e)
  } finally {
    refreshing.value = false
  }
}

const deleteResult = async () => {
  const confirmed = await confirm('确定要删除这条执行记录吗？', { type: 'danger' })
  if (!confirmed) return
  try {
    await deleteRunResult(result.value.id)
    router.push('/results')
  } catch (e) {
    console.error('删除失败:', e)
  }
}

const viewReport = () => {
  if (result.value?.report_url) window.open(result.value.report_url, '_blank')
  else alert('报告尚未生成，请稍后查看')
}

const getStatusClass = (status) => ({
  0: 'status-init', 1: 'status-ready', 2: 'status-running',
  3: 'status-reporting', 4: 'status-done', '-1': 'status-error'
}[status] || 'status-init')

const getStatusText = (status) => ({
  0: '初始化', 1: '准备开始', 2: '正在执行',
  3: '生成报告', 4: '执行完毕', '-1': '执行出错'
}[status] || '未知')

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

onMounted(async () => {
  await loadResult()
  if (result.value) {
    const isDone = result.value.status === 4 || result.value.status === -1
    isDone ? fetchLog() : startPolling()
  }
})
onUnmounted(() => stopPolling())
</script>

<style scoped>
.result-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 100%;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.log-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-back   { background: white; border: 1px solid var(--border); color: var(--text); }
.btn-refresh { background: #8e44ad; color: white; }
.btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }

/* ---- 信息卡片 ---- */
.info-card { margin-bottom: 4px; }

.card-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.card-title-row h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label {
  font-size: 11px;
  color: var(--text-light);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.info-item span {
  font-size: 15px;
  color: var(--text);
}

/* ---- 日志卡片 ---- */
.log-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.log-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  background: white;
}

.log-card-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.log-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.log-status-text {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-light);
}

.live-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #2ecc71;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.8); }
}

.auto-scroll-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-light);
  cursor: pointer;
  user-select: none;
}

.log-body {
  background: #0d1117;
  padding: 16px 20px;
  overflow-y: auto;
  height: calc(100vh - 260px);
  min-height: 480px;
}

.log-content {
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #c9d1d9;
  white-space: pre-wrap;
  word-break: break-all;
}

/* ---- badges ---- */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.status-init, .status-ready   { background: #e3f2fd; color: #1976d2; }
.status-running, .status-reporting { background: #fff3e0; color: #f57c00; }
.status-done   { background: #e8f5e9; color: #388e3c; }
.status-error  { background: #ffebee; color: #d32f2f; }
.pass-badge { color: #27ae60; font-weight: 600; font-size: 15px; }
.fail-badge { color: #e74c3c; font-weight: 600; font-size: 15px; }

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--text-light);
  font-size: 15px;
}
</style>
