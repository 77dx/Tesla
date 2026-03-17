<template>
  <div class="account-view">
    <div class="toolbar">
      <h2></h2>
      <div class="toolbar-actions">
        <button @click="showModifyDialog = true" class="btn btn-primary">修改信息</button>
        <button @click="showPasswordDialog = true" class="btn btn-secondary">修改密码</button>
      </div>
    </div>

    <div class="content-container">
      <!-- 用户信息卡片 -->
      <div class="card user-info-card">
        <div class="card-body">
          <div v-if="userInfo" class="user-profile">
            <!-- 头像区域 -->
            <div class="profile-header">
              <div class="avatar-section">
                <div class="avatar-container">
                  <img v-if="userInfo.avatar_url" :src="userInfo.avatar_url" alt="用户头像" class="avatar" />
                  <div v-else class="avatar-placeholder">
                    {{ userInfo.userInfo?.username?.charAt(0) || 'U' }}
                  </div>
                </div>
                <div class="avatar-actions">
                  <button @click="triggerAvatarUpload" class="btn btn-secondary" :disabled="isUploading">
                    {{ isUploading ? '上传中...' : '更换头像' }}
                  </button>
                </div>
                <!-- 隐藏的文件输入 -->
                <input 
                  type="file" 
                  ref="fileInput"
                  style="display: none" 
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  @change="handleFileSelect"
                />
                <!-- 上传状态显示 -->
                <div v-if="isUploading || uploadError" class="upload-status">
                  <div v-if="isUploading" class="upload-progress">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
                    </div>
                    <span class="progress-text">{{ uploadProgress }}%</span>
                  </div>
                  <div v-if="uploadError" class="upload-error">
                    {{ uploadError }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 用户详情 -->
            <div class="user-details">
              <div class="detail-grid">
                <div class="detail-item">
                  <label>用户名</label>
                  <span class="detail-value">{{ userInfo.userInfo?.username }}</span>
                </div>
                <div class="detail-item">
                  <label>邮箱</label>
                  <span class="detail-value">{{ userInfo.userInfo?.email || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>昵称</label>
                  <span class="detail-value">{{ userInfo.nickname || '-' }}</span>
                </div>
                <div class="detail-item">
                  <label>状态</label>
                  <span :class="['detail-value', userInfo.userInfo?.is_active ? 'status-active' : 'status-inactive']">
                    {{ userInfo.userInfo?.is_active ? '激活' : '未激活' }}
                  </span>
                </div>
                <div class="detail-item full-width">
                  <label>角色</label>
                  <div class="roles">
                    <span v-for="role in userInfo.role_list" :key="role.id" class="role-badge">
                      {{ role.name }}
                    </span>
                    <span v-if="!userInfo.role_list?.length" class="text-muted">暂无角色</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改信息对话框 -->
    <div v-if="showModifyDialog" class="modal" @click.self="closeModifyDialog">
      <div class="modal-content">
        <h3>修改个人信息</h3>
        <form @submit.prevent="handleModify">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="modifyForm.username" disabled readonly />
            <small class="form-text text-muted">用户名不可修改</small>
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="modifyForm.email" type="email" />
          </div>
          <div class="form-group">
            <label>昵称</label>
            <input v-model="modifyForm.nickname" required />
          </div>
          <div class="form-group">
            <label>角色</label>
            <div class="role-selection">
              <div v-for="role in allRoles" :key="role.id" class="role-checkbox">
                <label>
                  <input type="checkbox" :value="role.id" v-model="modifyForm.role_ids" />
                  {{ role.name }}
                </label>
              </div>
              <div v-if="!allRoles.length" class="text-muted">暂无角色数据</div>
            </div>
          </div>
          <div class="form-group">
            <label>头像URL</label>
            <input v-model="modifyForm.avatar_url" />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModifyDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <div v-if="showPasswordDialog" class="modal" @click.self="closePasswordDialog">
      <div class="modal-content">
        <h3>修改密码</h3>
        <form @submit.prevent="handleResetPassword">
          <div class="form-group">
            <label>旧密码</label>
            <input v-model="passwordForm.old_password" type="password" required minlength="6" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.new_password" type="password" required minlength="6" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="passwordForm.confirm_password" type="password" required minlength="6" />
          </div>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          <div class="modal-actions">
            <button type="button" @click="closePasswordDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProfile, resetPassword, modify, imgUpload } from '@/api/account'
import { getRoles, assignRole } from '@/api/system'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = ref(null)
const allRoles = ref([])
const showModifyDialog = ref(false)
const showPasswordDialog = ref(false)
const passwordError = ref('')

const modifyForm = ref({
  username: '',
  email: '',
  nickname: '',
  role_ids: [],
  avatar_url: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 头像上传相关变量
const fileInput = ref(null)
const selectedFile = ref(null)
const uploadProgress = ref(0)
const isUploading = ref(false)
const uploadError = ref('')

const loadUserInfo = async () => {
  try {
    const res = await getProfile()
    userInfo.value = res.result || res
    // 同步更新 store，确保 LayoutView 头像实时刷新
    userStore.userInfo = userInfo.value
    modifyForm.value = {
      username: userInfo.value.userInfo?.username || '',
      email: userInfo.value.userInfo?.email || '',
      nickname: userInfo.value.nickname || '',
      role_ids: userInfo.value.role_list?.map(role => role.id) || [],
      avatar_url: userInfo.value.avatar_url || ''
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

const loadRoles = async () => {
  try {
    const res = await getRoles({ page: 1, page_size: 100 })
    allRoles.value = res.result?.list || res.results || res || []
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

const handleModify = async () => {
  try {
    // 1. 准备基本信息的修改数据（排除用户名和角色ID）
    const modifyData = {
      nickname: modifyForm.value.nickname,
      email: modifyForm.value.email,
      avatar_url: modifyForm.value.avatar_url
    }
    
    // 2. 调用modify接口更新基本信息
    const modifyRes = await modify(modifyData)
    
    // 3. 更新角色分配（如果角色有变化）
    // 获取当前用户的ID
    const userId = userInfo.value.userInfo?.id
    if (userId && modifyForm.value.role_ids) {
      // 调用角色分配接口
      await assignRole({
        user_id: userId,
        role_ids: modifyForm.value.role_ids
      })
    }
    
    // 4. 重新加载用户信息
    await loadUserInfo()
    
    // 5. 显示成功消息并关闭对话框
    alert('个人信息更新成功！')
    closeModifyDialog()
  } catch (error) {
    console.error('修改失败:', error)
    alert(`更新失败: ${error.response?.data?.message || error.message}`)
  }
}

const triggerAvatarUpload = () => {
  // 触发隐藏的文件输入元素
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    uploadError.value = '请选择图片文件 (JPEG, PNG, GIF, WebP)'
    return
  }
  
  // 验证文件大小 (限制5MB)
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    uploadError.value = '文件大小不能超过5MB'
    return
  }
  
  selectedFile.value = file
  uploadError.value = ''
  
  // 立即上传
  uploadAvatar()
}

const uploadAvatar = async () => {
  if (!selectedFile.value) {
    uploadError.value = '请先选择文件'
    return
  }
  
  isUploading.value = true
  uploadProgress.value = 0
  uploadError.value = ''
  
  try {
    const formData = new FormData()
    formData.append('avatar', selectedFile.value)
    
    // 模拟上传进度（实际API可能不支持进度事件）
    uploadProgress.value = 30
    
    const res = await imgUpload(formData)
    
    uploadProgress.value = 70
    
    console.log('头像上传响应:', res)
    
    // 处理头像URL - 支持多种响应格式
    let avatarUrl = ''
    
    // 提取实际数据，处理可能的包装格式
    // 格式1: {"code":200,"message":"ok","result":{...}}
    // 格式2: 直接返回序列化器数据
    let responseData = res
    if (res && typeof res === 'object' && res.result) {
      responseData = res.result
    }
    
    console.log('处理后的响应数据:', responseData)
    
    // 检查各种可能的头像字段
    const avatarFields = ['avatar_url', 'avatar', 'url', 'image', 'image_url', 'file', 'file_url']
    
    for (const field of avatarFields) {
      if (responseData[field]) {
        const fieldValue = responseData[field]
        console.log(`找到头像字段 ${field}:`, fieldValue)
        
        // 构建完整URL
        if (fieldValue.startsWith('http')) {
          avatarUrl = fieldValue
        } else if (fieldValue.startsWith('/')) {
          // 如果已经是绝对路径，直接使用
          avatarUrl = fieldValue
        } else {
          // 相对路径，添加/media/前缀
          avatarUrl = `/media/${fieldValue}`
        }
        
        console.log('构建的头像URL:', avatarUrl)
        break
      }
    }
    
    if (avatarUrl) {
      // 更新本地状态
      userInfo.value.avatar_url = avatarUrl
      modifyForm.value.avatar_url = avatarUrl
      
      // 调用modify接口更新Profile表中的avatar_url字段
      uploadProgress.value = 85
      try {
        await modify({
          nickname: userInfo.value.nickname || '', // 保持原有昵称
          avatar_url: avatarUrl
        })
        console.log('Profile头像URL更新成功')
      } catch (modifyError) {
        console.warn('更新Profile头像URL失败，但头像已上传:', modifyError)
        // 继续执行，因为头像已上传到Avatar表
      }
      
      // 重新加载用户信息以确保数据同步
      uploadProgress.value = 95
      await loadUserInfo()
      
      uploadProgress.value = 100
      alert('头像上传成功！')
    } else {
      console.warn('响应中没有找到头像字段，完整响应:', res)
      uploadError.value = '上传成功但未返回头像URL，响应数据: ' + JSON.stringify(res)
    }
  } catch (error) {
    console.error('头像上传失败:', error)
    uploadError.value = error.response?.data?.message || '头像上传失败，请重试'
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
    selectedFile.value = null
    // 清空文件输入的值，以便可以再次选择同一文件
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const handleResetPassword = async () => {
  passwordError.value = ''
  
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = '两次输入的密码不一致'
    return
  }
  
  try {
    await resetPassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    alert('密码修改成功，请重新登录')
    userStore.logout()
    window.location.href = '/login'
  } catch (error) {
    passwordError.value = error.response?.data?.message || '密码修改失败'
  }
}

const closeModifyDialog = () => {
  showModifyDialog.value = false
}

const closePasswordDialog = () => {
  showPasswordDialog.value = false
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
  passwordError.value = ''
}

onMounted(() => {
  loadUserInfo()
  loadRoles()
})
</script>

<style scoped>
/* 全局样式 */
.toolbar {
  margin-bottom: 24px;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.content-container {
  padding: 0 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  background: #f8f9fa;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.card-body {
  padding: 24px;
}

.card-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border);
  background: #f8f9fa;
}

/* 个人资料布局 */
.user-profile {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.avatar-container {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid #f0f0f0;
  transition: all 0.3s ease;
}

.avatar-container:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), #3498db);
  color: white;
  font-size: 40px;
  font-weight: 600;
}

.avatar-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

/* 上传状态 */
.upload-status {
  width: 100%;
  max-width: 300px;
  margin-top: 8px;
}

.upload-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--text-light);
  text-align: center;
}

.upload-error {
  font-size: 12px;
  color: #e74c3c;
  text-align: center;
  padding: 8px;
  background: #fee;
  border-radius: 4px;
}

/* 用户详情 */
.user-details {
  width: 100%;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 14px;
  color: var(--text-light);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 16px;
  color: var(--text);
  font-weight: 500;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

/* 角色标签 */
.roles {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  min-height: 40px;
  align-items: center;
}

.role-badge {
  padding: 6px 14px;
  background: linear-gradient(135deg, var(--accent), #3498db);
  color: white;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 状态样式 */
.status-active {
  color: #27ae60;
  font-weight: 600;
}

.status-inactive {
  color: #e74c3c;
  font-weight: 600;
}

.text-muted {
  color: var(--text-light);
  font-style: italic;
}

/* 按钮区域 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 表单样式 */
.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.form-text {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 4px;
  display: block;
}

/* 角色选择 */
.role-selection {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 200px;
  overflow-y: auto;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.role-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.role-checkbox:hover {
  background: #e9ecef;
}

.role-checkbox label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text);
  margin: 0;
  flex: 1;
}

.role-checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* 模态框 */
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
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 500px;
  animation: slideUp 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 24px 0;
  text-align: center;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-secondary {
  background: #f8f9fa;
  color: var(--text);
  border: 1px solid #e9ecef;
}

.btn-secondary:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 动画 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-container {
    padding: 0 16px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .modal-content {
    width: 95%;
    padding: 24px;
  }
  
  .avatar-container {
    width: 80px;
    height: 80px;
  }
  
  .avatar-placeholder {
    font-size: 32px;
  }
}
</style>
