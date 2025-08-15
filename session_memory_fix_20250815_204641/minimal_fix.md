# 🔧 最小化修复方案

## 问题分析

根据用户的反馈，核心问题是：
1. `q chat --trust-all-tools` 本身具备会话记忆能力
2. 我们不应该重复发送历史上下文
3. 应该让 `q chat` 自然维护其会话状态

## 最小化修复

只需要修改 `_prepare_message` 方法，不发送上下文：

```python
def _prepare_message(self, message: str, context: str = "") -> str:
    """
    准备发送给Q CLI的消息 - 简化版本
    
    不再发送历史上下文，让Q Chat自己维护会话记忆
    """
    if config.FORCE_CHINESE:
        return f"请用中文回答：{message}"
    else:
        return message
```

## 实施步骤

1. 只修改 `qcli_service.py` 中的 `_prepare_message` 方法
2. 保持其他代码不变
3. 测试验证效果

这样可以避免复杂的进程管理，同时解决核心问题。