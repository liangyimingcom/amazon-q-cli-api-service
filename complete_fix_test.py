#!/usr/bin/env python3
"""
完整的AI回复内容显示修复测试
使用Playwright进行端到端测试
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright
from datetime import datetime

async def test_frontend_streaming():
    """测试前端流式对话功能"""
    print("🎭 启动前端流式对话测试...")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 访问前端页面
            print("📱 访问前端页面...")
            await page.goto('http://localhost:3001')
            await page.wait_for_load_state('networkidle')
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 检查是否显示欢迎界面
            welcome_button = page.locator('button:has-text("创建新会话")')
            if await welcome_button.is_visible():
                print("✅ 欢迎界面显示正常")
                await welcome_button.click()
                await asyncio.sleep(2)
            
            # 查找消息输入框
            input_selector = 'textarea[placeholder*="输入消息"], input[placeholder*="输入消息"]'
            await page.wait_for_selector(input_selector, timeout=10000)
            print("✅ 找到消息输入框")
            
            # 启用流式模式
            stream_switch = page.locator('text=流式模式').locator('..').locator('.ant-switch')
            if await stream_switch.is_visible():
                is_checked = await stream_switch.is_checked()
                if not is_checked:
                    await stream_switch.click()
                    print("✅ 启用流式模式")
                else:
                    print("✅ 流式模式已启用")
            
            # 输入测试消息
            test_message = "请简单介绍一下Amazon Q的主要功能"
            await page.fill(input_selector, test_message)
            print(f"✅ 输入测试消息: {test_message}")
            
            # 发送消息
            send_button = page.locator('button[type="submit"], button:has-text("发送")')
            await send_button.click()
            print("📤 发送消息")
            
            # 等待AI回复开始
            await asyncio.sleep(3)
            
            # 监控消息列表变化
            print("👀 监控AI回复内容...")
            
            # 等待AI消息出现
            ai_message_selector = '.ant-card:has(.anticon-robot)'
            await page.wait_for_selector(ai_message_selector, timeout=30000)
            print("✅ AI消息容器出现")
            
            # 监控流式内容更新
            previous_content = ""
            update_count = 0
            max_wait_time = 30  # 最多等待30秒
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    # 获取AI消息内容
                    ai_messages = await page.locator(ai_message_selector).all()
                    if ai_messages:
                        # 获取最后一条AI消息的内容
                        last_ai_message = ai_messages[-1]
                        content_element = last_ai_message.locator('.ant-typography')
                        current_content = await content_element.text_content()
                        
                        if current_content and current_content != previous_content:
                            update_count += 1
                            print(f"  📝 内容更新 {update_count}: {current_content[:100]}...")
                            previous_content = current_content
                            
                            # 检查是否包含完整回复
                            if len(current_content) > 50 and not current_content.endswith('...'):
                                # 等待一下看是否还有更新
                                await asyncio.sleep(2)
                                final_content = await content_element.text_content()
                                if final_content == current_content:
                                    print("✅ 流式内容更新完成")
                                    break
                    
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️  监控过程中出现异常: {e}")
                    break
            
            # 获取最终内容
            final_content = previous_content
            print(f"\n📊 测试结果:")
            print(f"  内容更新次数: {update_count}")
            print(f"  最终内容长度: {len(final_content)}")
            print(f"  最终内容: {final_content}")
            
            # 判断测试结果
            success = (
                update_count > 0 and 
                len(final_content) > 20 and 
                "Amazon Q" in final_content
            )
            
            if success:
                print("🎉 流式对话测试成功！")
                return True
            else:
                print("❌ 流式对话测试失败")
                return False
                
        except Exception as e:
            print(f"❌ 测试过程中出现异常: {e}")
            return False
            
        finally:
            await browser.close()

async def test_standard_chat():
    """测试标准聊天功能"""
    print("🎭 启动前端标准聊天测试...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 访问前端页面
            await page.goto('http://localhost:3001')
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # 创建新会话
            welcome_button = page.locator('button:has-text("创建新会话")')
            if await welcome_button.is_visible():
                await welcome_button.click()
                await asyncio.sleep(2)
            
            # 关闭流式模式
            stream_switch = page.locator('text=流式模式').locator('..').locator('.ant-switch')
            if await stream_switch.is_visible():
                is_checked = await stream_switch.is_checked()
                if is_checked:
                    await stream_switch.click()
                    print("✅ 关闭流式模式")
                else:
                    print("✅ 流式模式已关闭")
            
            # 输入测试消息
            input_selector = 'textarea[placeholder*="输入消息"], input[placeholder*="输入消息"]'
            test_message = "你好，请简单介绍一下你自己"
            await page.fill(input_selector, test_message)
            
            # 发送消息
            send_button = page.locator('button[type="submit"], button:has-text("发送")')
            await send_button.click()
            print("📤 发送标准消息")
            
            # 等待AI回复
            ai_message_selector = '.ant-card:has(.anticon-robot)'
            await page.wait_for_selector(ai_message_selector, timeout=30000)
            
            # 获取AI回复内容
            await asyncio.sleep(3)  # 等待内容完全加载
            ai_messages = await page.locator(ai_message_selector).all()
            if ai_messages:
                last_ai_message = ai_messages[-1]
                content_element = last_ai_message.locator('.ant-typography')
                content = await content_element.text_content()
                
                print(f"📝 AI回复内容: {content}")
                
                success = len(content) > 20 and "Amazon Q" in content
                if success:
                    print("🎉 标准聊天测试成功！")
                    return True
                else:
                    print("❌ 标准聊天测试失败")
                    return False
            
        except Exception as e:
            print(f"❌ 标准聊天测试异常: {e}")
            return False
            
        finally:
            await browser.close()

async def main():
    """主测试函数"""
    print("🚀 开始完整的AI回复内容显示修复测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查服务状态
    import requests
    try:
        health_response = requests.get('http://localhost:8080/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ 后端服务正常")
        else:
            print(f"⚠️  后端服务状态异常: {health_response.status_code}")
            return
    except:
        print("❌ 后端服务不可用")
        return
    
    try:
        frontend_response = requests.get('http://localhost:3001', timeout=5)
        print("✅ 前端服务正常")
    except:
        print("❌ 前端服务不可用")
        return
    
    # 运行测试
    results = {}
    
    print("\n🧪 测试1: 标准聊天功能")
    results['标准聊天'] = await test_standard_chat()
    
    print("\n🧪 测试2: 流式聊天功能")  
    results['流式聊天'] = await test_frontend_streaming()
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    all_passed = True
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！AI回复内容显示问题已完全修复！")
        print("\n✨ 修复成果:")
        print("  ✅ 标准对话功能完全正常")
        print("  ✅ 流式对话功能完全正常") 
        print("  ✅ 前端正确显示AI回复内容")
        print("  ✅ 流式内容正确累积显示")
    else:
        print("\n⚠️  部分测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())