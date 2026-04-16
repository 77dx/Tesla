<template>
  <div class="case-view">
    <div class="case-view__layout">

      <!-- 左侧：目录树 -->
      <div class="case-view__sidebar">
        <div class="form-card">
          <div class="tree-header">
            <FolderOpenOutlined class="tree-header__icon" />
            <span class="tree-header__title">用例目录</span>
          </div>
          <div class="tree-body" v-if="caseTree" ref="treeBodyRef">
            <div
              v-for="n in visibleTreeNodes"
              :key="n.id"
              class="tree-row"
              :class="{ active: isSameId(n.id, selectedNodeId) }"
              :style="{ paddingLeft: (n.level * 18 + 8) + 'px' }"
              @click="selectNode(n)"
              @contextmenu.prevent="openContextMenu(n, $event)"
              draggable="true"
              @dragstart="onDragStart(n, $event)"
              @dragover.prevent="onDragOverNode(n, $event)"
              @drop.prevent="onDropOnNode(n, $event)"
            >
              <span class="tree-toggle" @click.stop="toggleFolder(n)">
                {{ isFolderNode(n) ? (isExpanded(n.id) ? '▾' : '▸') : '' }}
              </span>
              <span class="tree-node-icon">
                <svg v-if="isFolderNode(n) && isExpanded(n.id)" viewBox="0 0 24 24" fill="none" width="16" height="16">
                  <path d="M3.5 8.5a2 2 0 0 1 2-2h4.1a2 2 0 0 1 1.4.58l.92.92H18.5a2 2 0 0 1 2 2v6.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-8Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
                <svg v-else-if="isFolderNode(n)" viewBox="0 0 24 24" fill="none" width="16" height="16">
                  <path d="M3.5 9a2 2 0 0 1 2-2h4.1a2 2 0 0 1 1.4.58l.92.92H18.5a2 2 0 0 1 2 2v5.5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2V9Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" width="16" height="16">
                  <path d="M7 3.8h6.2L18 8.6V20.2H7V3.8Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                  <path d="M13.2 3.8v4.8H18" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                </svg>
              </span>
              <span class="tree-node-label">
                <span class="tree-node-name" :title="displayTreeNodeName(n)">{{ displayTreeNodeName(n) }}</span>
              </span>
            </div>
          </div>
          <div v-if="contextMenuVisible" ref="contextMenuRef" class="context-menu"
            :style="{ left: `${contextMenuX}px`, top: `${contextMenuY}px` }" @click.stop>
            <button @click.stop.prevent="createFolderUnderContext">
              <FolderAddOutlined /> 新增子文件夹
            </button>
            <button @click.stop.prevent="createCaseUnderContext">
              <PlusCircleOutlined /> 新增用例
            </button>
            <button :disabled="!canMoveContextNode" @click.stop.prevent="moveContextNode">
              <SwapOutlined /> 移动到
            </button>
            <button @click.stop.prevent="renameContextNode">
              <EditOutlined /> 重命名
            </button>
            <button :disabled="!canDeleteContextNode" @click.stop.prevent="deleteContextNode" class="danger">
              <DeleteOutlined /> 删除节点
            </button>
          </div>
        </div>
      </div>

      <!-- 右侧：列表 + 预览 -->
      <div class="case-view__main">

        <!-- 操作按钮区（新增用例+刷新） -->
        <div class="case-toolbar">
          <button class="btn btn--primary btn--sm" @click="goCreate">
            <PlusOutlined /> 新建用例
          </button>
          <button class="btn btn--ghost btn--sm" @click="loadCases(1)" :disabled="loading">
            <ReloadOutlined :class="{ 'spin': loading }" />
          </button>
        </div>

        <!-- 工具栏（筛选区 + 操作按钮） -->
        <div class="filter-bar">
          <div class="filter-bar__left">
            <div class="filter-bar__search">
              <span class="filter-bar__search-icon">🔍</span>
              <input
                v-model="searchText"
                type="text"
                placeholder="搜索用例名称..."
                class="filter-bar__input"
                @keyup.enter="handleSearch"
              />
            </div>
            <div class="filter-bar__filters">
              <div class="filter-item">
                <label class="filter-label">所属接口</label>
                <select v-model="filterEndpoint" class="filter-bar__select" @change="handleSearch">
                  <option value="">全部</option>
                  <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
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
            <div class="toolbar-info">
              共 <strong>{{ displayedCases.length }}</strong> 个用例
            </div>
            <div class="toolbar-actions">
              <button
                v-if="selectedIds.length"
                class="btn btn--ghost btn--sm"
                @click="openBatchMoveDialog"
              >
                <FolderOutlined /> 批量移动 ({{ selectedIds.length }})
              </button>
              <button
                v-if="selectedIds.length"
                class="btn btn--danger-ghost btn--sm"
                @click="batchDelete"
              >
                <DeleteOutlined /> 删除 ({{ selectedIds.length }})
              </button>
            </div>
          </div>

          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:40px">
                    <input type="checkbox" :checked="allSelected" @change="toggleAll" />
                  </th>
                  <th style="width:70px">ID</th>
                  <th>用例名称</th>
                  <th style="width:160px">关联接口</th>
                  <th style="width:120px">创建人</th>
                  <th style="width:160px">创建时间</th>
                  <th style="width:120px">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in displayedCases"
                  :key="item.id"
                  :class="{ 'row-active': previewCaseId === item.id }"
                  @click="previewCase(item)"
                >
                  <td @click.stop>
                    <input type="checkbox" :value="item.id" v-model="selectedIds" />
                  </td>
                  <td class="cell-mono">{{ item.id }}</td>
                  <td class="cell-name">
                    <a @click.prevent.stop="viewDetail(item.id)" class="link-primary">{{ item.name }}</a>
                  </td>
                  <td>
                    <a
                      v-if="item.endpoint?.id"
                      @click.prevent.stop="viewEndpointDetail(item.endpoint.id)"
                      class="link-primary"
                    >
                      {{ item.endpoint?.name || '-' }}
                    </a>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span class="creator-badge">{{ item.created_by_name || '-' }}</span>
                  </td>
                  <td class="cell-mono">{{ formatDate(item.created_at) }}</td>
                  <td @click.stop>
                    <div class="row-actions">
                      <button class="btn-action" @click="viewDetail(item.id)" title="打开">
                        <EyeOutlined />
                      </button>
                      <button class="btn-action" @click="goEdit(item.id)" title="编辑">
                        <EditOutlined />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>

            <div v-if="!displayedCases.length && !loading" class="empty-table">
              <FileProtectOutlined class="empty-table__icon" />
              <p>当前目录下暂无用例</p>
            </div>

            <div v-if="loading" class="loading-table">
              <a-spin size="default" />
            </div>
          </div>
        </div>

        <!-- 用例预览面板 -->
        <div v-if="previewCaseData" class="preview-card">
          <div class="preview-card__header">
            <div class="preview-card__title-group">
              <span class="preview-id">#{{ previewCaseData.id }}</span>
              <span class="preview-name">{{ previewCaseData.name }}</span>
            </div>
            <div class="preview-card__actions">
              <button class="btn btn--primary btn--sm" @click="viewDetail(previewCaseData.id)">
                <ArrowRightOutlined /> 打开详情
              </button>
              <button class="btn btn--ghost btn--sm" @click="previewCaseId = null">
                <CloseOutlined />
              </button>
            </div>
          </div>
          <div class="preview-card__body">
            <div class="preview-meta">
              <div class="preview-meta__item">
                <span class="preview-meta__label">关联接口</span>
                <span class="preview-meta__value">{{ previewCaseData.endpoint?.name || '-' }}</span>
              </div>
              <div class="preview-meta__item" v-if="previewCaseData.product_line_name">
                <span class="preview-meta__label">产品线</span>
                <span class="preview-meta__value">{{ previewCaseData.product_line_name }}</span>
              </div>
              <div class="preview-meta__item">
                <span class="preview-meta__label">创建人</span>
                <span class="preview-meta__value">{{ previewCaseData.created_by_name || '-' }}</span>
              </div>
              <div class="preview-meta__item">
                <span class="preview-meta__label">创建时间</span>
                <span class="preview-meta__value">{{ formatDate(previewCaseData.created_at) }}</span>
              </div>
            </div>
            <div v-if="previewCaseData.alluer" class="preview-section">
              <div class="preview-section__title">Allure 标注</div>
              <pre class="preview-code">{{ JSON.stringify(previewCaseData.alluer, null, 2) }}</pre>
            </div>
            <div v-if="previewCaseData.extract && Object.keys(previewCaseData.extract).length" class="preview-section">
              <div class="preview-section__title">数据提取</div>
              <pre class="preview-code">{{ JSON.stringify(previewCaseData.extract, null, 2) }}</pre>
            </div>
            <div v-if="previewCaseData.validate" class="preview-section">
              <div class="preview-section__title">断言规则</div>
              <pre class="preview-code">{{ JSON.stringify(previewCaseData.validate, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动节点弹窗 -->
    <div v-if="moveDialogVisible" class="modal" @click.self="moveDialogVisible = false">
      <div class="modal-card">
        <div class="modal-card__header">
          <span class="modal-card__title">移动节点</span>
          <button class="modal-close" @click="moveDialogVisible = false"><CloseOutlined /></button>
        </div>
        <div class="modal-card__body">
          <div class="form-group">
            <label class="form-label">选择目标文件夹</label>
            <select v-model="moveTargetFolderId" class="form-select">
              <option v-for="f in folderOptions" :key="f.id" :value="f.id">
                {{ '　'.repeat(f.level) }}{{ f.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="modal-card__footer">
          <button class="btn btn--ghost" @click="moveDialogVisible = false">取消</button>
          <button class="btn btn--primary" @click="confirmMoveNode">确认移动</button>
        </div>
      </div>
    </div>

    <!-- 批量移动弹窗 -->
    <div v-if="batchMoveDialogVisible" class="modal" @click.self="batchMoveDialogVisible = false">
      <div class="modal-card">
        <div class="modal-card__header">
          <span class="modal-card__title">批量移动用例</span>
          <button class="modal-close" @click="batchMoveDialogVisible = false"><CloseOutlined /></button>
        </div>
        <div class="modal-card__body">
          <div class="form-group">
            <label class="form-label">选择目标文件夹</label>
            <select v-model="batchMoveTargetFolderId" class="form-select">
              <option v-for="f in folderOptions" :key="f.id" :value="f.id">
                {{ '　'.repeat(f.level) }}{{ f.name }}
              </option>
            </select>
          </div>
        </div>
        <div class="modal-card__footer">
          <button class="btn btn--ghost" @click="batchMoveDialogVisible = false">取消</button>
          <button class="btn btn--primary" :disabled="!batchMoveTargetFolderId" @click="confirmBatchMove">
            确认移动（{{ selectedIds.length }} 条）
          </button>
        </div>
      </div>
    </div>

    <!-- 文件夹增改名弹窗 -->
    <div v-if="folderDialogVisible" class="modal" @click.self="closeFolderDialog">
      <div class="modal-card">
        <div class="modal-card__header">
          <span class="modal-card__title">{{ folderDialogTitle }}</span>
          <button class="modal-close" @click="closeFolderDialog"><CloseOutlined /></button>
        </div>
        <div class="modal-card__body">
          <div class="form-group">
            <label class="form-label">名称</label>
            <input
              v-model="folderDialogValue"
              class="form-input"
              placeholder="请输入名称"
              @keyup.enter="confirmFolderDialog"
            />
          </div>
        </div>
        <div class="modal-card__footer">
          <button class="btn btn--ghost" @click="closeFolderDialog">取消</button>
          <button class="btn btn--primary" :disabled="!folderDialogValue.trim()" @click="confirmFolderDialog">确定</button>
        </div>
      </div>
    </div>

    <!-- 新建/编辑用例弹窗 -->
    <div v-if="showCreateDialog" class="modal" @click.self="closeDialog">
      <div class="modal-card modal-card--lg">
        <div class="modal-card__header">
          <span class="modal-card__title">{{ editingItem ? '编辑用例' : '新建用例' }}</span>
          <button class="modal-close" @click="closeDialog"><CloseOutlined /></button>
        </div>

        <!-- Tab 导航 -->
        <div class="modal-tabs-nav">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="modal-tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="modal-card__body">
          <!-- 基本信息 -->
          <div v-show="activeTab === 'basic'" class="modal-tab-content">
            <div class="form-row-2">
              <div class="form-group">
                <label class="form-label">用例名称 <span class="required">*</span></label>
                <input v-model="formData.name" class="form-input" required placeholder="用例名称" />
              </div>
              <div class="form-group">
                <label class="form-label">关联接口</label>
                <select v-model="formData.endpoint" class="form-select">
                  <option :value="null">不指定</option>
                  <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Allure 标注 <span class="form-label-hint">(JSON，可选)</span></label>
              <textarea v-model="formData.alluer" class="form-textarea" rows="4"
                placeholder='{"feature": "用户模块", "story": "登录"}'></textarea>
            </div>
          </div>

          <!-- 接口参数 -->
          <div v-show="activeTab === 'params'" class="modal-tab-content">
            <div class="params-type-bar">
              <button type="button"
                v-for="pt in paramTypes"
                :key="pt.key"
                class="params-type-btn"
                :class="{ active: formData.paramType === pt.key }"
                @click="formData.paramType = pt.key"
              >{{ pt.label }}</button>
            </div>

            <div v-if="formData.paramType === 'json'" class="kv-section">
              <div class="kv-tip">application/json，值可用 <code>${变量名}</code></div>
              <div class="kv-table">
                <div class="kv-head"><span>Key</span><span>Value</span><span></span></div>
                <div v-for="(row, idx) in formData.jsonRows" :key="idx" class="kv-row">
                  <input v-model="row.k" class="kv-input" placeholder="key" />
                  <input v-model="row.v" class="kv-input" placeholder="value" />
                  <button type="button" class="kv-del" @click="formData.jsonRows.splice(idx, 1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="formData.jsonRows.push({ k: '', v: '' })">+ 添加字段</button>
            </div>

            <div v-else-if="formData.paramType === 'form'" class="kv-section">
              <div class="kv-tip">application/x-www-form-urlencoded</div>
              <div class="kv-table">
                <div class="kv-head"><span>Key</span><span>Value</span><span></span></div>
                <div v-for="(row, idx) in formData.formRows" :key="idx" class="kv-row">
                  <input v-model="row.k" class="kv-input" placeholder="key" />
                  <input v-model="row.v" class="kv-input" placeholder="value" />
                  <button type="button" class="kv-del" @click="formData.formRows.splice(idx, 1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="formData.formRows.push({ k: '', v: '' })">+ 添加字段</button>
            </div>

            <div v-else-if="formData.paramType === 'query'" class="kv-section">
              <div class="kv-tip">附加到 URL 的查询参数</div>
              <div class="kv-table">
                <div class="kv-head"><span>Key</span><span>Value</span><span></span></div>
                <div v-for="(row, idx) in formData.queryRows" :key="idx" class="kv-row">
                  <input v-model="row.k" class="kv-input" placeholder="key" />
                  <input v-model="row.v" class="kv-input" placeholder="value" />
                  <button type="button" class="kv-del" @click="formData.queryRows.splice(idx, 1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="formData.queryRows.push({ k: '', v: '' })">+ 添加字段</button>
            </div>

            <div v-else class="kv-section">
              <textarea v-model="formData.api_args" class="form-textarea" rows="7"
                placeholder='{"json":{"key":"value"}}'></textarea>
            </div>

            <!-- 请求头 -->
            <div class="kv-section" style="margin-top: 16px">
              <div class="kv-tip">请求头（headers），值可用 <code>${变量名}</code></div>
              <div class="kv-table">
                <div class="kv-head"><span>Header 名</span><span>Header 值</span><span></span></div>
                <div v-for="(row, idx) in formData.headerRows" :key="`h-${idx}`" class="kv-row">
                  <input v-model="row.k" class="kv-input" placeholder="Authorization" />
                  <input v-model="row.v" class="kv-input" placeholder="Bearer ${token}" />
                  <button type="button" class="kv-del" @click="formData.headerRows.splice(idx, 1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="formData.headerRows.push({ k: '', v: '' })">+ 添加请求头</button>
            </div>
          </div>

          <!-- 数据提取 -->
          <div v-show="activeTab === 'extract'" class="modal-tab-content">
            <div class="extract-tip">
              接口响应后按 JSONPath 提取值，存为变量。后续用例在参数中使用 <code>${变量名}</code> 引用。
            </div>
            <div class="extract-toolbar">
              <span class="extract-count">共 {{ editExtractRules.length }} 条规则</span>
              <button type="button" class="btn-add-row" @click="addExtractRule">+ 添加规则</button>
            </div>
            <div v-if="editExtractRules.length" class="extract-table">
              <div class="extract-head"><span>变量名</span><span>JSONPath 表达式</span><span>取第几个</span><span></span></div>
              <div v-for="(rule, idx) in editExtractRules" :key="idx" class="extract-row">
                <input v-model="rule.name" class="kv-input" placeholder="token" />
                <input v-model="rule.expr" class="kv-input" placeholder="$.data.token" />
                <input v-model.number="rule.index" type="number" min="0" class="kv-input kv-input--sm" />
                <button type="button" class="kv-del" @click="removeExtractRule(idx)">✕</button>
              </div>
            </div>
            <div v-else class="empty-tab" style="padding: 24px">暂无提取规则，点击「+ 添加规则」新增</div>
          </div>

          <!-- 断言规则 -->
          <div v-show="activeTab === 'validate'" class="modal-tab-content">
            <div class="assert-tip">按顺序执行所有断言规则，支持状态码、JSONPath、响应文本等来源。</div>
            <div class="assert-toolbar">
              <span class="extract-count">共 {{ editAssertRules.length }} 条规则</span>
              <div class="assert-add-btns">
                <button type="button" class="btn-add-assert" @click="addAssertRule('status_code')">+ 状态码</button>
                <button type="button" class="btn-add-assert" @click="addAssertRule('jsonpath')">+ JSONPath</button>
                <button type="button" class="btn-add-assert" @click="addAssertRule('text')">+ 响应文本</button>
              </div>
            </div>
            <div v-if="editAssertRules.length" class="assert-table">
              <div class="assert-head">
                <span>#</span><span>描述</span><span>类型</span><span>来源</span><span>表达式</span><span>期望值</span><span></span>
              </div>
              <div v-for="(rule, idx) in editAssertRules" :key="idx" class="assert-row">
                <span class="assert-idx">{{ idx + 1 }}</span>
                <input v-model="rule.name" class="kv-input" placeholder="断言描述" />
                <select v-model="rule.type" class="kv-select">
                  <option value="eq">eq</option>
                  <option value="not_eq">not_eq</option>
                  <option value="contains">contains</option>
                  <option value="not_contains">not_contains</option>
                  <option value="exists">exists</option>
                  <option value="regex">regex</option>
                </select>
                <select v-model="rule.source" class="kv-select">
                  <option value="status_code">状态码</option>
                  <option value="jsonpath">JSONPath</option>
                  <option value="text">响应文本</option>
                </select>
                <input v-if="rule.source !== 'status_code'" v-model="rule.expr" class="kv-input"
                  :placeholder="rule.source === 'jsonpath' ? '$.data.code' : '正则表达式'" />
                <span v-else class="kv-placeholder">HTTP 状态码</span>
                <input v-if="rule.type !== 'exists'" v-model="rule.expect" class="kv-input" placeholder="期望值" />
                <span v-else class="kv-placeholder">存在即通过</span>
                <button type="button" class="kv-del" @click="editAssertRules.splice(idx, 1)">✕</button>
              </div>
            </div>
            <div v-else class="empty-tab" style="padding: 24px">暂无断言规则，点击上方按钮添加</div>
            <div v-if="editAssertRules.length" class="assert-preview">
              <span class="assert-preview-label">JSON 预览</span>
              <pre class="assert-preview-code">{{ JSON.stringify(buildAssertList(), null, 2) }}</pre>
            </div>
          </div>

          <!-- 用例脚本 -->
          <div v-show="activeTab === 'script'" class="modal-tab-content">
            <div class="script-tip">
              可在执行前后运行 Python 脚本，支持 <code>ctx</code> 上下文变量。
              内置 helper：<code>now_ts()</code> <code>now_str()</code> <code>rand_int()</code> <code>rand_str()</code>
              <code>uuid4()</code> <code>md5()</code> <code>sha256()</code> <code>b64_encode()</code>。
            </div>
            <div class="form-group">
              <label class="form-label">
                <span class="script-badge script-badge--pre">PRE</span> 前置脚本
              </label>
              <textarea v-model="formData.pre_script" class="script-editor" rows="8"
                placeholder="# 请求前执行&#10;ctx['ts'] = now_ts()&#10;ctx['nonce'] = rand_str(10)&#10;ctx['sign'] = md5(ctx['ts'] + ctx['nonce'])"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">
                <span class="script-badge script-badge--post">POST</span> 后置脚本
              </label>
              <textarea v-model="formData.post_script" class="script-editor" rows="8"
                placeholder="# 请求后执行&#10;if response_json:&#10;    ctx['uid'] = response_json.get('data',{}).get('id')&#10;ctx['done_at'] = now_str('%Y-%m-%d %H:%M:%S')"></textarea>
            </div>
          </div>

          <div class="modal-card__footer">
            <button type="button" class="btn btn--ghost" @click="closeDialog">取消</button>
            <button type="submit" class="btn btn--primary">确定</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  FolderOpenOutlined, FolderOutlined, FolderAddOutlined, PlusCircleOutlined,
  SwapOutlined, EditOutlined, DeleteOutlined, SearchOutlined, ReloadOutlined,
  FileProtectOutlined, EyeOutlined, CloseOutlined, ArrowRightOutlined,
  PlusOutlined,
} from '@ant-design/icons-vue'
import {
  getCases, createCase, updateCase, deleteCase, getEndpoints,
  getCaseTree, createCaseFolder, attachCaseToFolder,
  moveCaseNode, renameCaseNode, deleteCaseNode,
} from '@/api/case'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const router = useRouter()

// ─── 数据 ───────────────────────────────────────
const cases           = ref([])
const endpoints       = ref([])
const showCreateDialog = ref(false)
const caseTree        = ref(null)
const selectedFolderId = ref(null)
const selectedNodeId   = ref(null)
const previewCaseId    = ref(null)
const editingItem      = ref(null)
const loading          = ref(false)
const searchText = ref('')
const selectedIds      = ref([])
const filterEndpoint   = ref('')

// ─── 目录树状态 ─────────────────────────────────
const expandedFolders    = ref(new Set())
const moveDialogVisible  = ref(false)
const moveTargetFolderId = ref(null)
const batchMoveDialogVisible  = ref(false)
const batchMoveTargetFolderId = ref(null)
const draggingNodeId     = ref(null)
const contextMenuVisible = ref(false)
const contextMenuRef     = ref(null)
const folderDialogVisible = ref(false)
const folderDialogMode   = ref('create')
const folderDialogTitle  = ref('')
const folderDialogValue  = ref('')
const contextMenuX       = ref(0)
const contextMenuY       = ref(0)
const contextNode        = ref(null)
const contextTargetFolderId = ref(null)
const treeBodyRef        = ref(null)

// ─── 弹窗表单 ───────────────────────────────────
const activeTab = ref('basic')
const tabs = [
  { key: 'basic',    label: '基本信息' },
  { key: 'params',   label: '接口参数' },
  { key: 'extract',  label: '数据提取' },
  { key: 'validate', label: '断言规则' },
  { key: 'script',   label: '用例脚本' },
]
const paramTypes = [
  { key: 'json',  label: 'JSON Body' },
  { key: 'form',  label: 'Form Data' },
  { key: 'query', label: 'Query Params' },
  { key: 'raw',   label: '原始 JSON' },
]
const formData = ref({
  name: '', endpoint: null,
  alluer: '', api_args: '',
  pre_script: '', post_script: '',
  paramType: 'json',
  jsonRows: [], formRows: [], queryRows: [], headerRows: [],
})
const editExtractRules = ref([])
const editAssertRules  = ref([])

// ─── 工具函数 ───────────────────────────────────
const isSameId = (a, b) => String(a) === String(b)
const hasNodeId = (v) => v !== null && v !== undefined && v !== ''

const findTreeNodeById = (node, id) => {
  if (!node) return null
  if (isSameId(node.id, id)) return node
  for (const child of (node.children || [])) {
    const found = findTreeNodeById(child, id)
    if (found) return found
  }
  return null
}

const canOperateFolder = (node) => {
  if (!node) return false
  if (node.node_type === 'folder') return true
  if (typeof node.node_type === 'string' && node.node_type.includes('root')) return true
  if (node.node_type !== 'case' && Array.isArray(node.children)) return true
  return false
}

const isFolderNode = (node) => canOperateFolder(node)
const displayTreeNodeName = (node) => node?.name?.trim() || '无名称'

const isExpanded = (id) => Array.from(expandedFolders.value).some(v => isSameId(v, id))

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

const displayedCases = computed(() => {
  let result = cases.value
  if (filterEndpoint.value) {
    result = result.filter(c => c.endpoint?.id === Number(filterEndpoint.value))
  }
  if (!selectedFolderId.value || !caseTree.value) return result
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
  if (!node) return result
  const ids = new Set()
  collectCaseIds(node, ids)
  return result.filter(c => ids.has(c.id))
})

const previewCaseData = computed(() => {
  if (!previewCaseId.value) return null
  return cases.value.find(c => c.id === previewCaseId.value) || null
})

const allSelected = computed(() =>
  displayedCases.value.length > 0 && displayedCases.value.every(i => selectedIds.value.includes(i.id))
)

// ─── 目录树操作 ─────────────────────────────────
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
    const folders = children.filter(c => c?.node_type === 'folder')
      .sort((a, b) => Number(a?.id || 0) - Number(b?.id || 0))
    const caselist = children.filter(c => c?.node_type !== 'folder')
      .sort((a, b) => Number(b?.id || 0) - Number(a?.id || 0))
    return { ...node, children: [...folders, ...caselist] }
  }
  caseTree.value = sortTreeByRule(rawTree)
  if (caseTree.value && !selectedFolderId.value) selectedFolderId.value = caseTree.value.id
  if (caseTree.value) {
    prev.add(caseTree.value.id)
    expandedFolders.value = prev
  }
}

// ─── 右键菜单 ───────────────────────────────────
const canMoveContextNode = computed(() =>
  hasNodeId(contextNode.value?.id) && hasNodeId(contextNode.value?.parent)
)
const canDeleteContextNode = computed(() => {
  const node = contextNode.value
  if (!node || !hasNodeId(node.id)) return false
  return !Array.isArray(node.children) || node.children.length === 0
})

const closeContextMenu = () => { contextMenuVisible.value = false }

const onGlobalClick = () => { if (contextMenuVisible.value) closeContextMenu() }
const onGlobalKeydown = (e) => { if (e.key === 'Escape' && contextMenuVisible.value) closeContextMenu() }

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

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const createFolderUnderContext = () => openFolderDialog('create', '新增子文件夹', '')

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
      closeContextMenu()
      closeFolderDialog()
      await loadCaseTree()
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
  if (!folderId) { alert('未找到目标目录'); return }
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
    alert('删除节点失败：' + (e.response?.data?.message || e.response?.data?.msg || e.message))
  }
}

const confirmMoveNode = async () => {
  if (!moveTargetFolderId.value || !selectedNodeId.value) return
  await moveCaseNode({ node_id: selectedNodeId.value, target_parent_id: moveTargetFolderId.value })
  moveDialogVisible.value = false
  await loadCaseTree()
}

// ─── 列表数据加载 ───────────────────────────────
const loadCases = async (page = 1) => {
  loading.value = true
  try {
    const params = { page: 1, page_size: 500 }
    if (searchText.value)     params.search    = searchText.value
    if (filterEndpoint.value) params.endpoint  = filterEndpoint.value
    const res = await getCases(params)
    cases.value = res.result?.list || []
  } catch (error) {
    console.error('加载用例列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch   = () => loadCases(1)
const resetFilter    = () => { searchText.value = ''; filterEndpoint.value = ''; loadCases(1) }
const toggleAll      = (e) => { selectedIds.value = e.target.checked ? displayedCases.value.map(i => i.id) : [] }

const openBatchMoveDialog = () => {
  if (!selectedIds.value.length) return
  batchMoveTargetFolderId.value = selectedFolderId.value || caseTree.value?.id || null
  batchMoveDialogVisible.value = true
}

const confirmBatchMove = async () => {
  if (!batchMoveTargetFolderId.value || !selectedIds.value.length) return
  const failed = []
  for (const caseId of selectedIds.value) {
    try { await attachCaseToFolder({ case_id: caseId, parent_id: batchMoveTargetFolderId.value }) }
    catch (e) { failed.push(caseId) }
  }
  batchMoveDialogVisible.value = false
  selectedIds.value = []
  await Promise.all([loadCases(), loadCaseTree()])
  if (failed.length) alert(`已移动 ${selectedIds.value.length - failed.length}/${selectedIds.value.length} 条，失败 ID：${failed.join(', ')}`)
}

const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条用例吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteCase(id)))
    cases.value = cases.value.filter(c => !selectedIds.value.includes(c.id))
    selectedIds.value = []
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}

const loadEndpoints = async () => {
  try {
    const res = await getEndpoints({ page_size: 200 })
    endpoints.value = res.result?.list || []
  } catch (error) { console.error('加载接口列表失败:', error) }
}

const viewDetail          = (id) => router.push(`/cases/${id}`)
const goCreate            = () => router.push('/cases/new')
const goEdit              = (id) => router.push(`/cases/${id}/edit`)
const viewEndpointDetail  = (id) => router.push(`/endpoints/${id}`)
const previewCase         = (item) => { if (!item) return; previewCaseId.value = item.id }

// ─── 弹窗表单 ───────────────────────────────────
const rowsToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.k.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}
const objToRows = (obj) =>
  obj ? Object.entries(obj).map(([k, v]) => ({ k, v: String(v) })) : []

const buildApiArgs = () => {
  if (formData.value.paramType === 'raw')
    return formData.value.api_args ? JSON.parse(formData.value.api_args) : null
  const obj = {}
  if (formData.value.paramType === 'json') {
    const d = rowsToObj(formData.value.jsonRows); if (d) obj.json = d }
  else if (formData.value.paramType === 'form') {
    const d = rowsToObj(formData.value.formRows); if (d) obj.data = d }
  else if (formData.value.paramType === 'query') {
    const d = rowsToObj(formData.value.queryRows); if (d) obj.params = d }
  const headers = rowsToObj(formData.value.headerRows)
  if (headers) obj.headers = headers
  return Object.keys(obj).length ? obj : null
}

const parseApiArgs = (api_args) => {
  if (!api_args) return { paramType: 'json', jsonRows: [], formRows: [], queryRows: [], headerRows: [], api_args: '' }
  const headers = objToRows(api_args.headers)
  if (api_args.json)   return { paramType: 'json',  jsonRows: objToRows(api_args.json),   formRows: [], queryRows: [], headerRows: headers, api_args: '' }
  if (api_args.data)   return { paramType: 'form',  formRows: objToRows(api_args.data),   jsonRows: [], queryRows: [], headerRows: headers, api_args: '' }
  if (api_args.params) return { paramType: 'query', queryRows: objToRows(api_args.params), jsonRows: [], formRows: [], headerRows: headers, api_args: '' }
  return { paramType: 'raw', api_args: JSON.stringify(api_args, null, 2), jsonRows: [], formRows: [], queryRows: [], headerRows: headers }
}

const addExtractRule     = () => editExtractRules.value.push({ name: '', expr: '', index: 0 })
const removeExtractRule  = (idx) => editExtractRules.value.splice(idx, 1)
const buildExtractObj    = () => {
  const obj = {}
  for (const r of editExtractRules.value)
    if (r.name.trim()) obj[r.name.trim()] = ['json', r.expr.trim(), r.index ?? 0]
  return Object.keys(obj).length ? obj : null
}

const addAssertRule = (source = 'jsonpath') => {
  editAssertRules.value.push({ name: '', type: 'eq', source, expr: '', expect: source === 'status_code' ? '200' : '' })
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
      name: r.name || '', type: r.type || 'eq', source: r.source || 'jsonpath',
      expr: r.expr || '', expect: r.expect != null ? String(r.expect) : '',
    }))
  }
  const rows = []
  for (const [k, v] of Object.entries(validate)) {
    if (k === 'status_code') { rows.push({ name: '状态码', type: 'eq', source: 'status_code', expr: '', expect: String(v) }); continue }
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

const editCase = (item) => {
  editingItem.value = item
  activeTab.value = 'basic'
  const parsed = parseApiArgs(item.api_args)
  formData.value = {
    name: item.name, endpoint: item.endpoint?.id || item.endpoint,
    alluer: item.alluer ? JSON.stringify(item.alluer, null, 2) : '',
    validate: item.validate ? JSON.stringify(item.validate, null, 2) : '',
    pre_script: item.pre_script || '', post_script: item.post_script || '',
    ...parsed,
  }
  editExtractRules.value = item.extract
    ? Object.entries(item.extract).map(([name, rule]) =>
        Array.isArray(rule) ? { name, expr: rule[1] ?? '', index: rule[2] ?? 0 } : { name, expr: String(rule), index: 0 })
    : []
  editAssertRules.value = parseAssertList(item.validate)
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  try {
    const api_args = buildApiArgs()
    const data = {
      name: formData.value.name,
      endpoint: formData.value.endpoint,
      parent_node_id: selectedFolderId.value || caseTree.value?.id,
      project: null, product_line: null,
      alluer: formData.value.alluer ? JSON.parse(formData.value.alluer) : null,
      api_args,
      extract: buildExtractObj(),
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

const closeDialog = () => {
  showCreateDialog.value = false
  editingItem.value = null
  activeTab.value = 'basic'
  editExtractRules.value = []
  editAssertRules.value = []
  formData.value = {
    name: '', endpoint: null, alluer: '', api_args: '',
    pre_script: '', post_script: '',
    paramType: 'json', jsonRows: [], formRows: [], queryRows: [], headerRows: [],
  }
}

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

onMounted(() => {
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
</script>

<style scoped>
/* ─── 整体布局 ─── */
.case-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.case-view__layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.case-view__sidebar {
  position: sticky;
  top: 16px;
}

.case-view__main {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
  padding-top: 8px;
}

@media (max-width: 1200px) {
  .case-view__layout { grid-template-columns: 1fr; }
}

/* ─── 目录树 ─── */
.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.tree-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  border-bottom: 1px solid #f0f0f0;
}

.tree-header__icon { font-size: 16px; color: #6b7280; }
.tree-header__title { font-size: 14px; font-weight: 700; color: #111827; }

.tree-body {
  padding: 8px;
  max-height: 520px;
  overflow-y: auto;
}

.tree-body::-webkit-scrollbar { width: 5px; }
.tree-body::-webkit-scrollbar-track { background: transparent; }
.tree-body::-webkit-scrollbar-thumb { background: rgba(127, 151, 189, 0.4); border-radius: 99px; }

.tree-row {
  display: flex;
  align-items: center;
  gap: 4px;
  line-height: 32px;
  cursor: pointer;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  transition: background 0.15s, color 0.15s;
  user-select: none;
  margin-bottom: 2px;
}

.tree-row:hover { background: #edf4ff; color: #174f93; }
.tree-row.active { background: #e3efff; color: #0b57ad; font-weight: 600; }

.tree-toggle {
  display: inline-flex;
  width: 16px;
  height: 16px;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #7587a4;
  flex-shrink: 0;
}

.tree-node-icon {
  display: inline-flex;
  flex-shrink: 0;
  color: #6b7f9f;
}

.tree-row.active .tree-node-icon { color: #2f6eb9; }

.tree-node-label {
  display: inline-flex;
  align-items: center;
  max-width: calc(100% - 24px);
}

.tree-node-name {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ─── 右键菜单 ─── */
.context-menu {
  position: fixed;
  z-index: 1200;
  min-width: 188px;
  padding: 6px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 14px 34px rgba(17, 49, 96, 0.16);
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
  padding: 9px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #374151;
  transition: background 0.14s, color 0.14s;
}

.context-menu button:hover { background: #f0f9ff; color: #0369a1; }
.context-menu button.danger:hover { background: #fef2f2; color: #dc2626; }
.context-menu button:disabled { opacity: 0.45; cursor: not-allowed; }
.context-menu button:disabled:hover { background: transparent; color: #374151; }

/* ─── 工具栏 ─── */
/* ─── 筛选区（与项目列表一致） ─── */
.case-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: var(--radius-lg);
  overflow-x: auto;
  flex-wrap: wrap;
}

.filter-bar__left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.filter-bar__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  margin-left: 8px;
}

.filter-bar__search {
  display: flex;
  align-items: center;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0 12px;
  background: #f9fafb;
  width: 260px;
  flex-shrink: 0;
  gap: 8px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.filter-bar__search:focus-within {
  border-color: #e94f4f;
  box-shadow: 0 0 0 2px rgba(233, 79, 79, 0.1);
}

.filter-bar__search-icon {
  color: #9CA3AF;
  font-size: 13px;
  flex-shrink: 0;
}

.filter-bar__input {
  flex: 1;
  border: none;
  outline: none;
  padding: 9px 0;
  font-size: 13px;
  background: transparent;
  color: #111827;
}

.filter-bar__input::placeholder {
  color: #9CA3AF;
}

.filter-bar__filters {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-label {
  font-size: 13px;
  color: #6b7280;
  white-space: nowrap;
}

.filter-bar__select {
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  background: #f9fafb;
  color: #111827;
  outline: none;
  cursor: pointer;
  min-width: 100px;
  transition: border-color 0.2s;
}

.filter-bar__select:focus {
  border-color: #e94f4f;
}

/* ─── 表格卡片 ─── */
.table-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.table-card__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-info { font-size: 13px; color: #6b7280; }
.toolbar-info strong { color: #111827; }
.toolbar-actions { display: flex; align-items: center; gap: 8px; }

.table-wrapper { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead tr {
  background: #f9fafb;
}

.data-table thead th {
  padding: 10px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  border-bottom: 1px solid #e5e7eb;
}

.data-table tbody tr {
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.12s;
  cursor: pointer;
}

.data-table tbody tr:hover { background: #f9fafb; }
.data-table tbody tr.row-active { background: #eff6ff; }
.data-table tbody tr:last-child { border-bottom: none; }

.data-table tbody td {
  padding: 11px 16px;
  color: #374151;
  vertical-align: middle;
}

.cell-mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; color: #9CA3AF; }
.cell-name { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #111827; }
.link-primary { color: #111827; cursor: pointer; font-weight: 500; text-decoration: none; }
.link-primary:hover { color: #e94f4f; text-decoration: underline; }
.text-muted { color: #9CA3AF; }

.creator-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  background: linear-gradient(135deg, #e8f4fd, #d6eaf8);
  color: #1a6fa8;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid #aed6f1;
}

.row-actions { display: flex; align-items: center; gap: 6px; }

.btn-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 7px;
  background: #f3f4f6;
  color: #6b7280;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}

.btn-action:hover { background: #e5e7eb; color: #374151; }
.btn-action--danger:hover { background: #fef2f2; color: #dc2626; }

.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 56px 24px;
  color: #9CA3AF;
  font-size: 14px;
}

.empty-table__icon { font-size: 36px; color: #d1d5db; }

.loading-table {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

/* ─── 预览面板 ─── */
.preview-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.preview-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  border-bottom: 1px solid #f0f0f0;
}

.preview-card__title-group { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.preview-id { font-family: 'SF Mono', monospace; font-size: 12px; color: #9CA3AF; font-weight: 600; }
.preview-name { font-size: 15px; font-weight: 700; color: #111827; }

.preview-card__actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

.preview-card__body { padding: 16px 20px; }

.preview-meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.preview-meta__item { display: flex; flex-direction: column; gap: 4px; }
.preview-meta__label { font-size: 11px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px; }
.preview-meta__value { font-size: 13px; color: #374151; font-weight: 500; }

.preview-section { margin-bottom: 12px; }
.preview-section__title { font-size: 12px; font-weight: 700; color: #374151; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
.preview-code {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 14px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #374151;
  overflow-x: auto;
  margin: 0;
}

/* ─── 按钮系统 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
  white-space: nowrap;
}

.btn--primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn--primary:hover {
  background: linear-gradient(135deg, #2563EB 0%, #1d4ed8 100%);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

.btn--primary:active { transform: translateY(0); box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3); }

.btn--ghost {
  background: white;
  color: #374151;
  border: 1.5px solid #e5e7eb;
}

.btn--ghost:hover { background: #f9fafb; border-color: #d1d5db; }

.btn--danger-ghost {
  background: white;
  color: #ef4444;
  border: 1.5px solid #fecaca;
}

.btn--danger-ghost:hover { background: #fef2f2; border-color: #ef4444; }

.btn--sm { padding: 7px 14px; font-size: 13px; border-radius: 8px; }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ─── Modal ─── */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-card {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 520px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.25s ease;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-card--lg { max-width: 720px; }

.modal-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  flex-shrink: 0;
}

.modal-card__title { font-size: 17px; font-weight: 700; color: #111827; }

.modal-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #9CA3AF;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.15s;
}

.modal-close:hover { background: #f3f4f6; color: #374151; }

.modal-card__body {
  padding: 20px 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-card__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfb;
  flex-shrink: 0;
}

/* ─── Modal Tabs ─── */
.modal-tabs-nav {
  display: flex;
  padding: 0 24px;
  border-bottom: 2px solid #f0f0f0;
  background: #fafbfb;
  flex-shrink: 0;
}

.modal-tab-btn {
  padding: 12px 20px;
  border: none;
  background: none;
  font-size: 13px;
  font-weight: 500;
  color: #9CA3AF;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.15s, border-color 0.15s;
}

.modal-tab-btn:hover { color: #374151; }
.modal-tab-btn.active { color: #3B82F6; border-bottom-color: #3B82F6; font-weight: 700; }

.modal-tab-content { min-height: 200px; }

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ─── 表单元素 ─── */
.form-group { margin-bottom: 16px; }
.form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-label { display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.form-label-hint { font-size: 11px; color: #9CA3AF; font-weight: 400; margin-left: 4px; }
.required { color: #ef4444; }

.form-input, .form-select, .form-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 9px 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: #111827;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: white;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea { resize: vertical; font-family: 'SF Mono', 'Fira Code', monospace; }

/* ─── KV 表格 ─── */
.kv-section { margin-bottom: 4px; }
.kv-tip { font-size: 12px; color: #9CA3AF; margin-bottom: 8px; }
.kv-tip code { background: #eff6ff; color: #3B82F6; padding: 1px 5px; border-radius: 4px; font-size: 11px; }

.kv-table { border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; margin-bottom: 8px; }
.kv-head {
  display: grid;
  grid-template-columns: 1fr 1fr 32px;
  gap: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  font-size: 11px;
  font-weight: 700;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kv-row {
  display: grid;
  grid-template-columns: 1fr 1fr 32px;
  gap: 8px;
  padding: 6px 12px;
  border-top: 1px solid #f3f4f6;
  align-items: center;
  background: white;
  transition: background 0.1s;
}

.kv-row:hover { background: #f9fafb; }

.kv-input {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 5px 8px;
  font-size: 12px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  color: #111827;
  transition: border-color 0.15s;
}

.kv-input:focus { border-color: #3B82F6; }
.kv-input--sm { text-align: center; }

.kv-select {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 5px 8px;
  font-size: 12px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  background: white;
  color: #374151;
  cursor: pointer;
}

.kv-placeholder { font-size: 12px; color: #9CA3AF; font-style: italic; padding: 0 4px; }

.kv-del {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #d1d5db;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}

.kv-del:hover { background: #fef2f2; color: #ef4444; }

.btn-add-row {
  font-size: 12px;
  padding: 5px 14px;
  border: 1.5px dashed #3B82F6;
  border-radius: 8px;
  background: white;
  color: #3B82F6;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-add-row:hover { background: #eff6ff; }

/* ─── 参数类型切换 ─── */
.params-type-bar {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.params-type-btn {
  padding: 5px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.params-type-btn:hover { border-color: #3B82F6; color: #3B82F6; background: #eff6ff; }
.params-type-btn.active { background: #3B82F6; color: white; border-color: #3B82F6; }

/* ─── 数据提取 ─── */
.extract-tip {
  background: #eff6ff;
  border-left: 3px solid #3B82F6;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  color: #1e40af;
  margin-bottom: 14px;
}

.extract-tip code { background: white; color: #3B82F6; padding: 1px 5px; border-radius: 4px; font-size: 11px; }

.extract-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.extract-count { font-size: 13px; color: #6b7280; }

.extract-table { border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; margin-bottom: 10px; }

.extract-head {
  display: grid;
  grid-template-columns: 160px 1fr 80px 32px;
  gap: 8px;
  padding: 8px 12px;
  background: #eff6ff;
  font-size: 11px;
  font-weight: 700;
  color: #1d4ed8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.extract-row {
  display: grid;
  grid-template-columns: 160px 1fr 80px 32px;
  gap: 8px;
  padding: 6px 12px;
  border-top: 1px solid #f0f0f0;
  align-items: center;
  background: white;
}

.extract-row:hover { background: #f9fafb; }

/* ─── 断言 ─── */
.assert-tip {
  background: #f0fdf4;
  border-left: 3px solid #10B981;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  color: #065f46;
  margin-bottom: 14px;
}

.assert-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}

.assert-add-btns { display: flex; gap: 6px; }

.btn-add-assert {
  font-size: 12px;
  padding: 5px 14px;
  border: 1.5px dashed #10B981;
  border-radius: 8px;
  background: white;
  color: #10B981;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-add-assert:hover { background: #f0fdf4; }

.assert-table { border: 1px solid #d1fae5; border-radius: 8px; overflow: hidden; margin-bottom: 14px; }

.assert-head {
  display: grid;
  grid-template-columns: 28px 140px 100px 90px 1fr 120px 32px;
  gap: 8px;
  padding: 8px 12px;
  background: #f0fdf4;
  font-size: 11px;
  font-weight: 700;
  color: #065f46;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.assert-row {
  display: grid;
  grid-template-columns: 28px 140px 100px 90px 1fr 120px 32px;
  gap: 8px;
  padding: 6px 12px;
  border-top: 1px solid #d1fae5;
  align-items: center;
  background: white;
}

.assert-row:hover { background: #f0fdf4; }

.assert-idx { text-align: center; font-size: 12px; color: #9CA3AF; font-weight: 700; }

.assert-preview-label {
  font-size: 11px;
  font-weight: 700;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 6px;
}

.assert-preview-code {
  background: #1a1a2e;
  color: #a8ff78;
  padding: 14px 16px;
  border-radius: 8px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
}

/* ─── 用例脚本 ─── */
.script-tip {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  color: #92400e;
  margin-bottom: 14px;
  line-height: 1.6;
}

.script-tip code { background: #1f2937; color: #f9fafb; padding: 1px 5px; border-radius: 4px; font-size: 11px; }

.script-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  margin-right: 6px;
}

.script-badge--pre  { background: #dbeafe; color: #1d4ed8; }
.script-badge--post { background: #d1fae5; color: #065f46; }

.script-editor {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid #374151;
  border-radius: 8px;
  padding: 12px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.7;
  background: #0f172a;
  color: #d1fae5;
  outline: none;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.script-editor:focus {
  border-color: #10B981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

/* ─── 空状态 ─── */
.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #9CA3AF;
  font-size: 14px;
  text-align: center;
}
</style>
