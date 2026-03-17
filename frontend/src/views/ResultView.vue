<template>
  <div class="result-view">
    <div class="toolbar">
      <button @click="loadResults(1)" class="btn btn-refresh-all" :disabled="loading">
        {{ loading ? '刷新中...' : '↻ 刷新' }}
      </button>
      <button @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-batch-delete">
        🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
      </button>
    </div>

    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索套件名称或ID..." @keyup.enter="handleSearch" />
      </div>
      <select v-model="filterIsPass" class="filter-select">
        <option value="">全部结果</option>
        <option value="true">✓ 通过</option>
        <option value="false">✗ 未通过</option>
      </select>
      <button @click="handleSearch" class="btn btn-primary btn-sm">搜索</button>
      <button @click="resetFilter" class="btn btn-sm">重置</button>
    </div>

    <div class="table-container card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
            <th>执行ID</th>
            <th>套件名称</th>
            <th>所属项目</th>
            <th>执行状态</th>
            <th>是否通过</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in results" :key="item.id">
            <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
            <td>{{ item.id }}</td>
            <td>{{ item.suite_name || `套件 #${item.suite}` }}</td>
            <td>{{ item.project_name || `项目 #${item.project}` }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(item.status)">
                {{ getStatusText(item.status) }}
              </span>
            </td>
            <td>
              <span v-if="item.status === 4" :class="item.is_pass ? 'pass-badge' : 'fail-badge'">
                {{ item.is_pass ? '✓ 通过' : '✗ 失败' }}
              </span>
              <span v-else>-</span>
            </td>
            <td>{{ formatDate(item.created_at) }}</td>
            <td style="white-space: nowrap; overflow: visible; max-width: none;">
              <button @click="$router.push(`/results/${item.id}`)" class="btn-action btn-info">查看详情</button>
              <button v-if="item.report_url" @click="viewReport(item.report_url)" class="btn-action btn-success">查看报告</button>

            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!results.length" class="empty-state">暂无执行记录</div>

      <div v-if="pagination.pageCount > 1" class="pagination">
        <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
        <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
        <button v-for="p in pagination.pageCount" :key="p" class="page-btn" :class="{ active: p === pagination.page }" @click="changePage(p)">{{ p }}</button>
        <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRunResults, getRunResult, deleteRunResult } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const route = useRoute()
const router = useRouter()
const results = ref([])
const selectedIds = ref([])
const refreshingIds = ref(new Set())
const loading = ref(false)
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })

const searchText = ref('')
const filterIsPass = ref('')

const allSelected = computed(() =>
  results.value.length > 0 && results.value.every(i => selectedIds.value.includes(i.id))
)
const toggleAll = (e) => {
  selectedIds.value = e.target.checked ? results.value.map(i => i.id) : []
}

const loadResults = async (page = 1) => {
  loading.value = true
  try {
    const params = { page, page_size: 10 }
    if (searchText.value)   params.search  = searchText.value
    if (filterIsPass.value) params.is_pass = filterIsPass.value
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getRunResults(params)
    results.value = res.result?.list || res.list || []
    pagination.value = {
      page: res.result?.page || 1,
      pageCount: res.result?.pageCount || 1,
      itemCount: res.result?.itemCount || 0
    }
  } catch (e) {
    console.error('加载执行结果失败:', e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => loadResults(1)
const resetFilter = () => { searchText.value = ''; filterIsPass.value = ''; loadResults(1) }

const changePage = (page) => { selectedIds.value = []; loadResults(page) }

const refreshResult = async (item) => {
  if (refreshingIds.value.has(item.id)) return
  refreshingIds.value = new Set([...refreshingIds.value, item.id])
  try {
    const res = await getRunResult(item.id)
    const updated = res.result || res
    const idx = results.value.findIndex(r => r.id === item.id)
    if (idx !== -1) results.value.splice(idx, 1, { ...results.value[idx], ...updated })
  } catch (e) {
    console.error('刷新结果失败:', e)
  } finally {
    const s = new Set(refreshingIds.value)
    s.delete(item.id)
    refreshingIds.value = s
  }
}

const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条执行结果吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteRunResult(id)))
    results.value = results.value.filter(i => !selectedIds.value.includes(i.id))
    selectedIds.value = []
  } catch (e) {
    console.error('批量删除失败:', e)
  }
}

const viewReport = (url) => {
  if (url) window.open(url, '_blank')
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

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

watch(() => route.query.id, () => loadResults(1))
onMounted(() => loadResults(1))
</script>

<style scoped>
.result-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }

.table-container {
  overflow-x: auto;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.status-init, .status-ready       { background: #e3f2fd; color: #1976d2; }
.status-running, .status-reporting { background: #fff3e0; color: #f57c00; }
.status-done                       { background: #e8f5e9; color: #388e3c; }
.status-error                      { background: #ffebee; color: #d32f2f; }

.pass-badge { color: #27ae60; font-weight: 600; }
.fail-badge { color: #e74c3c; font-weight: 600; }

.btn-action {
  padding: 5px 11px;
  margin: 0 3px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: white;
}
.btn-action:hover { opacity: 0.82; }
.btn-action.btn-info    { background: #3498db; }
.btn-action.btn-success { background: #27ae60; }
.btn-action.btn-refresh { background: #8e44ad; }
.btn-action:disabled    { opacity: 0.5; cursor: not-allowed; }

.btn-batch-delete { background: #e74c3c; color: white; }
.btn-batch-delete:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-refresh-all { background: #8e44ad; color: white; }
.btn-refresh-all:disabled { opacity: 0.5; cursor: not-allowed; }

.empty-state {
  text-align: center;
  padding: 48px;
  color: var(--text-light);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px 0 8px;
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 13px;
  color: var(--text-light);
  margin-right: 8px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 10px;
  border: 1px solid var(--border, #e5e7eb);
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text);
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled) {
  background: var(--accent, #3498db);
  color: white;
  border-color: var(--accent, #3498db);
}
.page-btn.active {
  background: var(--accent, #3498db);
  color: white;
  border-color: var(--accent, #3498db);
  font-weight: 600;
}
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
