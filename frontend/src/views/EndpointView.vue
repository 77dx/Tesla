<template>
  <div class="endpoint-view">
    <!-- 页面标题区 -->
    <div class="page-hero">
      <div class="page-hero__content">
        <p class="page-hero__desc">管理测试接口，支持 HTTP 全方法测试</p>
        <button v-if="hasPermission('endpoint:create')" class="btn btn--primary" @click="router.push('/endpoints/new')">
          <PlusOutlined />
          新建接口
        </button>
      </div>
    </div>

    <!-- 筛选区 -->
    <div class="filter-bar">
      <div class="filter-bar__left">
        <div class="filter-bar__search">
          <span class="filter-bar__search-icon">&#128269;</span>
          <input
            type="text"
            v-model="searchText"
            placeholder="搜索名称/URL/ID..."
            class="filter-bar__input"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="filter-bar__filters">
          <div class="filter-item">
            <label class="filter-label">所属项目</label>
            <select v-model="filterProject" class="filter-bar__select" @change="handleSearch">
              <option value="">全部</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label class="filter-label">请求方法</label>
            <select v-model="filterMethod" class="filter-bar__select" @change="handleSearch">
              <option value="">全部</option>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
        </div>
      </div>
      <div class="filter-bar__right">
        <button class="btn btn--primary btn--sm" @click="handleSearch">搜索</button>
        <button class="btn btn--ghost btn--sm" @click="resetFilter">重置</button>
      </div>
    </div>

    <!-- 表格卡片 -->
    <div class="table-card">
      <div class="table-card__toolbar">
        <div class="toolbar__left">
          <span class="toolbar__info">共 <strong>{{ pagination.itemCount }}</strong> 个接口</span>
        </div>
        <div class="toolbar__right">
          <button class="btn btn--ghost btn--sm" @click="() => loadEndpoints(1)" :disabled="loading">
            <span class="btn__icon" :class="{ 'btn__icon--spin': loading }">&#8635;</span>
          </button>
          <button
            class="btn btn--sm"
            :class="selectedRowKeys.length ? 'btn--danger' : 'btn--disabled'"
            :disabled="!selectedRowKeys.length"
            @click="openBatchDeleteModal"
          >
            &#128465; 批量删除{{ selectedRowKeys.length ? ` (${selectedRowKeys.length})` : '' }}
          </button>
        </div>
      </div>

      <a-table
        :dataSource="endpoints"
        :columns="columns"
        :row-key="record => record.id"
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        :pagination="false"
        :loading="loading"
        :scroll="{ x: 1200 }"
        size="middle"
        class="endpoint-table"
      >
        <!-- 接口名称 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <div class="endpoint-name-cell" @click="viewDetail(record.id)">
              <span class="endpoint-name">{{ record.name }}</span>
            </div>
          </template>

          <!-- 请求方法 -->
          <template v-if="column.key === 'method'">
            <span class="method-tag" :class="`method-tag--${record.method.toLowerCase()}`">
              {{ record.method }}
            </span>
          </template>

          <!-- URL -->
          <template v-if="column.key === 'url'">
            <span class="url-text" :title="record.url">{{ record.url }}</span>
          </template>

          <!-- 请求头 -->
          <template v-if="column.key === 'headers'">
            <span v-if="record.headers" class="badge badge--success">✓</span>
            <span v-else class="badge badge--muted">—</span>
          </template>

          <!-- 参数 -->
          <template v-if="column.key === 'params'">
            <span v-if="record.params || record.json || record.data" class="badge badge--success">✓</span>
            <span v-else class="badge badge--muted">—</span>
          </template>

          <!-- 更新人 -->
          <template v-if="column.key === 'created_by'">
            <span v-if="record.created_by_name" class="updater-tag" :style="{ background: stringToColor(record.created_by_name) + '22', color: stringToColor(record.created_by_name) }">
              {{ record.created_by_name }}
            </span>
            <span v-else class="text-tertiary">—</span>
          </template>

          <!-- 操作 -->
          <template v-if="column.key === 'actions'">
            <div class="action-cell">
              <a-tooltip title="编辑接口">
                <a-button type="text" size="small" class="action-btn" @click="editEndpoint(record.id)">
                  <EditOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="查看详情">
                <a-button type="text" size="small" class="action-btn" @click="viewDetail(record.id)">
                  <EyeOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="删除">
                <a-button
                  type="text"
                  size="small"
                  class="action-btn action-btn--danger"
                  @click="deleteEndpointItem(record.id)"
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
            <ApiOutlined class="empty-icon" />
            <p class="empty-title">暂无接口</p>
            <p class="empty-desc">创建一个新接口，开始你的接口测试之旅</p>
            <button v-if="hasPermission('endpoint:create')" class="btn btn--primary" @click="router.push('/endpoints/new')">
              <PlusOutlined />
              创建第一个接口
            </button>
          </div>
        </template>
      </a-table>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.pageCount > 1">
        <a-pagination
          v-model:current="pagination.page"
          :total="pagination.itemCount"
          :page-size="pagination.pageSize"
          :show-total="(total) => `共 ${total} 条`"
          show-quick-jumper
          @change="changePage"
        />
      </div>
    </div>

    <!-- 批量删除确认弹窗 -->
    <a-modal
      v-model:open="deleteModalVisible"
      title="确认删除"
      :maskClosable="false"
      @ok="handleBatchDelete"
      okText="删除"
      cancelText="取消"
      okType="danger"
    >
      <p style="font-size: 14px; color: var(--color-text-primary);">
        确定要删除选中的 {{ selectedRowKeys.length }} 个接口吗？此操作不可恢复。
      </p>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  ApiOutlined,
} from '@ant-design/icons-vue'
import { getEndpoints, deleteEndpoint } from '@/api/endpoint'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const pmColorList = ['#6366F1', '#EC4899', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EF4444', '#06B6D4']
const stringToColor = (str) => {
  if (!str) return pmColorList[0]
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  return pmColorList[Math.abs(hash) % pmColorList.length]
}

const router = useRouter()
const userStore = useUserStore()
const { hasPermission } = userStore

// 状态
const endpoints = ref([])
const projects = ref([])
const loading = ref(false)
const selectedRowKeys = ref([])
const deleteModalVisible = ref(false)

const searchText = ref('')
const filterProject = ref('')
const filterMethod = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  pageCount: 1,
  itemCount: 0
})

// 表格列
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, align: 'center' },
  { title: '接口名称', dataIndex: 'name', key: 'name', width: 200, ellipsis: true, align: 'left', className: 'col-name-left' },
  { title: '请求方法', key: 'method', width: 100, align: 'center' },
  { title: 'URL', key: 'url', width: 300, ellipsis: true, align: 'left', className: 'col-name-left' },
  { title: '请求头', key: 'headers', width: 80, align: 'center' },
  { title: '参数', key: 'params', width: 80, align: 'center' },
  { title: '更新人', key: 'created_by', width: 110, align: 'center' },
  { title: '操作', key: 'actions', width: 140, fixed: 'right', align: 'center' },
]

// 工具函数
const onSelectChange = (keys) => {
  selectedRowKeys.value = keys
}

// 加载数据
const loadEndpoints = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: pagination.pageSize
    }
    if (searchText.value) params.search = searchText.value
    if (filterProject.value) params.project = filterProject.value
    if (filterMethod.value) params.method = filterMethod.value
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id

    const res = await getEndpoints(params)
    endpoints.value = res.result?.list || []
    pagination.page = res.result?.page || page
    pagination.pageCount = res.result?.pageCount || 1
    pagination.itemCount = res.result?.itemCount || 0
  } catch (e) {
    console.error('加载接口列表失败:', e)
  } finally {
    loading.value = false
  }
}

// 搜索和筛选
const handleSearch = () => {
  selectedRowKeys.value = []
  pagination.page = 1
  loadEndpoints(1)
}

const resetFilter = () => {
  searchText.value = ''
  filterProject.value = ''
  filterMethod.value = ''
  selectedRowKeys.value = []
  pagination.page = 1
  loadEndpoints(1)
}

const changePage = (page) => {
  selectedRowKeys.value = []
  loadEndpoints(page)
}

// 操作
const viewDetail = (id) => router.push(`/endpoints/${id}`)
const editEndpoint = (id) => router.push(`/endpoints/edit/${id}`)

const deleteEndpointItem = async (id) => {
  const ok = await confirm('确定要删除这个接口吗？', { type: 'danger' })
  if (!ok) return
  try {
    await deleteEndpoint(id)
    endpoints.value = endpoints.value.filter(e => e.id !== id)
    message.success('删除成功')
  } catch (e) {
    console.error('删除失败:', e)
    message.error('删除失败')
  }
}

const openBatchDeleteModal = () => {
  if (!selectedRowKeys.value.length) return
  deleteModalVisible.value = true
}

const handleBatchDelete = async () => {
  try {
    await Promise.all(selectedRowKeys.value.map(id => deleteEndpoint(id)))
    endpoints.value = endpoints.value.filter(i => !selectedRowKeys.value.includes(i.id))
    selectedRowKeys.value = []
    deleteModalVisible.value = false
    message.success(`成功删除 ${selectedRowKeys.value.length} 个接口`)
  } catch (e) {
    console.error('批量删除失败:', e)
    message.error('批量删除失败')
  }
}

onMounted(async () => {
  await loadEndpoints()
  try {
    const pr = await getProjects({
      page_size: 200,
      ...(userStore.currentProductLine ? { product_line: userStore.currentProductLine.id } : {})
    })
    projects.value = pr.result?.list || []
  } catch (e) {
    console.error('加载项目列表失败:', e)
  }
})
</script>
<style scoped>
.endpoint-view {
  max-width: 1400px;
  margin: 0 auto;
}

/* ─── 方法标签 ─── */
.method-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.method-tag--get    { background: #d1fae5; color: #059669; }
.method-tag--post   { background: #dbeafe; color: #2563eb; }
.method-tag--put    { background: #fef3c7; color: #d97706; }
.method-tag--delete { background: #fee2e2; color: #dc2626; }
.method-tag--patch  { background: #ede9fe; color: #7c3aed; }

/* ─── URL 文字 ─── */
.url-text {
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  color: var(--color-text-secondary);
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

/* ─── Badge ─── */
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.badge--success { background: #d1fae5; color: #059669; }
.badge--muted { background: #f3f4f6; color: #9ca3af; }

/* ─── 接口名称单元格 ─── */
.endpoint-name-cell {
  cursor: pointer;
  padding: 4px 0;
}

.endpoint-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.15s;
}

.endpoint-name-cell:hover .endpoint-name {
  color: var(--color-primary-hover);
  text-decoration: underline;
}

/* ─── 负责人头像文字 ─── */
.pm-avatar-text {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e8f4fd, #d6eaf8);
  color: #1a6fa8;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

/* ─── 更新人标签 ─── */
.updater-tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

/* ─── 分页 ─── */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
}
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
  flex: 1;
  min-width: 0;
}

.filter-bar__right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.filter-bar__search {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0 12px;
  background: white;
  width: 240px;
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
  border: none;
  outline: none;
  padding: 9px 0;
  font-size: 13px;
  width: 100%;
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
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-bar__select {
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  font-size: 13px;
  background: white;
  color: var(--color-text-primary);
  outline: none;
  cursor: pointer;
  min-width: 120px;
  transition: border-color 0.2s;
}

.filter-bar__select:focus {
  border-color: var(--color-primary);
}

/* 表格卡片 */
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
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-border);
  background: #fafafa;
}

.toolbar__left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar__info {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.toolbar__info strong {
  color: var(--color-text-primary);
  font-weight: 600;
}

.toolbar__right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn__icon {
  font-size: 16px;
  line-height: 1;
  display: inline-block;
}

.btn__icon--spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 表格样式 */
:deep(.endpoint-table) {
  border-radius: var(--radius-lg);
}

:deep(.endpoint-table .ant-table-thead > tr > th.ant-table-cell) {
  background: linear-gradient(135deg, #5c1a1a 0%, #3b0a0a 100%) !important;
  color: #ffffff !important;
  font-weight: 600;
  font-size: 13px !important;
  text-align: center !important;
  padding: 14px 16px !important;
  border-bottom: none !important;
  letter-spacing: 0.3px;
}

:deep(.endpoint-table .ant-table-tbody .ant-table-cell) {
  text-align: center !important;
  padding: 12px 16px !important;
}

:deep(.col-name-left) {
  text-align: left !important;
}

:deep(.endpoint-table .ant-table-tbody .ant-table-row:hover > td) {
  background: #f8f9fa !important;
}

/* 操作按钮 */
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
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  transition: all 0.15s;
}

.action-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

.action-btn--danger:hover {
  color: var(--color-error);
  background: var(--color-error-bg);
}

/* 空状态 */
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
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.empty-desc {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin: 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .filter-bar {
    overflow-x: auto;
  }

  .filter-bar__left {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar__left {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar__right {
    justify-content: flex-end;
  }

  .page-hero__content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
