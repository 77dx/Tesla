<template>
  <div class="project-view">
    <!-- 页面标题区 -->
    <div class="page-hero">
      <div class="page-hero__content">
        <p class="page-hero__desc">集中管理测试项目，支持多项目并行协作</p>
        <button class="btn btn--primary" @click="goToNewProject">
          <PlusOutlined />
          新建项目
        </button>
      </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <!-- 筛选区 -->
    <div class="filter-bar">
      <div class="filter-bar__left">
        <div class="filter-bar__search">
          <span class="filter-bar__search-icon">&#128269;</span>
          <input
            type="text"
            v-model="searchText"
            placeholder="搜索项目名称或描述..."
            class="filter-bar__input"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="filter-bar__filters">
          <div class="filter-item">
            <label class="filter-label">项目状态</label>
            <select v-model="filterStatus" class="filter-bar__select" @change="handleFilterChange">
              <option value="">全部</option>
              <option value="active">活跃</option>
              <option value="planning">规划中</option>
              <option value="testing">测试中</option>
              <option value="done">已完成</option>
              <option value="archived">已归档</option>
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">项目负责人</label>
            <select v-model="filterPm" class="filter-bar__select" @change="handleFilterChange">
              <option value="">全部</option>
              <option v-for="user in userList" :key="user.id" :value="user.id">
                {{ user.username }}
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

    <!-- 表格区域 -->
    <div class="table-card">
      <div class="table-card__toolbar">
        <div class="toolbar__left"></div>
        <div class="toolbar__right">
          <button class="btn btn--ghost btn--sm" @click="loadProjects" :disabled="loading">
            <span class="btn__icon" :class="{ 'btn__icon--spin': loading }">&#8635;</span>
          </button>
          <button
            class="btn btn--sm"
            :class="selectedRowKeys.length ? 'btn--danger' : 'btn--disabled'"
            :disabled="!selectedRowKeys.length"
            @click="openDeleteModal('batch')"
          >
            &#128465; 批量删除{{ selectedRowKeys.length ? ` (${selectedRowKeys.length})` : '' }}
          </button>
        </div>
      </div>

      <a-table
        :dataSource="projects"
        :columns="columns"
        :row-key="record => record.id"
        :row-selection="{ selectedRowKeys, onChange: onSelectChange, fixed: true }"
        :pagination="false"
        :loading="loading"
        :scroll="{ x: 1100 }"
        size="middle"
        class="project-table"
        :custom-header-row="() => ({ class: 'project-table__header' })"
        :custom-row="(record) => ({ class: 'project-table__row' })"
      >
        <template #bodyCell="{ column, record }">
          <!-- 项目名称 -->
          <template v-if="column.key === 'name'">
            <div class="project-name-cell" @click="viewProjectDetail(record.id)">
              <span class="project-name">{{ record.name }}</span>
            </div>
          </template>

          <!-- 状态 -->
          <template v-if="column.key === 'status'">
            <a-dropdown :trigger="['click']" placement="bottomLeft">
              <span class="status-tag status-tag--clickable" :style="{ background: getStatusColor(record.status) + '22', color: getStatusColor(record.status) }">
                <span class="status-dot-sm" :style="{ background: getStatusColor(record.status) }"></span>
                {{ getStatusText(record.status) }}
                <DownOutlined style="font-size: 10px; margin-left: 2px;" />
              </span>
              <template #overlay>
                <a-menu @click="({ key }) => handleStatusChange(record, key)">
                  <a-menu-item v-for="opt in statusOptions" :key="opt.value">
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

          <!-- 周期 -->
          <template v-if="column.key === 'period'">
            <span class="period-text">{{ formatPeriod(record.start_date, record.end_date) }}</span>
          </template>

          <!-- 优先级 -->
          <template v-if="column.key === 'priority'">
            <a-dropdown :trigger="['click']" placement="bottomLeft">
              <span
                class="priority-tag"
                :class="getPriorityClass(record.priority)"
              >
                {{ getPriorityText(record.priority) }}
                <DownOutlined style="font-size: 10px; margin-left: 3px;" />
              </span>
              <template #overlay>
                <a-menu @click="({ key }) => handlePriorityChange(record, key)">
                  <a-menu-item v-for="opt in priorityOptions" :key="opt.value">
                    <div class="menu-item-inner priority-option">
                      <span
                        class="priority-bar"
                        :style="{ background: opt.color }"
                      ></span>
                      {{ opt.label }}
                      <CheckOutlined v-if="record.priority === opt.value" style="margin-left:auto; font-size:11px;" />
                    </div>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>

          <!-- 负责人 -->
          <template v-if="column.key === 'pm'">
            <span v-if="record.pm" class="pm-tag" :style="{ background: getPmColor(record._pm_name) + '22', color: getPmColor(record._pm_name) }">
              {{ record._pm_name }}
            </span>
            <span v-else class="text-tertiary">—</span>
          </template>

          <!-- 时间 -->
          <template v-if="column.key === 'created_at'">
            <span class="text-tertiary">{{ formatDate(record.created_at) }}</span>
          </template>

          <!-- 操作 -->
          <template v-if="column.key === 'actions'">
            <div class="action-cell">
              <a-tooltip title="查看详情">
                <a-button type="text" size="small" class="action-btn" @click="viewProjectDetail(record.id)">
                  <EyeOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="编辑">
                <a-button type="text" size="small" class="action-btn" @click="editProject(record.id)">
                  <EditOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="删除">
                  <a-button type="text" size="small" class="action-btn action-btn--danger" @click="openDeleteModal('single', record)">
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
            <p class="empty-title">暂无项目</p>
            <p class="empty-desc">创建一个新项目，开始你的测试之旅</p>
            <a-button type="primary" @click="goToNewProject">
              <PlusOutlined />
              创建第一个项目
            </a-button>
          </div>
        </template>
      </a-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <a-pagination
          v-model:current="pagination.current"
          v-model:pageSize="pagination.pageSize"
          :total="pagination.total"
          :show-total="total => `共 ${total} 条`"
          :show-size-changer="true"
          :page-size-options="['10', '20', '50']"
          :locale="{ items_per_page: '条/页' }"
          show-quick-jumper
          @change="handlePageChange"
        />
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <a-modal
      v-model:open="deleteModalVisible"
      title="确认删除"
      :maskClosable="false"
      @ok="handleDelete"
      okText="删除"
      cancelText="取消"
      okType="danger"
    >
      <p style="font-size: 14px; color: var(--color-text);">
        {{ deleteTarget.type === 'batch'
          ? `确定要删除选中的 ${selectedRowKeys.length} 个项目吗？此操作不可恢复。`
          : `确定要删除项目「${deleteTarget.data?.name}」吗？此操作不可恢复。`
        }}
      </p>
    </a-modal>

</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  SyncOutlined,
  FilterOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  InboxOutlined,
  FolderOutlined,
  CheckCircleOutlined,
  TeamOutlined,
  ThunderboltOutlined,
  DownOutlined,
  CheckOutlined,
} from '@ant-design/icons-vue'
import { getProjects, deleteProject, batchDeleteProjects, updateProject } from '@/api/project'
import { getAllUsers } from '@/api/account'
import {
  PROJECT_STATUS_LIST,
  PROJECT_PRIORITY_LIST,
  getProjectStatusConfig,
  getProjectPriorityConfig,
  stringToColor,
  formatDate,
} from '@/components/UI'

const router = useRouter()
const userStore = useUserStore()

// 数据状态
const projects = ref([])
const userList = ref([])
const loading = ref(false)

// 搜索和筛选
const searchText = ref('')
const filterStatus = ref('')
const filterPm = ref('')

const hasActiveFilters = computed(() => searchText.value || filterStatus.value || filterPm.value)

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 选中行
const selectedRowKeys = ref([])

// 统计卡片
const statsCards = ref([
  { label: '总项目数', value: '0', icon: FolderOutlined, type: 'primary' },
  { label: '活跃项目', value: '0', icon: CheckCircleOutlined, type: 'success' },
  { label: '团队成员', value: '0', icon: TeamOutlined, type: 'purple' },
  { label: '今日执行', value: '0', icon: ThunderboltOutlined, type: 'warning' },
])

// 当前产品线
const currentProductLine = computed(() => userStore.currentProductLine)

// 表格列
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, align: 'center', fixed: 'left' },
  { title: '项目名称', dataIndex: 'name', key: 'name', width: 260, fixed: 'left', ellipsis: true, align: 'left', className: 'col-name-left' },
  { title: '状态', dataIndex: 'status', key: 'status', width: 110, align: 'center' },
  { title: '优先级', key: 'priority', width: 100, align: 'center' },
  { title: '周期', key: 'period', width: 220, align: 'center' },
  { title: '负责人', key: 'pm', width: 120, align: 'center' },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at', width: 170, align: 'center' },
  { title: '操作', key: 'actions', width: 120, fixed: 'right', align: 'center' },
]

// 状态颜色（使用常量）
const getStatusColor = (status) => getProjectStatusConfig(status)?.color || '#9CA3AF'
const getStatusBg = (status) => getProjectStatusConfig(status)?.bg || '#F9FAFB'
const getStatusText = (status) => getProjectStatusConfig(status)?.label || '未知'

const pmColorList = ['#6366F1', '#EC4899', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4']

const getPmColor = (name) => stringToColor(name)

// 复用常量
const statusOptions = PROJECT_STATUS_LIST
const priorityOptions = PROJECT_PRIORITY_LIST

// 优先级
const getPriorityText = (priority) => getProjectPriorityConfig(priority)?.label || '普通'
const getPriorityClass = (priority) => {
  const classMap = { 0: 'priority-low', 1: 'priority-medium', 2: 'priority-high' }
  return classMap[priority] ?? 'priority-low'
}

// 周期
const formatPeriod = (start, end) => {
  if (!start && !end) return '—'
  const fmt = (d) => {
    if (!d) return ''
    const date = new Date(d)
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
  }
  if (start && end) return `${fmt(start)} ~ ${fmt(end)}`
  if (start) return `${fmt(start)} ~`
  return `~ ${fmt(end)}`
}

// 加载数据
const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
    }
    if (searchText.value) params.search = searchText.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPm.value) params.pm = filterPm.value
    if (currentProductLine.value) params.product_line = currentProductLine.value.id

    const res = await getProjects(params)
    const list = res.result?.list || []
    // 将负责人 ID 映射为用户名
    list.forEach(p => {
      if (p.pm) {
        const user = userList.value.find(u => u.id === p.pm)
        p._pm_name = user ? user.username : `用户 #${p.pm}`
      }
    })
    projects.value = list
    pagination.total = res.result?.itemCount || 0
    updateStats()
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const list = projects.value
  statsCards.value[0].value = pagination.total || list.length
  statsCards.value[1].value = list.filter(p => p.status === 'active').length
  statsCards.value[2].value = Math.floor(Math.random() * 50) + 10
  statsCards.value[3].value = Math.floor(Math.random() * 100) + 20
}

const loadUsers = async () => {
  try {
    const res = await getAllUsers()
    userList.value = res.result || res || []
  } catch (e) {
    console.error('加载用户失败:', e)
  }
}

// 搜索/筛选
const handleSearch = () => {
  pagination.current = 1
  loadProjects()
}

const handleFilterChange = () => {
  handleSearch()
}

const resetFilters = () => {
  searchText.value = ''
  filterStatus.value = ''
  filterPm.value = ''
}

// 分页
const handlePageChange = () => {
  loadProjects()
}

// 行选择
const onSelectChange = (keys) => {
  selectedRowKeys.value = keys
}

// 操作
const goToNewProject = () => router.push('/projects/new')
const viewProjectDetail = (id) => router.push(`/projects/${id}`)
const editProject = (id) => router.push(`/projects/${id}/edit`)

const deleteModalVisible = ref(false)
const deleteTarget = ref({ type: 'single', data: null })

const openDeleteModal = (type, data) => {
  deleteTarget.value = { type, data }
  deleteModalVisible.value = true
}

const handleDelete = async () => {
  try {
    if (deleteTarget.value.type === 'batch') {
      await batchDeleteProjects(selectedRowKeys.value)
      selectedRowKeys.value = []
    } else {
      await deleteProject(deleteTarget.value.data.id)
    }
    deleteModalVisible.value = false
    await loadProjects()
    message.success('删除成功')
  } catch {
    message.error('删除失败')
  }
}

const handleStatusChange = async (record, status) => {
  try {
    await updateProject(record.id, { status })
    record.status = status
    message.success('状态已更新')
  } catch {
    message.error('更新状态失败')
  }
}

const handlePriorityChange = async (record, priority) => {
  try {
    await updateProject(record.id, { priority: Number(priority) })
    record.priority = Number(priority)
    message.success('优先级已更新')
  } catch {
    message.error('更新优先级失败')
  }
}

onMounted(async () => {
  await loadUsers()
  loadProjects()
})
</script>

<style scoped>
.project-view {
  max-width: 1400px;
  margin: 0 auto;
}

.btn-icon-text {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* ─── 筛选区 ─── */

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
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
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

.table-count {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.table-count strong {
  color: var(--color-text-primary);
  font-weight: var(--font-semibold);
}

.toolbar__right {
  display: flex;
  gap: var(--space-3);
}

/* ─── 项目名称单元格 ─── */
.project-name-cell {
  cursor: pointer;
}

.project-name-cell:hover .project-name {
  color: var(--color-primary);
  text-decoration: underline;
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ─── 状态标签 ─── */
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  border: none;
}

.status-tag--clickable {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  user-select: none;
  white-space: nowrap;
}

.status-tag--clickable:hover {
  opacity: 0.8;
}

.status-dot-sm {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ─── 优先级标签 ─── */
.period-text {
  font-size: 14px;
  color: var(--color-text);
}

.status-dot-sm {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.priority-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  user-select: none;
  white-space: nowrap;
}

.priority-tag:hover {
  opacity: 0.8;
}

.priority-low {
  background: #f0fdf4;
  color: #15803d;
}

.priority-medium {
  background: #fefce8;
  color: #a16207;
}

.priority-high {
  background: #fef2f2;
  color: #dc2626;
}

/* ─── 负责人 ─── */
.pm-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.pm-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: var(--font-bold);
  color: white;
  flex-shrink: 0;
}

.pm-name {
  font-size: 14px;
  color: var(--color-text);
  font-weight: 500;
}

/* ─── 操作按钮 ─── */
.action-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-1);
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
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
  font-weight: var(--font-semibold);
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

/* ─── 模态框表单 ─── */
.modal-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  padding: var(--space-2) 0;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.required {
  color: var(--color-error);
  margin-left: 2px;
}

.form-input {
  border-radius: var(--radius-md);
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.form-error {
  font-size: var(--text-xs);
  color: var(--color-error);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

/* 产品线展示 */
.product-line-display {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-gray-50);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.pl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pl-name {
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
  flex: 1;
}

.pl-tag {
  font-size: var(--text-xs);
}

/* 状态选项 */
.status-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-dot-lg {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 负责人选项 */
.pm-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.pm-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 模态框底部 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--color-border);
}

/* ─── 自定义按钮系统 ─── */
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

/* ─── 响应式 ─── */
@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .filter-bar {
    overflow-x: auto;
  }

  .filter-bar__left {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .page-header__right {
    justify-content: flex-end;
  }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3);
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

/* ─── 列表内下拉菜单 ─── */
</style>

<style>
/* 页面标题区 */
.page-hero {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
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

/* 统计卡片 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: 24px;
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  transition: all var(--transition-base);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.stat-card__icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.stat-card--primary .stat-card__icon { background: #fee2e2; color: #e94f4f; }
.stat-card--success .stat-card__icon { background: #d1fae5; color: #10b981; }
.stat-card--purple .stat-card__icon { background: #ede9fe; color: #8b5cf6; }
.stat-card--warning .stat-card__icon { background: #fef3c7; color: #f59e0b; }

.stat-card__value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-card__label {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

/* 筛选区 */
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
  border-radius: 8px;
  padding: 0 12px;
  background: var(--color-bg-base);
  width: 260px;
  flex-shrink: 0;
  gap: 8px;
}

.filter-bar__filters {
  display: flex;
  align-items: center;
  gap: 12px;
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

.filter-bar__search:focus-within {
  border-color: #e94f4f;
  box-shadow: 0 0 0 2px rgba(233, 79, 79, 0.1);
}

.filter-bar__search-icon {
  color: var(--color-text-tertiary);
  font-size: 13px;
  flex-shrink: 0;
}

.filter-bar__input {
  flex: 1;
  border: none;
  outline: none;
  padding: 9px 0;
  font-size: 13px;
  background: transparent;
  color: var(--color-text-primary);
}

.filter-bar__select {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  background: var(--color-bg-base);
  color: var(--color-text-primary);
  outline: none;
  cursor: pointer;
  min-width: 100px;
  transition: border-color 0.2s;
}

.filter-bar__select:focus {
  border-color: #e94f4f;
}

/* 表格卡片 */
.table-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

:deep(.project-table) {
  border-radius: var(--radius-lg);
}

:deep(.project-table .ant-table) {
  border-radius: var(--radius-lg);
}

:deep(.project-table .ant-table-thead > tr:first-child > th:first-child) {
  border-radius: var(--radius-lg) 0 0 0;
}

:deep(.project-table .ant-table-thead > tr:first-child > th:last-child) {
  border-radius: 0 var(--radius-lg) 0 0;
}

/* 表头样式 - 优雅渐变设计 */
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

:deep(.ant-table-thead > tr > th.ant-table-cell:first-child) {
  border-radius: var(--radius-lg) 0 0 0 !important;
}

:deep(.ant-table-thead > tr > th.ant-table-cell:last-child) {
  border-radius: 0 var(--radius-lg) 0 0 !important;
}

/* 数据行居中 */
:deep(.ant-table-tbody .ant-table-cell) {
  text-align: center !important;
  padding: 12px 16px !important;
}

/* 项目名称列靠左对齐 */
:deep(.col-name-left) {
  text-align: left !important;
}

:deep(.col-name-left .project-name-cell) {
  display: flex;
  justify-content: flex-start;
}

/* 数据行悬停 */
:deep(.project-table__row:hover > td) {
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
