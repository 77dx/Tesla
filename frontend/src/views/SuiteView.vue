<template>
  <div class="suite-view">
    <div class="main-layout">
      <div class="tree-column">
        <div class="tree-panel card">
          <div class="tree-header">
            <strong>套件目录</strong>
          </div>
          <div class="tree-body" v-if="suiteTree" ref="treeBodyRef">
            <div v-for="n in visibleTreeNodes" :key="n.id" class="tree-row" :class="{ active: n.id === selectedNodeId }" :style="{ paddingLeft: (n.level * 18 + 8) + 'px' }" @click="selectNode(n)"
              @contextmenu.prevent="openContextMenu(n, $event)"
              draggable="true" @dragstart="onDragStart(n, $event)" @dragover.prevent="onDragOverNode(n, $event)" @drop.prevent="onDropOnNode(n, $event)">
              <span class="tree-toggle" @click.stop="toggleFolder(n)">{{ n.node_type === 'folder' ? (isExpanded(n.id) ? '▾' : '▸') : '' }}</span>
              <span class="tree-node-label">
                <span class="tree-node-icon" aria-hidden="true">
                  <svg v-if="n.node_type === 'folder' && isExpanded(n.id)" viewBox="0 0 24 24" fill="none">
                    <path d="M3.5 8.5a2 2 0 0 1 2-2h4.1a2 2 0 0 1 1.4.58l.92.92H18.5a2 2 0 0 1 2 2v6.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-8Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else-if="n.node_type === 'folder'" viewBox="0 0 24 24" fill="none">
                    <path d="M3.5 9a2 2 0 0 1 2-2h4.1a2 2 0 0 1 1.4.58l.92.92H18.5a2 2 0 0 1 2 2v5.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2V9Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none">
                    <path d="M7 3.8h6.2L18 8.6V20.2H7V3.8Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                    <path d="M13.2 3.8v4.8H18" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                  </svg>
                </span>
                <span class="tree-node-name" :data-full-name="displayTreeNodeName(n)">{{ displayTreeNodeName(n) }}</span>
              </span>
            </div>
          </div>
          <div v-if="contextMenuVisible" ref="contextMenuRef" class="context-menu" :style="{ left: `${contextMenuX}px`, top: `${contextMenuY}px` }" @click.stop>
            <button @click.stop.prevent="createFolderUnderContext">新增子文件夹</button>
            <button @click.stop.prevent="createSuiteUnderContext">新增套件</button>
            <button :disabled="!canMoveContextNode" :title="moveDisabledReason" @click.stop.prevent="moveContextNode">移动到</button>
            <button @click.stop.prevent="renameContextNode">重命名</button>
            <button :disabled="!canDeleteContextNode" @click.stop.prevent="deleteContextNode">删除节点</button>
          </div>
        </div>
      </div>

      <div class="content-column">
        <div class="filter-bar card">
          <div class="current-folder">
            <span class="folder-label">当前目录</span>
            <span class="folder-name" :title="selectedFolderPath">{{ selectedFolderPath }}</span>
          </div>
          <div class="filter-input-wrap">
            <span class="filter-icon">🔍</span>
            <input v-model="searchText" class="filter-input" placeholder="搜索名称或ID..." @keyup.enter="handleSearch" />
          </div>
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
          <div class="case-list-header">
            <div class="case-list-title"><strong>套件列表</strong></div>
            <div class="case-list-actions">
              <button @click="loadSuites(1)" class="btn btn-sm">↻ 刷新</button>
              <button @click="openBatchMoveDialog" :disabled="!selectedIds.length" class="btn btn-sm btn-batch-move">📁 批量移动 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}</button>
              <button v-if="hasPermission('suite:delete')" @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-sm btn-danger">
                🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
              </button>
            </div>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
                <th>ID</th>
                <th>套件名称</th>
                <th>运行类型</th>
                <th>下次执行</th>
                <th>更新人</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in displayedSuites" :key="item.id">
                <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
                <td class="cell-sm">{{ item.id }}</td>
                <td class="cell-md" :title="item.name">
                  <a @click.prevent="viewDetail(item.id)" class="link-text">{{ item.name }}</a>
                </td>
                <td class="cell-sm"><span class="type-tag" :class="'type-' + item.run_type">{{ { O: '手动执行', C: '定时执行', W: 'WebHook' }[item.run_type] || item.run_type }}</span></td>
                <td class="cell-md">{{ item.run_type === 'C' ? formatDate(item.cron_next_run_at) : '-' }}</td>
                <td class="cell-sm">
                  <span class="creator-badge">{{ item.updated_by_name || '-' }}</span>
                </td>
                <td class="cell-md">{{ formatDate(item.created_at) }}</td>
                <td>
                  <div class="suite-row-actions">
                    <button @click="runSuiteItem(item)" class="btn-action btn-success">▶ 执行</button>
                    <button v-if="item.run_type === 'C'" @click="stopCronItem(item)" class="btn-action btn-warning">⏹ 停止定时</button>
                    <button @click="viewDetail(item.id)" class="btn-action btn-info">详情</button>
                    <button @click="deleteSuiteItem(item.id)" class="btn-action btn-danger">删除</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!displayedSuites.length" class="empty-state">当前目录下暂无套件</div>
          <div class="case-list-footer" v-if="displayedSuites.length"><div class="case-list-count">共 {{ displayedSuites.length }} 条</div></div>
          <div v-if="pagination.pageCount > 1" class="pagination">
            <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
            <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
            <button v-for="p in pagination.pageCount" :key="p" class="page-btn" :class="{ active: p === pagination.page }" @click="changePage(p)">{{ p }}</button>
            <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="moveDialogVisible" class="modal" @click.self="moveDialogVisible = false">
      <div class="modal-content" style="max-width:460px">
        <h3>移动节点</h3>
        <div class="form-group">
          <label>目标文件夹</label>
          <select v-model="moveTargetFolderId">
            <option v-for="f in folderOptions" :key="f.id" :value="f.id">{{ ' '.repeat(f.level * 2) }}{{ f.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="moveDialogVisible = false">取消</button>
          <button class="btn btn-primary" @click="confirmMoveNode">确定移动</button>
        </div>
      </div>
    </div>

    <div v-if="batchMoveDialogVisible" class="modal" @click.self="batchMoveDialogVisible = false">
      <div class="modal-content" style="max-width:460px">
        <h3>批量移动套件</h3>
        <div class="form-group">
          <label>目标文件夹</label>
          <select v-model="batchMoveTargetFolderId">
            <option v-for="f in folderOptions" :key="f.id" :value="f.id">{{ ' '.repeat(f.level * 2) }}{{ f.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="batchMoveDialogVisible = false">取消</button>
          <button class="btn btn-primary" :disabled="!batchMoveTargetFolderId || !selectedIds.length" @click="confirmBatchMove">确认移动（{{ selectedIds.length }}）</button>
        </div>
      </div>
    </div>

    <div v-if="folderDialogVisible" class="modal" @click.self="closeFolderDialog">
      <div class="modal-content" style="max-width:460px">
        <h3>{{ folderDialogTitle }}</h3>
        <div class="form-group">
          <label>名称</label>
          <input v-model="folderDialogValue" placeholder="请输入名称" @keyup.enter="confirmFolderDialog" />
        </div>
        <div class="modal-actions">
          <button class="btn" @click="closeFolderDialog">取消</button>
          <button class="btn btn-primary" :disabled="!folderDialogValue.trim()" @click="confirmFolderDialog">确定</button>
        </div>
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
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getSuites, deleteSuite, runSuite, stopCron, getSuiteTree, createSuiteFolder, attachSuiteToFolder, moveSuiteNode, renameSuiteNode, deleteSuiteNode } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const { hasPermission } = userStore
const suites = ref([])
const suiteTree = ref(null)
const selectedFolderId = ref(null)
const selectedNodeId = ref(null)
const expandedFolders = ref(new Set())
const moveDialogVisible = ref(false)
const moveTargetFolderId = ref(null)
const batchMoveDialogVisible = ref(false)
const batchMoveTargetFolderId = ref(null)
const draggingNodeId = ref(null)
const contextMenuVisible = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextNode = ref(null)
const contextMenuRef = ref(null)
const contextTargetFolderId = ref(null)
const treeBodyRef = ref(null)
const folderDialogVisible = ref(false)
const folderDialogMode = ref('create')
const folderDialogTitle = ref('')
const folderDialogValue = ref('')
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const selectedIds = ref([])
const runResult = ref({ loading: false, success: false, error: null, result_id: null })

// 搜索/筛选
const searchText = ref('')
const filterRunType = ref('')

const showRunDialog = ref(false)
const isSameId = (a, b) => String(a) === String(b)
const hasNodeId = (v) => v !== null && v !== undefined && v !== ''

const TREE_STATE_KEY = 'tesla_suite_tree_state'

const flatTreeNodes = computed(() => {
  const res = []
  const walk = (node, level = 0) => {
    if (!node) return
    res.push({ ...node, level })
    ;(node.children || []).forEach(c => walk(c, level + 1))
  }
  walk(suiteTree.value, 0)
  return res
})

const folderOptions = computed(() => flatTreeNodes.value.filter(n => n.node_type === 'folder'))

const visibleTreeNodes = computed(() => {
  const list = []
  const walk = (node, level = 0) => {
    if (!node) return
    list.push({ ...node, level })
    if (node.node_type === 'folder' && isExpanded(node.id)) {
      ;(node.children || []).forEach(c => walk(c, level + 1))
    }
  }
  walk(suiteTree.value, 0)
  return list
})

const canMoveContextNode = computed(() => hasNodeId(contextNode.value?.id) && hasNodeId(contextNode.value?.parent))
const moveDisabledReason = computed(() => canMoveContextNode.value ? '' : '根目录不支持移动')
const canDeleteContextNode = computed(() => {
  const node = contextNode.value
  if (!node || !hasNodeId(node.id)) return false
  return !Array.isArray(node.children) || node.children.length === 0
})

const displayTreeNodeName = (node) => node?.name?.trim() || '无名称'

const isExpanded = (id) => Array.from(expandedFolders.value).some(v => isSameId(v, id))
const toggleFolder = (node) => {
  if (node.node_type !== 'folder') return
  const s = new Set(expandedFolders.value)
  const existed = Array.from(s).find(v => isSameId(v, node.id))
  if (existed !== undefined) s.delete(existed)
  else s.add(node.id)
  expandedFolders.value = s
}

const selectNode = (node) => {
  selectedNodeId.value = node.id
  if (node.node_type === 'folder') selectedFolderId.value = node.id
  if (node.node_type === 'suite' && node.item?.id) viewDetail(node.item.id)
}

const findNode = (node, id) => {
  if (!node) return null
  if (isSameId(node.id, id)) return node
  for (const child of (node.children || [])) {
    const found = findNode(child, id)
    if (found) return found
  }
  return null
}

const displayedSuites = computed(() => {
  const sortDescById = (list) => [...list].sort((a, b) => Number(b.id || 0) - Number(a.id || 0))
  if (!selectedFolderId.value || !suiteTree.value) return sortDescById(suites.value)
  const selectedNode = findNode(suiteTree.value, selectedFolderId.value)
  if (!selectedNode) return sortDescById(suites.value)
  const ids = new Set()
  const collect = (node) => {
    if (!node) return
    if (node.node_type === 'suite' && node.item?.id) ids.add(node.item.id)
    ;(node.children || []).forEach(collect)
  }
  collect(selectedNode)
  return sortDescById(suites.value.filter(s => ids.has(s.id)))
})

const selectedFolderName = computed(() => {
  if (!suiteTree.value) return '全部'
  const node = selectedFolderId.value ? findNode(suiteTree.value, selectedFolderId.value) : suiteTree.value
  return displayTreeNodeName(node)
})

const selectedFolderPath = computed(() => {
  if (!suiteTree.value) return '全部'
  const names = []
  const walk = (node, targetId) => {
    if (!node) return false
    names.push(displayTreeNodeName(node))
    if (isSameId(node.id, targetId)) return true
    for (const child of (node.children || [])) {
      if (walk(child, targetId)) return true
    }
    names.pop()
    return false
  }
  const targetId = selectedFolderId.value || suiteTree.value.id
  if (!walk(suiteTree.value, targetId)) return '全部'
  return names.join(' / ')
})

const saveTreeState = () => {
  try {
    const expandedIds = Array.from(expandedFolders.value || []).map(String)
    const payload = {
      expandedIds,
      selectedFolderId: selectedFolderId.value != null ? String(selectedFolderId.value) : null,
    }
    localStorage.setItem(TREE_STATE_KEY, JSON.stringify(payload))
  } catch (e) {
    // ignore
  }
}

const loadTreeState = () => {
  try {
    const raw = localStorage.getItem(TREE_STATE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed.expandedIds)) {
      expandedFolders.value = new Set(parsed.expandedIds)
    }
    if (parsed.selectedFolderId) {
      selectedFolderId.value = parsed.selectedFolderId
    }
  } catch (e) {
    // ignore
  }
}

const onDragStart = (node, event) => {
  draggingNodeId.value = node.id
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOverNode = (node, event) => {
  if (node.node_type !== 'folder') return
  event.dataTransfer.dropEffect = 'move'
}

const onDropOnNode = async (node) => {
  if (node.node_type !== 'folder') return
  if (!draggingNodeId.value || draggingNodeId.value === node.id) return
  await moveSuiteNode({ node_id: draggingNodeId.value, target_parent_id: node.id })
  draggingNodeId.value = null
  await loadSuiteTree()
}

const loadSuiteTree = async () => {
  const res = await getSuiteTree()
  const prev = new Set(expandedFolders.value)
  const rawTree = res.result || res
  const sortTreeByRule = (node) => {
    if (!node) return null
    const children = Array.isArray(node.children)
      ? node.children.map(sortTreeByRule)
      : []
    const folders = children
      .filter(c => c?.node_type === 'folder')
      .sort((a, b) => Number(a?.id || 0) - Number(b?.id || 0))
    const suites = children
      .filter(c => c?.node_type !== 'folder')
      .sort((a, b) => Number(b?.id || 0) - Number(a?.id || 0))
    return { ...node, children: [...folders, ...suites] }
  }
  suiteTree.value = sortTreeByRule(rawTree)
  if (suiteTree.value && !selectedFolderId.value) selectedFolderId.value = suiteTree.value.id
  if (suiteTree.value) {
    prev.add(suiteTree.value.id)
    expandedFolders.value = prev
  }
}

const openContextMenu = async (node, event) => {
  contextNode.value = node
  contextTargetFolderId.value = hasNodeId(node?.id) ? node.id : null
  selectedNodeId.value = node.id
  if (node.node_type === 'folder') selectedFolderId.value = node.id
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuVisible.value = true

  await nextTick()
  const el = contextMenuRef.value
  if (!el) return
  const margin = 8
  const maxX = window.innerWidth - el.offsetWidth - margin
  const maxY = window.innerHeight - el.offsetHeight - margin
  contextMenuX.value = Math.max(margin, Math.min(contextMenuX.value, maxX))
  contextMenuY.value = Math.max(margin, Math.min(contextMenuY.value, maxY))
}

const closeContextMenu = () => {
  contextMenuVisible.value = false
}

const onGlobalClick = () => {
  if (contextMenuVisible.value) closeContextMenu()
}

const onGlobalKeydown = (e) => {
  if (e.key === 'Escape' && contextMenuVisible.value) closeContextMenu()
}

const openFolderDialog = (mode, title, defaultValue = '') => {
  closeContextMenu()
  folderDialogMode.value = mode
  folderDialogTitle.value = title
  folderDialogValue.value = defaultValue || ''
  folderDialogVisible.value = true
}

const closeFolderDialog = () => {
  folderDialogVisible.value = false
  folderDialogValue.value = ''
}

const resolveCurrentFolderId = async () => {
  let id = hasNodeId(contextTargetFolderId.value)
    ? contextTargetFolderId.value
    : (hasNodeId(contextNode.value?.id)
      ? contextNode.value.id
      : (hasNodeId(selectedFolderId.value)
        ? selectedFolderId.value
        : (hasNodeId(suiteTree.value?.id) ? suiteTree.value.id : null)))
  if (hasNodeId(id)) return id
  await loadSuiteTree()
  id = hasNodeId(suiteTree.value?.id) ? suiteTree.value.id : null
  return hasNodeId(id) ? id : null
}

const createFolderUnderContext = async () => {
  openFolderDialog('create', '新增子文件夹', '')
}

const confirmFolderDialog = async () => {
  const name = (folderDialogValue.value || '').trim()
  if (!name) return
  try {
    if (folderDialogMode.value === 'create') {
      const parentId = await resolveCurrentFolderId()
      const payload = hasNodeId(parentId) ? { name, parent_id: parentId } : { name }
      await createSuiteFolder(payload)
      if (hasNodeId(parentId)) expandedFolders.value = new Set([...expandedFolders.value, parentId])
    } else {
      const nodeId = contextNode.value?.id || suiteTree.value?.id
      if (!nodeId) return
      await renameSuiteNode({ node_id: nodeId, name })
    }
    closeFolderDialog()
    closeContextMenu()
    await loadSuiteTree()
  } catch (e) {
    alert((folderDialogMode.value === 'rename' ? '重命名失败：' : '新建子文件夹失败：') + (e.response?.data?.message || e.response?.data?.msg || e.message))
  }
}

const renameContextNode = () => {
  const currentName = contextNode.value?.name || suiteTree.value?.name || '根目录'
  openFolderDialog('rename', '重命名目录', currentName)
}

const createSuiteUnderContext = async () => {
  const folderId = await resolveCurrentFolderId()
  closeContextMenu()
  router.push(`/suites/new${folderId ? `?parent_node_id=${folderId}` : ''}`)
}

const moveContextNode = () => {
  if (!hasNodeId(contextNode.value?.id) || !hasNodeId(contextNode.value?.parent)) return
  selectedNodeId.value = contextNode.value.id
  moveTargetFolderId.value = contextNode.value.parent
  closeContextMenu()
  moveDialogVisible.value = true
}

const deleteContextNode = async () => {
  const node = contextNode.value
  if (!node || !hasNodeId(node.id)) return
  if (!canDeleteContextNode.value) return
  const ok = await confirm('确定要删除该节点吗？', { type: 'danger' })
  if (!ok) return
  try {
    await deleteSuiteNode(node.id)
    closeContextMenu()
    await loadSuiteTree()
  } catch (e) {
    const msg = e.response?.data?.message || e.response?.data?.msg || e.message || String(e)
    alert('删除节点失败：' + msg)
  }
}

const confirmMoveNode = async () => {
  if (!moveTargetFolderId.value || !selectedNodeId.value) return
  await moveSuiteNode({ node_id: selectedNodeId.value, target_parent_id: moveTargetFolderId.value })
  moveDialogVisible.value = false
  await loadSuiteTree()
}

const openBatchMoveDialog = () => {
  if (!selectedIds.value.length) return
  batchMoveTargetFolderId.value = selectedFolderId.value || suiteTree.value?.id || null
  batchMoveDialogVisible.value = true
}

const confirmBatchMove = async () => {
  if (!batchMoveTargetFolderId.value || !selectedIds.value.length) return
  const total = selectedIds.value.length
  const failed = []
  for (const suiteId of selectedIds.value) {
    try {
      await attachSuiteToFolder({ suite_id: suiteId, parent_id: batchMoveTargetFolderId.value })
    } catch (e) {
      failed.push(suiteId)
    }
  }
  batchMoveDialogVisible.value = false
  selectedIds.value = []
  await Promise.all([loadSuites(pagination.value.page || 1), loadSuiteTree()])
  if (failed.length) {
    alert(`已移动 ${total - failed.length}/${total} 条，失败 ID：${failed.join(', ')}`)
  }
}

const allSelected = computed(() => displayedSuites.value.length > 0 && displayedSuites.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? displayedSuites.value.map(i => i.id) : [] }

const loadSuites = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (searchText.value)    params.search   = searchText.value
    if (filterRunType.value) params.run_type  = filterRunType.value
    const res = await getSuites(params)
    suites.value = res.result?.list || []
    pagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (e) { console.error('加载失败:', e) }
}

const handleSearch = () => loadSuites(1)
const resetFilter = () => { searchText.value = ''; filterRunType.value = ''; loadSuites(1) }

const changePage = (page) => { selectedIds.value = []; loadSuites(page) }
const viewDetail = (id) => router.push(`/suites/${id}`)
const viewResult = (id) => { showRunDialog.value = false; router.push(`/results?id=${id}`) }

onMounted(async () => {
  loadTreeState()
  await Promise.all([loadSuites(), loadSuiteTree()])
  window.addEventListener('click', onGlobalClick)
  window.addEventListener('keydown', onGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', onGlobalClick)
  window.removeEventListener('keydown', onGlobalKeydown)
})

watch([expandedFolders, selectedFolderId], saveTreeState, { deep: false })

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
.main-layout { display:grid; grid-template-columns: 320px minmax(0,1fr); gap:16px; align-items:start; }
.tree-column { min-width:0; }
.content-column { min-width:0; }
@media (max-width: 1200px) {
  .main-layout { grid-template-columns: 1fr; }
}
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
.tree-panel {
  margin-bottom: 16px;
  padding: 12px;
  position: relative;
  border: 1px solid #e7eef8;
  border-radius: 14px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  box-shadow: 0 8px 20px rgba(21, 70, 142, 0.05);
}
.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 4px 8px;
}
.tree-header strong {
  font-size: 14px;
  font-weight: 600;
  color: #1f2f45;
}
.context-menu {
  position: fixed;
  z-index: 1200;
  min-width: 188px;
  padding: 8px;
  background: #fff;
  border: 1px solid #dce8f7;
  border-radius: 12px;
  box-shadow: 0 14px 34px rgba(17, 49, 96, 0.16);
  backdrop-filter: blur(4px);
}
.context-menu button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  border: none;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  padding: 10px 10px;
  cursor: pointer;
  font-size: 12px;
  color: #2f3f58;
  transition: background .14s ease, color .14s ease;
}
.context-menu button::before {
  content: '•';
  color: #6f89b2;
  font-size: 14px;
}
.context-menu button:hover {
  background: #eaf2ff;
  color: #0c57b8;
}
.context-menu button:hover::before {
  color: #0c57b8;
}
.context-menu button:disabled { opacity: .45; cursor: not-allowed; }
.tree-body {
  margin-top: 8px;
  border: 1px solid #e4edf8;
  border-radius: 12px;
  max-height: 520px;
  overflow: auto;
  background: #f8fbff;
  padding: 4px 4px 6px;
}
.tree-row {
  line-height: 30px;
  cursor: pointer;
  border-bottom: none;
  user-select: none;
  transition: background .16s ease, color .16s ease, box-shadow .16s ease;
  border-radius: 9px;
  margin-bottom: 2px;
  font-size: 15px;
  color: #2a3b52;
  padding: 0 6px;
  position: relative;
  overflow: visible;
}
.tree-row:hover { background: #edf4ff; color: #174f93; }
.tree-row:last-child { border-bottom:none; }
.tree-row.active {
  background: #e3efff;
  color: #0b57ad;
  font-weight: 600;
  box-shadow: inset 0 0 0 1px #c6dcff;
}
.tree-toggle {
  display: inline-flex;
  width: 16px;
  height: 16px;
  align-items: center;
  color: #7587a4;
  font-weight: 700;
  justify-content: center;
  vertical-align: middle;
  transform: translateY(-5px);
}
.tree-node-label { display: inline-flex; align-items: center; gap: 6px; }
.tree-node-icon { display: inline-flex; width: 16px; height: 16px; color: #6b7f9f; flex: 0 0 16px; }
.tree-node-icon svg { width: 16px; height: 16px; }
.tree-row.active .tree-node-icon { color: #2f6eb9; }
.tree-node-label { max-width: calc(100% - 18px); }
.tree-node-name {
  display: inline-block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  position: relative;
}
.tree-node-name:hover::after {
  content: attr(data-full-name);
  position: absolute;
  left: 0;
  top: -30px;
  max-width: 420px;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #d8e4f5;
  background: #fff;
  color: #243447;
  font-size: 12px;
  line-height: 1.4;
  white-space: nowrap;
  box-shadow: 0 6px 16px rgba(20, 51, 101, 0.12);
  z-index: 2200;
  pointer-events: none;
}
.tree-body::-webkit-scrollbar { width: 6px; }
.tree-body::-webkit-scrollbar-track { background: transparent; }
.tree-body::-webkit-scrollbar-thumb { background: rgba(127, 151, 189, 0.45); border-radius: 999px; }
.tree-body::-webkit-scrollbar-thumb:hover { background: rgba(104, 132, 177, 0.8); }
.current-folder { display:flex; align-items:center; gap:8px; background:#f6f8fc; border:1px solid var(--border); border-radius:6px; padding:6px 10px; min-width:180px; }
.folder-label { font-size:12px; color:var(--text-light); }
.folder-name { font-size:13px; font-weight:600; color:var(--text); max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }
.table-container { overflow-x:auto; }
.case-list-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.case-list-title strong { font-size: 14px; }
.case-list-actions { display:inline-flex; align-items:center; gap:8px; }
.btn-action {
  padding: 5px 10px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  line-height: 1.3;
}
.btn-action:hover { opacity:.9; }
.btn-action.btn-success { background:#27ae60; }
.btn-action.btn-warning { background:#f39c12; }
.btn-action.btn-danger  { background:var(--danger); }
.btn-action.btn-info    { background:#3498db; }
.suite-row-actions { display: inline-flex; align-items: center; gap: 6px; }
.link-text { color:var(--primary); cursor:pointer; text-decoration:none; font-weight:500; }
.link-text:hover { text-decoration:underline; }
.empty-state { text-align:center; padding:48px; color:var(--text-light); }
.case-list-footer { margin-top: 8px; display:flex; align-items:center; justify-content:space-between; font-size:13px; }
.table-container table { font-size: 13px; }
.table-container thead th {
  font-size: 12px;
  color: #fff;
  font-weight: 500;
  white-space: nowrap;
}
.table-container tbody td { vertical-align: middle; }
.modal { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:1000; }
.modal-content { background:white; border-radius:12px; padding:20px; width:90%; max-width:420px; text-align:left; }
.modal-content h3 { margin-bottom:20px; font-size:18px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: var(--text); font-size: 13px; }
.form-group input, .form-group select { width: 100%; box-sizing: border-box; }
.modal-actions { display:flex; gap:12px; justify-content:flex-end; padding-top:8px; }
.loading-state,.success-state,.error-state { padding:16px; }
.spinner { width:40px; height:40px; border:4px solid var(--border); border-top-color:var(--accent); border-radius:50%; animation:spin 1s linear infinite; margin:0 auto 16px; }
.success-icon,.error-icon { width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:26px; margin:0 auto 12px; }
.success-icon { background:#27ae60; color:white; }
.error-icon   { background:#e74c3c; color:white; }
.result-id { color:var(--text-light); font-size:13px; margin:10px 0; }
@keyframes spin { to { transform:rotate(360deg); } }
</style>
