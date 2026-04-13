<template>
  <div class="sprint-detail">
    <div class="toolbar">
      <button class="btn btn-back" @click="$router.back()">← 返回</button>
      <button class="btn btn-primary" @click="openCreateReq">+ 新增需求</button>
      <button class="btn btn-refresh" @click="loadAll">↻ 刷新</button>
    </div>

    <div v-if="sprint" class="info-card card">
      <h2>{{ sprint.name }}</h2>
      <div class="info-grid">
        <div><label>迭代周期</label><span>{{ formatCycle(sprint) }}</span></div>
        <div><label>负责人</label><span>{{ sprint.owner_name || '-' }}</span></div>
        <div><label>状态</label><span>{{ statusText[sprint.status] }}</span></div>
      </div>
    </div>

    <div class="card tabs-card">
      <div class="tab-head">
        <button class="tab-btn" :class="{active:activeTab==='suite'}" @click="activeTab='suite'">引用套件 ({{ suiteRefs.length }})</button>
        <button class="tab-btn" :class="{active:activeTab==='case'}" @click="activeTab='case'">引用用例 ({{ caseRefs.length }})</button>
        <button class="tab-btn" :class="{active:activeTab==='req'}" @click="activeTab='req'">需求 ({{ requirements.length }})</button>
      </div>

      <div v-if="activeTab==='suite'" class="tab-panel">
        <div class="panel-actions">
          <button class="btn btn-sm btn-primary" @click="runSuites">执行套件</button>
          <button class="btn btn-sm btn-secondary" @click="openSuiteRefDialog">+ 引用套件</button>
        </div>
        <div v-for="ref in suiteRefs" :key="ref.id" class="row-item">
          <span>{{ ref.suite_name || `套件 #${ref.suite}` }}</span>
          <button class="btn btn-xs btn-danger" @click="removeSuiteRef(ref)">移除</button>
        </div>
        <div v-if="!suiteRefs.length" class="empty">暂无引用套件</div>
      </div>

      <div v-if="activeTab==='case'" class="tab-panel">
        <div class="panel-actions">
          <button class="btn btn-sm btn-primary" @click="runCases">执行用例</button>
          <button class="btn btn-sm btn-secondary" @click="openCaseRefDialog">+ 引用用例</button>
        </div>
        <div v-for="ref in caseRefs" :key="ref.id" class="row-item">
          <span>{{ ref.case_name || `用例 #${ref.case}` }}</span>
          <div class="actions">
            <button class="btn btn-xs btn-secondary" @click="runSingleCase(ref)">执行</button>
            <button class="btn btn-xs btn-danger" @click="removeCaseRef(ref)">移除</button>
          </div>
        </div>
        <div v-if="!caseRefs.length" class="empty">暂无引用用例</div>
      </div>

      <div v-if="activeTab==='req'" class="tab-panel">
        <div v-for="r in requirements" :key="r.id" class="row-item">
          <span>{{ r.title }}</span>
          <span class="muted">{{ r.status_label }} / {{ r.priority_label }} / {{ r.assignee_name || '-' }}</span>
          <div class="actions">
            <button class="btn btn-xs btn-secondary" @click="openEditReq(r)">编辑</button>
            <button class="btn btn-xs btn-danger" @click="deleteReq(r)">删除</button>
          </div>
        </div>
        <div v-if="!requirements.length" class="empty">暂无需求</div>
      </div>
    </div>

    <div v-if="showSuiteRefDialog" class="modal" @click.self="closeSuiteRefDialog">
      <div class="modal-content picker-modal">
        <div class="picker-header">
          <h3>批量引入套件</h3>
          <label class="picker-scope-toggle">
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
                @click="selectSuiteTreeNode(node)"
              >
                <span class="picker-tree-toggle" @click.stop="toggleSuiteFolder(node)">{{ isSuiteFolderNode(node) ? (isSuiteFolderExpanded(node.id) ? '▾' : '▸') : '' }}</span>
                <span class="picker-tree-text">{{ isSuiteFolderNode(node) ? '📁' : '📄' }} {{ displayTreeNodeName(node) }}</span>
              </div>
            </div>
            <div v-else class="empty">暂无目录树</div>
          </div>

          <div class="picker-list-panel">
            <div class="picker-toolbar">
              <input v-model="suitePickerSearch" class="picker-search" placeholder="搜索套件名称或 ID" />
              <div class="picker-toolbar-right">
                <span class="picker-count">已选 {{ selectedSuiteIds.length }} 项</span>
                <label class="picker-checkall" v-if="availableSuiteCandidates.length">
                  <input type="checkbox" :checked="allAvailableSuitesSelected" @change="toggleAllAvailableSuites" />
                  <span>全选当前可引入</span>
                </label>
              </div>
            </div>
            <div class="picker-list">
              <div v-for="item in filteredSuiteCandidates" :key="`suite-${item.id}`" class="picker-list-row" :class="{ disabled: isSuiteReferenced(item.id) }">
                <label class="picker-checkbox-wrap">
                  <input type="checkbox" :value="item.id" v-model="selectedSuiteIds" :disabled="isSuiteReferenced(item.id)" />
                  <span class="picker-item-title">#{{ item.id }} {{ item.name }}</span>
                  <div class="picker-item-meta">
                    <span v-if="isSuiteReferenced(item.id)" class="picker-badge disabled">已引用</span>
                    <span v-else class="picker-badge">可引入</span>
                  </div>
                </label>
              </div>
              <div v-if="!filteredSuiteCandidates.length" class="empty">当前目录下暂无可展示套件</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="closeSuiteRefDialog">取消</button>
          <button class="btn btn-primary" :disabled="!selectedSuiteIds.length" @click="submitSuiteRefs">确认引入 {{ selectedSuiteIds.length ? `(${selectedSuiteIds.length})` : '' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showCaseRefDialog" class="modal" @click.self="closeCaseRefDialog">
      <div class="modal-content picker-modal">
        <div class="picker-header">
          <h3>批量引入用例</h3>
          <label class="picker-scope-toggle">
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
                @click="selectCaseTreeNode(node)"
              >
                <span class="picker-tree-toggle" @click.stop="toggleCaseFolder(node)">{{ isCaseFolderNode(node) ? (isCaseFolderExpanded(node.id) ? '▾' : '▸') : '' }}</span>
                <span class="picker-tree-text">{{ isCaseFolderNode(node) ? '📁' : '📄' }} {{ displayTreeNodeName(node) }}</span>
              </div>
            </div>
            <div v-else class="empty">暂无目录树</div>
          </div>

          <div class="picker-list-panel">
            <div class="picker-toolbar">
              <input v-model="casePickerSearch" class="picker-search" placeholder="搜索用例名称或 ID" />
              <div class="picker-toolbar-right">
                <span class="picker-count">已选 {{ selectedCaseIds.length }} 项</span>
                <label class="picker-checkall" v-if="availableCaseCandidates.length">
                  <input type="checkbox" :checked="allAvailableCasesSelected" @change="toggleAllAvailableCases" />
                  <span>全选当前可引入</span>
                </label>
              </div>
            </div>
            <div class="picker-list">
              <div v-for="item in filteredCaseCandidates" :key="`case-${item.id}`" class="picker-list-row" :class="{ disabled: isCaseReferenced(item.id) }">
                <label class="picker-checkbox-wrap">
                  <input type="checkbox" :value="item.id" v-model="selectedCaseIds" :disabled="isCaseReferenced(item.id)" />
                  <span class="picker-item-title">#{{ item.id }} {{ item.name }}</span>
                  <div class="picker-item-meta">
                    <span class="picker-item-endpoint">{{ item.endpoint?.name || '未关联接口' }}</span>
                    <span v-if="isCaseReferenced(item.id)" class="picker-badge disabled">已引用</span>
                    <span v-else class="picker-badge">可引入</span>
                  </div>
                </label>
              </div>
              <div v-if="!filteredCaseCandidates.length" class="empty">当前目录下暂无可展示用例</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="closeCaseRefDialog">取消</button>
          <button class="btn btn-primary" :disabled="!selectedCaseIds.length" @click="submitCaseRefs">确认引入 {{ selectedCaseIds.length ? `(${selectedCaseIds.length})` : '' }}</button>
        </div>
      </div>
    </div>

    <div v-if="showReqDialog" class="modal" @click.self="showReqDialog=false">
      <div class="modal-content">
        <h3>{{ editingReq ? '编辑需求' : '新建需求' }}</h3>
        <div class="form-group"><label>标题</label><input v-model="reqForm.title" /></div>
        <div class="form-group"><label>描述</label><textarea v-model="reqForm.desc" rows="3"></textarea></div>
        <div class="modal-actions"><button class="btn" @click="showReqDialog=false">取消</button><button class="btn btn-primary" @click="saveReq">保存</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getSprintDetail, getSprintSuiteRefs, createSprintSuiteRef, deleteSprintSuiteRef, getSprintCaseRefs, createSprintCaseRef, deleteSprintCaseRef, getRequirements, createRequirement, updateRequirement, deleteRequirement, runSprint } from '@/api/sprint'
import { getSuites, getSuiteTree } from '@/api/suite'
import { getCases, getCaseTree, runCaseById } from '@/api/case'
import { useUserStore } from '@/stores/user'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'

const route = useRoute()
const userStore = useUserStore()
const sprint = ref(null)
const suiteRefs = ref([])
const caseRefs = ref([])
const requirements = ref([])
const activeTab = ref('suite')

const showSuiteRefDialog = ref(false)
const showCaseRefDialog = ref(false)
const showReqDialog = ref(false)
const editingReq = ref(null)
const reqForm = ref({ title: '', desc: '', status: 'todo', priority: 1, assignee: null })

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

const statusText = { planning: '规划中', active: '进行中', reviewing: '评审中', done: '已完成' }
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

const loadAll = async () => {
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
}

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

const runSuites = async () => {
  const ids = suiteRefs.value.map(i => i.suite)
  if (!ids.length) return alert('暂无引用套件')
  await runSprint(route.params.id, { suite_ids: ids })
  alert('已触发套件执行')
}
const runCases = async () => {
  if (!caseRefs.value.length) return alert('暂无引用用例')
  for (const ref of caseRefs.value) await runCaseById(ref.case)
  alert(`已触发 ${caseRefs.value.length} 条用例执行`)
}
const runSingleCase = async (ref) => { await runCaseById(ref.case); alert('已触发执行') }

const openCreateReq = () => {
  editingReq.value = null
  reqForm.value = { title: '', desc: '', status: 'todo', priority: 1, assignee: null }
  showReqDialog.value = true
}
const openEditReq = (r) => {
  editingReq.value = r
  reqForm.value = { title: r.title, desc: r.desc || '', status: r.status || 'todo', priority: r.priority ?? 1, assignee: r.assignee || null }
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
    await createRequirement({ sprint: route.params.id, title: reqForm.value.title, desc: reqForm.value.desc, status: 'todo', priority: 1 })
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

const formatCycle = (s) => [s.start_date || '-', s.end_date || '-'].join(' ~ ')
onMounted(loadAll)
</script>

<style scoped>
.toolbar { display:flex; gap:8px; margin-bottom:12px; }
.info-card { margin-bottom:12px; }
.info-grid { display:grid; grid-template-columns:repeat(3, minmax(160px,1fr)); gap:12px; }
.info-grid label { display:block; font-size:12px; color:#6b7280; }
.tab-head { display:flex; gap:8px; border-bottom:1px solid #edf0f2; padding:10px; }
.tab-btn { border:1px solid #d1d5db; background:#fff; border-radius:8px; padding:6px 12px; font-size:12px; }
.tab-btn.active { background:#1677ff; color:#fff; border-color:#1677ff; }
.tab-panel { padding:10px; }
.panel-actions { display:flex; justify-content:flex-end; gap:8px; margin-bottom:8px; }
.row-item { display:flex; justify-content:space-between; align-items:center; padding:8px; border-bottom:1px dashed #eee; }
.empty { color:#8b949e; padding:8px; }
.muted { color:#6b7280; font-size:12px; }
.modal { position:fixed; inset:0; background:rgba(0,0,0,.28); display:flex; align-items:center; justify-content:center; z-index:1000; padding:12px; }
.modal-content { background:#fff; border:1px solid #e5e7eb; border-radius:12px; padding:18px; width:min(640px,92vw); }
.picker-modal { width:700px; height:900px; max-width:95vw; max-height:96vh; display:flex; flex-direction:column; }
.picker-header { display:flex; align-items:end; justify-content:space-between; gap:12px; margin-bottom:14px; }
.picker-subtitle { color:#6b7280; font-size:12px; }
.picker-scope-toggle { display:flex; align-items:center; gap:6px; font-size:12px; color:#475569; white-space:nowrap; }
.picker-layout { display:grid; grid-template-columns:220px minmax(0, 1fr); gap:16px; min-height:0; flex:1; }
.picker-tree-panel,.picker-list-panel { border:1px solid #e5e7eb; border-radius:12px; background:#fbfcfe; display:flex; flex-direction:column; min-height:0; min-width:0; }
.picker-panel-title { padding:12px 14px; font-size:12px; font-weight:600; border-bottom:1px solid #e5e7eb; }
.picker-tree,.picker-list { padding:8px; overflow:auto; min-height:0; }
.picker-tree-row { display:flex; align-items:center; gap:6px; min-height:28px; border-radius:8px; cursor:pointer; color:#334155; font-size:12px; }
.picker-tree-row:hover { background:#f0f7ff; }
.picker-tree-row.active { background:#e8f2ff; color:#0f3b87; }
.picker-tree-toggle { width:16px; text-align:center; color:#64748b; font-size:11px; }
.picker-tree-text { flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.picker-toolbar { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:12px 14px; border-bottom:1px solid #e5e7eb; }
.picker-search { flex:1; min-width:0; padding:8px 10px; border:1px solid #d1d5db; border-radius:8px; }
.picker-toolbar-right { display:flex; align-items:center; gap:14px; flex:none; }
.picker-count,.picker-checkall { color:#475569; font-size:12px; }
.picker-checkall { display:flex; align-items:center; gap:6px; white-space:nowrap; }
.picker-list-row { border:1px solid #edf2f7; border-radius:10px; padding:10px 12px; background:#fff; }
.picker-list-row + .picker-list-row { margin-top:8px; }
.picker-list-row.disabled { opacity:.65; background:#f8fafc; }
.picker-checkbox-wrap { display:grid; grid-template-columns:18px minmax(260px, 1fr) auto; align-items:center; gap:10px; cursor:pointer; min-width:0; width:100%; }
.picker-checkbox-wrap input { flex:none; }
.picker-item-title { display:block; min-width:260px; font-size:12px; color:#0f172a; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.picker-item-meta { display:flex; flex-wrap:nowrap; gap:8px; align-items:center; color:#64748b; font-size:12px; white-space:nowrap; flex:none; }
.picker-item-endpoint { max-width:360px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.picker-badge { display:inline-flex; align-items:center; height:20px; padding:0 8px; border-radius:999px; background:#e0f2fe; color:#0369a1; flex:none; font-size:12px; }
.picker-badge.disabled { background:#e5e7eb; color:#6b7280; }
.form-group { margin-bottom:10px; }
.form-group input,.form-group textarea,.modal-content select { width:100%; padding:8px 10px; border:1px solid #d1d5db; border-radius:8px; }
.modal-actions { display:flex; justify-content:flex-end; gap:8px; margin-top:14px; }
@media (max-width: 900px) {
  .picker-layout { grid-template-columns:1fr; }
}
</style>
