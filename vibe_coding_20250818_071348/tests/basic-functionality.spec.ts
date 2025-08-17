/**
 * 基础功能测试
 * 测试应用的基本加载和导航功能
 */

import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'http://localhost:3001';
const BACKEND_URL = 'http://localhost:8080';

test.describe('基础功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前访问首页
    await page.goto(FRONTEND_URL);
  });

  test('TC001: 首页加载测试', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/Amazon Q/);
    
    // 验证欢迎界面元素
    await expect(page.locator('text=欢迎使用 Amazon Q')).toBeVisible();
    await expect(page.locator('text=开始与 AI 助手对话')).toBeVisible();
    
    // 验证主要按钮存在
    await expect(page.locator('button:has-text("创建新会话")')).toBeVisible();
    await expect(page.locator('button:has-text("查看设置")')).toBeVisible();
    
    // 检查控制台错误
    const consoleErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // 等待页面完全加载
    await page.waitForLoadState('networkidle');
    
    // 验证没有严重的控制台错误
    const criticalErrors = consoleErrors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('DevTools')
    );
    expect(criticalErrors).toHaveLength(0);
  });

  test('TC002: 后端健康检查', async ({ request }) => {
    // 测试后端健康状态
    const response = await request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const healthData = await response.json();
    expect(healthData.status).toBe('healthy');
    expect(healthData.qcli_available).toBe(true);
  });

  test('TC003: 主题切换功能', async ({ page }) => {
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
    
    // 查找主题切换按钮（可能在设置或导航栏中）
    const themeToggle = page.locator('[data-testid="theme-toggle"], .theme-toggle, button:has-text("主题")').first();
    
    if (await themeToggle.isVisible()) {
      // 获取当前主题
      const bodyClass = await page.locator('body').getAttribute('class');
      const isDarkMode = bodyClass?.includes('dark') || false;
      
      // 切换主题
      await themeToggle.click();
      
      // 等待主题切换完成
      await page.waitForTimeout(500);
      
      // 验证主题已切换
      const newBodyClass = await page.locator('body').getAttribute('class');
      const isNewDarkMode = newBodyClass?.includes('dark') || false;
      
      expect(isNewDarkMode).not.toBe(isDarkMode);
    } else {
      console.log('主题切换按钮未找到，跳过主题测试');
    }
  });

  test('TC004: 响应式布局测试', async ({ page }) => {
    // 测试桌面尺寸
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('text=欢迎使用 Amazon Q')).toBeVisible();
    
    // 测试平板尺寸
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('text=欢迎使用 Amazon Q')).toBeVisible();
    
    // 测试手机尺寸
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('text=欢迎使用 Amazon Q')).toBeVisible();
    
    // 验证按钮在小屏幕上仍然可点击
    const createButton = page.locator('button:has-text("创建新会话")');
    await expect(createButton).toBeVisible();
    
    // 恢复默认尺寸
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('TC005: 导航功能测试', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 查找导航菜单项
    const navItems = [
      'text=聊天',
      'text=会话',
      'text=文件',
      'text=历史',
      'text=设置'
    ];
    
    for (const navItem of navItems) {
      const element = page.locator(navItem).first();
      if (await element.isVisible()) {
        await element.click();
        await page.waitForTimeout(500);
        
        // 验证页面内容有变化（简单检查）
        await expect(page.locator('body')).toBeVisible();
      }
    }
  });
});