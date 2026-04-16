<template>
  <div class="sprint-detail-view">
    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回迭代列表
      </button>
      <div class="page-header__actions">
        <button class="btn btn--ghost btn--sm" @click="loadAll">
          <SyncOutlined :class="{ 'spin-icon': loading }" />
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <a-spin size="large" />
      <span>加载中...</span>
    </div>

    <!-- 主要内容 -->
    <div v-if="sprint && !loading" class="detail-content">
      <!-- 迭代信息卡片 -->
      <div class="form-card">
        <div class="form-card__header">
          <div class="form-card__icon">
            <ThunderboltOutlined />
          </div>
          <div class="form-card__content">
            <div class="form-card__title">{{ sprint.name }}</div>
            <div v-if="sprint.goal" class="form-card__subtitle">{{ sprint.goal }}</div>
          </div>
        </div>
        <div class="form-card__body">
          <div class="info-grid">
            <div class="info-item">
              <label class="info-label">迭代周期</label>
              <span class="info-value">{{ formatPeriod(sprint.start_date, sprint.end_date) }}</span>
            </div>
            <div class="info-item">
              <label class="info-label">负责人</label>
              <div v-if="sprint.owner_name" class="pm-info">
                <span class="pm-avatar" :style="{ background: getOwnerColor(sprint.owner_name) }">
                  {{ sprint.owner_name?.charAt(0).toUpperCase() }}
                </span>
                <span class="pm-name">{{ sprint.owner_name }}</span>
              </div>
              <span v-else class="info-value text-tertiary">—</span>
            </div>
            <div class="info-item">
              <label class="info-label">迭代状态</label>
              <span
                class="status-badge"
                :style="{
                  background: getStatusConfig(sprint.status)?.bg,
                  color: getStatusConfig(sprint.status)?.color
                }"
              >
                {{ getStatusText(sprint.status) }}
              </span>
            </div>
            <div class="info-item">
              <label class="info-label">需求进度</label>
              <div class="progress-info">
                <span class="progress-value">{{ sprint.done_count || 0 }}/{{ sprint.requirement_count || 0 }}</span>
                <div class="progress-bar-wrap">
                  <div
                    class="progress-bar-fill"
                    :style="{ width: getProgressPercent() + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 切换区 -->
      <div class="form-card form-card--no-clip">
        <div class="tabs-wrapper">
          <div class="tabs-nav">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ 'tab-btn--active': activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              <component :is="tab.icon" class="tab-btn__icon" />
              {{ tab.label }}
              <span class="tab-btn__count">{{ tab.count }}</span>
            </button>
          </div>

          <!-- 引用套件 Tab -->
          <div v-show="activeTab === 'suite'" class="tab-content">
            <div class="tab-toolbar">
              <div class="tab-toolbar__info">
                共 <strong>{{ suiteRefs.length }}</strong> 个引用套件
              </div>
              <div class="tab-toolbar__actions">
                <button class="btn btn--primary btn--sm" @click="runSuites" :disabled="!suiteRefs.length">
                  <PlayCircleOutlined /> 执行套件
                </button>
                <button class="btn btn--ghost btn--sm" @click="openSuiteRefDialog">
                  <PlusOutlined /> 引用套件
                </button>
              </div>
            </div>
            <div v-if="suiteRefs.length" class="ref-list">
              <div
                v-for="ref in suiteRefs"
                :key="ref.id"
                class="ref-item"
                @click="viewSuite(ref.suite)"
              >
                <span class="ref-item__icon">
                  <ProfileOutlined />
                </span>
                <span class="ref-item__name">{{ ref.suite_name || `套件 #${ref.suite}` }}</span>
                <button
                  class="btn btn-xs btn--danger-ghost"
                  @click.stop="removeSuiteRef(ref)"
                  title="移除"
                >
                  <MinusCircleOutlined />
                </button>
                <ArrowRightOutlined class="ref-item__arrow" />
              </div>
            </div>
            <div v-else class="empty-tab">
              <ProfileOutlined class="empty-tab__icon" />
              <p>暂无引用套件</p>
              <button class="btn btn--primary btn--sm" @click="openSuiteRefDialog">
                <PlusOutlined /> 引用套件
              </button>
            </div>
          </div>

          <!-- 引用用例 Tab -->
          <div v-show="activeTab === 'case'" class="tab-content">
            <div class="tab-toolbar">
              <div class="tab-toolbar__info">
                共 <strong>{{ caseRefs.length }}</strong> 个引用用例
              </div>
              <div class="tab-toolbar__actions">
                <button class="btn btn--primary btn--sm" @click="runCases" :disabled="!caseRefs.length">
                  <PlayCircleOutlined /> 执行用例
                </button>
                <button class="btn btn--ghost btn--sm" @click="openCaseRefDialog">
                  <PlusOutlined /> 引用用例
                </button>
              </div>
            </div>
            <div v-if="caseRefs.length" class="ref-list">
              <div
                v-for="ref in caseRefs"
                :key="ref.id"
                class="ref-item"
                @click="viewCase(ref.case)"
              >
                <span class="ref-item__icon">
                  <FileProtectOutlined />
                </span>
                <span class="ref-item__name">{{ ref.case_name || `用例 #${ref.case}` }}</span>
                <button
                  class="btn btn-xs btn--secondary-ghost"
                  @click.stop="runSingleCase(ref)"
                  title="执行"
                >
                  <PlayCircleOutlined />
                </button>
                <button
                  class="btn btn-xs btn--danger-ghost"
                  @click.stop="removeCaseRef(ref)"
                  title="移除"
                >
                  <MinusCircleOutlined />
                </button>
                <ArrowRightOutlined class="ref-item__arrow" />
              </div>
            </div>
            <div v-else class="empty-tab">
              <FileProtectOutlined class="empty-tab__icon" />
              <p>暂无引用用例</p>
              <button class="btn btn--primary btn--sm" @click="openCaseRefDialog">
                <PlusOutlined /> 引用用例
              </button>
            </div>
          </div>

          <!-- 需求 Tab -->
          <div v-show="activeTab === 'req'" class="tab-content">
            <div class="tab-toolbar">
              <div class="tab-toolbar__info">
                共 <strong>{{ requirements.length }}</strong> 个需求
              </div>
              <div class="tab-toolbar__actions">
                <button class="btn btn--primary btn--sm" @click="openCreateReq">
                  <PlusOutlined /> 新增需求
                </button>
              </div>
            </div>
            <div v-if="requirements.length" class="req-list">
              <div
                v-for="r in requirements"
                :key="r.id"
                class="req-item"
              >
                <div class="req-item__main">
                  <span class="req-item__title">{{ r.title }}</span>
                  <div class="req-item__meta">
                    <span
                      class="req-badge"
                      :style="{
                        background: getReqStatusConfig(r.status)?.bg,
                        color: getReqStatusConfig(r.status)?.color
                      }"
                    >
                      {{ getReqStatusText(r.status) }}
                    </span>
                    <span
                      class="req-badge"
                      :style="{
                        background: getReqPriorityConfig(r.priority)?.bg,
                        color: getReqPriorityConfig(r.priority)?.color
                      }"
                    >
                      {{ getReqPriorityText(r.priority) }}
                    </span>
                    <span v-if="r.assignee_name" class="pm-mini">
                      {{ r.assignee_name?.charAt(0).toUpperCase() }}
                    </span>
                  </div>
                </div>
                <div class="req-item__actions">
                  <button class="btn btn-xs btn--ghost" @click="openEditReq(r)">
                    <EditOutlined />
                  </button>
                  <button class="btn btn-xs btn--danger-ghost" @click="deleteReq(r)">
                    <DeleteOutlined />
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="empty-tab">
              <InboxOutlined class="empty-tab__icon" />
              <p>暂无需求</p>
              <button class="btn btn--primary btn--sm" @click="openCreateReq">
                <PlusOutlined /> 新增需求
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input ref="importFileRef" type="file" accept=".csv,.xlsx,.xls" style="display: none" />

    <!-- 引用套件弹窗 -->
    <div v-if="showSuiteRefDialog" class="modal" @click.self="closeSuiteRefDialog">
      <div class="modal-content modal-content--wide">
        <div class="modal-header">
          <div>
            <h3 class="modal-content__title">批量引入套件</h3>
            <p class="modal-content__sub">从目录树中选择要引用的套件</p>
          </div>
          <label class="cross-product-toggle">
            <input type="checkbox" v-model="suitePickerCrossProduct" @change="openSuiteRefDialog" />
            <span>显示全部有权限产品线</span>
          </label>
        </div>

        <div class="picker-layout">
          <div class="picker-tree-panel">
            <div class="picker-panel-title">套件目录树</div>
            <div class="picker-tree" v-if="suiteTree">
              <div
                v-for="node in visibleSuiteTreeNodes"
                :key="`suite-node-${node.id}`"
                class="picker-tree-row"
                :class="{ active: isSameId(node.id, selectedSuiteFolderId) }"
                :style="{ paddingLeft: `${node.level * 18 + 10}px` }"
                @click="isSuiteFolderNode(node) ? toggleSuiteFolder(node) : selectSuiteTreeNode(node)"
              >
                <span class="picker-tree-toggle">
                  {{ isSuiteFolderNode(node) ? (isSuiteFolderExpanded(node.id) ? '▾' : '▸') : '' }}
                </span>
                <span class="picker-tree-text">
                  {{ isSuiteFolderNode(node) ? '📁' : '📄' }}
                  {{ displayTreeNodeName(node) }}
                </span>
              </div>
            </div>
            <div v-else class="empty-picker">暂无目录树</div>
          </div>

          <div class="picker-list-panel">
            <div class="picker-toolbar">
              <input v-model="suitePickerSearch" class="picker-search" placeholder="搜索套件名称或 ID" />
              <div class="picker-toolbar-right">
                <span class="picker-count">已选 {{ selectedSuiteIds.length }} 项</span>
                <label class="picker-checkall" v-if="availableSuiteCandidates.length">
                  <input type="checkbox" :checked="allAvailableSuitesSelected" @change="toggleAllAvailableSuites" />
                  <span>全选</span>
                </label>
              </div>
            </div>
            <div class="picker-list">
              <div
                v-for="item in filteredSuiteCandidates"
                :key="`suite-${item.id}`"
                class="picker-list-row"
                :class="{ disabled: isSuiteReferenced(item.id) }"
              >
                <label class="picker-checkbox-wrap">
                  <input
                    type="checkbox"
                    :value="item.id"
                    v-model="selectedSuiteIds"
                    :disabled="isSuiteReferenced(item.id)"
                  />
                  <span class="picker-item-title">#{{ item.id }} {{ item.name }}</span>
                  <span v-if="isSuiteReferenced(item.id)" class="picker-badge picker-badge--disabled">已引用</span>
                  <span v-else class="picker-badge picker-badge--available">可引入</span>
                </label>
              </div>
              <div v-if="!filteredSuiteCandidates.length" class="empty-picker">当前目录下暂无可展示套件</div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn--ghost" @click="closeSuiteRefDialog">取消</button>
          <button
            class="btn btn--primary"
            :disabled="!selectedSuiteIds.length"
            @click="submitSuiteRefs"
          >
            确认引入 {{ selectedSuiteIds.length ? `(${selectedSuiteIds.length})` : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 引用用例弹窗 -->
    <div v-if="showCaseRefDialog" class="modal" @click.self="closeCaseRefDialog">
      <div class="modal-content modal-content--xl">
        <div class="modal-header">
          <div>
            <h3 class="modal-content__title">批量引入用例</h3>
            <p class="modal-content__sub">从目录树中选择要引用的用例</p>
          </div>
          <label class="cross-product-toggle">
            <input type="checkbox" v-model="casePickerCrossProduct" @change="openCaseRefDialog" />
            <span>显示全部有权限产品线</span>
          </label>
        </div>

        <div class="picker-layout">
          <div class="picker-tree-panel">
            <div class="picker-panel-title">用例目录树</div>
            <div class="picker-tree" v-if="caseTree">
              <div
                v-for="node in visibleCaseTreeNodes"
                :key="`case-node-${node.id}`"
                class="picker-tree-row"
                :class="{ active: isSameId(node.id, selectedCaseFolderId) }"
                :style="{ paddingLeft: `${node.level * 18 + 10}px` }"
                @click="isCaseFolderNode(node) ? toggleCaseFolder(node) : selectCaseTreeNode(node)"
              >
                <span class="picker-tree-toggle">
                  {{ isCaseFolderNode(node) ? (isCaseFolderExpanded(node.id) ? '▾' : '▸') : '' }}
                </span>
                <span class="picker-tree-text">
                  {{ isCaseFolderNode(node) ? '📁' : '📄' }}
                  {{ displayTreeNodeName(node) }}
                </span>
              </div>
            </div>
            <div v-else class="empty-picker">暂无目录树</div>
          </div>

          <div class="picker-list-panel">
            <div class="picker-toolbar">
              <input v-model="casePickerSearch" class="picker-search" placeholder="搜索用例名称或 ID" />
              <div class="picker-toolbar-right">
                <span class="picker-count">已选 {{ selectedCaseIds.length }} 项</span>
                <label class="picker-checkall" v-if="availableCaseCandidates.length">
                  <input type="checkbox" :checked="allAvailableCasesSelected" @change="toggleAllAvailableCases" />
                  <span>全选</span>
                </label>
              </div>
            </div>
            <div class="picker-list">
              <div
                v-for="item in filteredCaseCandidates"
                :key="`case-${item.id}`"
                class="picker-list-row"
                :class="{ disabled: isCaseReferenced(item.id) }"
              >
                <label class="picker-checkbox-wrap">
                  <input
                    type="checkbox"
                    :value="item.id"
                    v-model="selectedCaseIds"
                    :disabled="isCaseReferenced(item.id)"
                  />
                  <span class="picker-item-title">#{{ item.id }} {{ item.name }}</span>
                  <span class="picker-item-endpoint">{{ item.endpoint?.name || '未关联接口' }}</span>
                  <span v-if="isCaseReferenced(item.id)" class="picker-badge picker-badge--disabled">已引用</span>
                  <span v-else class="picker-badge picker-badge--available">可引入</span>
                </label>
              </div>
              <div v-if="!filteredCaseCandidates.length" class="empty-picker">当前目录下暂无可展示用例</div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn--ghost" @click="closeCaseRefDialog">取消</button>
          <button
            class="btn btn--primary"
            :disabled="!selectedCaseIds.length"
            @click="submitCaseRefs"
          >
            确认引入 {{ selectedCaseIds.length ? `(${selectedCaseIds.length})` : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 新建/编辑需求弹窗 -->
    <div v-if="showReqDialog" class="modal" @click.self="showReqDialog=false">
      <div class="modal-content">
        <h3 class="modal-content__title">{{ editingReq ? '编辑需求' : '新建需求' }}</h3>
        <p class="modal-content__sub">{{ editingReq ? '修改需求信息' : '添加一个新的测试需求' }}</p>

        <div class="form-group">
          <label class="field-label">需求标题 <span class="required">*</span></label>
          <input v-model="reqForm.title" class="field-input" placeholder="输入需求标题" />
        </div>

        <div class="form-group">
          <label class="field-label">需求描述</label>
          <textarea v-model="reqForm.desc" class="field-input field-textarea" rows="3" placeholder="描述需求的详细信息"></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="field-label">状态</label>
            <select v-model="reqForm.status" class="field-input">
              <option v-for="opt in reqStatusOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="field-label">优先级</label>
            <select v-model="reqForm.priority" class="field-input">
              <option v-for="opt in reqPriorityOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn--ghost" @click="showReqDialog=false">取消</button>
          <button class="btn btn--primary" @click="saveReq">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeftOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  ProfileOutlined,
  FileProtectOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  MinusCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  ArrowRightOutlined,
  InboxOutlined,
} from '@ant-design/icons-vue'
import {
  getSprintDetail,
  getSprintSuiteRefs,
  createSprintSuiteRef,
  deleteSprintSuiteRef,
  getSprintCaseRefs,
  createSprintCaseRef,
  deleteSprintCaseRef,
  getRequirements,
  createRequirement,
  updateRequirement,
  deleteRequirement,
  runSprint,
} from '@/api/sprint'
import { getSuites, getSuiteTree } from '@/api/suite'
import { getCases, getCaseTree, runCaseById } from '@/api/case'
import { useUserStore } from '@/stores/user'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import {
  SPRINT_STATUS_LIST,
  REQUIREMENT_STATUS_LIST,
  REQUIREMENT_PRIORITY_LIST,
  getSprintStatusConfig,
  getRequirementStatusConfig,
  getRequirementPriorityConfig,
  getSprintStatusText as getStatusText,
  getRequirementStatusText as getReqStatusText,
  getRequirementPriorityText as getReqPriorityText,
  stringToColor,
  formatSprintPeriod as formatPeriod,
} from '@/components/UI'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 状态
const sprint = ref(null)
const suiteRefs = ref([])
const caseRefs = ref([])
const requirements = ref([])
const activeTab = ref('suite')
const loading = ref(false)

// 弹窗状态
const showSuiteRefDialog = ref(false)
const showCaseRefDialog = ref(false)
const showReqDialog = ref(false)
const editingReq = ref(null)
const reqForm = ref({ title: '', desc: '', status: 'todo', priority: 1, assignee: null })

// 选择器状态
const suiteTree = ref(null)
const caseTree = ref(null)
const suitePool = ref([])
const casePool = ref([])
const selectedSuiteFolderId = ref(null)
const selectedCaseFolderId = ref(null)
const selectedSuiteIds = ref([])
const selectedCaseIds = ref([])
const expandedSuiteFolders = ref(new Set())
const expandedCaseFolders = ref(new Set())
const suitePickerSearch = ref('')
const casePickerSearch = ref('')
const suitePickerCrossProduct = ref(false)
const casePickerCrossProduct = ref(false)

// 常量
const sprintStatusOptions = SPRINT_STATUS_LIST
const reqStatusOptions = REQUIREMENT_STATUS_LIST
const reqPriorityOptions = REQUIREMENT_PRIORITY_LIST

// Tabs
const tabs = computed(() => [
  { key: 'suite', label: '引用套件', icon: ProfileOutlined, count: suiteRefs.value.length },
  { key: 'case', label: '引用用例', icon: FileProtectOutlined, count: caseRefs.value.length },
  { key: 'req', label: '需求', icon: InboxOutlined, count: requirements.value.length },
])

// 工具函数
const getStatusConfig = (status) => getSprintStatusConfig(status)
const getReqStatusConfig = (status) => getRequirementStatusConfig(status)
const getReqPriorityConfig = (priority) => getRequirementPriorityConfig(priority)
const getOwnerColor = (name) => stringToColor(name)

const getProgressPercent = () => {
  const total = sprint.value?.requirement_count || 0
  if (total === 0) return 0
  return Math.round(((sprint.value?.done_count || 0) / total) * 100)
}

// 树形结构相关
const isSameId = (a, b) => String(a) === String(b)
const hasId = (v) => v !== null && v !== undefined && v !== ''
const displayTreeNodeName = (node) => node?.name?.trim() || '无名称'
const isFolderNode = (node) => {
  if (!node) return false
  if (node.node_type === 'folder') return true
  if (typeof node.node_type === 'string' && node.node_type.includes('root')) return true
  return node.node_type !== 'case' && node.node_type !== 'suite' && Array.isArray(node.children)
}
const isSuiteFolderNode = (node) => isFolderNode(node)
const isCaseFolderNode = (node) => isFolderNode(node)

const suiteReferencedIds = computed(() => new Set(suiteRefs.value.map(i => String(i.suite))))
const caseReferencedIds = computed(() => new Set(caseRefs.value.map(i => String(i.case))))
const isSuiteReferenced = (id) => suiteReferencedIds.value.has(String(id))
const isCaseReferenced = (id) => caseReferencedIds.value.has(String(id))

const suitePoolMap = computed(() => new Map(suitePool.value.map(item => [String(item.id), item])))
const casePoolMap = computed(() => new Map(casePool.value.map(item => [String(item.id), item])))

const findTreeNodeById = (node, id) => {
  if (!node) return null
  if (isSameId(node.id, id)) return node
  for (const child of (node.children || [])) {
    const found = findTreeNodeById(child, id)
    if (found) return found
  }
  return null
}

const flatVisibleNodes = (root, isFolder, expandedSet) => {
  const rows = []
  const walk = (node, level = 0) => {
    if (!node) return
    rows.push({ ...node, level })
    if (isFolder(node) && Array.from(expandedSet.value).some(v => isSameId(v, node.id))) {
      ;(node.children || []).forEach(child => walk(child, level + 1))
    }
  }
  walk(root.value, 0)
  return rows
}

const visibleSuiteTreeNodes = computed(() => flatVisibleNodes(suiteTree, isSuiteFolderNode, expandedSuiteFolders))
const visibleCaseTreeNodes = computed(() => flatVisibleNodes(caseTree, isCaseFolderNode, expandedCaseFolders))

const toggleExpandedFolder = (setRef, id) => {
  const next = new Set(setRef.value)
  const existed = Array.from(next).find(v => isSameId(v, id))
  if (existed !== undefined) next.delete(existed)
  else next.add(id)
  setRef.value = next
}
const isExpandedFolder = (setRef, id) => Array.from(setRef.value).some(v => isSameId(v, id))
const toggleSuiteFolder = (node) => { if (isSuiteFolderNode(node)) toggleExpandedFolder(expandedSuiteFolders, node.id) }
const toggleCaseFolder = (node) => { if (isCaseFolderNode(node)) toggleExpandedFolder(expandedCaseFolders, node.id) }
const isSuiteFolderExpanded = (id) => isExpandedFolder(expandedSuiteFolders, id)
const isCaseFolderExpanded = (id) => isExpandedFolder(expandedCaseFolders, id)

const collectLeafItems = (node, itemType, target = []) => {
  if (!node) return target
  if (node.node_type === itemType && node.item?.id) {
    target.push(node.item)
  }
  ;(node.children || []).forEach(child => collectLeafItems(child, itemType, target))
  return target
}

const currentSuiteTreeNode = computed(() => {
  if (!suiteTree.value) return null
  return hasId(selectedSuiteFolderId.value) ? findTreeNodeById(suiteTree.value, selectedSuiteFolderId.value) : suiteTree.value
})
const currentCaseTreeNode = computed(() => {
  if (!caseTree.value) return null
  return hasId(selectedCaseFolderId.value) ? findTreeNodeById(caseTree.value, selectedCaseFolderId.value) : caseTree.value
})

const suiteCandidates = computed(() => {
  const items = collectLeafItems(currentSuiteTreeNode.value, 'suite', [])
  const seen = new Set()
  return items
    .map(item => suitePoolMap.value.get(String(item.id)) || item)
    .filter(item => {
      if (!item?.id || seen.has(String(item.id))) return false
      seen.add(String(item.id))
      return true
    })
})
const caseCandidates = computed(() => {
  const items = collectLeafItems(currentCaseTreeNode.value, 'case', [])
  const seen = new Set()
  return items
    .map(item => casePoolMap.value.get(String(item.id)) || item)
    .filter(item => {
      if (!item?.id || seen.has(String(item.id))) return false
      seen.add(String(item.id))
      return true
    })
})

const filterByKeyword = (list, keyword, extraText = () => '') => {
  const q = keyword.trim().toLowerCase()
  if (!q) return list
  return list.filter(item => {
    const text = `${item.id} ${item.name || ''} ${extraText(item)}`.toLowerCase()
    return text.includes(q)
  })
}

const filteredSuiteCandidates = computed(() => filterByKeyword(suiteCandidates.value, suitePickerSearch.value))
const filteredCaseCandidates = computed(() => filterByKeyword(caseCandidates.value, casePickerSearch.value, item => item.endpoint?.name || ''))
const availableSuiteCandidates = computed(() => filteredSuiteCandidates.value.filter(item => !isSuiteReferenced(item.id)))
const availableCaseCandidates = computed(() => filteredCaseCandidates.value.filter(item => !isCaseReferenced(item.id)))
const allAvailableSuitesSelected = computed(() => availableSuiteCandidates.value.length > 0 && availableSuiteCandidates.value.every(item => selectedSuiteIds.value.some(id => isSameId(id, item.id))))
const allAvailableCasesSelected = computed(() => availableCaseCandidates.value.length > 0 && availableCaseCandidates.value.every(item => selectedCaseIds.value.some(id => isSameId(id, item.id))))

const toggleAllItems = (selectedRef, items, checked) => {
  const next = new Set(selectedRef.value.map(String))
  items.forEach(item => {
    if (checked) next.add(String(item.id))
    else next.delete(String(item.id))
  })
  selectedRef.value = Array.from(next)
}
const toggleAllAvailableSuites = (e) => toggleAllItems(selectedSuiteIds, availableSuiteCandidates.value, e.target.checked)
const toggleAllAvailableCases = (e) => toggleAllItems(selectedCaseIds, availableCaseCandidates.value, e.target.checked)

const getPickerProductLineId = () => sprint.value?.product_line || userStore.currentProductLine?.id || null

const expandRootNode = (treeRef, expandedRef) => {
  if (!treeRef.value?.id) return
  expandedRef.value = new Set([treeRef.value.id])
}

// 加载数据
const loadAll = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const [s, sr, cr, rr] = await Promise.all([
      getSprintDetail(id),
      getSprintSuiteRefs({ sprint: id, page_size: 200 }),
      getSprintCaseRefs({ sprint: id, page_size: 200 }),
      getRequirements({ sprint: id, page_size: 300 }),
    ])
    sprint.value = s.result || s
    suiteRefs.value = sr.result?.list || []
    caseRefs.value = cr.result?.list || []
    requirements.value = rr.result?.list || []
  } catch (e) {
    console.error('加载失败:', e)
  } finally {
    loading.value = false
  }
}

// 套件引用
const openSuiteRefDialog = async () => {
  const productLineId = getPickerProductLineId()
  const params = !suitePickerCrossProduct.value && productLineId ? { product_line: productLineId, page_size: 500 } : { page_size: 500 }
  const treeParams = !suitePickerCrossProduct.value && productLineId ? { product_line: productLineId } : {}
  const [treeRes, suiteRes] = await Promise.all([getSuiteTree(treeParams), getSuites(params)])
  suiteTree.value = treeRes.result || treeRes
  suitePool.value = suiteRes.result?.list || []
  selectedSuiteFolderId.value = suiteTree.value?.id ?? null
  selectedSuiteIds.value = []
  suitePickerSearch.value = ''
  expandRootNode(suiteTree, expandedSuiteFolders)
  showSuiteRefDialog.value = true
}
const closeSuiteRefDialog = () => {
  showSuiteRefDialog.value = false
  selectedSuiteIds.value = []
  suitePickerSearch.value = ''
}
const selectSuiteTreeNode = (node) => {
  if (isSuiteFolderNode(node)) selectedSuiteFolderId.value = node.id
}
const submitSuiteRefs = async () => {
  if (!selectedSuiteIds.value.length) return alert('请选择套件')
  const sprintId = Number(route.params.id)
  for (const suiteId of selectedSuiteIds.value) {
    await createSprintSuiteRef({ sprint: sprintId, suite: Number(suiteId) })
  }
  closeSuiteRefDialog()
  await loadAll()
}
const removeSuiteRef = async (ref) => {
  const ok = await confirm('确定移除该套件引用吗？', { type: 'danger' })
  if (!ok) return
  await deleteSprintSuiteRef(ref.id)
  await loadAll()
}
const runSuites = async () => {
  const ids = suiteRefs.value.map(i => i.suite)
  if (!ids.length) return alert('暂无引用套件')
  await runSprint(route.params.id, { suite_ids: ids })
  alert('已触发套件执行')
}

// 用例引用
const openCaseRefDialog = async () => {
  const productLineId = getPickerProductLineId()
  const params = !casePickerCrossProduct.value && productLineId ? { product_line: productLineId, page_size: 500 } : { page_size: 500 }
  const treeParams = !casePickerCrossProduct.value && productLineId ? { product_line: productLineId } : {}
  const [treeRes, caseRes] = await Promise.all([getCaseTree(treeParams), getCases(params)])
  caseTree.value = treeRes.result || treeRes
  casePool.value = caseRes.result?.list || []
  selectedCaseFolderId.value = caseTree.value?.id ?? null
  selectedCaseIds.value = []
  casePickerSearch.value = ''
  expandRootNode(caseTree, expandedCaseFolders)
  showCaseRefDialog.value = true
}
const closeCaseRefDialog = () => {
  showCaseRefDialog.value = false
  selectedCaseIds.value = []
  casePickerSearch.value = ''
}
const selectCaseTreeNode = (node) => {
  if (isCaseFolderNode(node)) selectedCaseFolderId.value = node.id
}
const submitCaseRefs = async () => {
  if (!selectedCaseIds.value.length) return alert('请选择用例')
  const sprintId = Number(route.params.id)
  for (const caseId of selectedCaseIds.value) {
    await createSprintCaseRef({ sprint: sprintId, case: Number(caseId) })
  }
  closeCaseRefDialog()
  await loadAll()
}
const removeCaseRef = async (ref) => {
  const ok = await confirm('确定移除该用例引用吗？', { type: 'danger' })
  if (!ok) return
  await deleteSprintCaseRef(ref.id)
  await loadAll()
}
const runCases = async () => {
  if (!caseRefs.value.length) return alert('暂无引用用例')
  for (const ref of caseRefs.value) await runCaseById(ref.case)
  alert(`已触发 ${caseRefs.value.length} 条用例执行`)
}
const runSingleCase = async (ref) => {
  await runCaseById(ref.case)
  alert('已触发执行')
}

// 需求管理
const openCreateReq = () => {
  editingReq.value = null
  reqForm.value = { title: '', desc: '', status: 'todo', priority: 1, assignee: null }
  showReqDialog.value = true
}
const openEditReq = (r) => {
  editingReq.value = r
  reqForm.value = {
    title: r.title,
    desc: r.desc || '',
    status: r.status || 'todo',
    priority: r.priority ?? 1,
    assignee: r.assignee || null
  }
  showReqDialog.value = true
}
const saveReq = async () => {
  if (!reqForm.value.title?.trim()) return alert('需求标题必填')
  if (editingReq.value) {
    await updateRequirement(editingReq.value.id, {
      sprint: route.params.id,
      title: reqForm.value.title,
      desc: reqForm.value.desc,
      status: reqForm.value.status,
      priority: reqForm.value.priority,
      assignee: reqForm.value.assignee,
    })
  } else {
    await createRequirement({
      sprint: route.params.id,
      title: reqForm.value.title,
      desc: reqForm.value.desc,
      status: 'todo',
      priority: 1
    })
  }
  showReqDialog.value = false
  await loadAll()
}
const deleteReq = async (r) => {
  const ok = await confirm(`确定删除需求「${r.title}」吗？`, { type: 'danger' })
  if (!ok) return
  await deleteRequirement(r.id)
  await loadAll()
}

// 跳转
const viewSuite = (id) => router.push(`/suites/${id}`)
const viewCase = (id) => router.push(`/cases/${id}`)

onMounted(loadAll)
</script>

<style scoped>
/* ─── 页面整体 ─── */
.sprint-detail-view {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ─── 顶部返回栏 ─── */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-header__actions {
  margin-left: auto;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-back:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

/* ─── 加载状态 ─── */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: var(--color-text-tertiary);
}

/* ─── 主内容 ─── */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ─── 表单卡片 ─── */
.form-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.form-card--no-clip {
  overflow: visible;
}

.form-card__header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--color-gray-100);
  background: linear-gradient(to bottom, var(--color-gray-50), var(--color-bg-card));
}

.form-card__icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  flex-shrink: 0;
}

.form-card__content {
  flex: 1;
  min-width: 0;
}

.form-card__title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.3;
  margin-bottom: 4px;
}

.form-card__subtitle {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.form-card__body {
  padding: 20px 24px;
}

/* ─── 信息网格 ─── */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
}

.info-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.text-tertiary {
  color: var(--color-text-tertiary);
}

/* ─── 状态标签 ─── */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: 600;
  width: fit-content;
}

/* ─── 负责人 ─── */
.pm-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pm-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.pm-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

/* ─── 进度 ─── */
.progress-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-value {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.progress-bar-wrap {
  width: 100%;
  height: 6px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-success));
  border-radius: var(--radius-full);
  transition: width var(--transition-slow);
}

/* ─── Tabs ─── */
.tabs-wrapper {
  overflow: hidden;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
}

.tabs-nav {
  display: flex;
  border-bottom: 2px solid var(--color-gray-100);
  background: var(--color-bg-card);
  padding: 0 8px;
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border: none;
  background: transparent;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all var(--transition-base);
  position: relative;
}

.tab-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

.tab-btn--active {
  color: var(--color-primary);
}

.tab-btn--active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 3px;
  background: var(--color-primary);
  border-radius: 3px 3px 0 0;
}

.tab-btn__icon {
  font-size: 16px;
}

.tab-btn__count {
  background: var(--color-gray-100);
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
}

.tab-btn--active .tab-btn__count {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

/* ─── Tab 内容 ─── */
.tab-content {
  padding: 20px 24px;
  background: var(--color-gray-50);
  border-radius: 0 0 var(--radius-xl) var(--radius-xl);
}

.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tab-toolbar__info {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.tab-toolbar__info strong {
  color: var(--color-text-primary);
  font-weight: 700;
}

.tab-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ─── 引用列表 ─── */
.ref-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ref-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-gray-100);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
}

.ref-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--color-primary);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.ref-item:hover {
  background: var(--color-primary-bg);
  border-color: var(--color-primary-border);
  transform: translateX(4px);
}

.ref-item:hover::before {
  opacity: 1;
}

.ref-item__icon {
  font-size: 18px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.ref-item:hover .ref-item__icon {
  color: var(--color-primary);
}

.ref-item__name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ref-item__arrow {
  color: var(--color-text-tertiary);
  opacity: 0;
  transform: translateX(-8px);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.ref-item:hover .ref-item__arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--color-primary);
}

/* ─── 需求列表 ─── */
.req-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.req-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 18px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-gray-100);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.req-item:hover {
  border-color: var(--color-gray-200);
  box-shadow: var(--shadow-sm);
}

.req-item__main {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  min-width: 0;
}

.req-item__title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.req-item__meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.req-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: 600;
}

.pm-mini {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.req-item__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.req-item:hover .req-item__actions {
  opacity: 1;
}

/* ─── 空状态 ─── */
.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 20px;
  text-align: center;
}

.empty-tab__icon {
  font-size: 36px;
  color: var(--color-gray-300);
}

.empty-tab p {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

/* ─── 按钮 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
  outline: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-hover), var(--color-primary-active));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn--ghost {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1.5px solid var(--color-border);
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.btn--sm {
  padding: 8px 16px;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
}

.btn-xs {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: all var(--transition-fast);
}

.btn--secondary-ghost {
  background: transparent;
  color: var(--color-success);
}

.btn--secondary-ghost:hover {
  background: var(--color-success-bg);
}

.btn--danger-ghost {
  background: transparent;
  color: var(--color-error);
  opacity: 0;
}

.req-item:hover .btn--danger-ghost,
.ref-item:hover .btn--danger-ghost {
  opacity: 1;
}

.btn--danger-ghost:hover {
  background: var(--color-error-bg);
}

.btn--ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn--ghost:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.spin-icon {
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
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-content--wide {
  max-width: 800px;
}

.modal-content--xl {
  max-width: 1100px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
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
  margin: 0;
}

.cross-product-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  white-space: nowrap;
}

/* ─── 选择器布局 ─── */
.picker-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 16px;
  min-height: 400px;
}

.picker-tree-panel,
.picker-list-panel {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-gray-50);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.picker-panel-title {
  padding: 12px 14px;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.picker-tree,
.picker-list {
  padding: 8px;
  overflow-y: auto;
  flex: 1;
}

.picker-tree-row {
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--color-text-primary);
  font-size: var(--text-sm);
  transition: background var(--transition-fast);
}

.picker-tree-row:hover {
  background: var(--color-primary-bg);
}

.picker-tree-row.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

.picker-tree-toggle {
  width: 16px;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 11px;
}

.picker-tree-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.picker-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.picker-search {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  outline: none;
}

.picker-search:focus {
  border-color: var(--color-primary);
}

.picker-toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.picker-count,
.picker-checkall {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.picker-checkall {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.picker-list-row {
  padding: 10px 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-gray-100);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}

.picker-list-row:last-child {
  margin-bottom: 0;
}

.picker-list-row.disabled {
  opacity: 0.6;
  background: var(--color-gray-50);
}

.picker-checkbox-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  min-height: 32px;
}

.picker-item-title {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.picker-item-endpoint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

.picker-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.picker-badge--available {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.picker-badge--disabled {
  background: var(--color-gray-100);
  color: var(--color-text-tertiary);
}

.empty-picker {
  padding: 24px;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
}

/* ─── 表单 ─── */
.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.field-label {
  display: block;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.required {
  color: var(--color-error);
}

.field-input {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  outline: none;
  transition: border-color var(--transition-fast);
  font-family: inherit;
}

.field-input:focus {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-focus);
}

.field-textarea {
  resize: vertical;
  min-height: 80px;
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

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .tabs-nav {
    overflow-x: auto;
  }

  .picker-layout {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
