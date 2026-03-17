<template>
  <div class="system-view">
    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'roles' }]" @click="activeTab = 'roles'">角色管理</button>
      <button :class="['tab-btn', { active: activeTab === 'departments' }]" @click="activeTab = 'departments'">部门管理</button>
      <button :class="['tab-btn', { active: activeTab === 'positions' }]" @click="activeTab = 'positions'">职位管理</button>
      <button :class="['tab-btn', { active: activeTab === 'users' }]" @click="activeTab = 'users'">用户管理</button>
    </div>

    <!-- 角色管理 -->
    <div v-if="activeTab === 'roles'" class="tab-content">
      <div class="filter-bar card">
        <div class="filter-input-wrap">
          <span class="filter-icon">🔍</span>
          <input v-model="roleSearch" class="filter-input" placeholder="搜索角色名称..." @keyup.enter="loadRoles(1)" />
        </div>
        <button @click="loadRoles(1)" class="btn btn-primary btn-sm">搜索</button>
        <button @click="roleSearch = ''; loadRoles(1)" class="btn btn-sm">重置</button>
        <button @click="loadRoles(1)" class="btn btn-refresh">↻ 刷新</button>
        <span class="filter-spacer"></span>
        <button @click="showRoleDialog = true" class="btn btn-primary btn-sm">➕ 新建角色</button>
      </div>
      
      <div class="table-container card">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>角色名称</th>
              <th>用户数量</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in roles" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.user_count || 0 }}</td>
              <td style="white-space: nowrap; overflow: visible; max-width: none;">
                <button @click="editRole(item)" class="btn-action">编辑</button>
                <button @click="openPermissionDialog(item)" class="btn-action btn-info">配置权限</button>
                <button @click="openRoleUsersDialog(item)" class="btn-action btn-info">管理用户</button>
                <button @click="deleteRoleItem(item.id)" class="btn-action btn-danger">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!roles.length" class="empty-state">暂无数据</div>
        <div v-if="rolesPagination.pageCount > 1" class="pagination">
          <span class="pagination-info">共 {{ rolesPagination.itemCount }} 条</span>
          <button class="page-btn" :disabled="rolesPagination.page <= 1" @click="loadRoles(rolesPagination.page - 1)">‹</button>
          <button v-for="p in rolesPagination.pageCount" :key="p" class="page-btn" :class="{ active: p === rolesPagination.page }" @click="loadRoles(p)">{{ p }}</button>
          <button class="page-btn" :disabled="rolesPagination.page >= rolesPagination.pageCount" @click="loadRoles(rolesPagination.page + 1)">›</button>
        </div>
      </div>
    </div>

    <!-- 部门管理 -->
    <div v-if="activeTab === 'departments'" class="tab-content">
      <div class="filter-bar card">
        <div class="filter-input-wrap">
          <span class="filter-icon">🔍</span>
          <input v-model="deptSearch" class="filter-input" placeholder="搜索部门名称..." @keyup.enter="loadDepartments(1)" />
        </div>
        <button @click="loadDepartments(1)" class="btn btn-primary btn-sm">搜索</button>
        <button @click="deptSearch = ''; loadDepartments(1)" class="btn btn-sm">重置</button>
        <button @click="loadDepartments(1)" class="btn btn-refresh">↻ 刷新</button>
        <span class="filter-spacer"></span>
        <button @click="showDeptDialog = true" class="btn btn-primary btn-sm">➕ 新建部门</button>
      </div>
      
      <div class="table-container card">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>部门名称</th>
              <th>部门简介</th>
              <th>负责人</th>
              <th>默认角色</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in departments" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.intro || '-' }}</td>
              <td>{{ item.leader_name || '-' }}</td>
              <td>
                <span v-if="item.default_role_name" class="badge badge-success">{{ item.default_role_name }}</span>
                <span v-else class="badge badge-gray">未设置</span>
              </td>
              <td style="white-space: nowrap; overflow: visible; max-width: none;">
                <button @click="editDepartment(item)" class="btn-action">编辑</button>
                <button @click="deleteDepartmentItem(item.id)" class="btn-action btn-danger">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!departments.length" class="empty-state">暂无数据</div>
        <div v-if="deptPagination.pageCount > 1" class="pagination">
          <span class="pagination-info">共 {{ deptPagination.itemCount }} 条</span>
          <button class="page-btn" :disabled="deptPagination.page <= 1" @click="loadDepartments(deptPagination.page - 1)">‹</button>
          <button v-for="p in deptPagination.pageCount" :key="p" class="page-btn" :class="{ active: p === deptPagination.page }" @click="loadDepartments(p)">{{ p }}</button>
          <button class="page-btn" :disabled="deptPagination.page >= deptPagination.pageCount" @click="loadDepartments(deptPagination.page + 1)">›</button>
        </div>
      </div>
    </div>

    <!-- 职位管理 -->
    <div v-if="activeTab === 'positions'" class="tab-content">
      <div class="filter-bar card">
        <div class="filter-input-wrap">
          <span class="filter-icon">🔍</span>
          <input v-model="posSearch" class="filter-input" placeholder="搜索职位名称..." @keyup.enter="loadPositions(1)" />
        </div>
        <select v-model="posLeaderFilter" class="filter-select" @change="loadPositions(1)">
          <option value="">全部类型</option>
          <option value="true">负责人</option>
          <option value="false">普通职位</option>
        </select>
        <button @click="loadPositions(1)" class="btn btn-primary btn-sm">搜索</button>
        <button @click="posSearch = ''; posLeaderFilter = ''; loadPositions(1)" class="btn btn-sm">重置</button>
        <button @click="loadPositions(1)" class="btn btn-refresh">↻ 刷新</button>
        <span class="filter-spacer"></span>
        <button @click="showPosDialog = true" class="btn btn-primary btn-sm">➕ 新建职位</button>
      </div>
      
      <div class="table-container card">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>职位名称</th>
              <th>是否负责人</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in positions" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.name }}</td>
              <td>
                <span :class="item.is_leader ? 'badge-success' : 'badge-gray'" class="badge">
                  {{ item.is_leader ? '是' : '否' }}
                </span>
              </td>
              <td style="white-space: nowrap; overflow: visible; max-width: none;">
                <button @click="editPosition(item)" class="btn-action">编辑</button>
                <button @click="deletePositionItem(item.id)" class="btn-action btn-danger">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!positions.length" class="empty-state">暂无数据</div>
        <div v-if="posPagination.pageCount > 1" class="pagination">
          <span class="pagination-info">共 {{ posPagination.itemCount }} 条</span>
          <button class="page-btn" :disabled="posPagination.page <= 1" @click="loadPositions(posPagination.page - 1)">‹</button>
          <button v-for="p in posPagination.pageCount" :key="p" class="page-btn" :class="{ active: p === posPagination.page }" @click="loadPositions(p)">{{ p }}</button>
          <button class="page-btn" :disabled="posPagination.page >= posPagination.pageCount" @click="loadPositions(posPagination.page + 1)">›</button>
        </div>
      </div>
    </div>

    <!-- 角色对话框 -->
    <div v-if="showRoleDialog" class="modal" @click.self="closeRoleDialog">
      <div class="modal-content">
        <h3>{{ editingRole ? '编辑角色' : '新建角色' }}</h3>
        <form @submit.prevent="handleRoleSubmit">
          <div class="form-group">
            <label>角色名称</label>
            <input v-model="roleForm.name" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeRoleDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 部门对话框 -->
    <div v-if="showDeptDialog" class="modal" @click.self="closeDeptDialog">
      <div class="modal-content">
        <h3>{{ editingDept ? '编辑部门' : '新建部门' }}</h3>
        <form @submit.prevent="handleDeptSubmit">
          <div class="form-group">
            <label>部门名称</label>
            <input v-model="deptForm.name" required />
          </div>
          <div class="form-group">
            <label>部门简介</label>
            <textarea v-model="deptForm.intro" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>默认角色（加入部门自动获得）</label>
            <select v-model="deptForm.default_role">
              <option :value="null">不设置</option>
              <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeDeptDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 职位对话框 -->
    <div v-if="showPosDialog" class="modal" @click.self="closePosDialog">
      <div class="modal-content">
        <h3>{{ editingPos ? '编辑职位' : '新建职位' }}</h3>
        <form @submit.prevent="handlePosSubmit">
          <div class="form-group">
            <label>职位名称</label>
            <input v-model="posForm.name" required />
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="posForm.is_leader" />
              是否负责人
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closePosDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 用户管理 Tab -->
    <div v-if="activeTab === 'users'" class="tab-content">
      <div class="filter-bar card">
        <div class="filter-input-wrap">
          <span class="filter-icon">🔍</span>
          <input v-model="userSearch" class="filter-input" placeholder="搜索用户名或昵称..." @keyup.enter="applyUserFilter" />
        </div>
        <select v-model="userDeptFilter" class="filter-select">
          <option value="">全部部门</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
        <button @click="applyUserFilter" class="btn btn-primary btn-sm">搜索</button>
        <button @click="userSearch = ''; userDeptFilter = ''; applyUserFilter()" class="btn btn-sm">重置</button>
        <button @click="loadUsers" class="btn btn-refresh">↻ 刷新</button>
      </div>
      <div class="table-container card">
        <table class="table">
          <thead>
            <tr><th>ID</th><th>用户名</th><th>昵称</th><th>部门</th><th>职位</th><th>角色</th><th>管理员</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredUserList" :key="item.user_id">
              <td>{{ item.user_id }}</td>
              <td>{{ item.username }}</td>
              <td>{{ item.nickname }}</td>
              <td>{{ item.department_name || '-' }}</td>
              <td>{{ item.position_name || '-' }}</td>
              <td>
                <span v-for="r in item.role_list" :key="r.id" class="badge badge-success" style="margin:2px">{{ r.name }}</span>
                <span v-if="!item.role_list?.length" class="badge badge-gray">无角色</span>
              </td>
              <td><span :class="item.is_staff ? 'badge-success' : 'badge-gray'" class="badge">{{ item.is_staff ? '是' : '否' }}</span></td>
              <td style="white-space: nowrap; overflow: visible; max-width: none;"><button @click="editUser(item)" class="btn-action">编辑</button></td>
            </tr>
          </tbody>
        </table>
        <div v-if="!userList.length" class="empty-state">暂无数据</div>
      </div>
    </div>

    <!-- 权限配置弹窗 -->
    <div v-if="showPermDialog" class="modal" @click.self="showPermDialog = false">
      <div class="modal-content modal-wide">
        <h3>配置权限 — {{ permTargetRole?.name }}</h3>
        <div v-if="permLoading" class="empty-state">加载中...</div>
        <div v-else class="perm-groups">
          <div v-for="group in permGroups" :key="group.module" class="perm-group">
            <div class="perm-group-header">
              <input type="checkbox" :checked="isGroupAllChecked(group)" @change="toggleGroup(group, $event)" class="perm-group-checkbox" />
              <span class="perm-group-title">{{ moduleLabel(group.module) }}</span>
            </div>
            <div class="perm-items">
              <label v-for="perm in group.permissions" :key="perm.id" class="perm-item" :title="perm.name + ' (' + perm.code + ')'">
                <input type="checkbox" :value="perm.id" v-model="selectedPermIds" />
                <span class="perm-name">{{ perm.name }}</span>
                <span class="perm-code">{{ perm.code }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showPermDialog = false" class="btn">取消</button>
          <button @click="savePermissions" class="btn btn-primary">保存权限</button>
        </div>
      </div>
    </div>

    <!-- 角色用户管理弹窗 -->
    <div v-if="showRoleUsersDialog" class="modal" @click.self="showRoleUsersDialog = false">
      <div class="modal-content modal-wide">
        <h3>管理用户 — {{ roleUsersTarget?.name }}</h3>

        <!-- 已选用户展示区 -->
        <div class="selected-users-bar" v-if="selectedRoleUserIds.length">
          <span class="selected-label">已选 {{ selectedRoleUserIds.length }} 人：</span>
          <div class="selected-tags">
            <span
              v-for="uid in selectedRoleUserIds"
              :key="uid"
              class="selected-tag"
            >
              {{ allUsers.find(u => u.user_id === uid)?.username || uid }}
              <button class="tag-remove" @click.stop="selectedRoleUserIds = selectedRoleUserIds.filter(id => id !== uid)">✕</button>
            </span>
          </div>
        </div>
        <div class="selected-users-empty" v-else>暂未选择任何用户</div>

        <div class="user-list-divider">全部用户</div>

        <!-- 用户列表 -->
        <div class="user-select-grid">
          <label
            v-for="u in allUsers"
            :key="u.user_id"
            class="user-select-item"
            :class="{ 'is-selected': selectedRoleUserIds.includes(u.user_id) }"
          >
            <input type="checkbox" :value="u.user_id" v-model="selectedRoleUserIds" />
            <div class="user-avatar-mini" :class="{ 'avatar-selected': selectedRoleUserIds.includes(u.user_id) }">
              {{ (u.username || '?')[0].toUpperCase() }}
            </div>
            <div class="user-info-mini">
              <span class="user-name-text">{{ u.username }}</span>
              <span class="user-nick-text">{{ u.nickname }}</span>
            </div>
            <span class="user-check-icon" v-if="selectedRoleUserIds.includes(u.user_id)">✓</span>
          </label>
          <div v-if="!allUsers.length" class="empty-state">暂无用户数据</div>
        </div>

        <div class="modal-actions">
          <button @click="showRoleUsersDialog = false" class="btn">取消</button>
          <button @click="saveRoleUsers" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- 用户编辑弹窗 -->
    <div v-if="showUserDialog" class="modal" @click.self="showUserDialog = false">
      <div class="modal-content">
        <h3>编辑用户 — {{ editingUser?.username }}</h3>
        <div class="form-group">
          <label>部门</label>
          <select v-model="userForm.department">
            <option :value="null">不设置</option>
            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>职位</label>
          <select v-model="userForm.position">
            <option :value="null">不设置</option>
            <option v-for="p in positions" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>角色（可多选）</label>
          <div class="perm-items">
            <label v-for="r in roles" :key="r.id" class="perm-item">
              <input type="checkbox" :value="r.id" v-model="userForm.role_ids" />
              {{ r.name }}
            </label>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showUserDialog = false" class="btn">取消</button>
          <button @click="saveUser" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import {
  getRoles, createRole, updateRole, deleteRole,
  getDepartments, createDepartment, updateDepartment, deleteDepartment,
  getPositions, createPosition, updatePosition, deletePosition,
  getRoleDetail, setRolePermissions, setRoleUsers, getPermissionsGrouped,
} from '@/api/system'
import { getAdminUserList, updateAdminUser } from '@/api/account'
import { confirm } from '@/composables/useConfirm'

const activeTab = ref('roles')

// ── 列表数据 ──
const roles = ref([])
const departments = ref([])
const positions = ref([])
const userList = ref([])
const allUsers = ref([])

// ── 弹窗显示状态 ──
const showRoleDialog = ref(false)
const showDeptDialog = ref(false)
const showPosDialog = ref(false)
const showPermDialog = ref(false)
const showRoleUsersDialog = ref(false)
const showUserDialog = ref(false)

// ── 编辑目标 ──
const editingRole = ref(null)
const editingDept = ref(null)
const editingPos = ref(null)
const editingUser = ref(null)

// ── 表单数据 ──
const roleForm = ref({ name: '' })
const deptForm = ref({ name: '', intro: '', default_role: null })
const posForm = ref({ name: '', is_leader: false })
const userForm = ref({ department: null, position: null, role_ids: [] })

// ── 分页 ──
const rolesPagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const deptPagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const posPagination = ref({ page: 1, pageCount: 1, itemCount: 0 })

// ── 搜索/筛选 ──
const roleSearch = ref('')
const deptSearch = ref('')
const posSearch = ref('')
const posLeaderFilter = ref('')
const userSearch = ref('')
const userDeptFilter = ref('')
const filteredUserList = ref([])

// ── 权限配置 ──
const permGroups = ref([])
const selectedPermIds = ref([])
const permTargetRole = ref(null)
const permLoading = ref(false)

// ── 角色用户管理 ──
const roleUsersTarget = ref(null)
const selectedRoleUserIds = ref([])

const MODULE_LABELS = {
  project: '项目管理', endpoint: '接口管理', case: '用例管理',
  suite: '套件管理', result: '执行结果', environment: '环境管理',
  user: '用户管理', system: '系统管理', product_line: '产品线管理',
}
const moduleLabel = (m) => MODULE_LABELS[m] || m

// ── 加载函数 ──
const loadRoles = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (roleSearch.value) params.search = roleSearch.value
    const res = await getRoles(params)
    roles.value = res.result?.list || res.results || res || []
    rolesPagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (e) { console.error('加载角色列表失败:', e) }
}

const loadDepartments = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (deptSearch.value) params.search = deptSearch.value
    const res = await getDepartments(params)
    departments.value = res.result?.list || res.results || res || []
    deptPagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (e) { console.error('加载部门列表失败:', e) }
}

const loadPositions = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (posSearch.value) params.search = posSearch.value
    if (posLeaderFilter.value !== '') params.is_leader = posLeaderFilter.value
    const res = await getPositions(params)
    positions.value = res.result?.list || res.results || res || []
    posPagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (e) { console.error('加载职位列表失败:', e) }
}

const loadUsers = async () => {
  try {
    const res = await getAdminUserList()
    userList.value = res.result || res || []
    allUsers.value = userList.value
    applyUserFilter()
  } catch (e) { console.error('加载用户列表失败:', e) }
}

const applyUserFilter = () => {
  let list = userList.value
  if (userSearch.value) {
    const kw = userSearch.value.toLowerCase()
    list = list.filter(u =>
      (u.username || '').toLowerCase().includes(kw) ||
      (u.nickname || '').toLowerCase().includes(kw)
    )
  }
  if (userDeptFilter.value) {
    list = list.filter(u => u.department === userDeptFilter.value || u.department_id === userDeptFilter.value)
  }
  filteredUserList.value = list
}

// ── 角色 CRUD ──
const editRole = (item) => { editingRole.value = item; roleForm.value = { ...item }; showRoleDialog.value = true }
const closeRoleDialog = () => { showRoleDialog.value = false; editingRole.value = null; roleForm.value = { name: '' } }
const handleRoleSubmit = async () => {
  try {
    editingRole.value ? await updateRole(editingRole.value.id, roleForm.value) : await createRole(roleForm.value)
    closeRoleDialog(); loadRoles()
  } catch (e) { console.error('操作失败:', e) }
}
const deleteRoleItem = async (id) => {
  if (await confirm('确定要删除这个角色吗？', { type: 'danger' })) {
    try { await deleteRole(id); roles.value = roles.value.filter(r => r.id !== id) }
    catch (e) { console.error('删除失败:', e) }
  }
}

// ── 权限配置 ──
const openPermissionDialog = async (role) => {
  permTargetRole.value = role
  permLoading.value = true
  showPermDialog.value = true
  try {
    const [groupRes, detailRes] = await Promise.all([
      getPermissionsGrouped(),
      getRoleDetail(role.id)
    ])
    permGroups.value = groupRes.result || groupRes || []
    const detail = detailRes.result || detailRes
    selectedPermIds.value = (detail.permissions || []).map(p => p.id)
  } catch (e) { console.error('加载权限失败:', e) }
  finally { permLoading.value = false }
}
const isGroupAllChecked = (group) => group.permissions.every(p => selectedPermIds.value.includes(p.id))
const toggleGroup = (group, e) => {
  const ids = group.permissions.map(p => p.id)
  if (e.target.checked) {
    selectedPermIds.value = [...new Set([...selectedPermIds.value, ...ids])]
  } else {
    selectedPermIds.value = selectedPermIds.value.filter(id => !ids.includes(id))
  }
}
const savePermissions = async () => {
  try {
    await setRolePermissions(permTargetRole.value.id, { permission_ids: selectedPermIds.value })
    showPermDialog.value = false
    loadRoles()
  } catch (e) { console.error('保存权限失败:', e) }
}

// ── 角色用户管理 ──
const openRoleUsersDialog = async (role) => {
  roleUsersTarget.value = role
  if (!allUsers.value.length) await loadUsers()
  try {
    const res = await getRoleDetail(role.id)
    const detail = res.result || res
    // 从用户列表中找到已有该角色的用户
    const roleUserRes = await import('@/api/system').then(m => m.getRoleUsers({ role_id: role.id }))
    const roleUsers = roleUserRes.result?.users || roleUserRes.users || []
    selectedRoleUserIds.value = roleUsers.map(u => u.id)
  } catch (e) { selectedRoleUserIds.value = [] }
  showRoleUsersDialog.value = true
}
const saveRoleUsers = async () => {
  try {
    await setRoleUsers(roleUsersTarget.value.id, { user_ids: selectedRoleUserIds.value })
    showRoleUsersDialog.value = false
    loadRoles()
  } catch (e) { console.error('保存用户失败:', e) }
}

// ── 部门 CRUD ──
const editDepartment = (item) => { editingDept.value = item; deptForm.value = { name: item.name, intro: item.intro, default_role: item.default_role || null }; showDeptDialog.value = true }
const closeDeptDialog = () => { showDeptDialog.value = false; editingDept.value = null; deptForm.value = { name: '', intro: '', default_role: null } }
const handleDeptSubmit = async () => {
  try {
    editingDept.value ? await updateDepartment(editingDept.value.id, deptForm.value) : await createDepartment(deptForm.value)
    closeDeptDialog(); loadDepartments()
  } catch (e) { console.error('操作失败:', e) }
}
const deleteDepartmentItem = async (id) => {
  if (await confirm('确定要删除这个部门吗？', { type: 'danger' })) {
    try { await deleteDepartment({ id }); departments.value = departments.value.filter(d => d.id !== id) }
    catch (e) { console.error('删除失败:', e) }
  }
}

// ── 职位 CRUD ──
const editPosition = (item) => { editingPos.value = item; posForm.value = { ...item }; showPosDialog.value = true }
const closePosDialog = () => { showPosDialog.value = false; editingPos.value = null; posForm.value = { name: '', is_leader: false } }
const handlePosSubmit = async () => {
  try {
    editingPos.value ? await updatePosition(editingPos.value.id, posForm.value) : await createPosition(posForm.value)
    closePosDialog(); loadPositions()
  } catch (e) { console.error('操作失败:', e) }
}
const deletePositionItem = async (id) => {
  if (await confirm('确定要删除这个职位吗？', { type: 'danger' })) {
    try { await deletePosition(id); positions.value = positions.value.filter(p => p.id !== id) }
    catch (e) { console.error('删除失败:', e) }
  }
}

// ── 用户编辑 ──
const editUser = (item) => {
  editingUser.value = item
  userForm.value = {
    department: item.department || null,
    position: item.position || null,
    role_ids: (item.role_list || []).map(r => r.id)
  }
  showUserDialog.value = true
}
const saveUser = async () => {
  try {
    await updateAdminUser({ user_id: editingUser.value.user_id, ...userForm.value })
    showUserDialog.value = false
    loadUsers()
  } catch (e) { console.error('保存用户失败:', e) }
}

watch(activeTab, (tab) => {
  if (tab === 'roles') loadRoles()
  else if (tab === 'departments') { loadRoles(); loadDepartments() }
  else if (tab === 'positions') loadPositions()
  else if (tab === 'users') { loadUsers(); loadRoles(); loadDepartments(); loadPositions() }
})

onMounted(() => { loadRoles() })
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  margin-bottom: 16px;
  flex-wrap: nowrap;
}

.filter-input-wrap {
  display: flex;
  align-items: center;
  gap: 5px;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0 8px;
  background: white;
  width: 200px;
  flex-shrink: 0;
}

.filter-icon {
  color: var(--text-light);
  font-size: 13px;
}

.filter-input {
  border: none;
  outline: none;
  padding: 7px 0;
  font-size: 13px;
  width: 100%;
  background: transparent;
}

.filter-select {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 7px 8px;
  font-size: 13px;
  background: white;
  color: var(--text);
  outline: none;
  cursor: pointer;
  width: 120px;
  flex-shrink: 0;
}

.filter-select:focus {
  border-color: var(--accent);
}

.filter-spacer {
  flex: 1;
}

.btn-sm {
  padding: 7px 14px;
  font-size: 13px;
  white-space: nowrap;
}

.toolbar h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text);
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--border);
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: transparent;
  color: var(--text-light);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--primary);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.table-container {
  overflow-x: auto;
}

.btn-action {
  padding: 6px 12px;
  margin: 0 4px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.btn-action:hover {
  opacity: 0.8;
}

.btn-action.btn-danger {
  background: var(--danger);
}

.btn-action.btn-info {
  background: #3498db;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: #e8f5e9;
  color: #388e3c;
}

.badge-gray {
  background: #f5f5f5;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: var(--text-light);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 28px 32px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
  animation: slideUp 0.25s ease;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.modal-content h3 {
  margin-bottom: 20px;
  font-size: 17px;
  font-weight: 600;
  color: var(--text);
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border, #eee);
}

.modal-wide {
  max-width: 800px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-light, #666);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text);
  background: white;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--accent, #3498db);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border, #eee);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── 权限配置弹窗 ── */
.perm-groups {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  max-height: 55vh;
  overflow-y: auto;
  padding: 2px 2px 8px;
  margin-bottom: 4px;
}

.perm-group {
  border: 1px solid var(--border, #e8e8e8);
  border-radius: 10px;
  overflow: hidden;
  background: white;
}

.perm-group-header {
  background: var(--bg, #f7f8fa);
  padding: 9px 14px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: var(--text, #333);
  border-bottom: 1px solid var(--border, #eee);
  display: flex;
  align-items: center;
  gap: 8px;
}

.perm-group-checkbox {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  accent-color: var(--accent, #3498db);
  cursor: pointer;
  margin: 0;
}

.perm-group-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text, #333);
  user-select: none;
}

.perm-group-header label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.perm-items {
  display: flex;
  flex-direction: column;
  padding: 6px 0;
}

.perm-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 7px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
  user-select: none;
}

.perm-item:hover {
  background: var(--bg, #f7f8fa);
}

.perm-item input[type="checkbox"] {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  accent-color: var(--accent, #3498db);
  cursor: pointer;
}

.perm-name {
  flex: 1;
  font-size: 13px;
  color: var(--text, #333);
  white-space: normal;
  word-break: break-all;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.perm-code {
  font-size: 10px;
  color: #bbb;
  font-family: 'Monaco', monospace;
  background: #f5f5f5;
  padding: 1px 5px;
  border-radius: 3px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ── 已选用户展示区 ── */
.selected-users-bar {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #f0f7ff;
  border: 1px solid #c8e1f9;
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 12px;
  min-height: 44px;
}

.selected-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent, #3498db);
  white-space: nowrap;
  padding-top: 3px;
  flex-shrink: 0;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--accent, #3498db);
  color: white;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 8px 3px 10px;
  border-radius: 20px;
  line-height: 1.4;
}

.tag-remove {
  background: rgba(255,255,255,0.25);
  border: none;
  color: white;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
  transition: background 0.15s;
  flex-shrink: 0;
}

.tag-remove:hover {
  background: rgba(255,255,255,0.45);
}

.selected-users-empty {
  font-size: 12px;
  color: #bbb;
  background: #fafafa;
  border: 1px dashed #e0e0e0;
  border-radius: 10px;
  padding: 10px 14px;
  margin-bottom: 12px;
  text-align: center;
}

.user-list-divider {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-light, #999);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  margin-bottom: 8px;
  padding-left: 2px;
}

.user-check-icon {
  margin-left: auto;
  color: var(--accent, #3498db);
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.btn-refresh {
  background: var(--bg, #f5f7fa);
  color: var(--text, #333);
  border: 1px solid var(--border, #ddd);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

/* ── 用户选择弹窗 ── */
.user-select-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 8px;
  max-height: 55vh;
  overflow-y: auto;
  padding: 2px 2px 8px;
}

.user-select-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1.5px solid var(--border, #e8e8e8);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
  background: white;
  position: relative;
}

.user-select-item:hover {
  border-color: var(--accent, #3498db);
  background: #f0f7ff;
}

.user-select-item.is-selected {
  border-color: var(--accent, #3498db);
  background: #e8f4fd;
}

.user-select-item input[type="checkbox"] {
  display: none;
}

.user-avatar-mini {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #888;
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
}

.user-avatar-mini.avatar-selected {
  background: linear-gradient(135deg, var(--accent, #3498db), #2980b9);
  color: white;
}

.user-info-mini {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.user-name-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-nick-text {
  font-size: 11px;
  color: var(--text-light, #999);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

</style>
