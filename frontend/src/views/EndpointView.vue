<template>
  <div class="endpoint-view">
    <div class="toolbar">
      <button v-if="hasPermission('endpoint:create')" @click="router.push('/endpoints/new')" class="btn btn-primary">➕ 新建接口</button>
      <button @click="loadEndpoints(1)" class="btn btn-refresh">↻ 刷新</button>
      <button v-if="hasPermission('endpoint:delete')" @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-batch-delete">
        🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
      </button>
    </div>

    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索名称/URL/ID..." @keyup.enter="handleSearch" />
      </div>
      <select v-model="filterProject" class="filter-select">
        <option value="">全部项目</option>
        <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <select v-model="filterMethod" class="filter-select">
        <option value="">全部方法</option>
        <option value="GET">GET</option>
        <option value="POST">POST</option>
        <option value="PUT">PUT</option>
        <option value="PATCH">PATCH</option>
        <option value="DELETE">DELETE</option>
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
            <th>接口名称</th>
            <th>请求方法</th>
            <th>URL</th>
            <th>请求头</th>
            <th>参数</th>
            <th>更新人</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in endpoints" :key="item.id">
            <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
            <td class="cell-sm">{{ item.id }}</td>
            <td class="cell-md" :title="item.name">
              <a @click.prevent="viewDetail(item.id)" class="link-text">{{ item.name }}</a>
            </td>
            <td class="cell-sm"><span class="method-tag" :class="item.method">{{ item.method }}</span></td>
            <td class="cell-xl url-cell" :title="item.url">{{ item.url }}</td>
            <td>
              <span v-if="item.headers" class="badge badge-info">✓</span>
              <span v-else class="badge badge-gray">-</span>
            </td>
            <td>
              <span v-if="item.params || item.json || item.data" class="badge badge-success">✓</span>
              <span v-else class="badge badge-gray">-</span>
            </td>
            <td class="cell-sm">
              <span class="creator-badge">{{ item.created_by_name || '-' }}</span>
            </td>
            <td>
              <button @click="viewDetail(item.id)" class="btn-action btn-info">详情</button>
              <button @click="deleteEndpointItem(item.id)" class="btn-action btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!endpoints.length" class="empty-state">暂无数据</div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getEndpoints, deleteEndpoint } from '@/api/endpoint'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { hasPermission } = userStore
const endpoints = ref([])
const projects = ref([])
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const selectedIds = ref([])

const searchText = ref('')
const filterProject = ref('')
const filterMethod = ref('')

const allSelected = computed(() => endpoints.value.length > 0 && endpoints.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? endpoints.value.map(i => i.id) : [] }

const loadEndpoints = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (searchText.value)    params.search  = searchText.value
    if (filterProject.value) params.project = filterProject.value
    if (filterMethod.value)  params.method  = filterMethod.value
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getEndpoints(params)
    endpoints.value = res.result?.list || []
    pagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (e) { console.error('加载接口列表失败:', e) }
}

const handleSearch = () => loadEndpoints(1)
const resetFilter = () => { searchText.value = ''; filterProject.value = ''; filterMethod.value = ''; loadEndpoints(1) }

const changePage = (page) => { selectedIds.value = []; loadEndpoints(page) }

const viewDetail = (id) => router.push(`/endpoints/${id}`)

const deleteEndpointItem = async (id) => {
  const confirmed = await confirm('确定要删除这个接口吗？', { type: 'danger' })
  if (!confirmed) return
  try {
    await deleteEndpoint(id)
    endpoints.value = endpoints.value.filter(e => e.id !== id)
  } catch (e) { console.error('删除失败:', e) }
}

const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条数据吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteEndpoint(id)))
    endpoints.value = endpoints.value.filter(i => !selectedIds.value.includes(i.id))
    selectedIds.value = []
  } catch (e) { console.error('批量删除失败:', e) }
}

onMounted(async () => {
  const [, pr] = await Promise.all([loadEndpoints(), getProjects({ page_size: 200 })])
  projects.value = pr.result?.list || []
})
</script>

<style scoped>
.method-tag { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; color: white; }
.method-tag.GET    { background: #27ae60; }
.method-tag.POST   { background: #3498db; }
.method-tag.PUT    { background: #f39c12; }
.method-tag.DELETE { background: #e74c3c; }
.method-tag.PATCH  { background: #9b59b6; }
.url-cell { font-family: 'Monaco','Courier New',monospace; font-size: 13px; color: var(--text-light); }
.toolbar { margin-bottom: 16px; }
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }
.table-container { overflow-x: auto; }
.btn-action { padding: 6px 12px; margin: 0 4px; border: none; background: var(--accent); color: white; border-radius: 4px; cursor: pointer; font-size: 13px; }
.btn-action:hover { opacity: 0.8; }
.btn-action.btn-danger { background: var(--danger); }
.btn-action.btn-info   { background: #3498db; }
.link-text { color: var(--primary); cursor: pointer; text-decoration: none; font-weight: 500; }
.link-text:hover { text-decoration: underline; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
.badge-info    { background: #e3f2fd; color: #1976d2; }
.badge-success { background: #e8f5e9; color: #388e3c; }
.badge-gray    { background: #f5f5f5; color: #999; }
.creator-badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  background: linear-gradient(135deg, #e8f4fd, #d6eaf8);
  color: #1a6fa8; font-size: 12px; font-weight: 600;
  border: 1px solid #aed6f1; letter-spacing: 0.02em;
}
.empty-state { text-align: center; padding: 48px; color: var(--text-light); }
</style>
