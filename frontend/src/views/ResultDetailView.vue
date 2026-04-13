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

    <div v-if="result" class="snapshot-card card">
      <div class="card-title-row">
        <h3>执行快照</h3>
        <span class="snapshot-meta">{{ filteredSnapshots.length }}/{{ snapshots.length }} 条</span>
      </div>
      <div class="snapshot-tools">
        <label class="snapshot-check">
          <input type="checkbox" v-model="onlyFailedSnapshots" /> 仅看失败用例
        </label>
        <input v-model="snapshotSearch" class="snapshot-search" placeholder="搜索快照（用例名/ID/内容）" />
      </div>
      <div v-if="filteredSnapshots.length" class="snapshot-list">
        <details v-for="s in filteredSnapshots" :key="s.id" class="snapshot-item">
          <summary>
            <div class="snapshot-summary-main">
              <span class="snapshot-case-title">#{{ s.case_id }} {{ s.case_name || '-' }}</span>
              <span class="snapshot-type-badge" :class="(s.payload_json?.execution?.case_type || s.payload_json?.case_type || 'API').toLowerCase()">{{ s.payload_json?.execution?.case_type || s.payload_json?.case_type || 'API' }}</span>
              <span class="snapshot-version">v{{ s.case_version || '-' }}</span>
              <span v-if="snapshotExecutionLabel(s)" class="snapshot-exec-badge" :class="snapshotExecutionClass(s)">{{ snapshotExecutionLabel(s) }}</span>
            </div>
            <span class="snapshot-endpoint-inline">{{ snapshotHeadline(s) }}</span>
          </summary>

          <div class="snapshot-body">
            <div class="snapshot-grid">
              <div class="snapshot-block">
                <div class="snapshot-block-title">基础信息</div>
                <div class="snapshot-kv"><span>用例ID</span><code>{{ s.case_id }}</code></div>
                <div class="snapshot-kv"><span>名称</span><strong>{{ s.case_name || '-' }}</strong></div>
                <div class="snapshot-kv"><span>类型</span><code>{{ s.payload_json?.execution?.case_type || s.payload_json?.case_type || 'API' }}</code></div>
                <div class="snapshot-kv"><span>版本</span><code>v{{ s.case_version || '-' }}</code></div>
                <div class="snapshot-kv"><span>产品线</span><code>{{ s.payload_json?.product_line_id ?? '-' }}</code></div>
                <div class="snapshot-kv"><span>项目</span><code>{{ s.payload_json?.project_id ?? '-' }}</code></div>
              </div>

              <div class="snapshot-block">
                <div class="snapshot-block-title">{{ (s.payload_json?.execution?.case_type || s.payload_json?.case_type) === 'UI' ? 'UI 信息' : '接口信息' }}</div>
                <div class="snapshot-kv"><span>接口ID</span><code>{{ s.payload_json?.endpoint?.id ?? '-' }}</code></div>
                <div class="snapshot-kv"><span>接口名</span><strong>{{ s.payload_json?.endpoint?.name || '-' }}</strong></div>
                <div class="snapshot-kv"><span>请求方法</span><code>{{ s.payload_json?.endpoint?.method || '-' }}</code></div>
                <div class="snapshot-kv"><span>URL</span><code>{{ s.payload_json?.endpoint?.url || s.payload_json?.entry_url || '-' }}</code></div>
                <div class="snapshot-kv"><span>服务标识</span><code>{{ s.payload_json?.endpoint?.service_key || '-' }}</code></div>
              </div>
            </div>

            <div class="snapshot-sections">
              <div class="snapshot-section">
                <div class="snapshot-section-title">请求参数</div>
                <pre class="snapshot-json">{{ prettyJson(s.payload_json?.api_args) }}</pre>
              </div>
              <div class="snapshot-section">
                <div class="snapshot-section-title">数据提取</div>
                <pre class="snapshot-json">{{ prettyJson(s.payload_json?.extract) }}</pre>
              </div>
              <div class="snapshot-section">
                <div class="snapshot-section-title">断言</div>
                <pre class="snapshot-json">{{ prettyJson(s.payload_json?.validate) }}</pre>
              </div>
              <div class="snapshot-section">
                <div class="snapshot-section-title">前置脚本</div>
                <pre class="snapshot-json">{{ prettyJson(s.payload_json?.pre_script) }}</pre>
              </div>
              <div class="snapshot-section">
                <div class="snapshot-section-title">后置脚本</div>
                <pre class="snapshot-json">{{ prettyJson(s.payload_json?.post_script) }}</pre>
              </div>
              <div v-if="s.payload_json?.execution?.screenshots?.length" class="snapshot-section">
                <div class="snapshot-section-title">UI 截图</div>
                <div class="snapshot-shot-list">
                  <a v-for="(shot, idx) in s.payload_json.execution.screenshots" :key="`${s.id}-shot-${idx}`" class="snapshot-shot-link" :href="normalizeArtifactUrl(shot)" target="_blank" rel="noreferrer">
                    截图 {{ idx + 1 }}
                  </a>
                </div>
                <div class="snapshot-shot-preview-grid">
                  <button v-for="(shot, idx) in s.payload_json.execution.screenshots" :key="`${s.id}-img-${idx}`" class="snapshot-shot-button" @click="openLightbox(shot)">
                    <img class="snapshot-shot-preview" :src="normalizeArtifactUrl(shot)" :alt="`截图 ${idx + 1}`" />
                  </button>
                </div>
              </div>
              <div v-if="s.payload_json?.execution" class="snapshot-section">
                <div class="snapshot-section-title">执行结果摘录</div>
                <pre class="snapshot-json">{{ prettyJson(s.payload_json?.execution) }}</pre>
              </div>
            </div>
          </div>
        </details>
      </div>
      <div v-else class="empty-inline">暂无快照</div>
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

    <div v-if="lightboxImage" class="lightbox-overlay" @click.self="closeLightbox">
      <div class="lightbox-box">
        <button class="lightbox-close" @click="closeLightbox">×</button>
        <img class="lightbox-image" :src="normalizeArtifactUrl(lightboxImage)" alt="截图放大预览" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRunResult, deleteRunResult, getExecutionSnapshots } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const result = ref(null)
const loading = ref(false)
const refreshing = ref(false)
const logContent = ref('')
const snapshots = ref([])
const onlyFailedSnapshots = ref(false)
const snapshotSearch = ref('')
const lightboxImage = ref('')
const autoScroll = ref(true)
const polling = ref(false)
const logContainer = ref(null)
let logTimer = null

const loadResult = async () => {
  loading.value = true
  try {
    const res = await getRunResult(route.params.id)
    result.value = res.result || res
    await loadSnapshots()
  } catch (e) {
    console.error('加载执行结果失败:', e)
  } finally {
    loading.value = false
  }
}

const loadSnapshots = async () => {
  if (!result.value) {
    snapshots.value = []
    return
  }
  try {
    if (result.value.snapshot_id) {
      const res = await getExecutionSnapshots({ id: result.value.snapshot_id, page_size: 1 })
      const list = res.result?.list || []
      snapshots.value = list[0]?.case_snapshots || []
      return
    }
    if (!result.value.scope_type || result.value.scope_id == null) {
      snapshots.value = []
      return
    }
    const res = await getExecutionSnapshots({ scope_type: result.value.scope_type, scope_id: result.value.scope_id, page_size: 1 })
    const list = res.result?.list || []
    snapshots.value = list[0]?.case_snapshots || []
  } catch {
    snapshots.value = []
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
const normalizeArtifactUrl = (path) => {
  if (!path) return '#'
  if (String(path).startsWith('http://') || String(path).startsWith('https://') || String(path).startsWith('file://')) return path
  return `file://${path}`
}
const openLightbox = (path) => { lightboxImage.value = path || '' }
const closeLightbox = () => { lightboxImage.value = '' }
const snapshotHeadline = (s) => {
  const caseType = s.payload_json?.execution?.case_type || s.payload_json?.case_type || 'API'
  if (caseType === 'UI') return s.payload_json?.entry_url || s.payload_json?.platform || 'UI 用例'
  return `${s.payload_json?.endpoint?.method || '-'} ${s.payload_json?.endpoint?.name || '-'}`
}
const prettyJson = (obj) => {
  if (obj == null || obj === '') return '—'
  if (typeof obj === 'string') return obj
  return JSON.stringify(obj, null, 2)
}
const snapshotExecutionLabel = (s) => {
  const exec = s.payload_json?.execution
  if (!exec) return ''
  if (exec.is_pass === true) return '执行通过'
  if (exec.is_pass === false) return '执行失败'
  return exec.status || ''
}
const snapshotExecutionClass = (s) => {
  const exec = s.payload_json?.execution
  if (!exec) return ''
  return exec.is_pass === true ? 'exec-pass' : exec.is_pass === false ? 'exec-fail' : 'exec-neutral'
}

const isFailedSnapshot = (s) => {
  const exec = s.payload_json?.execution
  if (exec && typeof exec.is_pass === 'boolean') return !exec.is_pass
  const t = JSON.stringify(s.payload_json || {}).toLowerCase()
  return t.includes('"is_pass":false') || t.includes('"status":-1') || t.includes('"status":"failed"') || t.includes('"status":"error"')
}

const filteredSnapshots = computed(() => {
  let arr = snapshots.value || []
  if (onlyFailedSnapshots.value) {
    arr = arr.filter(isFailedSnapshot)
  }
  const kw = snapshotSearch.value.trim().toLowerCase()
  if (!kw) return arr
  return arr.filter((s) => {
    const base = `${s.case_id} ${s.case_name || ''} ${s.case_version || ''}`.toLowerCase()
    const body = JSON.stringify(s.payload_json || {}).toLowerCase()
    return base.includes(kw) || body.includes(kw)
  })
})

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
.snapshot-card { padding: 16px 20px; }
.snapshot-meta { font-size: 12px; color: var(--text-light); }
.snapshot-tools { display:flex; gap:10px; align-items:center; margin-bottom:10px; }
.snapshot-check { font-size: 13px; color: var(--text); display:flex; align-items:center; gap:6px; }
.snapshot-search { flex:1; min-width:220px; border:1px solid var(--border); border-radius:8px; padding:6px 10px; }
.snapshot-list { display: flex; flex-direction: column; gap: 10px; }
.snapshot-item { border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; background: #fff; }
.snapshot-item summary { display: flex; justify-content: space-between; cursor: pointer; font-weight: 500; }
.snapshot-version { color: #6b7280; font-size: 12px; }
.snapshot-json { margin-top: 8px; background: #0d1117; color: #c9d1d9; padding: 10px; border-radius: 6px; overflow: auto; }
.snapshot-body { margin-top: 12px; display: flex; flex-direction: column; gap: 14px; }
.snapshot-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.snapshot-block { border: 1px solid var(--border); border-radius: 10px; background: #fafcff; padding: 12px; }
.snapshot-block-title, .snapshot-section-title { font-size: 12px; font-weight: 700; color: var(--primary); margin-bottom: 8px; }
.snapshot-kv { display: flex; justify-content: space-between; gap: 12px; padding: 6px 0; border-bottom: 1px dashed #e7eef8; font-size: 13px; }
.snapshot-kv:last-child { border-bottom: none; }
.snapshot-kv span { color: var(--text-light); }
.snapshot-kv code { background: #eef4ff; color: #274472; padding: 2px 6px; border-radius: 6px; }
.snapshot-sections { display: grid; grid-template-columns: 1fr; gap: 12px; }
.snapshot-section { border: 1px solid var(--border); border-radius: 10px; padding: 12px; background: white; }
.snapshot-summary-main { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.snapshot-case-title { font-weight: 700; color: var(--text); }
.snapshot-type-badge { display:inline-flex; align-items:center; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; }
.snapshot-type-badge.api { background:#e8f1ff; color:#2457b2; }
.snapshot-type-badge.ui { background:#e8f7ee; color:#1f8f52; }
.snapshot-endpoint-inline { color: var(--text-light); font-size: 12px; }
.snapshot-shot-list { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px; }
.snapshot-shot-link { display:inline-flex; align-items:center; padding:6px 10px; border-radius:999px; background:#f4f7ff; color:#2457b2; text-decoration:none; font-size:12px; font-weight:700; }
.snapshot-shot-link:hover { background:#e8efff; }
.snapshot-shot-preview-grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:12px; }
.snapshot-shot-button { border:none; background:none; padding:0; cursor:zoom-in; }
.snapshot-shot-preview { width:100%; height:140px; object-fit:cover; border-radius:10px; border:1px solid var(--border); background:#f6f8fb; }
.snapshot-exec-badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.lightbox-overlay { position:fixed; inset:0; background:rgba(0,0,0,.72); display:flex; align-items:center; justify-content:center; z-index:1200; }
.lightbox-box { position:relative; max-width:92vw; max-height:88vh; }
.lightbox-image { max-width:92vw; max-height:88vh; border-radius:14px; box-shadow:0 10px 40px rgba(0,0,0,.35); }
.lightbox-close { position:absolute; top:-14px; right:-14px; width:36px; height:36px; border:none; border-radius:50%; background:#fff; cursor:pointer; font-size:24px; line-height:1; }
.snapshot-exec-badge.exec-pass { background: #e8f7ee; color: #1f8f52; }
.snapshot-exec-badge.exec-fail { background: #fdecec; color: #c0392b; }
.snapshot-exec-badge.exec-neutral { background: #eef2f7; color: #4b5563; }
@media (max-width: 900px) { .snapshot-grid { grid-template-columns: 1fr; } }
.empty-inline { color: var(--text-light); font-size: 13px; }

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
