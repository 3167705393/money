"""数据管理模块 - 资金追踪系统"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

# 数据文件路径
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
FUNDS_FILE = DATA_DIR / "funds.json"
HISTORY_FILE = DATA_DIR / "history.json"


def _ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(file_path: Path, default: dict) -> dict:
    """加载JSON文件"""
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _save_json(file_path: Path, data: dict):
    """保存JSON文件"""
    _ensure_data_dir()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========== 平台和渠道类型管理 ==========

def get_platforms() -> list[dict]:
    """获取所有平台"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    return data.get("platforms", [])


def get_channel_types() -> list[dict]:
    """获取所有渠道类型"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    return data.get("channel_types", [])


def add_platform(name: str, icon: str = "💰") -> dict:
    """添加平台"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    platform = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "icon": icon
    }
    data["platforms"].append(platform)
    _save_json(ACCOUNTS_FILE, data)
    return platform


def update_platform(platform_id: str, name: str = None, icon: str = None) -> Optional[dict]:
    """更新平台"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    for i, p in enumerate(data["platforms"]):
        if p["id"] == platform_id:
            if name:
                p["name"] = name
            if icon:
                p["icon"] = icon
            data["platforms"][i] = p
            _save_json(ACCOUNTS_FILE, data)
            return p
    return None


def delete_platform(platform_id: str) -> bool:
    """删除平台"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    for i, p in enumerate(data["platforms"]):
        if p["id"] == platform_id:
            data["platforms"].pop(i)
            _save_json(ACCOUNTS_FILE, data)
            return True
    return False


def add_channel_type(name: str) -> dict:
    """添加渠道类型"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    channel = {
        "id": str(uuid.uuid4())[:8],
        "name": name
    }
    data["channel_types"].append(channel)
    _save_json(ACCOUNTS_FILE, data)
    return channel


def update_channel_type(channel_id: str, name: str) -> Optional[dict]:
    """更新渠道类型"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    for i, c in enumerate(data["channel_types"]):
        if c["id"] == channel_id:
            c["name"] = name
            data["channel_types"][i] = c
            _save_json(ACCOUNTS_FILE, data)
            return c
    return None


def delete_channel_type(channel_id: str) -> bool:
    """删除渠道类型"""
    data = _load_json(ACCOUNTS_FILE, {"platforms": [], "channel_types": []})
    for i, c in enumerate(data["channel_types"]):
        if c["id"] == channel_id:
            data["channel_types"].pop(i)
            _save_json(ACCOUNTS_FILE, data)
            return True
    return False


def get_platform_name(platform_id: str) -> str:
    """获取平台名称"""
    for p in get_platforms():
        if p["id"] == platform_id:
            return f"{p['icon']} {p['name']}"
    return "未知平台"


def get_channel_name(channel_id: str) -> str:
    """获取渠道名称"""
    for c in get_channel_types():
        if c["id"] == channel_id:
            return c["name"]
    return "未知渠道"


# ========== 资金记录管理 ==========

def get_all_records() -> list[dict]:
    """获取所有资金记录"""
    data = _load_json(FUNDS_FILE, {"records": []})
    return data.get("records", [])


def get_record_by_id(record_id: str) -> Optional[dict]:
    """根据ID获取记录"""
    for record in get_all_records():
        if record["id"] == record_id:
            return record
    return None


def add_record(platform_id: str, channel_type: str, amount: float,
               note: str = "") -> dict:
    """添加资金记录"""
    data = _load_json(FUNDS_FILE, {"records": []})
    record = {
        "id": str(uuid.uuid4())[:8],
        "platform_id": platform_id,
        "channel_type": channel_type,
        "amount": amount,
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "updated_at": datetime.now().strftime("%Y-%m-%d")
    }
    data["records"].append(record)
    _save_json(FUNDS_FILE, data)

    # 记录初始历史
    add_history(record["id"], 0, amount, "初始录入")

    return record


def update_record(record_id: str, **kwargs) -> Optional[dict]:
    """更新资金记录"""
    data = _load_json(FUNDS_FILE, {"records": []})
    for i, record in enumerate(data["records"]):
        if record["id"] == record_id:
            old_amount = record["amount"]

            # 更新字段
            for key, value in kwargs.items():
                if key in ["platform_id", "channel_type", "amount", "note"]:
                    record[key] = value

            record["updated_at"] = datetime.now().strftime("%Y-%m-%d")
            data["records"][i] = record
            _save_json(FUNDS_FILE, data)

            # 如果金额变化，记录历史
            if "amount" in kwargs and kwargs["amount"] != old_amount:
                add_history(record_id, old_amount, kwargs["amount"],
                           kwargs.get("note", ""))

            return record
    return None


def delete_record(record_id: str) -> bool:
    """删除资金记录"""
    data = _load_json(FUNDS_FILE, {"records": []})
    for i, record in enumerate(data["records"]):
        if record["id"] == record_id:
            data["records"].pop(i)
            _save_json(FUNDS_FILE, data)
            return True
    return False


# ========== 变动历史管理 ==========

def get_all_history() -> list[dict]:
    """获取所有变动历史"""
    data = _load_json(HISTORY_FILE, {"changes": []})
    return data.get("changes", [])


def add_history(record_id: str, old_amount: float, new_amount: float,
                note: str = "") -> dict:
    """添加变动历史"""
    data = _load_json(HISTORY_FILE, {"changes": []})
    change = {
        "id": str(uuid.uuid4())[:8],
        "record_id": record_id,
        "old_amount": old_amount,
        "new_amount": new_amount,
        "change": new_amount - old_amount,
        "note": note,
        "changed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["changes"].insert(0, change)  # 最新的在前面
    _save_json(HISTORY_FILE, data)
    return change


def get_history_by_record(record_id: str) -> list[dict]:
    """获取某条记录的所有变动历史"""
    return [h for h in get_all_history() if h["record_id"] == record_id]


# ========== 统计功能 ==========

def get_total_amount() -> float:
    """获取总金额"""
    return sum(r["amount"] for r in get_all_records())


def get_platform_stats() -> dict[str, float]:
    """获取各平台金额统计"""
    stats = {}
    for record in get_all_records():
        pid = record["platform_id"]
        stats[pid] = stats.get(pid, 0) + record["amount"]
    return stats


def get_channel_stats() -> dict[str, float]:
    """获取各渠道金额统计"""
    stats = {}
    for record in get_all_records():
        cid = record["channel_type"]
        stats[cid] = stats.get(cid, 0) + record["amount"]
    return stats


def get_recent_history(limit: int = 10) -> list[dict]:
    """获取最近的变动历史"""
    return get_all_history()[:limit]


def init_default_data():
    """初始化默认数据"""
    _ensure_data_dir()

    if not ACCOUNTS_FILE.exists():
        default_data = {
            "platforms": [
                {"id": "alipay", "name": "支付宝", "icon": "💳"},
                {"id": "wechat", "name": "微信", "icon": "💚"},
                {"id": "icbc", "name": "工商银行", "icon": "🏦"},
                {"id": "ccb", "name": "建设银行", "icon": "🏛️"},
                {"id": "citic", "name": "中信证券", "icon": "📈"},
                {"id": "cash", "name": "现金", "icon": "💵"}
            ],
            "channel_types": [
                {"id": "checking", "name": "活期"},
                {"id": "fixed", "name": "定期"},
                {"id": "fund", "name": "理财"},
                {"id": "stock", "name": "股票"},
                {"id": "other", "name": "其他"}
            ]
        }
        _save_json(ACCOUNTS_FILE, default_data)

    if not FUNDS_FILE.exists():
        _save_json(FUNDS_FILE, {"records": []})

    if not HISTORY_FILE.exists():
        _save_json(HISTORY_FILE, {"changes": []})


# 初始化数据
init_default_data()