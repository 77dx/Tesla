# Claude Code 斜杠命令参考 (Recovery CLI 模式)

以下命令在 `claude-code-haha` 的 Recovery CLI 模式（即 `CLAUDE_CODE_FORCE_RECOVERY_CLI=1` 启动后）中可用。输入时需以 `/` 开头。

| 命令 | 中文解释 | 示例 / 备注 |
|------|----------|-------------|
| `/help` | 显示帮助信息，列出所有可用命令 | `/help` |
| `/exit` 或 `/quit` | 退出 Claude Code | `/exit` |
| `/clear` | 清空当前对话历史（不删除文件） | `/clear` |
| `/model` | 查看或切换当前使用的模型 | `/model` 显示当前模型；`/model deepseek-chat` 切换 |
| `/compact` | 压缩对话上下文（当对话过长时使用） | `/compact` |
| `/init` | 在当前目录初始化一个 `CLAUDE.md` 项目说明文件 | `/init` |
| `/agents` | 列出可用的自定义 Agent（角色） | 需要 `~/.claude/agents/` 目录中有角色文件 |
| `/agent <名称>` | 激活指定的 Agent 角色 | `/agent 前端开发专家` |
| `/cost` | 显示本次会话的预估 API 费用 | `/cost` |
| `/status` | 显示当前会话状态（模型、token 使用等） | `/status` |
| `/logs` | 查看最近的错误日志 | `/logs` |
| `/export` | 导出当前对话记录到文件 | `/export conversation.json` |
| `/theme` | 切换终端主题（如果支持） | `/theme dark` |
| `/plugin` | 管理插件市场（如果编译版支持） | `/plugin install <name>` |
| `/skills` | 列出已安装的 Skills | `/skills` |
| `/doctor` | 运行诊断，检查环境配置 | `/doctor` |

## 补充说明
- 在 Recovery CLI 模式下，界面是简单的 `you>` 提示符，输入上述命令即可。
- 部分命令可能因 `claude-code-haha` 版本不同而缺失，可先用 `/help` 查看实际支持的命令。
- 若需要自定义命令，可以编写 Skills 或 Agents 来实现。