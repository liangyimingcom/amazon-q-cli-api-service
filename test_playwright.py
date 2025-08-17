#!/usr/bin/env python3
# 测试 Playwright 安装和浏览器可用性

try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright 模块导入成功")
    
    with sync_playwright() as p:
        print("✅ Playwright 上下文创建成功")
        
        # 检查可用的浏览器
        browsers = []
        try:
            browser = p.chromium.launch(headless=True)
            browsers.append("chromium")
            browser.close()
            print("✅ Chromium 浏览器可用")
        except Exception as e:
            print(f"❌ Chromium 浏览器不可用: {e}")
            
        try:
            browser = p.firefox.launch(headless=True)
            browsers.append("firefox")
            browser.close()
            print("✅ Firefox 浏览器可用")
        except Exception as e:
            print(f"❌ Firefox 浏览器不可用: {e}")
            
        try:
            browser = p.webkit.launch(headless=True)
            browsers.append("webkit")
            browser.close()
            print("✅ WebKit 浏览器可用")
        except Exception as e:
            print(f"❌ WebKit 浏览器不可用: {e}")
            
        print(f"可用浏览器: {browsers}")
        
except ImportError as e:
    print(f"❌ Playwright 模块导入失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")