# Bristol → China · 法律职业行动指南

响应式中文职业规划网站，适用于 2026 年 9 月开始 Bristol LLM、2027 年 5 月起回国全职实习的假设场景。

**公开网站：** https://zhouyi-xiaoxiao.github.io/bristol-law-career-roadmap/

包含月度路线、职业路径、具体团队定位、内推与联系方法、布大和行业活动、五家律所招聘入口、法考及技能准备、AI 训练方法、可复制模板与原始来源。

## 内容边界

- 5 月可全职到岗是用户已确认的规划条件，不代表本网站认证学校规则或个人法律资格。
- 页面整理于 2026-09-22；招聘和活动研究主要核查于 2026-09-21。
- 策略建议不等于招聘公告。没有核实到的 2027 具体截止日不作推测。
- 公开页面只含假设教育背景与职业资料，不包含私人身份、账户凭证或客户材料。
- 静态站，无统计跟踪、无第三方脚本、无后台。

## 构建与预览

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8765 --directory docs
```

`src/content.json` 是内容源。`docs/` 是 GitHub Pages 发布目录，使用 main 分支 /docs 源。CSS 与 JavaScript 不需要包管理器或构建依赖。页面正文在 HTML 中完整可读，JavaScript 仅增强目录状态与模板复制。

## 发布与恢复

验证后将修改提交并推送至 main，GitHub Pages 自动构建。需要撤回后续修改时，用 `git revert <需要撤回的提交>` 创建恢复提交并推送，不重写历史。首次发布前没有旧线上版本。
