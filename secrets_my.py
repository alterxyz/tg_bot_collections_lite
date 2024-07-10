import datetime
import json
import os
import sys
from typing import Dict, Any


def get_secret(
    secret_group: str, secret_key: str, secrets_file: str = "secrets_my.json"
) -> str:
    """Retrieves a specific secret from a JSON configuration file."""
    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
        return secrets[secret_group]["Inner Keys"][secret_key]
    except FileNotFoundError:
        raise FileNotFoundError(f"Secrets file not found: {secrets_file}")
    except KeyError:
        raise KeyError(f"Secret not found: Group '{secret_group}', Key '{secret_key}'")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in secrets file: {secrets_file}")


def to_env(secret_group: str, secrets_file: str = "secrets_my.json") -> None:
    """
    我们读取选定group的所有inner key from secrets_my.json, 然后比较每个key的value和系统环境变量的value。
    如果存在且不同，我们存储到一个临时的字典"temp_env"中.
    然后我们overwrite系统环境变量的值, 使其与secrets_my.json中的值相同。
    我们将"temp_env"中的值写入到 secrets_my.json 文件中 - 新建一个小属性, 名字是 当天的日期, 也就是
    然后再check一次系统的环境变量和secrets_my.json中的值是否相同。
    """
    inner_keys = load_inner_keys(
        secret_group, secrets_file
    )  # 读取选定group的所有inner key
    temp_env = check_env(
        inner_keys, secret_group
    )  # 比较每个key的value和系统环境变量的value
    set_environment_variables(temp_env)  # overwrite系统环境变量的值
    keys = datetime.now().strftime("%Y-%m-%d")
    write_inner_keys_to_my(
        secret_group, keys, temp_env, secrets_file
    )  # 将"temp_env"中的值写入到 secrets_my.json 文件中
    check_env(
        inner_keys, secret_group
    )  # 再check一次系统的环境变量和secrets_my.json中的值是否相同
    return None


def get_environment_variables(group_secrets=None):
    """获取环境变量。如果有group_secrets, 返回group_secrets中的key, 否则返回所有环境变量。"""
    if group_secrets is not None:
        return {key: os.environ.get(key) for key in group_secrets}
    else:
        return dict(os.environ)


def set_environment_variables(keys: dict):
    """设置环境变量。"""
    for key, value in keys.items():
        os.environ[key] = value
        # 直接修改系统的环境变量
        os.system(f'echo "export {key}={value}" >> /etc/environment')


def check_env(inner_keys: dict, group_secrets: str) -> dict:
    """对比. 将不一样的key-value存储到一个字典中."""
    my_var = inner_keys
    env_var = get_environment_variables(group_secrets)
    temp_env = {}

    print("Checking environment variables:")
    for key, json_value in my_var.items():
        env_value = env_var.get(key)
        if env_value is None:
            print(f"{key} missing !")
        elif env_value == json_value:
            print(f"{key} pass")
        else:
            print(f"{key} different ! (JSON: {json_value}, Env: {env_value})")
            temp_env[key] = json_value
    return temp_env


def write_inner_keys_to_my(
    group_secrets: str, keys: str, temp_env: dict, secrets_file: str = "secrets_my.json"
) -> None:
    for key, value in temp_env.items():
        write_inner_key_to_my(group_secrets, keys, key, value, secrets_file)
    return None


import json


def write_inner_key_to_my(
    group_secrets: str,
    keys: str,
    key: str,
    value: str,
    secrets_file: str = "secrets_my.json",
) -> None:
    """将key-value写入到secrets_my.json文件中, 如果没有 "keys" 它会自己创建.

    Args:
        group_secrets (str): secrets组的名称.
        keys (str): secrets键的名称.
        key (str): 要写入的内部键.
        value (str): 要写入的值.
        secrets_file (str, optional): secrets文件的名称. 默认为 "secrets_my.json".

    Raises:
        FileNotFoundError: 如果secrets文件不存在.
        ValueError: 如果secrets文件格式错误.
    """
    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
    except FileNotFoundError:
        secrets = {}

    if group_secrets not in secrets:
        secrets[group_secrets] = {}
    if keys not in secrets[group_secrets]:
        secrets[group_secrets][keys] = {}

    secrets[group_secrets][keys][key] = value

    with open(secrets_file, "w") as f:
        json.dump(secrets, f, indent=4)

    return None


####################


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Loads and returns the content of a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")


def load_inner_keys(
    group: str, secrets_file: str = "secrets_my.json"
) -> Dict[str, str]:
    """Loads the inner keys of a specific group from the secrets file."""
    try:
        with open(secrets_file, "r") as f:
            secrets = json.load(f)
        return secrets[group]["Inner Keys"]
    except FileNotFoundError:
        raise FileNotFoundError(f"Secrets file not found: {secrets_file}")
    except KeyError:
        raise KeyError(f"Group not found: {group}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in secrets file: {secrets_file}")


def init_json(
    example_secrets_file: str = "secrets_example.json",
    my_secrets_file: str = "secrets_my.json",
):
    """Initializes the user's secrets file based on an example template."""
    try:
        example_secrets = load_json_file(example_secrets_file)
        target_secrets = (
            load_json_file(my_secrets_file) if os.path.exists(my_secrets_file) else {}
        )

        for group, group_data in example_secrets.items():
            target_secrets.setdefault(group, {})
            for key_type in ["Inner Keys", "Outter Keys"]:
                target_secrets[group].setdefault(key_type, {})
                for key in group_data.get(key_type, {}):
                    if key not in target_secrets[group][key_type]:
                        target_secrets[group][key_type][key] = "YOUR_SECRET"

        with open(my_secrets_file, "w") as f:
            json.dump(target_secrets, f, indent=4)

        print(
            f"Secrets file '{my_secrets_file}' updated with missing keys from '{example_secrets_file}'."
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {str(e)}")


def export_example_json(
    secrets_file: str = "secrets_my.json", example_file: str = "secrets_example.json"
):
    """Exports an example secrets file with placeholder values."""
    try:
        secrets = load_json_file(secrets_file)

        for group_data in secrets.values():
            for key_type in ["Inner Keys", "Outter Keys"]:
                for key in group_data.get(key_type, {}):
                    group_data[key_type][key] = "YOUR_SECRET"

        with open(example_file, "w") as f:
            json.dump(secrets, f, indent=4)

        print(f"Example secrets file exported to '{example_file}'")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {str(e)}")


def main():
    if len(sys.argv) == 1:
        command = input("Please enter the command (init/export): ").lower()
    else:
        command = sys.argv[1].lower()

    if command == "init":
        init_json()
    elif command == "export":
        export_example_json()
    else:
        print("Invalid command. Use 'init' or 'export'.")


if __name__ == "__main__":
    # print(load_inner_keys("test"))
    main()
