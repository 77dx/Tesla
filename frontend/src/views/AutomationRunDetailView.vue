<template>
  <div v-if="run" class="run-detail">
    <div class="detail-head card">
      <div>
        <button class="btn btn-refresh" @click="$router.push('/automation')">← 返回</button>
        <h2>UI用例执行 #{{ run.id }}</h2>
        <p>{{ run.suite_name }} · {{ run.automation_project_name }}</p>
      </div>
      <div class="head-actions">
        <span class="status" :class="'s-' + run.status">{{ run.status }}</span>
        <a v-if="reportUrl" class="btn btn-primary" :href="reportUrl" target="_blank" rel="noopener">查看报告</a>
        <button class="btn btn-refresh" @click="loadAll">刷新</button>
      </div>
    </div>

    <div class="detail-grid">
      <div class="card block">
        <h3>执行信息</h3>
        <div class="info-grid">
          <div><label>套件</label><span>{{ run.suite_name }}</span></div>
          <div><label>分支</label><span>{{ run.branch || '-' }}</span></div>
          <div><label>命令</label><code>{{ run.command || '-' }}</code></div>
          <div><label>Base URL</label><span>{{ run.base_url || '-' }}</span></div>
          <div><label>工作目录</label><code>{{ run.workdir || '-' }}</code></div>
          <div><label>日志路径</label><code>{{ run.log_path || '-' }}</code></div>
          <div><label>报告路径</label><code>{{ run.report_path || '-' }}</code></div>
          <div><label>创建时间</label><span>{{ formatDate(run.created_at) }}</span></div>
          <div><label>开始时间</label><span>{{ formatDate(run.started_at) }}</span></div>
          <div><label>结束时间</label><span>{{ formatDate(run.finished_at) }}</span></div>
        </div>
      </div>

      <div class="card block">
        <h3>结果摘要</h3>
        <pre class="payload-box">{{ prettyPayload }}</pre>
      </div>
    </div>

    <div class="card block">
      <div class="block-head"><h3>日志预览</h3><span class="hint">展示最后 12000 个字符</span></div>
      <pre class="log-box">{{ logContent || '暂无日志' }}</pre>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAutomationRun, getAutomationRunLogPreview, getAutomationRunReportMeta } from '@/api/automation'

const route = useRoute()
const run = ref(null)
const logContent = ref('')
const reportUrl = ref('')
const prettyPayload = computed(() => JSON.stringify(run.value?.result_payload || {}, null, 2))
const formatDate = (v) => v ? new Date(v).toLocaleString('zh-CN') : '-'

const loadAll = async () => {
  const id = route.params.id
  const [detail, log, report] = await Promise.all([
    getAutomationRun(id),
    getAutomationRunLogPreview(id),
    getAutomationRunReportMeta(id)
  ])
  run.value = detail.result || detail
  logContent.value = log.content || ''
  reportUrl.value = report.report_url || ''
}

onMounted(loadAll)
</script>

<style scoped>
.run-detail { display:flex; flex-direction:column; gap:16px; }
.detail-head { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; padding:20px; }
.detail-head h2 { margin:12px 0 6px; }
.detail-head p { color:var(--text-light); }
.head-actions { display:flex; align-items:center; gap:10px; }
.detail-grid { display:grid; grid-template-columns:1.2fr .8fr; gap:16px; }
.block { padding:20px; }
.block h3 { margin-bottom:14px; }
.info-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.info-grid label { display:block; font-size:12px; color:var(--text-light); margin-bottom:4px; }
.info-grid span,.info-grid code { font-size:13px; color:var(--text); word-break:break-all; }
.payload-box,.log-box { background:#0f172a; color:#dbeafe; border-radius:10px; padding:16px; overflow:auto; white-space:pre-wrap; word-break:break-word; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; }
.block-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }
.hint { color:var(--text-light); font-size:12px; }
.status { display:inline-flex; padding:6px 12px; border-radius:999px; font-size:12px; font-weight:700; }
.s-pending { background:#eef2ff; color:#3949ab; } .s-running { background:#fff3e0; color:#ef6c00; } .s-passed { background:#e8f7ee; color:#1f8f52; } .s-failed,.s-error { background:#fdecec; color:#c0392b; }
@media (max-width: 980px) { .detail-grid { grid-template-columns:1fr; } .detail-head { flex-direction:column; } .info-grid { grid-template-columns:1fr; } }
</style>
