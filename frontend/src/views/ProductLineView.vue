<template>
  <div class="pl-view">
    <div class="toolbar">
      <button v-if="hasPermission('system:manage')" @click="openCreate" class="btn btn-primary">➕ 新建产品线</button>
      <button @click="loadAll" class="btn btn-refresh">↻ 刷新</button>
    </div>

    <div class="pl-grid">
      <div v-for="pl in productLines" :key="pl.id" class="pl-card card">
        <div class="pl-card-header">
          <div class="pl-card-title">
            <span class="pl-icon">⬡</span>
            <h3>{{ pl.name }}</h3>
          </div>
          <div class="pl-card-actions">
            <button v-if="hasPermission('system:manage')" @click="openEdit(pl)" class="btn-icon">✏️</button>
            <button v-if="hasPermission('system:manage')" @click="handleDelete(pl)" class="btn-icon btn-icon-danger">🗑</button>
          </div>
        </div>
        <p class="pl-desc">{{ pl.description || '暂无描述' }}</p>
        <div class="pl-meta">
          <span class="pl-stat"><b>{{ pl.members_count }}</b> 成员</span>
          <span class="pl-creator">创建人：{{ pl.created_by_name || '-' }}</span>
        </div>
        <div class="pl-footer">
          <button @click="openMembers(pl)" class="btn btn-sm btn-outline">👥 管理成员</button>
          <button v-if="userStore.currentProductLine?.id !== pl.id" @click="switchTo(pl)" class="btn btn-sm btn-primary">切换至此</button>
          <span v-else class="pl-current-badge">✓ 当前产品线</span>
        </div>
      </div>
      <div v-if="!productLines.length" class="empty-state">暂无产品线</div>
    </div>

    <!-- 新建/编辑产品线弹框 -->
    <div v-if="showFormDialog" class="modal" @click.self="showFormDialog = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingPl ? '编辑产品线' : '新建产品线' }}</h3>
          <button @click="showFormDialog = false" class="btn-close">✕</button>
        </div>
        <form @submit.prevent="handleSubmit" class="modal-body">
          <div class="form-group">
            <label>产品线名称 <span class="required">*</span></label>
            <input v-model="formData.name" required placeholder="如：用户端、师傅端、基础平台" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="formData.description" rows="3" placeholder="可选，描述该产品线的用途"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showFormDialog = false" class="btn">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 成员管理弹框 -->
    <div v-if="showMembersDialog" class="modal" @click.self="showMembersDialog = false">
      <div class="modal-content modal-wide">
        <div class="modal-header">
          <h3>{{ currentPl?.name }} — 成员管理</h3>
          <button @click="showMembersDialog = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body members-body">
          <!-- 左侧：用户选择 -->
          <div class="members-left">
            <div class="section-title">全部用户</div>
            <input v-model="userSearchText" class="user-search-input" placeholder="搜索用户名..." />
            <div class="user-select-grid">
              <label
                v-for="u in filteredAllUsers"
                :key="u.id"
                class="user-select-item"
                :class="{ 'is-selected': selectedUserIds.includes(u.id), 'is-member': existingMemberIds.includes(u.id) }"
              >
                <input type="checkbox" :value="u.id" v-model="selectedUserIds" :disabled="existingMemberIds.includes(u.id)" />
                <div class="user-avatar-mini" :class="{ 'avatar-selected': selectedUserIds.includes(u.id) }">
                  {{ (u.username || '?')[0].toUpperCase() }}
                </div>
                <div class="user-info-mini">
                  <span class="user-name-text">{{ u.username }}</span>
                  <span class="user-nick-text" v-if="existingMemberIds.includes(u.id)">已是成员</span>
                </div>
                <span class="user-check-icon" v-if="selectedUserIds.includes(u.id)">✓</span>
              </label>
              <div v-if="!filteredAllUsers.length" class="empty-tip">无匹配用户</div>
            </div>
          </div>

          <!-- 右侧：已选 + 现有成员 -->
          <div class="members-right">
            <div class="section-title">待添加
              <span class="badge" v-if="selectedUserIds.length">{{ selectedUserIds.length }}</span>
            </div>
            <div v-if="selectedUserIds.length" class="selected-users-bar">
              <div class="selected-tags">
                <span v-for="uid in selectedUserIds" :key="uid" class="selected-tag">
                  {{ allUsers.find(u => u.id === uid)?.username || uid }}
                  <button class="tag-remove" @click.stop="selectedUserIds = selectedUserIds.filter(id => id !== uid)">✕</button>
                </span>
              </div>
            </div>
            <div v-else class="selected-users-empty">从左侧勾选用户</div>
            <div class="form-group" style="margin-top:12px">
              <label>为所选用户指定角色（可选）</label>
              <select v-model="newMemberRole" class="member-select">
                <option :value="null">无角色</option>
                <option v-for="r in allRoles" :key="r.id" :value="r.id">{{ r.name }}</option>
              </select>
            </div>
            <button @click="handleBatchAddMembers" class="btn btn-primary btn-block" :disabled="!selectedUserIds.length || addingMembers">
              {{ addingMembers ? '添加中...' : `➕ 添加 ${selectedUserIds.length || ''} 位成员` }}
            </button>

            <div class="section-title" style="margin-top:20px">现有成员 <span class="badge">{{ members.length }}</span></div>
            <div class="existing-members">
              <div v-for="m in members" :key="m.id" class="existing-member-item">
                <div class="user-avatar-mini avatar-selected">{{ (m.username || '?')[0].toUpperCase() }}</div>
                <div class="user-info-mini">
                  <span class="user-name-text">{{ m.username }}</span>
                  <span class="user-nick-text">{{ m.role_name || '无角色' }}</span>
                </div>
                <select :value="m.role" @change="handleRoleChange(m, $event.target.value)" class="role-select-sm">
                  <option :value="null">无角色</option>
                  <option v-for="r in allRoles" :key="r.id" :value="r.id">{{ r.name }}</option>
                </select>
                <button @click="handleRemoveMember(m)" class="btn-remove">✕</button>
              </div>
              <div v-if="!members.length" class="empty-tip">暂无成员</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { confirm } from '@/composables/useConfirm'
import {
  getProductLines, createProductLine, updateProductLine, deleteProductLine,
  getProductLineMembers, addProductLineMember, removeProductLineMember, updateMemberRole
} from '@/api/productLine'
import { getRoles } from '@/api/system'
import { getAllUsers } from '@/api/account'

const userStore = useUserStore()
const { hasPermission } = userStore

const productLines = ref([])
const showFormDialog = ref(false)
const showMembersDialog = ref(false)
const editingPl = ref(null)
const currentPl = ref(null)
const members = ref([])
const allUsers = ref([])
const allRoles = ref([])
const saving = ref(false)
const addingMembers = ref(false)

// 成员管理状态
const userSearchText = ref('')
const selectedUserIds = ref([])  // 左侧勾选待添加的用户 id
const newMemberRole = ref(null)  // 批量添加时指定的角色

const formData = ref({ name: '', description: '' })

// 已是成员的 user id
const existingMemberIds = computed(() => members.value.map(m => m.user))

// 左侧过滤
const filteredAllUsers = computed(() => {
  const s = userSearchText.value.toLowerCase()
  if (!s) return allUsers.value
  return allUsers.value.filter(u => u.username.toLowerCase().includes(s))
})

const loadAll = async () => {
  const res = await getProductLines()
  productLines.value = res.result?.list || res.result || res || []
}

const openCreate = () => {
  editingPl.value = null
  formData.value = { name: '', description: '' }
  showFormDialog.value = true
}

const openEdit = (pl) => {
  editingPl.value = pl
  formData.value = { name: pl.name, description: pl.description || '' }
  showFormDialog.value = true
}

const handleSubmit = async () => {
  saving.value = true
  try {
    if (editingPl.value) {
      await updateProductLine(editingPl.value.id, formData.value)
    } else {
      await createProductLine(formData.value)
    }
    showFormDialog.value = false
    await loadAll()
    await userStore.fetchProductLines()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.name?.[0] || e.message))
  } finally {
    saving.value = false
  }
}

const handleDelete = async (pl) => {
  const ok = await confirm(`确定删除产品线「${pl.name}」吗？`, { type: 'danger' })
  if (!ok) return
  try {
    await deleteProductLine(pl.id)
    await loadAll()
    await userStore.fetchProductLines()
  } catch (e) { alert('删除失败: ' + e.message) }
}

const switchTo = async (pl) => {
  await userStore.switchProductLine(pl)
  window.location.reload()
}

const openMembers = async (pl) => {
  currentPl.value = pl
  showMembersDialog.value = true
  selectedUserIds.value = []
  userSearchText.value = ''
  newMemberRole.value = null
  const res = await getProductLineMembers(pl.id)
  members.value = res.result || res || []
}

const handleBatchAddMembers = async () => {
  if (!selectedUserIds.value.length) return
  addingMembers.value = true
  try {
    await Promise.all(
      selectedUserIds.value.map(uid =>
        addProductLineMember(currentPl.value.id, { user: uid, role: newMemberRole.value })
      )
    )
    const res = await getProductLineMembers(currentPl.value.id)
    members.value = res.result || res || []
    selectedUserIds.value = []
    newMemberRole.value = null
    await loadAll()
  } catch (e) { alert('添加失败: ' + e.message) }
  finally { addingMembers.value = false }
}

const handleRemoveMember = async (m) => {
  const ok = await confirm(`确定移除成员「${m.username}」吗？`, { type: 'danger' })
  if (!ok) return
  try {
    await removeProductLineMember(currentPl.value.id, m.id)
    members.value = members.value.filter(x => x.id !== m.id)
    await loadAll()
  } catch (e) { alert('移除失败: ' + e.message) }
}

const handleRoleChange = async (m, roleId) => {
  try {
    await updateMemberRole(currentPl.value.id, m.id, { role: roleId || null })
    m.role = roleId ? parseInt(roleId) : null
    m.role_name = allRoles.value.find(r => r.id == roleId)?.name || null
  } catch (e) { alert('更新角色失败: ' + e.message) }
}

onMounted(async () => {
  await loadAll()
  try {
    const [ur, rr] = await Promise.all([
      getAllUsers(),
      getRoles({ page_size: 200 })
    ])
    allUsers.value = ur.result?.list || ur.result || []
    allRoles.value = rr.result?.list || rr.result || []
  } catch (e) { console.error('加载用户/角色失败', e) }
})
</script>

<style scoped>
.pl-view { display: flex; flex-direction: column; gap: 20px; }
.toolbar { display: flex; gap: 10px; margin-bottom: 4px; }
.pl-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.pl-card { padding: 24px; border-radius: 14px; transition: box-shadow .2s; }
.pl-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,.1); }
.pl-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
.pl-card-title { display: flex; align-items: center; gap: 10px; }
.pl-icon { font-size: 22px; }
.pl-card-title h3 { font-size: 16px; font-weight: 700; color: var(--primary); margin: 0; }
.pl-card-actions { display: flex; gap: 6px; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 16px; padding: 4px 6px; border-radius: 6px; transition: background .15s; }
.btn-icon:hover { background: #f0f0f0; }
.btn-icon-danger:hover { background: #fdecea; }
.pl-desc { font-size: 13px; color: var(--text-light); margin: 0 0 14px; min-height: 20px; }
.pl-meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.pl-stat { font-size: 13px; color: var(--text-light); }
.pl-stat b { color: var(--primary); font-size: 15px; }
.pl-creator { font-size: 12px; color: #aaa; }
.pl-footer { display: flex; align-items: center; gap: 10px; padding-top: 14px; border-top: 1px solid var(--border); }
.btn-outline { background: white; border: 1.5px solid var(--accent); color: var(--accent); }
.btn-outline:hover { background: #e8f4fd; }
.pl-current-badge { font-size: 12px; color: #27ae60; font-weight: 600; padding: 4px 10px; background: #e8f5e9; border-radius: 12px; }
.empty-state { text-align: center; padding: 48px; color: var(--text-light); }
/* 弹框 */
.modal { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; border-radius: 14px; width: 90%; max-width: 500px; overflow: hidden; animation: slideUp .25s ease; }
.modal-wide { max-width: 920px; max-height: 88vh; display: flex; flex-direction: column; overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px 0; flex-shrink: 0; }
.modal-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
.btn-close { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-light); }
.modal-body { padding: 20px 24px 24px; overflow-y: auto; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.required { color: var(--danger); }
/* 成员管理双栏 */
.members-body { display: flex; gap: 20px; min-height: 0; }
.members-left { flex: 1; display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.members-right { width: 300px; flex-shrink: 0; display: flex; flex-direction: column; }
.section-title { font-size: 12px; font-weight: 700; color: var(--text-light); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.badge { background: var(--accent); color: white; font-size: 11px; border-radius: 10px; padding: 1px 7px; font-weight: 700; }
.user-search-input { width: 100%; border: 1.5px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 13px; outline: none; box-sizing: border-box; }
.user-search-input:focus { border-color: var(--accent); }
.user-select-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; max-height: 380px; overflow-y: auto; padding: 2px; }
.user-select-item { display: flex; align-items: center; gap: 8px; padding: 8px 10px; border: 1.5px solid var(--border, #e8e8e8); border-radius: 10px; cursor: pointer; transition: all .15s; user-select: none; background: white; }
.user-select-item:hover { border-color: var(--accent); background: #f0f7ff; }
.user-select-item.is-selected { border-color: var(--accent); background: #e8f4fd; }
.user-select-item.is-member { opacity: .5; cursor: not-allowed; background: #f9f9f9; }
.user-select-item input[type="checkbox"] { display: none; }
.user-avatar-mini { width: 30px; height: 30px; border-radius: 50%; background: #e0e0e0; color: #888; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all .15s; }
.user-avatar-mini.avatar-selected { background: linear-gradient(135deg, var(--accent, #3498db), #2980b9); color: white; }
.user-info-mini { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.user-name-text { font-size: 13px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-nick-text { font-size: 11px; color: #aaa; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-check-icon { margin-left: auto; color: var(--accent); font-size: 12px; font-weight: 700; flex-shrink: 0; }
.selected-users-bar { background: #f0f7ff; border: 1px solid #c8e1f9; border-radius: 10px; padding: 10px 12px; margin-bottom: 4px; }
.selected-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.selected-tag { display: inline-flex; align-items: center; gap: 4px; background: var(--accent); color: white; font-size: 12px; font-weight: 500; padding: 3px 8px 3px 10px; border-radius: 20px; }
.tag-remove { background: rgba(255,255,255,.25); border: none; color: white; width: 15px; height: 15px; border-radius: 50%; cursor: pointer; font-size: 9px; display: flex; align-items: center; justify-content: center; padding: 0; flex-shrink: 0; }
.tag-remove:hover { background: rgba(255,255,255,.45); }
.selected-users-empty { font-size: 12px; color: #bbb; background: #fafafa; border: 1px dashed #e0e0e0; border-radius: 10px; padding: 10px 14px; margin-bottom: 4px; text-align: center; }
.member-select { width: 100%; border: 1px solid var(--border); border-radius: 6px; padding: 7px 10px; font-size: 13px; outline: none; }
.btn-block { width: 100%; }
.existing-members { display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto; }
.existing-member-item { display: flex; align-items: center; gap: 8px; padding: 7px 10px; background: #f9f9f9; border-radius: 8px; }
.role-select-sm { border: 1px solid var(--border); border-radius: 5px; padding: 3px 6px; font-size: 11px; outline: none; flex: 1; min-width: 0; }
.btn-remove { background: none; border: none; color: #ccc; font-size: 14px; cursor: pointer; padding: 2px 4px; border-radius: 4px; flex-shrink: 0; transition: color .15s; }
.btn-remove:hover { color: var(--danger); }
.empty-tip { text-align: center; padding: 20px; color: #bbb; font-size: 13px; }
@keyframes slideUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
</style>
