# DragonLang Engine V2.3 · Semantic Fusion Edition

社区龙语风格实验。跨平台、可静态部署，保留 V2.0 的四种 API 协议、五种龙语流派、系统提示词编辑和二次审校。无第三方运行依赖。

## V2.3 全文语义融合升级

从首个完整语义单元起，将原文核心命题与针对过度推论的限定自然融合；禁止独立复述人话后追加免责声明。保留全部命题、原作者视角、语气、确定程度和言语行为；要求模型不把宣布完成改成质疑是否完成。可选二次审校从原文到输出逐项检查遗漏，再从输出回查新增断言和语义漂移；默认仍关闭，开启额外消耗一次调用。审校同时检查首句和全文是否存在人话前缀、无关防御尾巴或仅添加开场词的伪融合。审校不是客观保证，失败时保留未审校初稿并提示。

根目录与 docs 下的 HTML 保持一致。现有仓库若已配置 Pages Actions，请保留原有工作流及发布配置，不必重新配置。

## 双击启动（推荐长期 API 密钥使用本地模式）

解压 ZIP，安装 Python 3.9+（如果尚未安装）。
- macOS：双击 `启动龙语转换机.command`。若系统拦截，使用 Finder 右键打开；若解压器丢失执行权限，运行 `chmod +x 启动龙语转换机.command` 一次。
- Windows：双击 `Start DragonLang.bat`（Windows 英文文件名避免批处理编码问题）。
- Linux：执行 `./启动龙语转换机.sh`，桌面文件管理器支持执行脚本时也可双击。
- 通用备选：`python3 server.py`（Windows `py -3 server.py`）。

本地后端让操作系统分配空闲端口并自动打开浏览器。也可指定 `--port 8765`，若已占用则自动换端口。关闭启动窗口或 Ctrl+C 停止服务。终端显示真实访问地址。服务仅监听 127.0.0.1，不开放 CORS。

## 不装 Python / GitHub Pages

双击 `docs/index.html` 可打开独立静态网页（系统提示词已内置）。模型请求仍需要可访问的 API；file:// 来源的 CORS 限制可能更严格。

将项目内容上传至 GitHub 新仓库（例如 dragonlang），在 Settings → Pages → Build and deployment 选择 Deploy from a branch，选 main 和 /docs，保存。GitHub Pages 发布后使用其显示的 Visit site 链接。无需 Actions 或构建。只有 docs 会作为网站发布；不要上传密钥。GitHub Pages 网站通常公开，先确认你愿意公开代码和提示词。

静态网页没有 Python 后端。只有允许浏览器跨域访问的可信 API/网关才可直连；推荐由网关保管长期供应商密钥，网页只使用短期受限访问凭据或无需密钥的受信任本地服务。**不要把长期生产 API Key 放进网页或仓库。** 如果供应商不支持 CORS，或浏览器阻止从 HTTPS 页面访问本地 HTTP，使用本地启动器。不要通过关闭浏览器安全策略或公开无鉴权代理解决问题。项目不内置公共代理，不发送数据给第三方中转。静态模式请求只发往用户填写的端点。

官方部署文档：https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

## API 配置

| 协议 | Base URL 示例 | 自动追加 |
|---|---|---|
| Chat Completions | https://api.openai.com/v1 | /chat/completions |
| Responses | https://api.openai.com/v1 | /responses |
| Anthropic Messages | https://api.anthropic.com/v1 | /messages |
| Gemini generateContent | https://generativelanguage.googleapis.com/v1beta | /models/{model}:generateContent |
| Ollama Chat 兼容 | http://127.0.0.1:11434/v1 | /chat/completions |

实际模型 ID、协议、限制字段及 CORS 策略由供应商决定。API Key 不主动写入磁盘或浏览器存储；静态模式凭据仍可被浏览器脚本、扩展或调试器访问。本地模式通过受同源和会话令牌保护的本地后端发送请求。模型调用可能收费；二次审校额外调用一次，失败会保留初稿。

## 系统提示词

`system_prompt.txt` 可移植至其他 AI。网页内置同一份提示词，可编辑、复制、导出。若维护者修改默认提示词文件，需要同步更新两份 index.html 内的 initialPrompt。系统提示词不是严格安全边界。工程龙语只生成文字，不执行工程操作。无离线模板冒充真实 API 输出。

## 测试

`python3 -m unittest -v test_server.py` 检查本地协议及请求处理；`node test_browser.js` 检查静态请求构建、解析和审校。模拟测试不调用真实模型。

运行 `python3 -m unittest -v test_semantic_contract.py` 验证语义契约、双入口一致性及回归样例覆盖；`semantic_cases.json` 提供真实模型人工验收用例。模拟测试仅验证提示词与请求流程，不能证明真实模型语义保真。

V2.3 的语义用例提供 `must_fuse`、`bad_example` 和 `reference_example` 等人工验收信息；参考文本是示意而非实际 API 输出。验收同时检查命题完整、人称与言语行为一致、首句融合、全文关联及无新增事实。无需字面匹配参考文本。
