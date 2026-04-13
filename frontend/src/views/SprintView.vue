<template>
  <div class="sprint-view">
    <div class="toolbar">
      <button @click="openCreateSprint" class="btn btn-primary">+ 新建迭代</button>
      <button @click="loadSprints(1)" class="btn btn-refresh">↻ 刷新</button>
      <button @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-batch-delete">
        🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
      </button>
    </div>

    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索迭代名称..." @keyup.enter="loadSprints(1)" />
      </div>
      <select v-model="filterStatus" class="filter-select">
        <option value="">全部状态</option>
        <option value="planning">规划中</option>
        <option value="active">进行中</option>
        <option value="reviewing">评审中</option>
        <option value="done">已完成</option>
      </select>
      <select v-model="filterOwner" class="filter-select">
        <option value="">全部负责人</option>
        <option v-for="u in users" :key="u.id" :value="u.id">{{ u.profile?.nickname || u.username }}</option>
      </select>
      <button @click="loadSprints(1)" class="btn btn-primary btn-sm">搜索</button>
      <button @click="resetFilters" class="btn btn-sm">重置</button>
    </div>

    <div class="table-container card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
            <th>ID</th>
            <th>迭代名称</th>
            <th>迭代周期</th>
            <th>负责人</th>
            <th>状态</th>
            <th>需求进度</th>
            <th>操作人</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in sprints" :key="s.id">
            <td><input type="checkbox" :value="s.id" v-model="selectedIds" /></td>
            <td class="cell-sm">{{ s.id }}</td>
            <td class="cell-md"><a class="link-text" @click.prevent="viewDetail(s.id)">{{ s.name }}</a></td>
            <td class="cell-md">{{ formatCycle(s) }}</td>
            <td class="cell-sm">{{ s.owner_name || '-' }}</td>
            <td>
              <select
                v-if="editingStatusSprintId === s.id"
                :value="s.status"
                class="status-select"
                @change="changeSprintStatus(s, $event.target.value)"
                @blur="editingStatusSprintId = null"
              >
                <option value="planning">规划中</option>
                <option value="active">进行中</option>
                <option value="reviewing">评审中</option>
                <option value="done">已完成</option>
              </select>
              <span v-else class="badge status-badge" @click="editingStatusSprintId = s.id">{{ statusText[s.status] }}</span>
            </td>
            <td>{{ s.done_count }}/{{ s.requirement_count }}</td>
            <td>{{ s.operator_name || '-' }}</td>
            <td>
              <button class="btn-action btn-info" @click="viewDetail(s.id)">详情</button>
              <button class="btn-action" @click="openEditSprint(s)">编辑</button>
              <button class="btn-action btn-danger" @click="deleteSprintItem(s)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!sprints.length" class="empty-state">暂无迭代</div>
      <div v-if="pagination.pageCount > 1" class="pagination">
        <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
        <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
        <template v-for="p in visiblePages" :key="`p-${p}`">
          <span v-if="p === '...'" class="page-ellipsis">...</span>
          <button v-else class="page-btn" :class="{ active: p === pagination.page }" @click="changePage(p)">{{ p }}</button>
        </template>
        <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
      </div>
    </div>

    <div v-if="showSprintDialog" class="modal" @click.self="showSprintDialog=false">
      <div class="modal-content">
        <h3>{{ editingSprint ? '编辑迭代' : '新建迭代' }}</h3>
        <div class="form-group"><label>所属产品线</label><input :value="userStore.currentProductLine?.name || '-'" disabled /></div>
        <div class="form-group"><label>名称</label><input v-model="sprintForm.name" /></div>
        <div class="form-group"><label>迭代目标</label><textarea v-model="sprintForm.goal" rows="3"></textarea></div>
        <div class="form-row">
          <div class="form-group"><label>负责人</label>
            <select v-model="sprintForm.owner">
              <option :value="null">未指定</option>
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.profile?.nickname || u.username }}</option>
            </select>
          </div>
          <div class="form-group"><label>状态</label>
            <select v-model="sprintForm.status">
              <option value="planning">规划中</option><option value="active">进行中</option>
              <option value="reviewing">评审中</option><option value="done">已完成</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group"><label>开始</label><input type="date" v-model="sprintForm.start_date"/></div>
          <div class="form-group"><label>结束</label><input type="date" v-model="sprintForm.end_date"/></div>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showSprintDialog=false">取消</button>
          <button class="btn btn-primary" @click="saveSprint">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getAllUsers } from '@/api/account'
import { getSprints, createSprint, updateSprint, deleteSprint } from '@/api/sprint'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'

const router = useRouter()
const userStore = useUserStore()
const users = ref([])
const sprints = ref([])
const selectedIds = ref([])
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const searchText = ref('')
const filterStatus = ref('')
const filterOwner = ref('')

const showSprintDialog = ref(false)
const editingSprint = ref(null)
const editingStatusSprintId = ref(null)
const sprintForm = ref({ name: '', goal: '', status: 'planning', start_date: '', end_date: '', owner: null })

const allSelected = computed(() => sprints.value.length > 0 && sprints.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? sprints.value.map(i => i.id) : [] }

const statusText = { planning: '规划中', active: '进行中', reviewing: '评审中', done: '已完成' }

const loadSprints = async (page = 1) => {
  const params = { page, page_size: 10 }
  if (userStore.currentProductLine?.id) params.product_line = userStore.currentProductLine.id
  if (searchText.value) params.search = searchText.value
  if (filterStatus.value) params.status = filterStatus.value
  if (filterOwner.value) params.owner = filterOwner.value
  const res = await getSprints(params)
  sprints.value = res.result?.list || []
  selectedIds.value = []
  pagination.value = {
    page: res.result?.page || 1,
    pageCount: res.result?.pageCount || 1,
    itemCount: res.result?.itemCount || 0,
  }
}

const resetFilters = async () => {
  searchText.value = ''
  filterStatus.value = ''
  filterOwner.value = ''
  await loadSprints(1)
}

const changePage = (page) => loadSprints(page)

const changeSprintStatus = async (s, status) => {
  if (s.status === status) {
    editingStatusSprintId.value = null
    return
  }
  await updateSprint(s.id, {
    name: s.name,
    goal: s.goal || '',
    status,
    start_date: s.start_date || null,
    end_date: s.end_date || null,
    owner: s.owner || null,
    project: s.project || null,
    product_line: s.product_line || userStore.currentProductLine?.id || null,
  })
  editingStatusSprintId.value = null
  await loadSprints(pagination.value.page)
}

const visiblePages = computed(() => {
  const total = pagination.value.pageCount || 1
  const current = pagination.value.page || 1
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const pages = [1]
  const left = Math.max(2, current - 1)
  const right = Math.min(total - 1, current + 1)

  if (left > 2) pages.push('...')
  for (let p = left; p <= right; p += 1) pages.push(p)
  if (right < total - 1) pages.push('...')

  pages.push(total)
  return pages
})

const openCreateSprint = () => {
  editingSprint.value = null
  sprintForm.value = { name: '', goal: '', status: 'planning', start_date: '', end_date: '', owner: null }
  showSprintDialog.value = true
}

const openEditSprint = (s) => {
  editingSprint.value = s
  sprintForm.value = { name: s.name, goal: s.goal || '', status: s.status, start_date: s.start_date || '', end_date: s.end_date || '', owner: s.owner || null }
  showSprintDialog.value = true
}

const saveSprint = async () => {
  if (!sprintForm.value.name?.trim()) return alert('迭代名称必填')
  const payload = { ...sprintForm.value, project: null, product_line: userStore.currentProductLine?.id || null }
  if (editingSprint.value) await updateSprint(editingSprint.value.id, payload)
  else await createSprint(payload)
  showSprintDialog.value = false
  await loadSprints(1)
}

const deleteSprintItem = async (s) => {
  const ok = await confirm(`确定删除迭代「${s.name}」吗？`, { type: 'danger' })
  if (!ok) return
  await deleteSprint(s.id)
  await loadSprints(pagination.value.page)
}

const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const ok = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条迭代吗？`, { type: 'danger' })
  if (!ok) return
  await Promise.all(selectedIds.value.map(id => deleteSprint(id)))
  selectedIds.value = []
  await loadSprints(pagination.value.page)
}

const viewDetail = (id) => router.push(`/sprints/${id}`)
const formatCycle = (s) => [s.start_date || '-', s.end_date || '-'].join(' ~ ')

onMounted(async () => {
  const ur = await getAllUsers()
  users.value = ur.result || ur || []
  await loadSprints()
})
</script>

<style scoped>
.toolbar { margin-bottom:16px; }
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }
.table-container { overflow-x: auto; }
.table { font-size: 14px; }
.cell-sm { font-size: 13px; }
.cell-md { font-size: 13px; }
.empty-state { padding:18px; text-align:center; color:#8b949e; }
.badge { font-size:12px; background:#e8f4ff; color:#1677ff; padding:2px 8px; border-radius:10px; }
.status-badge { cursor: pointer; display:inline-block; }
.link-text { color: var(--primary); cursor:pointer; text-decoration:none; font-weight:500; }
.link-text:hover { text-decoration: underline; }
.status-select { height:30px; border:1px solid #d1d5db; border-radius:6px; padding:0 8px; font-size:12px; background:#fff; }
.status-select:focus { outline:none; border-color:#1677ff; }
.btn-action { padding: 6px 12px; margin: 0 4px; border: none; background: var(--accent); color: white; border-radius: 4px; cursor: pointer; font-size: 13px; }
.btn-action:hover { opacity:.8; }
.btn-action.btn-danger { background: var(--danger); }
.btn-action.btn-info { background: #3498db; }
.modal { position:fixed; inset:0; background:rgba(0,0,0,.28); display:flex; align-items:center; justify-content:center; z-index:1000; padding:20px; }
.modal-content { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:18px; width:min(680px,92vw); max-height:85vh; overflow:auto; box-shadow:0 14px 40px rgba(0,0,0,.18); }
.form-group { margin-bottom:10px; }
.form-group label { display:block; margin-bottom:4px; font-size:13px; color:#4b5563; }
.form-group input, .form-group textarea, .form-group select { width:100%; padding:8px 10px; border:1px solid #d1d5db; border-radius:8px; }
.form-row { display:grid; grid-template-columns:repeat(2, minmax(120px,1fr)); gap:10px; }
.modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:8px; }
.pagination { display:flex; align-items:center; gap:6px; justify-content:flex-end; padding:10px 4px 2px; }
.pagination-info { margin-right:8px; color:#6b7280; font-size:12px; }
.page-btn { min-width:28px; height:28px; border:1px solid #d1d5db; background:#fff; border-radius:6px; cursor:pointer; }
.page-ellipsis { display:inline-flex; align-items:center; justify-content:center; width:28px; color:#9ca3af; }
.page-btn.active { background:#1677ff; color:#fff; border-color:#1677ff; }
.page-btn:disabled { opacity:.45; cursor:not-allowed; }
</style>
