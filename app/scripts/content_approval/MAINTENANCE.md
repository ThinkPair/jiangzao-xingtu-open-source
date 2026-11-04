# 已有七问的定期事实维护

原批次截止日仍是 2026-10-02。后续普通七问事实更新必须由维护方在可信工具根目录的 `maintenance-authorizations.json` 登记；内容包不能自行授权，也不能借用要求事实不变的 `repair-legacy`。

注册表顶层为 `schemaVersion: 1`、`jobId: atlas-company-pilot-20261002`、`authorizations` 数组。每条记录必须包含：

- `authorizationId`：唯一标识。
- `status`：`active` 或 `revoked`。
- `code`、`bundlePath`：完整公司代码及精确的 `inbox/<code>/vNNN`。
- `manifestSha256`：该新包 manifest 的实际 SHA256。
- `cutoff`：晚于原批次截止日，不晚于真实 UTC+8 当日。
- `authorizedAt`：带时区、不晚于当前时间。
- `userAuthorityRef`、`owner`：实际用户授权的证据引用及维护责任人。
- `scope`：`ordinary_seven_fact_refresh`。

授权只是日期维护许可。来源披露日不得晚于读者稿资料日，读者稿资料日不得晚于授权截止日；证据截止日必须与授权完全相同。新包仍须独立语义审核、真实页面验收、内容投影和整站验证。

每一批应一次登记全部记录，再构建候选。整份注册表原始字节 SHA 和完整选中记录共同绑定机器回执及 adoption；之后增加、撤销或修改任何记录，旧绑定都失效。维护方须重新验证和重建受影响的候选，不能复用旧批准缓存。

旧七问及全部 L 概览沿用原合同，不依赖这个文件。公开快照仅用于复现已记录内容，不需要私有注册表，也不能据此生成新的当前批准。真实注册表、原始资料和私有审批工作区不进入公开源码。
