"""
Cloak 指纹浏览器管理系统 API 调用示例
所有接口均使用 POST 方法，请求和响应均为 JSON 格式。

创建/更新窗口时使用比特浏览器风格字段名，例如：
  - groupId、browserFingerPrint（camelCase）
  - tags、homepageUrl；默认打开地址亦可用顶层 url（与 homepageUrl 同义）
  - 扩展指纹：webglVendor、cssFontList、rectX/Y/W/H、loadImages、pluginsEnabled 等

代理 IP：
  - 无认证接口：POST /proxy/list、/proxy/add、/proxy/delete、/proxy/check（见下方示例）
  - 比特文档中与创建窗口同传的 proxyMethod、proxyType、host、port 等：见
    build_example_bitbrowser_proxy_browser_update()；当前服务端创建窗口时可能仍未把内联代理写入档案，
    绑定代理可在客户端选择已创建的代理，或使用 REST PUT /api/v1/profiles/{id} 传 proxyId（需 X-Api-Key）

运行：
  python cloak_api_example.py              # 默认不删除数据，便于在客户端核对
  python cloak_api_example.py --cleanup  # 演示结束后删除本脚本创建的窗口与分组
"""

import argparse
import requests
import json
import sys
from typing import Dict, List, Any, Optional

# 设置控制台输出编码为 UTF-8，解决中文乱码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class CloakAPI:
    """Cloak API 客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:54381"):
        """
        初始化 API 客户端
        
        Args:
            base_url: API 基础地址
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        发送 POST 请求
        
        Args:
            endpoint: API 端点
            data: 请求数据
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # 尝试解析错误响应
            try:
                error_data = response.json()
                print(f"请求失败 [{response.status_code}]: {error_data}")
                return {"success": False, "error": str(e), "details": error_data}
            except:
                print(f"请求失败 [{response.status_code}]: {e}")
                return {"success": False, "error": str(e)}
    
    # ==================== 浏览器窗口接口 ====================
    
    def browser_update(self, browser_config: Dict) -> Dict:
        """
        创建浏览器窗口
        
        Args:
            browser_config: 浏览器配置信息
            
        Returns:
            创建结果
        """
        return self._post("/browser/update", browser_config)
    
    def browser_update_partial(self, updates: Dict) -> Dict:
        """
        部分更新浏览器窗口配置（支持单个或批量）
        
        Args:
            updates: 更新配置
            
        Returns:
            更新结果
        """
        return self._post("/browser/update/partial", updates)
    
    def browser_open(self, browser_id: str) -> Dict:
        """
        打开浏览器窗口，返回 CDP 连接信息
        
        Args:
            browser_id: 浏览器窗口 ID
            
        Returns:
            CDP 连接信息
        """
        return self._post("/browser/open", {"id": browser_id})
    
    def browser_close(self, browser_id: str) -> Dict:
        """
        关闭浏览器窗口
        
        Args:
            browser_id: 浏览器窗口 ID
            
        Returns:
            关闭结果
        """
        return self._post("/browser/close", {"id": browser_id})
    
    def browser_close_all(self) -> Dict:
        """
        关闭所有浏览器窗口
        
        Returns:
            关闭结果
        """
        return self._post("/browser/close/all")
    
    def browser_delete(self, browser_id: str) -> Dict:
        """
        删除浏览器窗口
        
        Args:
            browser_id: 浏览器窗口 ID
            
        Returns:
            删除结果
        """
        return self._post("/browser/delete", {"id": browser_id})
    
    def browser_detail(self, browser_id: str) -> Dict:
        """
        获取窗口详情
        
        Args:
            browser_id: 浏览器窗口 ID
            
        Returns:
            窗口详情
        """
        return self._post("/browser/detail", {"id": browser_id})
    
    def browser_list(self, page: int = 0, page_size: int = 10, group_id: Optional[str] = None) -> Dict:
        """
        获取窗口列表
        
        Args:
            page: 页码（从 0 开始，与 Cloak API 一致）
            page_size: 每页数量
            group_id: 分组 ID（可选）
            
        Returns:
            窗口列表
        """
        data = {
            "page": page,
            "pageSize": page_size
        }
        if group_id:
            data["groupId"] = group_id
        return self._post("/browser/list", data)
    
    def browser_pids_all(self) -> Dict:
        """
        获取所有窗口 PID
        
        Returns:
            所有窗口 PID
        """
        return self._post("/browser/pids/all")
    
    def browser_ports(self) -> Dict:
        """
        获取所有窗口调试端口
        
        Returns:
            所有窗口调试端口
        """
        return self._post("/browser/ports")
    
    # ==================== 批量操作接口 ====================
    
    def browser_create_batch(self, count: int, group_id: Optional[str] = None) -> Dict:
        """
        批量创建浏览器窗口
        
        Args:
            count: 创建数量（1-100）
            group_id: 分组 ID（可选，统一分配到同一分组）
            
        Returns:
            创建结果
        """
        data = {"count": count}
        if group_id:
            data["groupId"] = group_id
        return self._post("/browser/create/batch", data)
    
    def browser_open_batch(self, browser_ids: List[str]) -> Dict:
        """
        批量打开指定浏览器窗口
        
        Args:
            browser_ids: 浏览器窗口 ID 列表
            
        Returns:
            打开结果
        """
        return self._post("/browser/open/batch", {"ids": browser_ids})
    
    def browser_open_all(self) -> Dict:
        """
        打开所有已关闭浏览器窗口
        
        Returns:
            打开结果
        """
        return self._post("/browser/open/all")
    
    def browser_delete_batch(self, browser_ids: List[str]) -> Dict:
        """
        批量删除指定浏览器窗口
        
        Args:
            browser_ids: 浏览器窗口 ID 列表
            
        Returns:
            删除结果
        """
        return self._post("/browser/delete/batch", {"ids": browser_ids})
    
    def browser_delete_all(self) -> Dict:
        """
        删除所有浏览器窗口
        
        Returns:
            删除结果
        """
        return self._post("/browser/delete/all")
    
    def browser_close_batch(self, browser_ids: List[str]) -> Dict:
        """
        批量关闭指定浏览器窗口
        
        Args:
            browser_ids: 浏览器窗口 ID 列表
            
        Returns:
            关闭结果
        """
        return self._post("/browser/close/batch", {"ids": browser_ids})
    
    # ==================== 分组管理接口 ====================
    
    def group_list(self) -> Dict:
        """
        获取分组列表
        
        Returns:
            分组列表
        """
        return self._post("/group/list")
    
    def group_add(self, name: str, sort_num: Optional[int] = None) -> Dict:
        """
        添加分组
        
        Args:
            name: 分组名称
            sort_num: 排序序号（可选）
            
        Returns:
            添加结果
        """
        data = {"groupName": name}
        if sort_num is not None:
            data["sortNum"] = sort_num
        return self._post("/group/add", data)
    
    def group_edit(self, group_id: str, name: str, sort_num: Optional[int] = None) -> Dict:
        """
        编辑分组
        
        Args:
            group_id: 分组 ID
            name: 分组名称
            sort_num: 排序序号（可选）
            
        Returns:
            编辑结果
        """
        data = {
            "id": group_id,
            "groupName": name
        }
        if sort_num is not None:
            data["sortNum"] = sort_num
        return self._post("/group/edit", data)
    
    def group_delete(self, group_id: str) -> Dict:
        """
        删除分组
        
        Args:
            group_id: 分组 ID
            
        Returns:
            删除结果
        """
        return self._post("/group/delete", {"id": group_id})
    
    def group_detail(self, group_id: str) -> Dict:
        """
        获取分组详情
        
        Args:
            group_id: 分组 ID
            
        Returns:
            分组详情
        """
        return self._post("/group/detail", {"id": group_id})

    # ==================== 代理 IP 接口（无需 X-Api-Key）====================

    def proxy_list(self) -> Dict:
        """获取代理列表 POST /proxy/list"""
        return self._post("/proxy/list", {})

    def proxy_add(self, payload: Dict[str, Any]) -> Dict:
        """
        创建代理 POST /proxy/add

        payload 使用 camelCase，与 Swagger CreateProxyRequest 一致，例如::
            {
                "name": "我的代理",
                "type": "SOCKS5",
                "host": "1.2.3.4",
                "port": "1080",
                "username": null,
                "password": null,
                "ipQueryChannel": "ip-api",
                "ipProtocol": "ipv4",
                "refreshUrl": null,
                "remark": null,
            }
        """
        return self._post("/proxy/add", payload)

    def proxy_delete(self, proxy_id: str) -> Dict:
        """删除代理 POST /proxy/delete"""
        return self._post("/proxy/delete", {"id": proxy_id})

    def proxy_check(self, proxy_id: str) -> Dict:
        """检测代理 POST /proxy/check"""
        return self._post("/proxy/check", {"id": proxy_id})


def print_result(title: str, result: Dict):
    """打印结果"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_demo_browser_fingerprint() -> Dict[str, Any]:
    """
    比特浏览器风格（camelCase）指纹对象，对应 Rust API 中 browserFingerPrint。
    含扩展字段：WebGL、Rect、CSS 字体、Canvas 字体、loadImages、pluginsEnabled 等。
    """
    return {
        "coreVersion": "130",
        "ostype": "PC",
        "os": "Win32",
        "osVersion": "11,10",
        "userAgent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        ),
        "timeZone": "Asia/Shanghai",
        "languages": "zh-CN",
        "webRTC": "3",
        "openWidth": 1280,
        "openHeight": 720,
        "windowX": 0,
        "windowY": 0,
        "resolution": "1920x1080",
        "devicePixelRatio": 1.0,
        "hardwareConcurrency": "8",
        "deviceMemory": "8",
        "canvas": "0",
        "webGL": "0",
        "audioContext": "0",
        # 扩展指纹（与 Swagger / handlers 一致）
        "webglVendor": "Google Inc. (Intel)",
        "webglRenderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "rectX": 0.0,
        "rectY": 0.0,
        "rectW": 0.0,
        "rectH": 0.0,
        "canvasFontFingerprint": 0.0,
        "cssFontList": "Calibri,SimHei,Arial,Microsoft YaHei,Times New Roman",
        "cssFontWidthOffset": 0,
        "cssFontHeightOffset": 0,
        "loadImages": True,
        "pluginsEnabled": True,
    }


def build_example_bitbrowser_proxy_browser_update() -> Dict[str, Any]:
    """
    比特浏览器文档中与「创建窗口」一并提交的代理字段示例（用于 Swagger 试调或兼容客户端）。
    字段含义：proxyMethod 2=自定义、3=API 提取；proxyType: noproxy/http/https/socks5；
    host/port/proxyUserName/proxyPassword 为代理连接信息。

    注意：请以当前 Cloak 服务端实现为准；若创建后窗口未自动绑定代理，请先 POST /proxy/add 再在客户端绑定，
    或使用带 X-Api-Key 的 REST 更新档案接口。
    """
    return {
        "name": "带代理的窗口示例",
        "proxyMethod": 2,
        "proxyType": "socks5",
        "host": "1.2.3.4",
        "port": 1080,
        "proxyUserName": "",
        "proxyPassword": "",
        "browserFingerPrint": {
            "coreVersion": "130",
            "ostype": "PC",
            "os": "Win32",
        },
    }


def build_demo_browser_update_body(group_id: str) -> Dict[str, Any]:
    """
    POST /browser/update 请求体示例。
    - groupId：分组（比特风格 camelCase）
    - tags、homepageUrl：档案级字段
    - 默认打开地址也可用顶层字段 url（与 homepageUrl 同义，二选一）
    """
    return {
        "name": "Python测试浏览器",
        "groupId": group_id,
        "tags": ["python-api-demo"],
        # 默认打开地址（与比特文档中的 url 同义，任选其一）
        "homepageUrl": "https://www.example.com",
        # "url": "https://www.example.com",
        "randomFingerprint": False,
        "browserFingerPrint": build_demo_browser_fingerprint(),
    }


def main():
    """主函数 - 演示 API；默认不删除数据，便于在 Cloak 客户端核对。"""
    parser = argparse.ArgumentParser(
        description="Cloak 指纹浏览器 API 调用示例（/browser/update 等为比特风格 JSON）"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="演示结束后删除本脚本创建的分组与相关浏览器窗口（默认不删除）",
    )
    args = parser.parse_args()

    api = CloakAPI()
    ids_to_cleanup: List[str] = []
    proxy_ids_to_cleanup: List[str] = []

    print("Cloak 指纹浏览器管理系统 API 调用示例")
    print("=" * 60)
    if not args.cleanup:
        print("提示: 默认保留创建的窗口与分组，便于在客户端核对。")
        print("     若需自动清理，请追加参数:  python cloak_api_example.py --cleanup")
    print("=" * 60)

    # ==================== 分组管理示例 ====================
    print("\n\n【分组管理接口示例】")

    print_result("1. 获取分组列表", api.group_list())

    group_result = api.group_add(name="Python测试分组")
    print_result("2. 添加分组", group_result)

    if group_result.get("success"):
        group_id = group_result.get("data", {}).get("id")
        print(f"\n✓ 成功创建分组，ID: {group_id}")
    else:
        print("\n✗ 创建分组失败，使用现有分组进行测试")
        groups = api.group_list()
        if groups.get("success") and groups.get("data", {}).get("list"):
            group_id = groups["data"]["list"][0]["id"]
            print(f"使用现有分组 ID: {group_id}")
        else:
            group_id = "default"

    print_result("3. 获取分组详情", api.group_detail(group_id))

    if group_id != "default":
        print_result(
            "4. 编辑分组",
            api.group_edit(group_id=group_id, name="Python测试分组（已修改）"),
        )

    # ==================== 代理 IP 接口示例 ====================
    print("\n\n【代理 IP 接口示例】")

    print_result("代理-1. 获取代理列表", api.proxy_list())

    proxy_add_payload = {
        "name": "Python示例代理",
        "type": "SOCKS5",
        "host": "127.0.0.1",
        "port": "1080",
        "remark": "cloak_api_example.py 演示用（请改为真实代理地址）",
    }
    proxy_create = api.proxy_add(proxy_add_payload)
    print_result("代理-2. 创建代理（自定义 SOCKS5，host/port 请按环境修改）", proxy_create)

    demo_proxy_id: Optional[str] = None
    if proxy_create.get("success") and proxy_create.get("data"):
        demo_proxy_id = proxy_create["data"].get("id")
        if demo_proxy_id:
            proxy_ids_to_cleanup.append(demo_proxy_id)
            print_result("代理-3. 检测代理", api.proxy_check(demo_proxy_id))

    print(
        "\n【说明】比特浏览器风格「创建窗口 + 内联代理」JSON 示例（可与 Swagger 对照，字段以服务端为准）："
    )
    print(json.dumps(build_example_bitbrowser_proxy_browser_update(), indent=2, ensure_ascii=False))

    # ==================== 浏览器窗口接口示例 ====================
    print("\n\n【浏览器窗口接口示例】")

    browser_config = build_demo_browser_update_body(group_id)
    browser_result = api.browser_update(browser_config)
    print_result("5. 创建浏览器窗口（browserFingerPrint + homepageUrl + tags）", browser_result)

    if browser_result.get("success"):
        browser_id = browser_result.get("data", {}).get("id")
        print(f"\n✓ 成功创建浏览器，ID: {browser_id}")
        if browser_id:
            ids_to_cleanup.append(browser_id)
    else:
        print("\n✗ 创建浏览器失败，使用现有浏览器进行测试")
        browsers = api.browser_list(page=0, page_size=1)
        if browsers.get("success") and browsers.get("data", {}).get("list"):
            browser_id = browsers["data"]["list"][0]["id"]
            print(f"使用现有浏览器 ID: {browser_id}")
        else:
            browser_id = None

    if browser_id:
        print_result("6. 获取窗口详情", api.browser_detail(browser_id))

        # 部分更新：名称、默认地址（亦可用 url）、指纹子集（扩展字段）
        print_result(
            "7. 部分更新浏览器窗口配置",
            api.browser_update_partial(
                {
                    "id": browser_id,
                    "name": "Python测试浏览器（已修改）",
                    # 与 homepageUrl 同义，演示比特字段名 url
                    "url": "https://www.example.com/partial-updated",
                    "browserFingerPrint": {
                        "cssFontList": "Arial,Helvetica,Microsoft YaHei,sans-serif",
                        "cssFontWidthOffset": 5,
                        "cssFontHeightOffset": 5,
                        "webglVendor": "Google Inc. (NVIDIA)",
                    },
                }
            ),
        )

    print_result("8. 获取窗口列表（page 从 0 开始）", api.browser_list(page=0, page_size=10))

    if browser_id:
        print_result("9. 打开浏览器窗口", api.browser_open(browser_id))

    print_result("10. 获取所有窗口 PID", api.browser_pids_all())
    print_result("11. 获取所有窗口调试端口", api.browser_ports())

    if browser_id:
        print_result("12. 关闭浏览器窗口", api.browser_close(browser_id))

    # ==================== 批量操作接口示例 ====================
    print("\n\n【批量操作接口示例】")

    batch_result = api.browser_create_batch(count=2, group_id=group_id)
    print_result("13. 批量创建浏览器窗口", batch_result)
    if batch_result.get("success") and batch_result.get("data"):
        extra_ids = batch_result["data"].get("ids") or []
        ids_to_cleanup.extend(extra_ids)

    all_browsers = api.browser_list(page=0, page_size=100)
    if all_browsers.get("success"):
        batch_ids = [b["id"] for b in all_browsers.get("data", {}).get("list", [])[:3]]
    else:
        batch_ids = []

    if batch_ids:
        print_result("14. 批量打开指定浏览器窗口", api.browser_open_batch(batch_ids))
        print_result("15. 批量关闭指定浏览器窗口", api.browser_close_batch(batch_ids))

    print_result("16. 打开所有已关闭浏览器窗口", api.browser_open_all())
    print_result("17. 关闭所有浏览器窗口", api.browser_close_all())

    # 可选清理（默认不执行，避免无法在客户端核对）
    if args.cleanup:
        print("\n\n【清理测试数据 (--cleanup)】")
        unique_ids = list(dict.fromkeys(ids_to_cleanup))
        if unique_ids:
            print_result("18. 批量删除本脚本涉及的浏览器窗口", api.browser_delete_batch(unique_ids))
        for pid in proxy_ids_to_cleanup:
            print_result(f"删除演示代理 {pid}", api.proxy_delete(pid))
        if group_id and group_id != "default":
            print_result("19. 删除测试分组", api.group_delete(group_id))
        print("\n✓ 已按 --cleanup 删除测试分组与相关窗口。")
    else:
        print("\n\n【未执行删除】")
        print(f"  本脚本记录的窗口 ID（可在客户端核对）: {ids_to_cleanup or '（无）'}")
        print(f"  分组 ID: {group_id}")
        print("  需要清理时请运行: python cloak_api_example.py --cleanup")

    print("\n\n✓ 所有 API 调用示例完成！")


if __name__ == "__main__":
    # 入口：默认保留演示创建的窗口与分组，便于在 Cloak 客户端核对。
    # 若需在脚本结束后自动删除本脚本创建的窗口与测试分组，请使用：
    #   python cloak_api_example.py --cleanup
    main()

