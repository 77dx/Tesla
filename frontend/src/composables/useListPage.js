/**
 * useListPage — 列表页通用逻辑封装
 *
 * 封装了所有列表页的共同逻辑：
 * - 数据加载（支持产品线过滤、搜索、分页）
 * - 分页状态管理
 * - 搜索（回车/按钮触发）
 * - 多选与批量删除
 * - 新建/编辑弹窗
 * - 单条删除
 *
 * 用法示例：
 * ```js
 * import { useListPage } from '@/composables/useListPage'
 * import { getProjects, createProject, updateProject, deleteProject } from '@/api/project'
 *
 * const {
 *   items, loading, pagination, searchText, selectedIds,
 *   showDialog, editingItem, formData,
 *   loadItems, handleSearch, resetFilter, changePage,
 *   openCreate, openEdit, closeDialog,
 *   handleDelete, handleBatchDelete,
 * } = useListPage({
 *   fetchList: getProjects,
 *   createItem: createProject,
 *   updateItem: updateProject,
 *   deleteItem: deleteProject,
 *   defaultForm: { name: '', intro: '', url: '', pm: null },
 * })
 * ```
 */
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { confirm } from '@/composables/useConfirm'

/**
 * @param {Object} options
 * @param {Function} options.fetchList   - (params) => Promise  列表查询 API
 * @param {Function} [options.createItem]  - (data) => Promise  创建 API
 * @param {Function} [options.updateItem]  - (id, data) => Promise  更新 API
 * @param {Function} [options.deleteItem]  - (id) => Promise  删除 API
 * @param {Object}   [options.defaultForm] - 表单初始值
 * @param {Object}   [options.extraParams] - 额外的固定查询参数
 * @param {Number}   [options.pageSize]    - 每页条数（默认 10）
 * @param {Boolean}  [options.withProductLine] - 是否带产品线过滤（默认 true）
 */
export function useListPage(options) {
  const {
    fetchList,
    createItem,
    updateItem,
    deleteItem,
    defaultForm = {},
    extraParams = {},
    pageSize = 10,
    withProductLine = true,
  } = options

  const userStore = useUserStore()

  // ── 状态 ──────────────────────────────────────────────────
  const items = ref([])
  const loading = ref(false)
  const searchText = ref('')
  const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })

  // 多选
  const selectedIds = ref([])
  const allSelected = computed(
    () => items.value.length > 0 && items.value.every(i => selectedIds.value.includes(i.id))
  )
  const toggleAll = (e) => {
    selectedIds.value = e.target.checked ? items.value.map(i => i.id) : []
  }

  // 弹窗
  const showDialog = ref(false)
  const editingItem = ref(null)
  const formData = ref({ ...defaultForm })
  const saving = ref(false)

  // ── 加载数据 ───────────────────────────────────────────────
  const loadItems = async (page = 1) => {
    loading.value = true
    try {
      const params = { page, page_size: pageSize, ...extraParams }
      if (searchText.value) params.search = searchText.value
      if (withProductLine && userStore.currentProductLine) {
        params.product_line = userStore.currentProductLine.id
      }
      const res = await fetchList(params)
      items.value = res.result?.list || res.list || res || []
      const r = res.result || res
      pagination.value = {
        page: r.page || page,
        pageCount: r.pageCount || 1,
        itemCount: r.itemCount || 0,
      }
    } catch (e) {
      console.error('[useListPage] loadItems error:', e)
    } finally {
      loading.value = false
    }
  }

  const handleSearch = () => loadItems(1)
  const resetFilter = () => { searchText.value = ''; loadItems(1) }
  const changePage = (page) => { selectedIds.value = []; loadItems(page) }

  // ── 弹窗操作 ───────────────────────────────────────────────
  const openCreate = () => {
    editingItem.value = null
    formData.value = { ...defaultForm }
    if (withProductLine && userStore.currentProductLine) {
      formData.value.product_line = userStore.currentProductLine.id
    }
    showDialog.value = true
  }

  const openEdit = (item) => {
    editingItem.value = item
    formData.value = { ...item }
    showDialog.value = true
  }

  const closeDialog = () => {
    showDialog.value = false
    editingItem.value = null
    formData.value = { ...defaultForm }
  }

  // ── 提交（新建 or 编辑）────────────────────────────────────
  const handleSubmit = async (extraData = {}) => {
    if (!createItem && !updateItem) return
    saving.value = true
    try {
      const data = { ...formData.value, ...extraData }
      if (editingItem.value) {
        await updateItem(editingItem.value.id, data)
      } else {
        await createItem(data)
      }
      closeDialog()
      await loadItems(pagination.value.page)
      return true
    } catch (e) {
      // 把后端字段级错误原样返回，由调用方处理
      return e.response?.data || e
    } finally {
      saving.value = false
    }
  }

  // ── 删除 ───────────────────────────────────────────────────
  const handleDelete = async (id, message = '确定要删除这条数据吗？') => {
    if (!deleteItem) return
    const confirmed = await confirm(message, { type: 'danger' })
    if (!confirmed) return
    try {
      await deleteItem(id)
      items.value = items.value.filter(i => i.id !== id)
      selectedIds.value = selectedIds.value.filter(sid => sid !== id)
    } catch (e) {
      console.error('[useListPage] delete error:', e)
    }
  }

  const handleBatchDelete = async (message) => {
    if (!selectedIds.value.length || !deleteItem) return
    const msg = message || `确定要删除选中的 ${selectedIds.value.length} 条数据吗？`
    const confirmed = await confirm(msg, { type: 'danger' })
    if (!confirmed) return
    try {
      await Promise.all(selectedIds.value.map(id => deleteItem(id)))
      items.value = items.value.filter(i => !selectedIds.value.includes(i.id))
      selectedIds.value = []
    } catch (e) {
      console.error('[useListPage] batchDelete error:', e)
    }
  }

  return {
    // 状态
    items,
    loading,
    searchText,
    pagination,
    selectedIds,
    allSelected,
    toggleAll,
    showDialog,
    editingItem,
    formData,
    saving,
    // 方法
    loadItems,
    handleSearch,
    resetFilter,
    changePage,
    openCreate,
    openEdit,
    closeDialog,
    handleSubmit,
    handleDelete,
    handleBatchDelete,
  }
}
