<template>
  <div class="sprint-view">
    <!-- 页面标题区 -->
    <div class="page-hero">
      <div class="page-hero__content">
        <p class="page-hero__desc">管理测试迭代，跟踪需求进度</p>
        <button class="btn btn--primary" @click="openCreateSprint">
          <PlusOutlined />
          新建迭代
        </button>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-bar">
      <div class="filter-bar__left">
        <div class="filter-bar__search">
          <span class="filter-bar__search-icon">&#128269;</span>
          <input
            v-model="searchText"
            type="text"
            class="filter-bar__input"
            placeholder="搜索迭代名称..."
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="filter-bar__filters">
          <div class="filter-item">
            <label class="filter-label">迭代状态</label>
            <select v-model="filterStatus" class="filter-bar__select" @change="handleSearch">
              <option value="">全部状态</option>
              <option v-for="opt in sprintStatusOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">负责人</label>
            <select v-model="filterOwner" class="filter-bar__select" @change="handleSearch">
              <option value="">全部负责人</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.profile?.nickname || u.username }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <div class="filter-bar__right">
        <button class="btn btn--primary btn--sm" @click="handleSearch">搜索</button>
        <button class="btn btn--ghost btn--sm" @click="resetFilters">重置</button>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card">
      <div class="table-card__toolbar">
        <div class="toolbar__left"></div>
        <div class="toolbar__right">
          <button class="btn btn--ghost btn--sm" @click="loadSprints(pagination.page)" :disabled="loading">
            <span class="btn__icon" :class="{ 'btn__icon--spin': loading }">&#8635;</span>
          </button>
          <button
            class="btn btn--sm"
            :class="selectedIds.length ? 'btn--danger' : 'btn--disabled'"
            :disabled="!selectedIds.length"
            @click="batchDelete"
          >
            🗑 批量删除{{ selectedIds.length ? ` (${selectedIds.length})` : '' }}
          </button>
        </div>
      </div>

      <a-table
        :dataSource="sprints"
        :columns="columns"
        :row-key="record => record.id"
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        :pagination="false"
        :loading="loading"
        :scroll="{ x: 1100 }"
        size="middle"
        class="sprint-table"
      >
        <template #bodyCell="{ column, record }">
          <!-- 迭代名称 -->
          <template v-if="column.key === 'name'">
            <div class="sprint-name-cell" @click="viewDetail(record.id)">
              <span class="sprint-name">{{ record.name }}</span>
            </div>
          </template>

          <!-- 迭代周期 -->
          <template v-if="column.key === 'period'">
            <span class="period-text">{{ formatPeriod(record.start_date, record.end_date) }}</span>
          </template>

          <!-- 负责人 -->
          <template v-if="column.key === 'owner'">
            <div v-if="record.owner_name" class="pm-info">
              <span class="pm-avatar" :style="{ background: getOwnerColor(record.owner_name) }">
                {{ record.owner_name?.charAt(0).toUpperCase() }}
              </span>
              <span class="pm-name">{{ record.owner_name }}</span>
            </div>
            <span v-else class="text-tertiary">—</span>
          </template>

          <!-- 状态 -->
          <template v-if="column.key === 'status'">
            <a-dropdown :trigger="['click']" placement="bottomLeft">
              <span
                class="status-tag status-tag--clickable"
                :style="{
                  background: getStatusConfig(record.status)?.bg,
                  color: getStatusConfig(record.status)?.color
                }"
              >
                <span class="status-dot-sm" :style="{ background: getStatusConfig(record.status)?.color }"></span>
                {{ getStatusText(record.status) }}
                <DownOutlined style="font-size: 10px; margin-left: 2px;" />
              </span>
              <template #overlay>
                <a-menu @click="({ key }) => changeSprintStatus(record, key)">
                  <a-menu-item v-for="opt in sprintStatusOptions" :key="opt.value">
                    <div class="menu-item-inner">
                      <span class="menu-dot" :style="{ background: opt.color }"></span>
                      {{ opt.label }}
                      <CheckOutlined v-if="record.status === opt.value" style="margin-left:auto; font-size:11px;" />
                    </div>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>

          <!-- 需求进度 -->
          <template v-if="column.key === 'progress'">
            <div class="progress-cell">
              <span class="progress-text">{{ record.done_count || 0 }}/{{ record.requirement_count || 0 }}</span>
              <div class="progress-bar-mini">
                <div
                  class="progress-bar-mini__fill"
                  :style="{ width: getProgressPercent(record) + '%' }"
                ></div>
              </div>
            </div>
          </template>

          <!-- 操作 -->
          <template v-if="column.key === 'actions'">
            <div class="action-cell">
              <a-tooltip title="查看详情">
                <a-button type="text" size="small" class="action-btn" @click="viewDetail(record.id)">
                  <EyeOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="编辑">
                <a-button type="text" size="small" class="action-btn" @click="openEditSprint(record)">
                  <EditOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="删除">
                <a-button
                  type="text"
                  size="small"
                  class="action-btn action-btn--danger"
                  @click="deleteSprintItem(record)"
                >
                  <DeleteOutlined />
                </a-button>
              </a-tooltip>
            </div>
          </template>
        </template>

        <!-- 空状态 -->
        <template #emptyText>
          <div class="empty-state">
            <InboxOutlined class="empty-icon" />
            <p class="empty-title">暂无迭代</p>
            <p class="empty-desc">创建一个新迭代，开始你的测试迭代管理</p>
            <button class="btn btn--primary" @click="openCreateSprint">
              <PlusOutlined />
              创建第一个迭代
            </button>
          </div>
        </template>
      </a-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <a-pagination
          v-model:current="pagination.page"
          v-model:pageSize="pagination.pageSize"
          :total="pagination.total"
          :show-total="total => `共 ${total} 条`"
          :show-size-changer="true"
          :page-size-options="['10', '20', '50']"
          :locale="{ items_per_page: '条/页' }"
          show-quick-jumper
          @change="loadSprints"
        />
      </div>
    </div>

    <!-- 新建/编辑迭代弹窗 -->
    <div v-if="showSprintDialog" class="modal" @click.self="showSprintDialog=false">
      <div class="modal-content">
        <h3 class="modal-content__title">{{ editingSprint ? '编辑迭代' : '新建迭代' }}</h3>
        <p class="modal-content__sub">{{ editingSprint ? '修改迭代信息' : '创建一个新的测试迭代' }}</p>

        <div class="form-layout">
          <!-- 左列 -->
          <div class="form-main">
            <div class="form-group">
              <label class="field-label">
                迭代名称 <span class="required">*</span>
              </label>
              <input
                v-model="sprintForm.name"
                class="field-input"
                :class="{ 'field-input--error': formError.name }"
                placeholder="输入迭代名称"
              />
              <span v-if="formError.name" class="field-error">{{ formError.name }}</span>
            </div>

            <div class="form-group">
              <label class="field-label">迭代目标</label>
              <textarea
                v-model="sprintForm.goal"
                class="field-input field-textarea"
                placeholder="描述迭代的目标和范围"
                rows="3"
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="field-label">开始日期</label>
                <input type="date" v-model="sprintForm.start_date" class="field-input" />
              </div>
              <div class="form-group">
                <label class="field-label">结束日期</label>
                <input type="date" v-model="sprintForm.end_date" class="field-input" :min="sprintForm.start_date" />
              </div>
            </div>
          </div>

          <!-- 右列 -->
          <div class="form-side">
            <div class="form-group">
              <label class="field-label">负责人</label>
              <div class="pm-selector">
                <div
                  class="pm-trigger"
                  :class="{ 'pm-trigger--open': pmDropdownOpen }"
                  @click="togglePmDropdown"
                >
                  <template v-if="sprintForm.owner && selectedOwnerUser">
                    <span class="pm-avatar" :style="{ background: getOwnerColor(selectedOwnerUser.username) }">
                      {{ selectedOwnerUser.username?.charAt(0).toUpperCase() }}
                    </span>
                    <span class="pm-name">{{ selectedOwnerUser.username }}</span>
                  </template>
                  <template v-else>
                    <span class="pm-avatar pm-avatar--empty">
                      <UserOutlined />
                    </span>
                    <span class="pm-placeholder">选择负责人</span>
                  </template>
                  <span class="pm-arrow" :class="{ 'pm-arrow--up': pmDropdownOpen }">
                    <DownOutlined />
                  </span>
                </div>

                <Transition name="dropdown">
                  <div
                    v-if="pmDropdownOpen"
                    class="pm-dropdown"
                  >
                    <div
                      class="pm-option"
                      :class="{ 'pm-option--selected': !sprintForm.owner }"
                      @click="selectOwner(null)"
                    >
                      <span class="pm-dot" style="background:#9CA3AF"></span>
                      <span>未指定</span>
                      <CheckOutlined v-if="!sprintForm.owner" class="pm-check" />
                    </div>
                    <div class="pm-dropdown__divider"></div>
                    <div
                      v-for="u in users"
                      :key="u.id"
                      class="pm-option"
                      :class="{ 'pm-option--selected': sprintForm.owner === u.id }"
                      @click="selectOwner(u.id)"
                    >
                      <span class="pm-avatar pm-avatar--sm" :style="{ background: getOwnerColor(u.username) }">
                        {{ (u.profile?.nickname || u.username)?.charAt(0).toUpperCase() }}
                      </span>
                      <span>{{ u.profile?.nickname || u.username }}</span>
                      <CheckOutlined v-if="sprintForm.owner === u.id" class="pm-check" />
                    </div>
                  </div>
                </Transition>
              </div>
            </div>

            <div class="form-group">
              <label class="field-label">迭代状态</label>
              <div class="status-grid">
                <button
                  v-for="opt in sprintStatusOptions"
                  :key="opt.value"
                  type="button"
                  class="status-chip"
                  :class="{ 'status-chip--active': sprintForm.status === opt.value }"
                  :style="sprintForm.status === opt.value
                    ? { background: opt.bg, borderColor: opt.border, color: opt.color }
                    : {}"
                  @click="sprintForm.status = opt.value"
                >
                  <span class="status-chip__dot" :style="{ background: opt.color }"></span>
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="field-label">所属产品线</label>
              <div class="pl-badge">
                <span class="pl-badge__dot" :style="{ background: plColor }"></span>
                <span class="pl-badge__name">{{ userStore.currentProductLine?.name || '默认产品线' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn--ghost" @click="showSprintDialog=false">取消</button>
          <button class="btn btn--primary" @click="saveSprint">
            {{ editingSprint ? '保存修改' : '创建迭代' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
  DownOutlined,
  CheckOutlined,
} from '@ant-design/icons-vue'
import { getSprints, createSprint, updateSprint, deleteSprint } from '@/api/sprint'
import { getAllUsers } from '@/api/account'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import {
  SPRINT_STATUS_LIST,
  getSprintStatusConfig,
  getSprintStatusText,
  stringToColor,
  formatSprintPeriod as formatPeriod,
  getProductLineColor,
} from '@/components/UI'

const router = useRouter()
const userStore = useUserStore()

// 数据
const sprints = ref([])
const users = ref([])
const loading = ref(false)
const selectedIds = ref([])
const searchText = ref('')
const filterStatus = ref('')
const filterOwner = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 弹窗状态
const showSprintDialog = ref(false)
const editingSprint = ref(null)
const pmDropdownOpen = ref(false)

const sprintForm = reactive({
  name: '',
  goal: '',
  status: 'planning',
  start_date: '',
  end_date: '',
  owner: null
})

const formError = reactive({ name: '' })

// 负责人选择
const selectedOwnerUser = computed(() =>
  users.value.find(u => u.id === sprintForm.owner) || null
)

const selectOwner = (userId) => {
  sprintForm.owner = userId
  pmDropdownOpen.value = false
}

const togglePmDropdown = (e) => {
  e.stopPropagation()
  pmDropdownOpen.value = !pmDropdownOpen.value
}

const handleOutsideClick = (e) => {
  if (pmDropdownOpen.value && !e.target.closest('.pm-selector')) {
    pmDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})

// 常量
const sprintStatusOptions = SPRINT_STATUS_LIST

const plColor = computed(() => {
  if (!userStore.currentProductLine) return '#9CA3AF'
  return getProductLineColor(userStore.currentProductLine.id)
})

// 表格列
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, align: 'center' },
  { title: '迭代名称', dataIndex: 'name', key: 'name', width: 200, ellipsis: true, align: 'left', className: 'col-name-left' },
  { title: '迭代周期', key: 'period', width: 220, align: 'center' },
  { title: '负责人', key: 'owner', width: 140, align: 'center' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 110, align: 'center' },
  { title: '需求进度', key: 'progress', width: 140, align: 'center' },
  { title: '操作', key: 'actions', width: 120, fixed: 'right', align: 'center' },
]

// 工具函数
const getStatusConfig = (status) => getSprintStatusConfig(status)
const getStatusText = (status) => getSprintStatusText(status)
const getOwnerColor = (name) => stringToColor(name)
const getProgressPercent = (record) => {
  const total = record.requirement_count || 0
  if (total === 0) return 0
  return Math.round(((record.done_count || 0) / total) * 100)
}

// 加载数据
const loadSprints = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: pagination.pageSize
    }
    if (userStore.currentProductLine?.id) params.product_line = userStore.currentProductLine.id
    if (searchText.value) params.search = searchText.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterOwner.value) params.owner = filterOwner.value

    const res = await getSprints(params)
    sprints.value = res.result?.list || []
    pagination.page = res.result?.page || page
    pagination.total = res.result?.itemCount || 0
  } catch (e) {
    console.error('加载迭代失败:', e)
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const res = await getAllUsers()
    users.value = res.result || res || []
  } catch (e) {
    console.error('加载用户失败:', e)
  }
}

// 操作
const onSelectChange = (keys) => {
  selectedIds.value = keys
}

// 搜索/筛选
const handleSearch = () => {
  pagination.page = 1
  loadSprints(1)
}

const resetFilters = () => {
  searchText.value = ''
  filterStatus.value = ''
  filterOwner.value = ''
  pagination.page = 1
  loadSprints(1)
}

const viewDetail = (id) => router.push(`/sprints/${id}`)

const openCreateSprint = () => {
  pmDropdownOpen.value = false
  editingSprint.value = null
  Object.assign(sprintForm, {
    name: '',
    goal: '',
    status: 'planning',
    start_date: '',
    end_date: '',
    owner: null
  })
  formError.name = ''
  showSprintDialog.value = true
}

const openEditSprint = (s) => {
  editingSprint.value = s
  Object.assign(sprintForm, {
    name: s.name,
    goal: s.goal || '',
    status: s.status,
    start_date: s.start_date || '',
    end_date: s.end_date || '',
    owner: s.owner || null
  })
  formError.name = ''
  showSprintDialog.value = true
}

const saveSprint = async () => {
  formError.name = ''
  if (!sprintForm.name?.trim()) {
    formError.name = '迭代名称不能为空'
    return
  }

  const payload = {
    ...sprintForm,
    project: null,
    product_line: userStore.currentProductLine?.id || null
  }
  if (!payload.start_date) payload.start_date = null
  if (!payload.end_date) payload.end_date = null
  if (!payload.owner) payload.owner = null

  try {
    if (editingSprint.value) {
      await updateSprint(editingSprint.value.id, payload)
      message.success('迭代更新成功')
    } else {
      await createSprint(payload)
      message.success('迭代创建成功')
    }
    showSprintDialog.value = false
    await loadSprints(pagination.page)
  } catch (e) {
    message.error('保存失败：' + (e.response?.data?.detail || ''))
  }
}

const changeSprintStatus = async (record, status) => {
  try {
    await updateSprint(record.id, {
      name: record.name,
      goal: record.goal || '',
      status,
      start_date: record.start_date || null,
      end_date: record.end_date || null,
      owner: record.owner || null,
      project: record.project || null,
      product_line: record.product_line || userStore.currentProductLine?.id || null,
    })
    record.status = status
    message.success('状态已更新')
  } catch {
    message.error('更新状态失败')
  }
}

const deleteSprintItem = async (s) => {
  const ok = await confirm(`确定删除迭代「${s.name}」吗？`, { type: 'danger' })
  if (!ok) return
  try {
    await deleteSprint(s.id)
    await loadSprints(pagination.page)
    message.success('删除成功')
  } catch {
    message.error('删除失败')
  }
}

const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const ok = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条迭代吗？`, { type: 'danger' })
  if (!ok) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteSprint(id)))
    selectedIds.value = []
    await loadSprints(pagination.page)
    message.success('批量删除成功')
  } catch {
    message.error('批量删除失败')
  }
}

onMounted(async () => {
  await loadUsers()
  await loadSprints()
})
</script>

<style scoped>
.sprint-view {
  max-width: 1400px;
  margin: 0 auto;
}

/* ─── 页面标题区 ─── */
.page-hero {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
}

.page-hero__content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-hero__desc {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* ─── 筛选区 ─── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  margin-bottom: 20px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow-x: auto;
}

.filter-bar__left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.filter-bar__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  margin-left: 8px;
}

.filter-bar__search {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 0 10px;
  background: var(--color-bg-page);
  width: 220px;
  flex-shrink: 0;
  transition: border-color 0.2s;
}

.filter-bar__search:focus-within {
  border-color: var(--color-primary);
}

.filter-bar__search-icon {
  color: var(--color-text-tertiary);
  font-size: 14px;
  flex-shrink: 0;
}

.filter-bar__input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px;
  font-size: 14px;
  background: transparent;
  color: var(--color-text-primary);
}

.filter-bar__input::placeholder {
  color: var(--color-text-tertiary);
}

.filter-bar__filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.filter-bar__select {
  padding: 7px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  outline: none;
  cursor: pointer;
  min-width: 120px;
}

.filter-bar__select:focus {
  border-color: var(--color-primary);
}

/* ─── 表格卡片 ─── */
.table-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.table-card__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-gray-50);
}

.toolbar__left {
  flex: 1;
}

.toolbar__right {
  display: flex;
  gap: var(--space-3);
}

/* ─── 迭代名称单元格 ─── */
.sprint-name-cell {
  cursor: pointer;
}

.sprint-name-cell:hover .sprint-name {
  color: var(--color-primary);
  text-decoration: underline;
}

.sprint-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

/* ─── 状态标签 ─── */
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  cursor: pointer;
  transition: opacity var(--transition-fast);
  user-select: none;
}

.status-tag:hover {
  opacity: 0.8;
}

.status-dot-sm {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ─── 进度 ─── */
.progress-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.progress-text {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.progress-bar-mini {
  width: 80px;
  height: 4px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar-mini__fill {
  height: 100%;
  background: var(--color-success);
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

/* ─── 负责人 ─── */
.pm-info {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.pm-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.pm-name {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

/* ─── 操作按钮 ─── */
.action-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  color: var(--color-text-secondary);
  transition: all 0.1s ease;
}

.action-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

.action-btn--danger:hover {
  color: var(--color-error);
  background: var(--color-error-bg);
}

/* ─── 空状态 ─── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-16) var(--space-8);
  gap: var(--space-4);
}

.empty-icon {
  font-size: 48px;
  color: var(--color-gray-300);
}

.empty-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.empty-desc {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0 0 var(--space-2);
}

/* ─── 分页 ─── */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: var(--space-5) var(--space-6);
  border-top: 1px solid var(--color-border);
}

/* ─── 文本辅助 ─── */
.text-tertiary {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

.period-text {
  font-size: var(--text-sm);
  color: var(--color-text);
}

/* ─── 按钮 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  outline: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn--ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(233, 84, 74, 0.05);
}

.btn--danger {
  background: var(--color-error);
  color: white;
  border-color: var(--color-error);
}

.btn--danger:hover:not(:disabled) {
  background: #c9302c;
  border-color: #c9302c;
}

.btn--disabled {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: not-allowed;
}

.btn--sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn__icon {
  font-size: 16px;
  line-height: 1;
}

.btn__icon--spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ─── 弹窗 ─── */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  padding: 28px;
  width: 90%;
  max-width: 720px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-content__title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
}

.modal-content__sub {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0 0 24px;
}

/* ─── 表单 ─── */
.form-layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 24px;
}

.form-main {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.required {
  color: var(--color-error);
}

.field-input {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.field-input::placeholder {
  color: #c4c9d4;
}

.field-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.field-input--error {
  border-color: var(--color-error);
}

.field-textarea {
  resize: vertical;
  min-height: 88px;
  line-height: 1.6;
}

.field-error {
  font-size: 12px;
  color: var(--color-error);
  display: flex;
  align-items: center;
  gap: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* ─── 状态选择 ─── */
.status-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.status-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 6px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.15s;
  user-select: none;
}

.status-chip:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.status-chip__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ─── 产品线徽章 ─── */
.pl-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: var(--color-gray-50);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.pl-badge__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pl-badge__name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

/* ─── 弹窗底部 ─── */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

/* ─── 菜单项 ─── */
.menu-item-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ─── 响应式 ─── */
@media (max-width: 1024px) {
  .filter-bar {
    overflow-x: auto;
  }

  .filter-bar__left {
    flex-wrap: wrap;
  }
}

@media (max-width: 900px) {
  .form-layout {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar__left {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .filter-bar__search {
    width: 100%;
  }

  .filter-bar__right {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

<style>
/* 表格样式（需要全局） */
.col-name-left {
  text-align: left !important;
}

.col-name-left .sprint-name-cell {
  display: flex;
  justify-content: flex-start;
}

:deep(.sprint-table .ant-table) {
  border-radius: 8px;
}

/* 表头样式 - 统一渐变设计 */
:deep(.sprint-table .ant-table-thead > tr:first-child > th:first-child) {
  border-radius: 8px 0 0 0;
}

:deep(.sprint-table .ant-table-thead > tr:first-child > th:last-child) {
  border-radius: 0 8px 0 0;
}

:deep(.ant-table-thead > tr > th.ant-table-cell) {
  background: linear-gradient(135deg, #5c1a1a 0%, #3b0a0a 100%) !important;
  color: #ffffff !important;
  font-weight: 600;
  font-size: 13px !important;
  text-align: center !important;
  padding: 14px 16px !important;
  border-bottom: none !important;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

/* 数据行居中 */
:deep(.ant-table-tbody .ant-table-cell) {
  text-align: center !important;
  padding: 12px 16px !important;
}

/* 数据行悬停 */
:deep(.sprint-table__row:hover > td) {
  background: #f8f9fa !important;
}

/* 固定列背景和阴影 */
:deep(.ant-table-cell-fix-left),
:deep(.ant-table-cell-fix-right) {
  background: var(--color-bg-card) !important;
}

:deep(.ant-table-cell-fix-left-last) {
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.08);
}

:deep(.ant-table-cell-fix-right-first) {
  box-shadow: -2px 0 6px rgba(0, 0, 0, 0.08);
}

/* 固定列悬停背景 */
:deep(.ant-table-tbody > tr.ant-table-row:hover > td.ant-table-cell-fix-left),
:deep(.ant-table-tbody > tr.ant-table-row:hover > td.ant-table-cell-fix-right) {
  background: #fef7f0 !important;
}
</style>
