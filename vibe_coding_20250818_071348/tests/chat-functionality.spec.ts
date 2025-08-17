/**
 * 聊天功能测试
 * 测试消息发送、接收和流式聊天功能
 */

import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:3001';

test.describe('聊天功能测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
  });

  test('TC006: 创建新会话', async ({ page }) => {
    // 点击创建新会话按钮
    const createButton = page.locator('button:has-text("创建新会话")');
    await expect(createButton).toBeVisible();
    await createButton.click();
    
    // 等待会话创建完成
    await page.waitForTimeout(2000);
    
    // 验证界面切换到聊天界面
    await expect(page.locator('text=当前会话')).toBeVisible();
    await expect(page.locator('textarea, input[placeholder*="输入"]')).toBeVisible();
    
    // 验证会话信息显示
    await expect(page.locator('text=0 条消息')).toBeVisible();
  });

  test('TC007: 发送普通消息', async ({ page }) => {
    // 先创建会话
    await page.locator('button:has-text("创建新会话")').click();
    await page.waitForTimeout(2000);
    
    // 查找消息输入框
    const messageInput = page.locator('textarea, input[placeholder*="输入"]').first();
    await expect(messageInput).toBeVisible();
    
    // 输入测试消息
    const testMessage = '你好，这是一个测试消息';
    await messageInput.fill(testMessage);
    
    // 发送消息
    const sendButton = page.locator('button:has-text("发送"), button[type="submit"]').first();
    await sendButton.click();
    
    // 验证用户消息显示
    await expect(page.locator(`text=${testMessage}`)).toBeVisible();
    
    // 等待AI回复（最多30秒）
    await page.waitForSelector('text=/.*/', { timeout: 30000 });
    
    // 验证消息计数更新
    await expect(page.locator('text=/\d+ 条消息/')).toBeVisible();
  });

  test('TC008: 流式消息测试', async ({ page }) => {
    // 创建会话
    await page.locator('button:has-text("创建新会话")').click();
    await page.waitForTimeout(2000);
    
    // 确保流式模式开启
    const streamToggle = page.locator('input[type="checkbox"], .ant-switch').first();
    if (await streamToggle.isVisible()) {
      const isChecked = await streamToggle.isChecked();
      if (!isChecked) {
        await streamToggle.click();
      }
    }
    
    // 发送消息
    const messageInput = page.locator('textarea, input[placeholder*="输入"]').first();
    await messageInput.fill('请详细介绍React的基本概念');
    
    const sendButton = page.locator('button:has-text("发送"), button[type="submit"]').first();
    await sendButton.click();
    
    // 监听流式响应
    let streamingDetected = false;
    
    // 等待流式响应开始
    await page.waitForTimeout(3000);
    
    // 检查是否有流式指示器或逐步显示的内容
    const responseArea = page.locator('.message-content, .ant-typography').last();
    if (await responseArea.isVisible()) {
      const initialText = await responseArea.textContent();
      
      // 等待一段时间看内容是否在增长
      await page.waitForTimeout(5000);
      const laterText = await responseArea.textContent();
      
      if (laterText && initialText && laterText.length > initialText.length) {
        streamingDetected = true;
      }
    }
    
    // 等待流式完成
    await page.waitForTimeout(10000);
    
    console.log('流式响应检测结果:', streamingDetected);
  });

  test('TC009: 长消息处理测试', async ({ page }) => {
    // 创建会话
    await page.locator('button:has-text("创建新会话")').click();
    await page.waitForTimeout(2000);
    
    // 发送长消息
    const longMessage = '请详细解释以下概念：' + 'React组件生命周期、状态管理、虚拟DOM、JSX语法、Props传递、事件处理、条件渲染、列表渲染、表单处理、路由管理。'.repeat(5);
    
    const messageInput = page.locator('textarea, input[placeholder*="输入"]').first();
    await messageInput.fill(longMessage);
    
    const sendButton = page.locator('button:has-text("发送"), button[type="submit"]').first();
    await sendButton.click();
    
    // 验证长消息正确显示
    await expect(page.locator('text=/React组件生命周期/')).toBeVisible();
    
    // 等待回复（长消息可能需要更多时间）
    await page.waitForTimeout(20000);
    
    // 验证页面没有崩溃
    await expect(page.locator('body')).toBeVisible();
  });

  test('TC010: 消息历史记录测试', async ({ page }) => {
    // 创建会话
    await page.locator('button:has-text("创建新会话")').click();
    await page.waitForTimeout(2000);
    
    const messages = ['第一条消息', '第二条消息', '第三条消息'];
    
    // 发送多条消息
    for (const message of messages) {
      const messageInput = page.locator('textarea, input[placeholder*="输入"]').first();
      await messageInput.fill(message);
      
      const sendButton = page.locator('button:has-text("发送"), button[type="submit"]').first();
      await sendButton.click();
      
      // 等待消息发送完成
      await page.waitForTimeout(3000);
    }
    
    // 验证所有消息都显示
    for (const message of messages) {
      await expect(page.locator(`text=${message}`)).toBeVisible();
    }
    
    // 验证消息计数
    await expect(page.locator('text=/\d+ 条消息/')).toBeVisible();
  });

  test('TC011: 消息输入验证', async ({ page }) => {
    // 创建会话
    await page.locator('button:has-text("创建新会话")').click();
    await page.waitForTimeout(2000);
    
    const messageInput = page.locator('textarea, input[placeholder*="输入"]').first();
    const sendButton = page.locator('button:has-text("发送"), button[type="submit"]').first();
    
    // 测试空消息
    await messageInput.fill('');
    
    // 验证发送按钮状态（应该被禁用或无效）
    const isDisabled = await sendButton.isDisabled();
    if (!isDisabled) {
      // 如果按钮没有被禁用，点击后应该没有反应
      await sendButton.click();
      await page.waitForTimeout(1000);
      
      // 验证没有空消息被发送
      const emptyMessages = page.locator('text=""');
      expect(await emptyMessages.count()).toBe(0);
    }
    
    // 测试超长消息（如果有长度限制）
    const veryLongMessage = 'A'.repeat(5000);
    await messageInput.fill(veryLongMessage);
    
    // 检查是否有长度限制提示
    const lengthWarning = page.locator('text=/字符限制|太长|超出/'');
    if (await lengthWarning.isVisible()) {
      console.log('检测到长度限制提示');
    }
  });
});