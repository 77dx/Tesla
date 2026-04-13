<template>
  <div class="case-view">
    <div class="main-layout">
      <div class="tree-column">
        <div class="tree-panel card">
          <div class="tree-header">
            <strong>用例目录</strong>
          </div>
          <div class="tree-body" v-if="caseTree" ref="treeBodyRef">
            <div v-for="n in visibleTreeNodes" :key="n.id" class="tree-row" :class="{ active: isSameId(n.id, selectedNodeId) }" :style="{ paddingLeft: (n.level * 18 + 8) + 'px' }" @click="selectNode(n)"
              @contextmenu.prevent="openContextMenu(n, $event)"
              draggable="true" @dragstart="onDragStart(n, $event)" @dragover.prevent="onDragOverNode(n, $event)" @drop.prevent="onDropOnNode(n, $event)">
              <span class="tree-toggle" @click.stop="toggleFolder(n)">{{ isFolderNode(n) ? (isExpanded(n.id) ? '▾' : '▸') : '' }}</span>
              <span class="tree-node-label">
                <span class="tree-node-icon" aria-hidden="true">
                  <svg v-if="isFolderNode(n) && isExpanded(n.id)" viewBox="0 0 24 24" fill="none">
                    <path d="M3.5 8.5a2 2 0 0 1 2-2h4.1a2 2 0 0 1 1.4.58l.92.92H18.5a2 2 0 0 1 2 2v6.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-8Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else-if="isFolderNode(n)" viewBox="0 0 24 24" fill="none">
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
            <button @click.stop.prevent="createCaseUnderContext">新增用例</button>
            <button :disabled="!canMoveContextNode" :title="moveDisabledReason" @click.stop.prevent="moveContextNode">移动到</button>
            <button @click.stop.prevent="renameContextNode">重命名</button>
            <button :disabled="!canDeleteContextNode" @click.stop.prevent="deleteContextNode">删除节点</button>
          </div>
        </div>
      </div>

      <div class="content-column">
        <!-- 顶部：当前目录 + 筛选 -->
        <div class="filter-bar card">
          <div class="current-folder">
            <span class="folder-label">当前目录</span>
            <span class="folder-name" :title="selectedFolderPath">{{ selectedFolderPath }}</span>
          </div>
          <div class="filter-input-wrap">
            <span class="filter-icon">🔍</span>
            <input v-model="searchText" class="filter-input" placeholder="搜索用例名称或ID..." @keyup.enter="handleSearch" />
          </div>
          <select v-model="filterEndpoint" class="filter-select">
            <option value="">全部接口</option>
            <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
          </select>
          <button @click="handleSearch" class="btn btn-primary btn-sm">搜索</button>
          <button @click="resetFilter" class="btn btn-sm">重置</button>
        </div>

        <!-- 中部：当前目录下用例列表（简化版） -->
        <div class="case-layout">
          <div class="table-container card case-list-panel">
            <div class="case-list-header">
              <div class="case-list-title">
                <strong>用例列表</strong>
              </div>
              <div class="case-list-actions">
                <button @click="loadCases(1)" class="btn btn-sm">↻ 刷新</button>
                <button @click="openBatchMoveDialog" :disabled="!selectedIds.length" class="btn btn-sm btn-batch-move">📁 批量移动 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}</button>
                <button @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-sm btn-danger">
                  🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
                </button>
              </div>
            </div>
            <table class="table">
              <thead>
                <tr>
                  <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
                  <th style="width:80px">ID</th>
                  <th>用例名称</th>
                  <th style="width:160px">所属接口</th>
                  <th style="width:110px">更新人</th>
                  <th style="width:150px">创建时间</th>
                  <th style="width:150px">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in displayedCases" :key="item.id" @click="previewCase(item)" :class="{ 'row-active': previewCaseId === item.id }">
                  <td><input type="checkbox" :value="item.id" v-model="selectedIds" @click.stop /></td>
                  <td class="cell-sm">{{ item.id }}</td>
                  <td class="cell-md" :title="item.name">
                    <a @click.prevent.stop="viewDetail(item.id)" class="link-text">{{ item.name }}</a>
                  </td>
                  <td class="cell-md" :title="item.endpoint?.name || ''">
                    <a
                      v-if="item.endpoint?.id"
                      @click.prevent.stop="viewEndpointDetail(item.endpoint.id)"
                      class="link-text"
                    >
                      {{ item.endpoint?.name || '-' }}
                    </a>
                    <span v-else>{{ item.endpoint?.name || '-' }}</span>
                  </td>
                  <td class="cell-sm">
                    <span class="creator-badge">{{ item.created_by_name || '-' }}</span>
                  </td>
                  <td class="cell-md">{{ formatDate(item.created_at) }}</td>
                  <td>
                    <div class="case-row-actions">
                      <button @click.stop="previewCase(item)" class="btn-action btn-info">预览</button>
                      <button @click.stop="viewDetail(item.id)" class="btn-action btn-info" title="在新页面中打开">打开</button>
                      <button @click.stop="deleteCaseItem(item.id)" class="btn-action btn-danger">删除</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="!displayedCases.length" class="empty-state">
              当前目录下暂无用例
            </div>
            <div class="case-list-footer" v-if="displayedCases.length">
              <div class="case-list-count">
                共 {{ displayedCases.length }} 条
              </div>
            </div>
            <div v-if="pagination.pageCount > 1" class="pagination">
              <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
              <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
              <button v-for="p in pagination.pageCount" :key="p" class="page-btn" :class="{ active: p === pagination.page }" @click="changePage(p)">{{ p }}</button>
              <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
            </div>
          </div>

          <!-- 底部 / 侧边：用例预览详情 -->
          <div class="card case-preview-panel" v-if="previewCaseData">
            <div class="case-preview-header">
              <div>
                <div class="case-preview-title">
                  <span class="case-id">#{{ previewCaseData.id }}</span>
                  <span class="case-name" :title="previewCaseData.name">{{ previewCaseData.name }}</span>
                </div>
                <div class="case-preview-sub">
                  <span>接口：{{ previewCaseData.endpoint?.name || '-' }}</span>
                  <span v-if="previewCaseData.product_line_name">｜产品线：{{ previewCaseData.product_line_name }}</span>
                  <span v-if="previewCaseData.project_name">｜项目：{{ previewCaseData.project_name }}</span>
                </div>
              </div>
              <div class="case-preview-actions">
                <button class="btn btn-sm" @click="viewDetail(previewCaseData.id)">在新页面打开</button>
              </div>
            </div>

            <div class="case-preview-body">
              <div class="case-preview-meta">
                <div><span class="meta-label">创建时间</span><span class="meta-value">{{ formatDate(previewCaseData.created_at) }}</span></div>
                <div><span class="meta-label">最近更新</span><span class="meta-value">{{ formatDate(previewCaseData.updated_at) }}</span></div>
                <div><span class="meta-label">创建人</span><span class="meta-value">{{ previewCaseData.created_by_name || '-' }}</span></div>
              </div>

              <div v-if="previewCaseData.alluer" class="case-preview-section">
                <div class="section-title">Allure 标注</div>
                <pre class="section-code">{{ JSON.stringify(previewCaseData.alluer, null, 2) }}</pre>
              </div>

              <div v-if="previewCaseData.validate" class="case-preview-section">
                <div class="section-title">断言规则（预览）</div>
                <pre class="section-code">{{ JSON.stringify(previewCaseData.validate, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="moveDialogVisible" class="modal" @click.self="moveDialogVisible = false">
      <div class="modal-content" style="max-width:460px">
        <h3>移动到</h3>
        <div class="form-group">
          <label>选择目标文件夹</label>
          <select v-model="moveTargetFolderId">
            <option v-for="f in folderOptions" :key="f.id" :value="f.id">{{ ' '.repeat(f.level * 2) }}{{ f.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="moveDialogVisible = false">取消</button>
          <button class="btn btn-primary" @click="confirmMoveNode">确认移动</button>
        </div>
      </div>
    </div>

    <div v-if="batchMoveDialogVisible" class="modal" @click.self="batchMoveDialogVisible = false">
      <div class="modal-content" style="max-width:460px">
        <h3>批量移动用例</h3>
        <div class="form-group">
          <label>选择目标文件夹</label>
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

    <!-- 创建/编辑对话框 -->
    <div v-if="showCreateDialog" class="modal" @click.self="closeDialog">
      <div class="modal-content modal-tab">
        <div class="modal-header">
          <h3>{{ editingItem ? '编辑用例' : '新建用例' }}</h3>
          <button type="button" @click="closeDialog" class="btn-close">✕</button>
        </div>

        <!-- Tab 导航 -->
        <div class="tab-nav">
          <button v-for="tab in tabs" :key="tab.key"
            class="tab-btn" :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key">{{ tab.label }}</button>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="tab-content">
            <!-- Tab 1: 基本信息 -->
            <div v-show="activeTab === 'basic'">
              <div class="form-group">
                <label>用例名称 *</label>
                <input v-model="formData.name" required placeholder="用例名称" />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>所属接口</label>
                  <select v-model="formData.endpoint">
                    <option :value="null">请选择接口</option>
                    <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label>Allure 标注 <span class="field-hint">(JSON 格式，可选)</span></label>
                <textarea v-model="formData.alluer" rows="4" placeholder='{"feature": "用户模块", "story": "登录"}'></textarea>
              </div>
            </div>

            <!-- Tab 2: 接口参数 -->
            <div v-show="activeTab === 'params'">
              <div class="form-group">
                <div class="param-type-row">
                  <label>接口参数</label>
                  <div class="param-type-tabs">
                    <button type="button" :class="['param-type-btn', formData.paramType==='json'?'active':'']"
                      @click="formData.paramType='json'">JSON Body</button>
                    <button type="button" :class="['param-type-btn', formData.paramType==='form'?'active':'']"
                      @click="formData.paramType='form'">Form Data</button>
                    <button type="button" :class="['param-type-btn', formData.paramType==='query'?'active':'']"
                      @click="formData.paramType='query'">Query Params</button>
                    <button type="button" :class="['param-type-btn', formData.paramType==='raw'?'active':'']"
                      @click="formData.paramType='raw'">原始 JSON</button>
                  </div>
                </div>
                <div v-if="formData.paramType==='json'">
                  <div class="kv-editor">
                    <div class="kv-header"><span>Key</span><span>Value</span><span></span></div>
                    <div v-for="(row,idx) in formData.jsonRows" :key="idx" class="kv-row">
                      <input v-model="row.k" placeholder="key" class="kv-input" />
                      <input v-model="row.v" placeholder="value" class="kv-input" />
                      <button type="button" class="btn-remove-rule" @click="formData.jsonRows.splice(idx,1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-rule" @click="formData.jsonRows.push({k:'',v:''})">+ 添加字段</button>
                </div>
                <div v-else-if="formData.paramType==='form'">
                  <div class="kv-editor">
                    <div class="kv-header"><span>Key</span><span>Value</span><span></span></div>
                    <div v-for="(row,idx) in formData.formRows" :key="idx" class="kv-row">
                      <input v-model="row.k" placeholder="key" class="kv-input" />
                      <input v-model="row.v" placeholder="value" class="kv-input" />
                      <button type="button" class="btn-remove-rule" @click="formData.formRows.splice(idx,1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-rule" @click="formData.formRows.push({k:'',v:''})">+ 添加字段</button>
                </div>
                <div v-else-if="formData.paramType==='query'">
                  <div class="kv-editor">
                    <div class="kv-header"><span>Key</span><span>Value</span><span></span></div>
                    <div v-for="(row,idx) in formData.queryRows" :key="idx" class="kv-row">
                      <input v-model="row.k" placeholder="key" class="kv-input" />
                      <input v-model="row.v" placeholder="value" class="kv-input" />
                      <button type="button" class="btn-remove-rule" @click="formData.queryRows.splice(idx,1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-rule" @click="formData.queryRows.push({k:'',v:''})">+ 添加字段</button>
                </div>
                <div v-else>
                  <textarea v-model="formData.api_args" rows="7" placeholder='{"json":{"key":"value"}}'></textarea>
                </div>

                <div class="param-hint" style="margin-top:10px">请求头（headers），值可用 <code>${变量名}</code></div>
                <div class="kv-editor">
                  <div class="kv-header"><span>Header 名</span><span>Header 值</span><span></span></div>
                  <div v-for="(row,idx) in formData.headerRows" :key="`h-${idx}`" class="kv-row">
                    <input v-model="row.k" placeholder="Authorization" class="kv-input" />
                    <input v-model="row.v" placeholder="Bearer ${token}" class="kv-input" />
                    <button type="button" class="btn-remove-rule" @click="formData.headerRows.splice(idx,1)">✕</button>
                  </div>
                </div>
                <button type="button" class="btn-add-rule" @click="formData.headerRows.push({k:'',v:''})">+ 添加请求头</button>
              </div>
            </div>

            <!-- Tab 3: 数据提取 -->
            <div v-show="activeTab === 'extract'">
              <div class="extract-tip">
                接口响应后按 JSONPath 提取值，存为变量。后续用例在参数/请求头中使用 <code>${变量名}</code> 引用。
              </div>
              <div class="extract-label-row">
                <span class="extract-count">共 {{ editExtractRules.length }} 条规则</span>
                <button type="button" class="btn-add-rule" @click="addExtractRule">+ 添加规则</button>
              </div>
              <div v-if="editExtractRules.length" class="extract-editor">
                <div class="extract-editor-header">
                  <span>变量名</span><span>JSONPath 表达式</span><span class="col-index">取第几个</span><span></span>
                </div>
                <div v-for="(rule, idx) in editExtractRules" :key="idx" class="extract-editor-row">
                  <input v-model="rule.name" placeholder="token" class="rule-input" />
                  <input v-model="rule.expr" placeholder="$.data.token" class="rule-input" />
                  <input v-model.number="rule.index" type="number" min="0" placeholder="0" class="rule-input rule-index" />
                  <button type="button" class="btn-remove-rule" @click="removeExtractRule(idx)">✕</button>
                </div>
              </div>
              <div v-else class="empty-hint" style="padding:20px 0">暂无提取规则，点击「+ 添加规则」新增</div>
            </div>

            <!-- Tab 4: 断言 -->
            <div v-show="activeTab === 'validate'">
              <div class="assert-tip">按顺序执行所有断言规则，支持状态码、JSONPath、响应文本等来源。</div>
              <div class="assert-label-row">
                <span class="assert-count">共 {{ editAssertRules.length }} 条规则</span>
                <div class="assert-add-btns">
                  <button type="button" class="btn-add-assert" @click="addAssertRule('status_code')">+ 状态码</button>
                  <button type="button" class="btn-add-assert" @click="addAssertRule('jsonpath')">+ JSONPath</button>
                  <button type="button" class="btn-add-assert" @click="addAssertRule('text')">+ 响应文本</button>
                </div>
              </div>
              <div v-if="editAssertRules.length" class="assert-editor">
                <div v-for="(rule, idx) in editAssertRules" :key="idx" class="assert-rule-row">
                  <span class="assert-idx">{{ idx + 1 }}</span>
                  <input v-model="rule.name" placeholder="断言描述" class="assert-input assert-name" />
                  <select v-model="rule.type" class="assert-select assert-type">
                    <option value="eq">等于 (eq)</option>
                    <option value="not_eq">不等于 (not_eq)</option>
                    <option value="contains">包含 (contains)</option>
                    <option value="not_contains">不包含 (not_contains)</option>
                    <option value="exists">存在 (exists)</option>
                    <option value="regex">正则匹配 (regex)</option>
                  </select>
                  <select v-model="rule.source" class="assert-select assert-source">
                    <option value="status_code">状态码</option>
                    <option value="jsonpath">JSONPath</option>
                    <option value="text">响应文本</option>
                  </select>
                  <input v-if="rule.source !== 'status_code'" v-model="rule.expr"
                    :placeholder="rule.source === 'jsonpath' ? '$.data.code' : '正则表达式'"
                    class="assert-input assert-expr" />
                  <span v-else class="assert-expr-placeholder">HTTP 状态码</span>
                  <input v-if="rule.type !== 'exists'" v-model="rule.expect" placeholder="期望值" class="assert-input assert-expect" />
                  <span v-else class="assert-expr-placeholder assert-exists-hint">值存在且非空即通过</span>
                  <button type="button" class="btn-remove-rule" @click="editAssertRules.splice(idx,1)">✕</button>
                </div>
              </div>
              <div v-else class="empty-hint" style="padding:20px 0">暂无断言规则，点击上方按钮添加</div>
              <div v-if="editAssertRules.length" class="assert-preview">
                <span class="assert-preview-label">JSON 预览</span>
                <pre class="assert-preview-code">{{ JSON.stringify(buildAssertList(), null, 2) }}</pre>
              </div>
            </div>

            <!-- Tab 5: 用例脚本 -->
            <div v-show="activeTab === 'script'">
              <div class="script-tip">可在执行前后运行 Python 脚本，支持 <code>ctx</code> 上下文变量。内置 helper：<code>now_ts()</code> <code>now_str()</code> <code>rand_int()</code> <code>rand_str()</code> <code>uuid4()</code> <code>md5()</code> <code>sha256()</code> <code>b64_encode()</code>。</div>
              <div class="form-group">
                <label><span class="script-badge pre">PRE</span> 前置脚本</label>
                <textarea v-model="formData.pre_script" rows="8" class="script-editor" placeholder="# 请求前执行\nctx['ts'] = now_ts()\nctx['nonce'] = rand_str(10)\nctx['sign'] = md5(ctx['ts'] + ctx['nonce'])"></textarea>
              </div>
              <div class="form-group">
                <label><span class="script-badge post">POST</span> 后置脚本</label>
                <textarea v-model="formData.post_script" rows="8" class="script-editor" placeholder="# 请求后执行\nif response_json:\n    ctx['uid'] = response_json.get('id')\nctx['done_at'] = now_str('%Y-%m-%d %H:%M:%S')"></textarea>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getCases, createCase, updateCase, deleteCase, getEndpoints, getCaseTree, createCaseFolder, attachCaseToFolder, moveCaseNode, renameCaseNode, deleteCaseNode } from '@/api/case'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const router = useRouter()
const cases = ref([])
const endpoints = ref([])
const showCreateDialog = ref(false)
const caseTree = ref(null)
const selectedFolderId = ref(null)
const selectedNodeId = ref(null)
const previewCaseId = ref(null)
const editingItem = ref(null)
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const activeTab = ref('basic')

const searchText = ref('')
const filterEndpoint = ref('')

const tabs = [
  { key: 'basic',    label: '基本信息' },
  { key: 'params',   label: '接口参数' },
  { key: 'extract',  label: '数据提取' },
  { key: 'validate', label: '断言规则' },
  { key: 'script',   label: '用例脚本' },
]

const expandedFolders = ref(new Set())
const moveDialogVisible = ref(false)
const moveTargetFolderId = ref(null)
const batchMoveDialogVisible = ref(false)
const batchMoveTargetFolderId = ref(null)
const draggingNodeId = ref(null)
const contextMenuVisible = ref(false)
const contextMenuRef = ref(null)
const folderDialogVisible = ref(false)
const folderDialogMode = ref('create')
const folderDialogTitle = ref('')
const folderDialogValue = ref('')
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextNode = ref(null)
const contextTargetFolderId = ref(null)
const treeBodyRef = ref(null)
const isSameId = (a, b) => String(a) === String(b)

const findTreeNodeById = (node, id) => {
  if (!node) return null
  if (isSameId(node.id, id)) return node
  for (const child of (node.children || [])) {
    const found = findTreeNodeById(child, id)
    if (found) return found
  }
  return null
}

const ensureNodeVisibleInTree = (parentId, nodeData) => {
  if (!caseTree.value || !nodeData?.id) return
  const effectiveParentId = hasNodeId(parentId) ? parentId : caseTree.value.id
  if (!hasNodeId(effectiveParentId)) return

  const parent = findTreeNodeById(caseTree.value, effectiveParentId)
  if (!parent) return

  if (!Array.isArray(parent.children)) parent.children = []
  if (!parent.children.some(c => isSameId(c.id, nodeData.id))) {
    parent.children = [{ ...nodeData, children: nodeData.children || [] }, ...parent.children]
    caseTree.value = { ...caseTree.value }
  }

  expandedFolders.value = new Set([...expandedFolders.value, effectiveParentId])
}

const expandByPath = (path) => {
  if (!path) return
  const ids = String(path).split('/').filter(Boolean)
  const s = new Set(expandedFolders.value)
  ids.forEach(id => s.add(id))
  expandedFolders.value = s
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const expandAllFoldersInTree = () => {
  const ids = []
  const walk = (node) => {
    if (!node) return
    if (isFolderNode(node)) ids.push(node.id)
    ;(node.children || []).forEach(walk)
  }
  walk(caseTree.value)
  expandedFolders.value = new Set([...expandedFolders.value, ...ids])
}

const scrollTreeToNode = async (nodeId) => {
  if (!hasNodeId(nodeId)) return
  await nextTick()
  const bodyEl = treeBodyRef.value
  if (!bodyEl) return
  const row = bodyEl.querySelector('.tree-row.active')
  if (row) row.scrollIntoView({ block: 'nearest' })
}

const displayedCases = computed(() => {
  if (!selectedFolderId.value || !caseTree.value) return cases.value

  const findNode = (node, id) => {
    if (!node) return null
    if (isSameId(node.id, id)) return node
    for (const child of (node.children || [])) {
      const found = findNode(child, id)
      if (found) return found
    }
    return null
  }

  const collectCaseIds = (node, set) => {
    if (!node) return
    if (node.node_type === 'case' && node.item?.id) set.add(node.item.id)
    ;(node.children || []).forEach(child => collectCaseIds(child, set))
  }

  const node = findNode(caseTree.value, selectedFolderId.value)
  if (!node) return cases.value

  const ids = new Set()
  collectCaseIds(node, ids)
  return cases.value.filter(c => ids.has(c.id))
})

const selectedFolderName = computed(() => {
  if (!caseTree.value) return '全部'
  const findNode = (node, id) => {
    if (!node) return null
    if (isSameId(node.id, id)) return node
    for (const child of (node.children || [])) {
      const found = findNode(child, id)
      if (found) return found
    }
    return null
  }
  const node = selectedFolderId.value ? findNode(caseTree.value, selectedFolderId.value) : caseTree.value
  return displayTreeNodeName(node)
})

const selectedFolderPath = computed(() => {
  if (!caseTree.value) return '全部'
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
  const targetId = selectedFolderId.value || caseTree.value.id
  if (!walk(caseTree.value, targetId)) return '全部'
  return names.join(' / ')
})

const TREE_STATE_KEY = 'tesla_case_tree_state'

const saveTreeState = () => {
  try {
    const expandedIds = Array.from(expandedFolders.value || []).map(String)
    const payload = {
      expandedIds,
      selectedFolderId: selectedFolderId.value != null ? String(selectedFolderId.value) : null,
    }
    localStorage.setItem(TREE_STATE_KEY, JSON.stringify(payload))
  } catch (e) {
    // 忽略本地存储错误
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
    // 忽略解析错误
  }
}

const flatTreeNodes = computed(() => {
  const res = []
  const walk = (node, level = 0) => {
    if (!node) return
    res.push({ ...node, level })
    ;(node.children || []).forEach(c => walk(c, level + 1))
  }
  walk(caseTree.value, 0)
  return res
})

const folderOptions = computed(() => flatTreeNodes.value.filter(n => isFolderNode(n)))

const visibleTreeNodes = computed(() => {
  const list = []
  const walk = (node, level = 0) => {
    if (!node) return
    list.push({ ...node, level })
    if (isFolderNode(node) && isExpanded(node.id)) {
      ;(node.children || []).forEach(c => walk(c, level + 1))
    }
  }
  walk(caseTree.value, 0)
  return list
})

const hasNodeId = (v) => v !== null && v !== undefined && v !== ''

const canMoveContextNode = computed(() => hasNodeId(contextNode.value?.id) && hasNodeId(contextNode.value?.parent))
const moveDisabledReason = computed(() => canMoveContextNode.value ? '' : '根目录不支持移动')

// 仅当节点下没有子节点时允许删除
const canDeleteContextNode = computed(() => {
  const node = contextNode.value
  if (!node || !hasNodeId(node.id)) return false
  return !Array.isArray(node.children) || node.children.length === 0
})

const canOperateFolder = (node) => {
  if (!node) return false
  if (node.node_type === 'folder') return true
  // 兼容根节点类型为 root / suite_root / case_root 的场景
  if (typeof node.node_type === 'string' && node.node_type.includes('root')) return true
  // 兜底：有 children 且不是 case 节点，也视作目录节点
  if (node.node_type !== 'case' && Array.isArray(node.children)) return true
  return false
}

const isFolderNode = (node) => canOperateFolder(node)

const displayTreeNodeName = (node) => node?.name?.trim() || '无名称'

const isExpanded = (id) => Array.from(expandedFolders.value).some(v => isSameId(v, id))
const toggleFolder = (node) => {
  if (!isFolderNode(node)) return
  const s = new Set(expandedFolders.value)
  const existed = Array.from(s).find(v => isSameId(v, node.id))
  if (existed !== undefined) s.delete(existed)
  else s.add(node.id)
  expandedFolders.value = s
}

const selectNode = (node) => {
  selectedNodeId.value = node.id
  if (isFolderNode(node)) selectedFolderId.value = node.id
  else if (node.node_type === 'case' && node.item?.id) viewDetail(node.item.id)
}

const onDragStart = (node, event) => {
  draggingNodeId.value = node.id
  event.dataTransfer.effectAllowed = 'move'
}

const onDragOverNode = (node, event) => {
  if (!isFolderNode(node)) return
  event.dataTransfer.dropEffect = 'move'
}

const onDropOnNode = async (node) => {
  if (!isFolderNode(node)) return
  if (!draggingNodeId.value || draggingNodeId.value === node.id) return
  await moveCaseNode({ node_id: draggingNodeId.value, target_parent_id: node.id })
  draggingNodeId.value = null
  await loadCaseTree()
}

const loadCaseTree = async () => {
  const res = await getCaseTree()
  const prev = new Set(expandedFolders.value)
  const rawTree = res.result || res
  const sortTreeByRule = (node) => {
    if (!node) return null
    const children = Array.isArray(node.children) ? node.children.map(sortTreeByRule) : []
    const folders = children
      .filter(c => c?.node_type === 'folder')
      .sort((a, b) => Number(a?.id || 0) - Number(b?.id || 0))
    const cases = children
      .filter(c => c?.node_type !== 'folder')
      .sort((a, b) => Number(b?.id || 0) - Number(a?.id || 0))
    return { ...node, children: [...folders, ...cases] }
  }
  caseTree.value = sortTreeByRule(rawTree)
  if (caseTree.value && !selectedFolderId.value) selectedFolderId.value = caseTree.value.id
  if (caseTree.value) {
    prev.add(caseTree.value.id)
    expandedFolders.value = prev
  }
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

const openContextMenu = async (node, event) => {
  event.preventDefault()
  event.stopPropagation()

  contextNode.value = node || null
  contextTargetFolderId.value = hasNodeId(node?.id) ? node.id : null

  if (hasNodeId(node?.id)) selectedNodeId.value = node.id
  if (canOperateFolder(node) && hasNodeId(node?.id)) selectedFolderId.value = node.id

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

const openFolderDialog = (mode, title, defaultValue = '') => {
  closeContextMenu()
  if (!hasNodeId(contextTargetFolderId.value) && hasNodeId(contextNode.value?.id)) {
    contextTargetFolderId.value = contextNode.value.id
  }
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
        : (hasNodeId(caseTree.value?.id) ? caseTree.value.id : null)))

  if (hasNodeId(id)) return id

  await loadCaseTree()

  id = hasNodeId(contextTargetFolderId.value)
    ? contextTargetFolderId.value
    : (hasNodeId(contextNode.value?.id)
      ? contextNode.value.id
      : (hasNodeId(selectedFolderId.value)
        ? selectedFolderId.value
        : (hasNodeId(caseTree.value?.id) ? caseTree.value.id : null)))

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
      let parentId = await resolveCurrentFolderId()
      if (!hasNodeId(parentId)) {
        const rootRes = await getCaseTree()
        const root = rootRes?.result || rootRes
        parentId = root?.id
      }

      const payload = hasNodeId(parentId) ? { name, parent_id: parentId } : { name }
      const res = await createCaseFolder(payload)
      const newNode = res.result || res
      if (hasNodeId(parentId)) {
        expandedFolders.value = new Set([...expandedFolders.value, parentId])
      }

      ensureNodeVisibleInTree(parentId, newNode)
      closeContextMenu()
      closeFolderDialog()

      if (newNode?.id) {
        selectedNodeId.value = newNode.id
        selectedFolderId.value = hasNodeId(parentId) ? parentId : (caseTree.value?.id ?? selectedFolderId.value)
      }

      // 后端目录树写入有轻微延迟：短轮询 3 次，确保新节点回显
      for (let i = 0; i < 3; i += 1) {
        await sleep(180)
        await loadCaseTree()
        const found = !!(newNode?.id && findTreeNodeById(caseTree.value, newNode.id))
        if (found) break
      }

      if (newNode?.path) expandByPath(newNode.path)
      if (hasNodeId(parentId)) expandedFolders.value = new Set([...expandedFolders.value, parentId])

      if (newNode?.id && !findTreeNodeById(caseTree.value, newNode.id)) {
        ensureNodeVisibleInTree(parentId, newNode)
      }

      expandAllFoldersInTree()
      await scrollTreeToNode(newNode?.id)
      return
    }

    if (folderDialogMode.value === 'rename') {
      const nodeId = contextNode.value?.id || caseTree.value?.id
      if (!nodeId) return
      await renameCaseNode({ node_id: nodeId, name })
      closeContextMenu()
      closeFolderDialog()
      await loadCaseTree()
      return
    }
  } catch (e) {
    alert((folderDialogMode.value === 'rename' ? '重命名失败：' : '新建子文件夹失败：') + (e.response?.data?.message || e.response?.data?.msg || e.message))
  }
}

const createCaseUnderContext = async () => {
  const folderId = await resolveCurrentFolderId()
  if (!folderId) {
    alert('未找到目标目录')
    return
  }
  selectedFolderId.value = folderId
  closeContextMenu()
  showCreateDialog.value = true
}

const renameContextNode = async () => {
  const nodeId = await resolveCurrentFolderId()
  if (!nodeId) return
  const currentName = contextNode.value?.name || caseTree.value?.name || '根目录'
  openFolderDialog('rename', '重命名目录', currentName)
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
    await deleteCaseNode(node.id)
    closeContextMenu()
    await loadCaseTree()
  } catch (e) {
    const msg = e.response?.data?.message || e.response?.data?.msg || e.message || String(e)
    alert('删除节点失败：' + msg)
  }
}

const openBatchMoveDialog = () => {
  if (!selectedIds.value.length) return
  batchMoveTargetFolderId.value = selectedFolderId.value || caseTree.value?.id || null
  batchMoveDialogVisible.value = true
}

const confirmBatchMove = async () => {
  if (!batchMoveTargetFolderId.value || !selectedIds.value.length) return
  const total = selectedIds.value.length
  const failed = []
  for (const caseId of selectedIds.value) {
    try {
      await attachCaseToFolder({ case_id: caseId, parent_id: batchMoveTargetFolderId.value })
    } catch (e) {
      failed.push(caseId)
    }
  }
  batchMoveDialogVisible.value = false
  selectedIds.value = []
  await Promise.all([loadCases(pagination.value.page || 1), loadCaseTree()])
  if (failed.length) {
    alert(`已移动 ${total - failed.length}/${total} 条，失败 ID：${failed.join(', ')}`)
  }
}

const confirmMoveNode = async () => {
  if (!moveTargetFolderId.value || !selectedNodeId.value) return
  await moveCaseNode({ node_id: selectedNodeId.value, target_parent_id: moveTargetFolderId.value })
  moveDialogVisible.value = false
  await loadCaseTree()
}

const loadCases = async (page = 1) => {
  try {
    const params = { page: 1, page_size: 500 }
    if (searchText.value)    params.search   = searchText.value
    if (filterEndpoint.value) params.endpoint = filterEndpoint.value
    const res = await getCases(params)
    cases.value = res.result?.list || []
    pagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (error) { console.error('加载用例列表失败:', error) }
}

const handleSearch = () => loadCases(1)
const resetFilter = () => { searchText.value = ''; filterEndpoint.value = ''; loadCases(1) }

const changePage = (page) => { selectedIds.value = []; loadCases(page) }

const selectedIds = ref([])
const allSelected = computed(() => displayedCases.value.length > 0 && displayedCases.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? displayedCases.value.map(i => i.id) : [] }
const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条数据吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteCase(id)))
    cases.value = cases.value.filter(i => !selectedIds.value.includes(i.id))
    selectedIds.value = []
  } catch (error) { console.error('批量删除失败:', error) }
}

const formData = ref({
  name: '', endpoint: null,
  alluer: '', api_args: '', validate: '',
  pre_script: '', post_script: '',
  paramType: 'json',
  jsonRows:  [],
  formRows:  [],
  queryRows: [],
  headerRows: []
})

// 把 kv 行数组转成 {k:v} 对象，过滤空行
const rowsToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.k.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}

// 把 {k:v} 对象还原成行数组
const objToRows = (obj) =>
  obj ? Object.entries(obj).map(([k, v]) => ({ k, v: String(v) })) : []

// 根据 paramType 和 kv 行构建 api_args
const buildApiArgs = () => {
  if (formData.value.paramType === 'raw') {
    return formData.value.api_args ? JSON.parse(formData.value.api_args) : null
  }
  const obj = {}
  if (formData.value.paramType === 'json') {
    const d = rowsToObj(formData.value.jsonRows)
    if (d) obj.json = d
  } else if (formData.value.paramType === 'form') {
    const d = rowsToObj(formData.value.formRows)
    if (d) obj.data = d
  } else if (formData.value.paramType === 'query') {
    const d = rowsToObj(formData.value.queryRows)
    if (d) obj.params = d
  }
  const headers = rowsToObj(formData.value.headerRows)
  if (headers) obj.headers = headers
  return Object.keys(obj).length ? obj : null
}

// 从已有 api_args 反推 paramType 和行数据
const parseApiArgs = (api_args) => {
  if (!api_args) return { paramType: 'json', jsonRows: [], formRows: [], queryRows: [], headerRows: [], api_args: '' }
  const headers = objToRows(api_args.headers)
  if (api_args.json)   return { paramType: 'json',  jsonRows: objToRows(api_args.json),   formRows: [], queryRows: [], headerRows: headers, api_args: '' }
  if (api_args.data)   return { paramType: 'form',  formRows: objToRows(api_args.data),   jsonRows: [], queryRows: [], headerRows: headers, api_args: '' }
  if (api_args.params) return { paramType: 'query', queryRows: objToRows(api_args.params), jsonRows: [], formRows: [], headerRows: headers, api_args: '' }
  // 其他情况用原始模式
  return { paramType: 'raw', api_args: JSON.stringify(api_args, null, 2), jsonRows: [], formRows: [], queryRows: [], headerRows: headers }
}

const editExtractRules = ref([])
const addExtractRule = () => editExtractRules.value.push({ name: '', expr: '', index: 0 })
const removeExtractRule = (idx) => editExtractRules.value.splice(idx, 1)
const buildExtractObj = () => {
  const obj = {}
  for (const r of editExtractRules.value)
    if (r.name.trim()) obj[r.name.trim()] = ['json', r.expr.trim(), r.index ?? 0]
  return Object.keys(obj).length ? obj : null
}

// ---- 断言规则 ----
const editAssertRules = ref([])

const addAssertRule = (source = 'jsonpath') => {
  editAssertRules.value.push({
    name:   '',
    type:   'eq',
    source,
    expr:   '',
    expect: source === 'status_code' ? '200' : '',
  })
}

const buildAssertList = () =>
  editAssertRules.value
    .filter(r => r.name.trim())
    .map(r => {
      const rule = { name: r.name.trim(), type: r.type, source: r.source }
      if (r.source !== 'status_code') rule.expr = r.expr.trim()
      if (r.type !== 'exists') rule.expect = r.expect
      return rule
    })

const parseAssertList = (validate) => {
  if (!validate) return []
  if (Array.isArray(validate)) {
    return validate.map(r => ({
      name:   r.name   || '',
      type:   r.type   || 'eq',
      source: r.source || 'jsonpath',
      expr:   r.expr   || '',
      expect: r.expect != null ? String(r.expect) : '',
    }))
  }
  const rows = []
  for (const [k, v] of Object.entries(validate)) {
    if (k === 'status_code') {
      rows.push({ name: '状态码', type: 'eq', source: 'status_code', expr: '', expect: String(v) })
      continue
    }
    if (typeof v === 'object' && v !== null) {
      for (const [desc, item] of Object.entries(v)) {
        const expected = Array.isArray(item) ? item[0] : ''
        const target   = Array.isArray(item) ? item[1] : null
        const expr     = Array.isArray(target) && target[1] ? target[1] : ''
        rows.push({ name: desc, type: k === 'equals' ? 'eq' : k, source: 'jsonpath', expr, expect: String(expected) })
      }
    }
  }
  return rows
}

const loadEndpoints = async () => {
  try {
    const params = { page_size: 100 }
    const res = await getEndpoints(params)
    endpoints.value = res.result?.list || []
  } catch (error) { console.error('加载接口列表失败:', error) }
}

const viewDetail = (id) => router.push(`/cases/${id}`)
const viewEndpointDetail = (id) => router.push(`/endpoints/${id}`)

const editCase = (item) => {
  editingItem.value = item
  activeTab.value = 'basic'
  const parsed = parseApiArgs(item.api_args)
  formData.value = {
    name:      item.name,
    endpoint:  item.endpoint?.id || item.endpoint,
    alluer:    item.alluer   ? JSON.stringify(item.alluer,   null, 2) : '',
    validate:  item.validate ? JSON.stringify(item.validate, null, 2) : '',
    pre_script: item.pre_script || '',
    post_script: item.post_script || '',
    ...parsed
  }
  editExtractRules.value = item.extract
    ? Object.entries(item.extract).map(([name, rule]) =>
        Array.isArray(rule) ? { name, expr: rule[1]??'', index: rule[2]??0 } : { name, expr: String(rule), index: 0 }
      )
    : []
  editAssertRules.value = parseAssertList(item.validate)
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  try {
    let api_args = buildApiArgs()
    const data = {
      name:     formData.value.name,
      endpoint: formData.value.endpoint,
      parent_node_id: selectedFolderId.value || caseTree.value?.id,
      project:  null,
      product_line: null,
      alluer:   formData.value.alluer   ? JSON.parse(formData.value.alluer)   : null,
      api_args,
      extract:  buildExtractObj(),
      validate: buildAssertList().length ? buildAssertList() : null,
      pre_script: formData.value.pre_script || '',
      post_script: formData.value.post_script || '',
    }
    if (editingItem.value) {
      await updateCase(editingItem.value.id, data)
      await attachCaseToFolder({ case_id: editingItem.value.id, parent_id: selectedFolderId.value || caseTree.value?.id })
    } else {
      await createCase(data)
    }
    closeDialog()
    await Promise.all([loadCases(), loadCaseTree()])
  } catch (error) {
    console.error('操作失败:', error)
    alert('保存失败，请检查JSON格式是否正确')
  }
}

const deleteCaseItem = async (id) => {
  const confirmed = await confirm('确定要删除这个用例吗？', { type: 'danger' })
  if (confirmed) {
    try { await deleteCase(id); cases.value = cases.value.filter(c => c.id !== id) }
    catch (error) { console.error('删除失败:', error) }
  }
}

// ---- 用例预览 ----
const previewCase = (item) => {
  if (!item) return
  previewCaseId.value = item.id
}

const previewCaseData = computed(() => {
  if (!previewCaseId.value) return null
  return cases.value.find(c => c.id === previewCaseId.value) || null
})

const closeDialog = () => {
  showCreateDialog.value = false
  editingItem.value = null
  activeTab.value = 'basic'
  editExtractRules.value = []
  editAssertRules.value = []
  formData.value = {
    name: '', endpoint: null,
    alluer: '', api_args: '',
    pre_script: '', post_script: '',
    paramType: 'json', jsonRows: [], formRows: [], queryRows: [], headerRows: []
  }
}

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

onMounted(() => {
  loadTreeState()
  loadCases()
  loadEndpoints()
  loadCaseTree()
  window.addEventListener('click', onGlobalClick)
  window.addEventListener('keydown', onGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', onGlobalClick)
  window.removeEventListener('keydown', onGlobalKeydown)
})

watch([expandedFolders, selectedFolderId], saveTreeState, { deep: false })
</script>

<style scoped>
.main-layout { display:grid; grid-template-columns: 320px minmax(0,1fr); gap:16px; align-items:start; }
.tree-column { min-width:0; }
.content-column { min-width:0; }
@media (max-width: 1200px) {
  .main-layout { grid-template-columns: 1fr; }
}
.toolbar { margin-bottom: 16px; }
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
.tree-tip { font-size:12px; color:var(--text-light); }
.tree-debug {
  margin-top: 8px;
  margin-bottom: 6px;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px dashed #b7c9e6;
  background: #f7fbff;
  color: #365079;
  font-size: 12px;
  line-height: 1.45;
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
.context-menu button:disabled {
  opacity: .45;
  cursor: not-allowed;
}
.context-menu button:disabled:hover {
  background: transparent;
  color: #2f3c53;
}
.context-menu button:disabled:hover::before {
  color: #6f89b2;
}
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
.tree-row:hover {
  background: #edf4ff;
  color: #174f93;
}
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
.tree-node-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: calc(100% - 18px);
}
.tree-node-icon {
  display: inline-flex;
  width: 16px;
  height: 16px;
  color: #6b7f9f;
  flex: 0 0 16px;
}
.tree-node-icon svg {
  width: 16px;
  height: 16px;
}
.tree-row.active .tree-node-icon {
  color: #2f6eb9;
}
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

/* 用例树滚动条美化 */
.tree-body::-webkit-scrollbar {
  width: 6px;
}
.tree-body::-webkit-scrollbar-track {
  background: transparent;
}
.tree-body::-webkit-scrollbar-thumb {
  background: rgba(127, 151, 189, 0.45);
  border-radius: 999px;
}
.tree-body::-webkit-scrollbar-thumb:hover {
  background: rgba(104, 132, 177, 0.8);
}
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
.table-container { overflow-x: auto; }
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
.btn-action:hover { opacity: 0.9; }
.btn-action.btn-danger { background: var(--danger); }
.btn-action.btn-info { background: #3498db; }
.case-row-actions {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.creator-badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  background: linear-gradient(135deg, #e8f4fd, #d6eaf8);
  color: #1a6fa8; font-size: 12px; font-weight: 600;
  border: 1px solid #aed6f1; letter-spacing: 0.02em;
}
.link-text { color: var(--primary); cursor: pointer; text-decoration: none; font-weight: 500; }
.link-text:hover { text-decoration: underline; }
.empty-state { text-align: center; padding: 48px; color: var(--text-light); }

/* 用例列表整体字体微调，保证统一 */
.case-list-panel table {
  font-size: 13px;
}
.case-list-panel thead th {
  font-size: 12px;
  color: #fff;
  font-weight: 500;
  white-space: nowrap;
}
.case-list-panel tbody td {
  vertical-align: middle;
}

.case-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.case-list-title strong {
  font-size: 14px;
}
.case-list-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.case-list-actions .btn-sm {
  font-size: 12px;
}

.case-list-footer {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

/* ===== Modal ===== */
.modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex;
  align-items: center; justify-content: center; z-index: 1000;
}
.modal-content {
  background: white; border-radius: 12px; width: 90%; max-width: 500px;
  animation: slideUp 0.3s ease; overflow: hidden;
}
.modal-tab { max-width: 680px; }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 0; margin-bottom: 0;
}
.modal-header h3 { font-size: 18px; font-weight: 600; margin: 0; }
.btn-close { border: none; background: none; font-size: 18px; color: var(--text-light); cursor: pointer; padding: 4px 8px; border-radius: 4px; }
.btn-close:hover { background: #f5f5f5; }

/* ===== Tab ===== */
.tab-nav {
  display: flex; border-bottom: 2px solid var(--border);
  padding: 0 16px; gap: 2px; margin-top: 16px; background: #fafafa;
}
.tab-btn {
  padding: 11px 18px; border: none; background: none;
  font-size: 13px; font-weight: 500; color: var(--text-light);
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: color .2s, border-color .2s;
}
.tab-btn:hover { color: var(--primary); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab-content { padding: 20px 24px 8px; max-height: 60vh; overflow-y: auto; }

/* ===== Form ===== */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: var(--text); font-size: 13px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; box-sizing: border-box; }
.field-hint { font-size: 11px; font-weight: 400; color: var(--text-light); margin-left: 6px; }
.field-hint code { background: #fff3e0; color: #e65100; padding: 1px 4px; border-radius: 3px; font-size: 11px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 12px 24px 20px; border-top: 1px solid var(--border); }

/* ===== 数据提取编辑器 ===== */
.extract-tip { background: #f0f8ff; border-left: 3px solid #3498db; padding: 9px 12px; border-radius: 4px; font-size: 12px; color: var(--text-light); margin-bottom: 14px; }
.extract-tip code { background: #fff3e0; color: #e65100; padding: 1px 4px; border-radius: 3px; font-size: 11px; }
.extract-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.extract-count { font-size: 13px; color: var(--text-light); }
.btn-add-rule { font-size: 12px; padding: 5px 14px; border: 1px solid #3498db; color: #3498db; background: white; border-radius: 5px; cursor: pointer; }
.btn-add-rule:hover { background: #e3f2fd; }
.extract-editor { border: 1px solid #d0e8f8; border-radius: 8px; overflow: hidden; }
.extract-editor-header { display: grid; grid-template-columns: 140px 1fr 70px 32px; background: #e3f2fd; font-size: 11px; font-weight: 600; color: #1565c0; padding: 6px 10px; gap: 6px; }
.extract-editor-row { display: grid; grid-template-columns: 140px 1fr 70px 32px; gap: 6px; padding: 7px 10px; border-top: 1px solid #e8f4fd; align-items: center; background: white; }
.extract-editor-row:hover { background: #f8fcff; }
.rule-input { border: 1px solid #d0e8f8; border-radius: 4px; padding: 4px 7px; font-size: 12px; font-family: 'Monaco','Courier New',monospace; outline: none; width: 100%; box-sizing: border-box; }
.rule-input:focus { border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,.12); }
.rule-index { text-align: center; font-family: inherit; }
.col-index { text-align: center; }
.empty-hint { color: var(--text-light); font-size: 13px; }
.btn-remove-rule { border: none; background: none; color: #e74c3c; cursor: pointer; font-size: 14px; padding: 2px 3px; border-radius: 3px; }
.btn-remove-rule:hover { background: #fdecea; }

/* ===== 接口参数类型切换 ===== */
.param-type-row {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;
}
.param-type-tabs { display: flex; gap: 4px; }
.param-type-btn {
  padding: 4px 12px; font-size: 12px; border: 1px solid #d0e8f8;
  background: white; color: var(--text-light); border-radius: 4px; cursor: pointer;
}
.param-type-btn:hover { background: #f0f8ff; color: var(--primary); }
.param-type-btn.active {
  background: var(--primary); color: white; border-color: var(--primary);
}
.param-hint {
  font-size: 12px; color: var(--text-light); margin-bottom: 8px;
}
.param-hint code {
  background: #f0f4ff; color: #3a56c9;
  padding: 1px 5px; border-radius: 3px; font-size: 11px;
}

/* ===== KV 编辑器 ===== */
.kv-editor { border: 1px solid #d0e8f8; border-radius: 8px; overflow: hidden; margin-bottom: 8px; }
.kv-header {
  display: grid; grid-template-columns: 1fr 1fr 32px;
  background: #e3f2fd; font-size: 11px; font-weight: 600;
  color: #1565c0; padding: 6px 10px; gap: 6px;
}
.kv-row {
  display: grid; grid-template-columns: 1fr 1fr 32px;
  gap: 6px; padding: 6px 10px; border-top: 1px solid #e8f4fd;
  align-items: center; background: white;
}
.kv-row:hover { background: #f8fcff; }
.kv-input {
  border: 1px solid #d0e8f8; border-radius: 4px;
  padding: 4px 7px; font-size: 12px;
  font-family: 'Monaco','Courier New',monospace;
  outline: none; width: 100%; box-sizing: border-box;
}
.kv-input:focus { border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,.12); }

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.assert-tip { background: #f0faf4; border-left: 3px solid #27ae60; padding: 10px 14px; border-radius: 4px; font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.assert-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.assert-count { font-size: 13px; color: var(--text-light); }
.assert-add-btns { display: flex; gap: 8px; }
.btn-add-assert { background: none; border: 1px dashed #27ae60; color: #27ae60; border-radius: 5px; padding: 4px 12px; font-size: 12px; cursor: pointer; }
.btn-add-assert:hover { background: #f0faf4; }
.assert-editor { border: 1px solid #d5e8d4; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }
.assert-rule-row { display: grid; grid-template-columns: 28px 160px 130px 110px 1fr 140px 32px; gap: 8px; padding: 8px 12px; border-top: 1px solid #e8f4e8; align-items: center; background: white; }
.assert-rule-row:first-child { border-top: none; }
.assert-rule-row:hover { background: #f6fdf6; }
.assert-idx { text-align: center; font-size: 12px; color: #aaa; font-weight: 600; }
.assert-input { border: 1px solid #d5e8d4; border-radius: 4px; padding: 5px 8px; font-size: 12px; outline: none; width: 100%; box-sizing: border-box; }
.assert-input:focus { border-color: #27ae60; box-shadow: 0 0 0 2px rgba(39,174,96,.12); }
.assert-select { border: 1px solid #d5e8d4; border-radius: 4px; padding: 5px 6px; font-size: 12px; outline: none; width: 100%; box-sizing: border-box; background: white; }
.assert-select:focus { border-color: #27ae60; }
.assert-name { font-family: inherit; }
.assert-expr { font-family: 'Monaco','Courier New',monospace; color: #2e7d32; }
.assert-expect { font-family: 'Monaco','Courier New',monospace; color: #1565c0; }
.assert-expr-placeholder { font-size: 12px; color: #aaa; font-style: italic; padding: 0 4px; }
.assert-exists-hint { font-size: 11px; }
.assert-preview { margin-top: 4px; }
.assert-preview-label { font-size: 11px; font-weight: 600; color: #aaa; text-transform: uppercase; letter-spacing: .05em; display: block; margin-bottom: 6px; }
.assert-preview-code { background: #1a1a2e; color: #a8ff78; padding: 14px 16px; border-radius: 8px; font-family: 'Monaco','Courier New',monospace; font-size: 12px; line-height: 1.6; overflow-x: auto; margin: 0; }

/* 用例脚本 */
.script-tip { background:#fffbeb; border-left:3px solid #f59e0b; padding:10px 14px; border-radius:4px; font-size:12px; color:#92400e; margin-bottom:14px; }
.script-tip code { background:#111827; color:#f9fafb; padding:1px 5px; border-radius:3px; font-size:11px; }
.script-editor { width:100%; box-sizing:border-box; border:1px solid #d1d5db; border-radius:8px; padding:10px 12px; font-family:'Monaco','Courier New',monospace; font-size:12px; line-height:1.7; background:#0b1020; color:#d1fae5; outline:none; }
.script-editor:focus { border-color:#10b981; box-shadow:0 0 0 2px rgba(16,185,129,.12); }
.script-badge { display:inline-block; padding:2px 7px; border-radius:4px; font-size:11px; font-weight:700; margin-right:6px; }
.script-badge.pre { background:#dbeafe; color:#1d4ed8; }
.script-badge.post { background:#d1fae5; color:#065f46; }
</style>
