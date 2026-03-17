<template>
  <div class="suite-view">
    <div class="toolbar">
      <button v-if="hasPermission('suite:create')" @click="router.push('/suites/new')" class="btn btn-primary">➕ 新建测试套件</button>
      <button @click="loadSuites(1)" class="btn btn-refresh">↻ 刷新</button>
      <button v-if="hasPermission('suite:delete')" @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-batch-delete">
        🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
      </button>
    </div>

    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索名称或ID..." @keyup.enter="handleSearch" />
      </div>
      <select v-model="filterProject" class="filter-select">
        <option value="">全部项目</option>
        <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <select v-model="filterRunType" class="filter-select">
        <option value="">全部类型</option>
        <option value="O">手动执行</option>
        <option value="C">定时执行</option>
        <option value="W">WebHook</option>
      </select>
      <button @click="handleSearch" class="btn btn-primary btn-sm">搜索</button>
      <button @click="resetFilter" class="btn btn-sm">重置</button>
    </div>

    <div class="table-container card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
            <th>ID</th>
            <th>套件名称</th>
            <th>运行类型</th>
            <th>所属项目</th>
            <th>更新人</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in suites" :key="item.id">
            <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
            <td class="cell-sm">{{ item.id }}</td>
            <td class="cell-md" :title="item.name">
              <a @click.prevent="viewDetail(item.id)" class="link-text">{{ item.name }}</a>
            </td>
            <td class="cell-sm"><span class="type-tag" :class="'type-' + item.run_type">{{ { O: '手动执行', C: '定时执行', W: 'WebHook' }[item.run_type] || item.run_type }}</span></td>
            <td class="cell-md">{{ item.project_name || '-' }}</td>
            <td class="cell-sm">
              <span class="creator-badge">{{ item.updated_by_name || '-' }}</span>
            </td>
            <td class="cell-md">{{ formatDate(item.created_at) }}</td>
            <td>
              <button @click="runSuiteItem(item)" class="btn-action btn-success">▶ 执行</button>
              <button v-if="item.run_type === 'C'" @click="stopCronItem(item)" class="btn-action btn-warning">⏹ 停止定时</button>
              <button @click="viewDetail(item.id)" class="btn-action btn-info">详情</button>
              <button @click="deleteSuiteItem(item.id)" class="btn-action btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!suites.length" class="empty-state">暂无数据</div>
      <div v-if="pagination.pageCount > 1" class="pagination">
        <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
        <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
        <button v-for="p in pagination.pageCount" :key="p" class="page-btn" :class="{ active: p === pagination.page }" @click="changePage(p)">{{ p }}</button>
        <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
      </div>
    </div>

    <!-- 执行结果弹框 -->
    <div v-if="showRunDialog" class="modal" @click.self="showRunDialog = false">
      <div class="modal-content">
        <h3>执行测试套件</h3>
        <div v-if="runResult.loading" class="loading-state">
          <div class="spinner"></div><p>正在执行测试...</p>
        </div>
        <div v-else-if="runResult.success" class="success-state">
          <div class="success-icon">✓</div>
          <p>测试套件已提交执行</p>
          <p class="result-id">执行ID: {{ runResult.result_id }}</p>
          <button @click="viewResult(runResult.result_id)" class="btn btn-primary">查看结果</button>
        </div>
        <div v-else-if="runResult.error" class="error-state">
          <div class="error-icon">✗</div>
          <p>执行失败: {{ runResult.error }}</p>
          <button @click="showRunDialog = false" class="btn">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSuites, deleteSuite, runSuite, stopCron } from '@/api/suite'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { hasPermission } = userStore
const suites = ref([])
const projects = ref([])
const showRunDialog = ref(false)
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const selectedIds = ref([])
const runResult = ref({ loading: false, success: false, error: null, result_id: null })

// 搜索/筛选
const searchText = ref('')
const filterProject = ref('')
const filterRunType = ref('')

const allSelected = computed(() => suites.value.length > 0 && suites.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? suites.value.map(i => i.id) : [] }

const loadSuites = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (searchText.value)    params.search   = searchText.value
    if (filterProject.value) params.project   = filterProject.value
    if (filterRunType.value) params.run_type  = filterRunType.value
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getSuites(params)
    suites.value = res.result?.list || []
    pagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (e) { console.error('加载失败:', e) }
}

const handleSearch = () => loadSuites(1)
const resetFilter = () => { searchText.value = ''; filterProject.value = ''; filterRunType.value = ''; loadSuites(1) }

const changePage = (page) => { selectedIds.value = []; loadSuites(page) }
const viewDetail = (id) => router.push(`/suites/${id}`)
const viewResult = (id) => { showRunDialog.value = false; router.push(`/results?id=${id}`) }

onMounted(async () => {
  const [, pr] = await Promise.all([loadSuites(), import('@/api/project').then(m => m.getProjects({ page_size: 200 }))])
  projects.value = pr.result?.list || []
})

const runSuiteItem = async (item) => {
  showRunDialog.value = true
  runResult.value = { loading: true, success: false, error: null, result_id: null }
  try {
    const res = await runSuite(item.id, {})
    const resultId = res.result?.result_id || res.result_id
    runResult.value = { loading: false, success: true, error: null, result_id: resultId }
    setTimeout(loadSuites, 1000)
  } catch (e) {
    runResult.value = { loading: false, success: false, error: e.response?.data?.msg || e.message || '执行失败', result_id: null }
  }
}

const deleteSuiteItem = async (id) => {
  const confirmed = await confirm('确定要删除这个测试套件吗？', { type: 'danger' })
  if (!confirmed) return
  try { await deleteSuite(id); suites.value = suites.value.filter(s => s.id !== id) }
  catch (e) { console.error('删除失败:', e) }
}

const stopCronItem = async (item) => {
  const confirmed = await confirm(`确定要停止套件「${item.name}」的定时任务吗？\n停止后将切换为手动执行模式。`, { type: 'warning' })
  if (!confirmed) return
  try {
    await stopCron(item.id)
    await loadSuites()
  } catch (e) {
    console.error('停止定时任务失败:', e)
    alert('停止失败：' + (e.response?.data?.msg || e.message))
  }
}

const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条数据吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteSuite(id)))
    suites.value = suites.value.filter(i => !selectedIds.value.includes(i.id))
    selectedIds.value = []
  } catch (e) { console.error('批量删除失败:', e) }
}

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'
</script>

<style scoped>
.type-tag { display:inline-block; padding:4px 10px; border-radius:4px; font-size:12px; font-weight:600; }
.type-O { background:#e3f2fd; color:#1976d2; }
.type-C { background:#fff3e0; color:#e65100; }
.type-W { background:#f3e5f5; color:#7b1fa2; }
.creator-badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  background: linear-gradient(135deg, #e8f4fd, #d6eaf8);
  color: #1a6fa8; font-size: 12px; font-weight: 600;
  border: 1px solid #aed6f1; letter-spacing: 0.02em;
}
.toolbar { margin-bottom:16px; }
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }
.table-container { overflow-x:auto; }
.btn-action { padding:6px 12px; margin:0 4px; border:none; background:var(--accent); color:white; border-radius:4px; cursor:pointer; font-size:13px; }
.btn-action:hover { opacity:.8; }
.btn-action.btn-success { background:#27ae60; }
.btn-action.btn-warning { background:#f39c12; }
.btn-action.btn-danger  { background:var(--danger); }
.btn-action.btn-info    { background:#3498db; }
.link-text { color:var(--primary); cursor:pointer; text-decoration:none; font-weight:500; }
.link-text:hover { text-decoration:underline; }
.empty-state { text-align:center; padding:48px; color:var(--text-light); }
.modal { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:1000; }
.modal-content { background:white; border-radius:12px; padding:32px; width:90%; max-width:420px; text-align:center; }
.modal-content h3 { margin-bottom:20px; font-size:18px; }
.loading-state,.success-state,.error-state { padding:16px; }
.spinner { width:40px; height:40px; border:4px solid var(--border); border-top-color:var(--accent); border-radius:50%; animation:spin 1s linear infinite; margin:0 auto 16px; }
.success-icon,.error-icon { width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:26px; margin:0 auto 12px; }
.success-icon { background:#27ae60; color:white; }
.error-icon   { background:#e74c3c; color:white; }
.result-id { color:var(--text-light); font-size:13px; margin:10px 0; }
@keyframes spin { to { transform:rotate(360deg); } }
</style>
