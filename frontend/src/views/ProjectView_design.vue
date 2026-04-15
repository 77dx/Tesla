<template>
  <div class="project-management">
    <!-- 页面标题和概览 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">项目管理</h1>
        <p class="page-description">管理所有测试项目，支持多项目并行协作和权限控制</p>
      </div>
      <div class="header-actions">
        <a-button type="primary" size="large" @click="showCreateModal">
          <template #icon><PlusOutlined /></template>
          新建项目
        </a-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <a-row :gutter="[24, 24]" class="stats-section">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6f7ff; color: #1890ff;">
              <FolderOutlined />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalProjects || 0 }}</div>
              <div class="stat-title">总项目数</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f6ffed; color: #52c41a;">
              <CheckCircleOutlined />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activeProjects || 0 }}</div>
              <div class="stat-title">活跃项目</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon" style="background: #fff7e6; color: #fa8c16;">
              <TeamOutlined />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalMembers || 0 }}</div>
              <div class="stat-title">总成员数</div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card class="stat-card" :bordered="false">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f9f0ff; color: #722ed1;">
              <RocketOutlined />
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.recentExecutions || 0 }}</div>
              <div class="stat-title">今日执行</div>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 过滤和搜索区域 -->
    <a-card class="filter-card">
      <a-row :gutter="[16, 16]" align="middle">
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索项目名称、描述或负责人"
            @search="handleSearch"
            allow-clear
          />
        </a-col>
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-select
            v-model:value="filterStatus"
            placeholder="项目状态"
            style="width: 100%"
            allow-clear
            @change="handleFilterChange"
          >
            <a-select-option value="active">活跃</a-select-option>
            <a-select-option value="planning">规划中</a-select-option>
            <a-select-option value="testing">测试中</a-select-option>
            <a-select-option value="completed">已完成</a-select-option>
            <a-select-option value="archived">已归档</a-select-option>
          </a-select>
        </a-col>
        <a-col :xs="24" :sm="12" :md="8" :lg="6">
          <a-select
            v-model:value="filterPm"
            placeholder="负责人"
            style="width: 100%"
            allow-clear
            @change="handleFilterChange"
          >
            <a-select-option v-for="user in userList" :key="user.user_id" :value="user.user_id">
              {{ user.nickname || user.username }}
            </a-select-option>
          </a-select>
        </a-col>
        <a-col :xs="24" :sm="12" :md="8" :lg="6" class="filter-actions">
          <a-button @click="resetFilters">重置</a-button>
          <a-button type="primary" @click="handleSearch">搜索</a-button>
        </a-col>
      </a-row>
    </a-card>

    <!-- 项目列表 -->
    <a-card class="projects-card">
      <template #title>
        <div class="projects-title">
          <span>项目列表</span>
          <span class="projects-count">共 {{ pagination.total || 0 }} 个项目</span>
        </div>
      </template>
      
      <template #extra>
        <a-space>
          <a-button :disabled="selectedRowKeys.length === 0" @click="handleBatchDelete" danger>
            <template #icon><DeleteOutlined /></template>
            批量删除
          </a-button>
          <a-button @click="refreshProjects">
            <template #icon><SyncOutlined /></template>
            刷新
          </a-button>
        </a-space>
      </template>

      <a-table
        :dataSource="projects"
        :columns="columns"
        :row-key="record => record.id"
        :row-selection="{ selectedRowKeys, onChange: onSelectChange }"
        :pagination="false"
        :loading="loading"
        size="middle"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a @click="viewProjectDetail(record.id)" class="project-name">
              <FolderOpenOutlined style="margin-right: 8px; color: #1890ff;" />
              {{ record.name }}
            </a>
          </template>
          
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'pm'">
            <div v-if="record.pm_name" class="pm-info">
              <a-avatar :size="24" style="background-color: #1890ff;">
                {{ record.pm_name.charAt(0).toUpperCase() }}
              </a-avatar>
              <span class="pm-name">{{ record.pm_name }}</span>
            </div>
            <span v-else>-</span>
          </template>
          
          <template v-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          
          <template v-if="column.key === 'actions'">
            <a-space size="small">
              <a-button type="link" size="small" @click="editProject(record)">
                <template #icon><EditOutlined /></template>
              </a-button>
              <a-button type="link" size="small" @click="viewProjectDetail(record.id)">
                <template #icon><EyeOutlined /></template>
              </a-button>
              <a-button type="link" size="small" danger @click="deleteProject(record)">
                <template #icon><DeleteOutlined /></template>
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>

      <!-- 空状态 -->
      <template v-if="projects.length === 0 && !loading">
        <a-empty class="empty-state" description="暂无项目数据">
          <template #image>
            <img src="https://gw.alipayobjects.com/zos/antfincdn/ZHrcdLPrvN/empty.svg" />
          </template>
          <a-button type="primary" @click="showCreateModal">创建第一个项目</a-button>
        </a-empty>
      </template>

      <!-- 分页 -->
      <div v-if="projects.length > 0" class="pagination-section">
        <a-pagination
          v-model:current="pagination.current"
          v-model:pageSize="pagination.pageSize"
          :total="pagination.total"
          :show-total="total => `共 ${total} 条`"
          :show-size-changer="true"
          :page-size-options="['10', '20', '50', '100']"
          @change="handlePageChange"
          @showSizeChange="handlePageSizeChange"
        />
      </div>
    </a-card>

    <!-- 创建/编辑项目模态框 - 重新设计 -->
    <a-modal
      v-model:open="showModal"
      :title="editingProject ? '编辑项目' : '创建新项目'"
      width="700px"
      @ok="handleSubmit"
      @cancel="closeModal"
      :confirm-loading="submitting"
      class="project-modal"
    >
      <div class="modal-content">
        <!-- 模态框头部提示 -->
        <div v-if="!editingProject" class="modal-header-tip">
          <a-alert 
            message="创建新项目" 
            description="填写项目基本信息以创建新的测试项目。所有项目都将与当前产品线关联。" 
            type="info" 
            show-icon 
            closable
          />
        </div>
        <div v-else class="modal-header-tip">
          <a-alert 
            message="编辑项目信息" 
            description="修改项目的基本信息和配置。" 
            type="warning" 
            show-icon 
            closable
          />
        </div>
        
        <!-- 主表单区域 -->
        <div class="form-section">
          <a-form
            ref="formRef"
            :model="formData"
            :rules="formRules"
            :label-col="{ span: 8 }"
            :wrapper-col="{ span: 16 }"
            layout="horizontal"
            size="large"
          >
            <a-row :gutter="[24, 16]">
              <a-col :span="24">
                <a-form-item label="项目名称" name="name" required>
                  <a-input 
                    v-model:value="formData.name" 
                    placeholder="请输入项目名称（2-50个字符）"
                    size="large"
                    :prefix="h(EditOutlined)"
                  />
                  <div class="form-item-help">项目的唯一标识名称，建议使用英文或数字</div>
                </a-form-item>
              </a-col>
              
              <a-col :span="24">
                <a-form-item label="项目描述" name="intro">
                  <a-textarea
                    v-model:value="formData.intro"
                    placeholder="请输入项目描述，包括项目目标、范围等信息"
                    :rows="4"
                    :maxlength="500"
                    show-count
                    size="large"
                  />
                  <div class="form-item-help">详细的项目描述有助于团队成员理解项目背景和目标</div>
                </a-form-item>
              </a-col>
              
              <a-col :span="12">
                <a-form-item label="项目状态" name="status">
                  <a-select 
                    v-model:value="formData.status" 
                    placeholder="请选择项目状态"
                    size="large"
                  >
                    <a-select-option value="planning">
                      <div class="status-option">
                        <span class="status-dot status-dot-planning"></span>
                        规划中
                      </div>
                    </a-select-option>
                    <a-select-option value="active">
                      <div class="status-option">
                        <span class="status-dot status-dot-active"></span>
                        活跃
                      </div>
                    </a-select-option>
                    <a-select-option value="testing">
                      <div class="status-option">
                        <span class="status-dot status-dot-testing"></span>
                        测试中
                      </div>
                    </a-select-option>
                    <a-select-option value="completed">
                      <div class="status-option">
                        <span class="status-dot status-dot-completed"></span>
                        已完成
                      </div>
                    </a-select-option>
                    <a-select-option value="archived">
                      <div class="status-option">
                        <span class="status-dot status-dot-archived"></span>
                        已归档
                      </div>
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              
              <a-col :span="12">
                <a-form-item label="项目负责人" name="pm">
                  <a-select 
                    v-model:value="formData.pm" 
                    placeholder="请选择负责人"
                    size="large"
                    :show-search="true"
                    option-filter-prop="children"
                  >
                    <a-select-option :value="null">
                      <div class="user-option">
                        <a-avatar :size="20" style="background-color: #d9d9d9; margin-right: 8px;">
                          <UserOutlined />
                        </a-avatar>
                        未指定负责人
                      </div>
                    </a-select-option>
                    <a-select-option v-for="user in userList" :key="user.user_id" :value="user.user_id">
                      <div class="user-option">
                        <a-avatar :size="20" :style="{ backgroundColor: stringToColor(user.username), marginRight: '8px' }">
                          {{ user.nickname?.charAt(0) || user.username?.charAt(0) }}
                        </a-avatar>
                        {{ user.nickname || user.username }}
                        <span class="user-email">{{ user.email || user.username }}</span>
                      </div>
                    </a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              
              <a-col :span="24">
                <a-form-item label="项目地址" name="url">
                  <a-input 
                    v-model:value="formData.url" 
                    placeholder="http://example.com 或 https://example.com"
                    size="large"
                    :prefix="h(GlobalOutlined)"
                  />
                  <div class="form-item-help">项目的部署地址或测试环境地址（可选）</div>
                </a-form-item>
              </a-col>
              
              <a-col :span="24">
                <a-form-item label="所属产品线" name="product_line">
                  <a-input-group compact>
                    <a-input 
                      :value="currentProductLine ? currentProductLine.name : '默认产品线'" 
                      placeholder="请选择产品线" 
                      disabled
                      size="large"
                      style="width: calc(100% - 120px)"
                    />
                    <a-button type="primary" disabled size="large">
                      不可更改
                    </a-button>
                  </a-input-group>
                  <div class="form-item-help">项目将关联到当前产品线，不可更改</div>
                </a-form-item>
              </a-col>
              
              <!-- 高级设置部分 -->
              <a-col :span="24">
                <a-divider orientation="left" style="margin-top: 16px;">高级设置</a-divider>
                <a-row :gutter="[16, 16]" style="margin-top: 8px;">
                  <a-col :span="12">
                    <a-form-item label="项目优先级">
                      <a-select placeholder="普通" size="large" disabled>
                        <a-select-option value="low">低</a-select-option>
                        <a-select-option value="normal">普通</a-select-option>
                        <a-select-option value="high">高</a-select-option>
                        <a-select-option value="urgent">紧急</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                  <a-col :span="12">
                    <a-form-item label="访问权限">
                      <a-select placeholder="私有" size="large" disabled>
                        <a-select-option value="private">私有（仅成员可见）</a-select-option>
                        <a-select-option value="public">公开（所有用户可见）</a-select-option>
                        <a-select-option value="restricted">受限（指定角色可见）</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                </a-row>
              </a-col>
            </a-row>
          </a-form>
        </div>
        
        <!-- 表单验证状态 -->
        <div v-if="formData.name" class="form-preview">
          <a-alert 
            :message="`项目预览: ${formData.name}`" 
            :description="formData.intro || '暂无描述'"
            type="info"
            show-icon
            style="margin-top: 16px;"
          />
        </div>
      </div>
      
      <template #footer>
        <a-space>
          <a-button @click="closeModal" size="large">取消</a-button>
          <a-button 
            type="primary" 
            @click="handleSubmit" 
            :loading="submitting" 
            size="large"
            :disabled="!formData.name"
          >
            {{ editingProject ? '更新项目' : '创建项目' }}
          </a-button>
        </a-space>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, h } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  PlusOutlined,
  FolderOutlined,
  CheckCircleOutlined,
  TeamOutlined,
  RocketOutlined,
  DeleteOutlined,
  SyncOutlined,
  FolderOpenOutlined,
  EditOutlined,
  EyeOutlined,
  ExclamationCircleOutlined,
  UserOutlined,
  GlobalOutlined
} from '@ant-design/icons-vue'
import { Modal, message, Alert } from 'ant-design-vue'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/project'
import { getAllUsers } from '@/api/account'

const router = useRouter()
const userStore = useUserStore()

// 数据状态
const projects = ref([])
const userList = ref([])
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const editingProject = ref(null)

// 搜索和过滤
const searchText = ref('')
const filterStatus = ref(null)
const filterPm = ref(null)

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0
})

// 选中行
const selectedRowKeys = ref([])

// 统计信息
const stats = reactive({
  totalProjects: 0,
  activeProjects: 0,
  totalMembers: 0,
  recentExecutions: 0
})

// 表单数据
const formData = reactive({
  name: '',
  intro: '',
  url: '',
  status: 'active',
  pm: null,
  product_line: null
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '项目名称长度在2到50个字符之间', trigger: 'blur' }
  ],
  url: [
    { pattern: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/, message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}

// 表格列定义
const columns = [
  {
    title: '项目名称',
    dataIndex: 'name',
    key: 'name',
    ellipsis: true
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '描述',
    dataIndex: 'intro',
    key: 'intro',
    ellipsis: true,
    width: 200
  },
  {
    title: '负责人',
    dataIndex: 'pm',
    key: 'pm',
    width: 120
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150
  },
  {
    title: '操作',
    key: 'actions',
    width: 120
  }
]

// 获取当前产品线
const currentProductLine = computed(() => userStore.currentProductLine)

// 状态颜色映射
const getStatusColor = (status) => {
  const colorMap = {
    planning: 'blue',
    active: 'green',
    testing: 'orange',
    completed: 'cyan',
    archived: 'default'
  }
  return colorMap[status] || 'default'
}

// 状态文本映射
const getStatusText = (status) => {
  const textMap = {
    planning: '规划中',
    active: '活跃',
    testing: '测试中',
    completed: '已完成',
    archived: '已归档'
  }
  return textMap[status] || '未知'
}

// 加载项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    }
    
    if (searchText.value) params.search = searchText.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPm.value) params.pm = filterPm.value
    if (currentProductLine.value) params.product_line = currentProductLine.value.id
    
    const res = await getProjects(params)
    projects.value = res.result?.list || []
    pagination.total = res.result?.itemCount || 0
    
    // 更新统计信息
    updateStats(res.result?.list || [])
  } catch (error) {
    console.error('加载项目列表失败:', error)
    message.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

// 更新统计信息
const updateStats = (projectList) => {
  stats.totalProjects = projectList.length
  stats.activeProjects = projectList.filter(p => p.status === 'active').length
  
  // 模拟其他统计数据（实际项目中应从API获取）
  stats.totalMembers = Math.floor(Math.random() * 50) + 10
  stats.recentExecutions = Math.floor(Math.random() * 100) + 20
}

// 搜索处理
const handleSearch = () => {
  pagination.current = 1
  loadProjects()
}

// 过滤变更处理
const handleFilterChange = () => {
  handleSearch()
}

// 重置过滤器
const resetFilters = () => {
  searchText.value = ''
  filterStatus.value = null
  filterPm.value = null
  handleSearch()
}

// 分页变化
const handlePageChange = (page, pageSize) => {
  pagination.current = page
  pagination.pageSize = pageSize
  loadProjects()
}

// 分页大小变化
const handlePageSizeChange = (current, size) => {
  pagination.current = 1
  pagination.pageSize = size
  loadProjects()
}

// 刷新项目
const refreshProjects = () => {
  loadProjects()
  message.success('刷新成功')
}

// 行选择变化
const onSelectChange = (selectedKeys) => {
  selectedRowKeys.value = selectedKeys
}

// 查看项目详情
const viewProjectDetail = (projectId) => {
  router.push(`/projects/${projectId}`)
}

// 编辑项目
const editProject = (project) => {
  editingProject.value = project
  Object.assign(formData, {
    name: project.name,
    intro: project.intro || '',
    url: project.url || '',
    status: project.status || 'active',
    pm: project.pm || null,
    product_line: project.product_line || currentProductLine.value?.id || null
  })
  showModal.value = true
}

// 删除项目
const deleteProject = (project) => {
  Modal.confirm({
    title: '确认删除',
    icon: <ExclamationCircleOutlined />,
    content: `确定要删除项目 "${project.name}" 吗？删除后数据将无法恢复。`,
    okText: '确认删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        await deleteProject(project.id)
        message.success('删除成功')
        loadProjects()
      } catch (error) {
        console.error('删除失败:', error)
        message.error('删除失败')
      }
    }
  })
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedRowKeys.value.length === 0) return
  
  Modal.confirm({
    title: '确认批量删除',
    icon: <ExclamationCircleOutlined />,
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个项目吗？删除后数据将无法恢复。`,
    okText: '确认删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        const deletePromises = selectedRowKeys.value.map(id => deleteProject(id))
        await Promise.all(deletePromises)
        message.success(`成功删除 ${selectedRowKeys.value.length} 个项目`)
        selectedRowKeys.value = []
        loadProjects()
      } catch (error) {
        console.error('批量删除失败:', error)
        message.error('批量删除失败')
      }
    }
  })
}

// 显示创建模态框
const showCreateModal = () => {
  editingProject.value = null
  Object.assign(formData, {
    name: '',
    intro: '',
    url: '',
    status: 'active',
    pm: null,
    product_line: currentProductLine.value?.id || null
  })
  showModal.value = true
}

// 提交表单
const handleSubmit = async () => {
  submitting.value = true
  try {
    if (editingProject.value) {
      await updateProject(editingProject.value.id, formData)
      message.success('项目更新成功')
    } else {
      await createProject(formData)
      message.success('项目创建成功')
    }
    showModal.value = false
    loadProjects()
  } catch (error) {
    console.error('保存失败:', error)
    message.error('保存失败')
  } finally {
    submitting.value = false
  }
}

// 关闭模态框
const closeModal = () => {
  showModal.value = false
  editingProject.value = null
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const res = await getAllUsers()
    userList.value = res.result || res || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 字符串生成颜色函数
const stringToColor = (str) => {
  if (!str) return '#1890ff'
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  const colors = [
    '#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1',
    '#13c2c2', '#eb2f96', '#faad14', '#a0d911', '#f759ab'
  ]
  return colors[Math.abs(hash) % colors.length]
}

// 组件挂载
onMounted(async () => {
  await loadUsers()
  loadProjects()
})
</script>

<style scoped>
.project-management {
  min-height: 100vh;
  background: #f0f2f5;
  padding: 24px;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f1f1f;
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.header-actions {
  flex-shrink: 0;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f1f1f;
  margin-bottom: 4px;
}

.stat-title {
  font-size: 14px;
  color: #666;
}

/* 过滤卡片 */
.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

/* 项目卡片 */
.projects-card {
  border-radius: 12px;
}

.projects-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.projects-count {
  font-size: 14px;
  color: #666;
  font-weight: normal;
}

/* 项目名称 */
.project-name {
  color: #1890ff;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s;
}

.project-name:hover {
  color: #40a9ff;
}

/* 负责人信息 */
.pm-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pm-name {
  font-size: 14px;
  color: #333;
}

/* 空状态 */
.empty-state {
  padding: 48px 0;
}

/* 分页 */
.pagination-section {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

/* 模态框样式 */
.project-modal .ant-modal-content {
  border-radius: 16px;
  overflow: hidden;
}

.project-modal .ant-modal-header {
  border-bottom: 1px solid #f0f0f0;
  padding: 24px 24px 16px;
}

.project-modal .ant-modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f1f1f;
}

.project-modal .ant-modal-body {
  padding: 0 24px 24px;
}

.modal-header-tip {
  margin-bottom: 20px;
}

.form-section {
  margin-top: 16px;
}

.form-item-help {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
  line-height: 1.4;
}

/* 状态选项样式 */
.status-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot-planning {
  background-color: #1890ff;
}

.status-dot-active {
  background-color: #52c41a;
}

.status-dot-testing {
  background-color: #fa8c16;
}

.status-dot-completed {
  background-color: #13c2c2;
}

.status-dot-archived {
  background-color: #d9d9d9;
}

/* 用户选项样式 */
.user-option {
  display: flex;
  align-items: center;
}

.user-email {
  font-size: 11px;
  color: #8c8c8c;
  margin-left: 8px;
  opacity: 0.8;
}

/* 表单预览 */
.form-preview {
  margin-top: 16px;
}

/* 模态框页脚 */
.project-modal .ant-modal-footer {
  border-top: 1px solid #f0f0f0;
  padding: 16px 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .project-management {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
  }
  
  .header-actions button {
    width: 100%;
  }
  
  .filter-actions {
    flex-direction: column;
  }
  
  .filter-actions button {
    width: 100%;
  }
  
  /* 模态框响应式 */
  .project-modal .ant-modal {
    max-width: calc(100vw - 32px);
    margin: 16px auto;
  }
  
  .project-modal .ant-modal-body {
    padding: 0 16px 16px;
  }
  
  .project-modal .ant-modal-header {
    padding: 16px 16px 12px;
  }
}
</style>